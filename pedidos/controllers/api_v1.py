# pedidos/controllers/api_v1.py
import base64
import json
from enum import Enum
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, inline_serializer
from rest_framework.permissions import AllowAny

from pedidos.services.order_service import OrderService


# ==========================================
# 1. ENUMS
# ==========================================
class OrderState(str, Enum):
    PROCCESING = "Procesando"
    WAITING    = "Pendiente"
    CANCELED   = "Cancelado"
    DELIVERED  = "Entregado"
    SHIPPED    = "Enviado"

class OrderType(str, Enum):
    NATIONAL      = "NATIONAL"
    INTERNATIONAL = "INTERNATIONAL"


# ==========================================
# 2. SERIALIZERS
# ==========================================
class ItemOrderSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(help_text="ID del producto en el inventario")
    amount     = serializers.IntegerField(help_text="Cantidad a pedir")
    unit_price = serializers.FloatField(help_text="Precio unitario al momento de la compra", required=False)

class OrderSerializer(serializers.Serializer):
    order_id   = serializers.CharField(read_only=True)
    user_id    = serializers.CharField(read_only=True)
    order_type = serializers.ChoiceField(choices=[e.value for e in OrderType])
    total      = serializers.FloatField(read_only=True)
    status     = serializers.ChoiceField(
        choices=[e.value for e in OrderState],
        default=OrderState.WAITING.value
    )
    items = ItemOrderSerializer(many=True)

class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[e.value for e in OrderState],
        help_text="El nuevo estado del pedido"
    )

class OrderUpdateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    datos   = OrderStatusUpdateSerializer()

class ErrorResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    error   = serializers.CharField(help_text="Descripción detallada del problema")


# ==========================================
# 3. CONTROLLER (ViewSet)
# ==========================================
class OrderController(viewsets.ViewSet):
    authentication_classes = []
    permission_classes     = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OrderService()

    # GET /api/orders/
    @extend_schema(
        summary="Listar todos los pedidos",
        description="Obtiene una lista completa de todas las órdenes en la base de datos.",
        responses={
            200: inline_serializer(
                name='ListOrdersResponse',
                fields={
                    'success': serializers.BooleanField(),
                    'data': OrderSerializer(many=True)
                }
            ),
            500: ErrorResponseSerializer
        },
        tags=["Orders"]
    )
    def list(self, request):
        try:
            orders = self.service.get_all_orders()
            return Response({"success": True, "data": orders}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # POST /api/orders/
    @extend_schema(
        summary="Crear un nuevo pedido",
        description="Registra una nueva orden. El user_id se extrae automáticamente del token JWT.",
        request=OrderSerializer,
        responses={
            201: inline_serializer(
                name='CreateOrderResponse',
                fields={
                    'success': serializers.BooleanField(),
                    'data': inline_serializer(
                        name='CreateOrderData',
                        fields={
                            'order_id': serializers.CharField(),
                            'total': serializers.FloatField(),
                            'items': ItemOrderSerializer(many=True),
                            'message': serializers.CharField(),
                        }
                    )
                }
            ),
            400: ErrorResponseSerializer,
            401: OpenApiResponse(description="No Autorizado - Falta el token")
        },
        tags=["Orders"],
        examples=[
            OpenApiExample(
                "Ejemplo de Pedido",
                value={
                    "order_type": "NATIONAL",
                    "items": [
                        {"product_id": 1, "amount": 2},
                        {"product_id": 2, "amount": 1}
                    ]
                }
            )
        ]
    )
    def create(self, request):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return Response(
                    {"error": "No se proporcionó el header de Authorization"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header

            # Extraer userId del payload del JWT sin validar firma
            payload_b64 = token.split('.')[1]
            payload_b64 += '=' * (4 - len(payload_b64) % 4)
            payload = json.loads(base64.b64decode(payload_b64).decode('utf-8'))
            user_id = str(payload.get('userId'))

            data = request.data

            new_order = self.service.process_new_order(
                user_id=user_id,
                items_raw=data.get('items', []),
                order_type=data.get('order_type'),
                token=token
            )
            return Response({"success": True, "data": new_order}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # PATCH /api/orders/{id}/
    @extend_schema(
        summary="Actualizar estado del pedido",
        description="Modifica únicamente el estado de una orden existente por su ID.",
        request=OrderStatusUpdateSerializer,
        responses={
            200: OrderUpdateResponseSerializer,
            400: ErrorResponseSerializer,
            404: OpenApiResponse(description="Pedido no encontrado")
        },
        tags=["Orders"]
    )
    def update(self, request, pk=None):
        serializer = OrderStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        actualizado = self.service.update_order_status(pk, serializer.validated_data.get('status'))
        if not actualizado:
            return Response(
                {"error": f"No se pudo actualizar. ID {pk} no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"message": f"Pedido {pk} actualizado", "datos": serializer.validated_data},
            status=status.HTTP_200_OK
        )

    # DELETE /api/orders/{id}/
    @extend_schema(
        summary="Eliminar un pedido",
        description="Elimina físicamente una orden de la base de datos usando su ID.",
        responses={
            204: OpenApiResponse(description="Eliminado exitosamente (Sin contenido)"),
            404: OpenApiResponse(description="Pedido no encontrado")
        },
        tags=["Orders"]
    )
    def destroy(self, request, pk=None):
        eliminado = self.service.delete_order(pk)
        if not eliminado:
            return Response({"error": "No encontrado"}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)