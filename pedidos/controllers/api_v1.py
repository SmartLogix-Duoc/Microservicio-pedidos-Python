from enum import Enum
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from pedidos.services.order_service import OrderService
from rest_framework.permissions import IsAuthenticated

# ==========================================
# 1. ENUMS
# ==========================================
class OrderState(str, Enum):
    PROCCESING = "Procesando"
    WAITING = "Pendiente"
    CANCELED = "Cancelado"
    DELIVERED = "Entregado"
    SHIPPED = "Enviado"

class OrderType(str, Enum):
    NATIONAL = "NATIONAL"
    INTERNATIONAL = "INTERNATIONAL"


# ==========================================
# 2. SERIALIZERS
# ==========================================
class ItemOrderSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    amount = serializers.IntegerField()
    unit_price = serializers.FloatField()

class OrderSerializer(serializers.Serializer):
    order_id = serializers.CharField(read_only=True)
    user_id = serializers.CharField(max_length=100)
    order_type = serializers.ChoiceField(choices=[e.value for e in OrderType])
    total = serializers.FloatField(read_only=True)
    status = serializers.ChoiceField(
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
    datos_actualizados = OrderStatusUpdateSerializer()

class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField(help_text="Descripción detallada del problema")


# ==========================================
# 3. CONTROLLER (ViewSet)
# ==========================================
class OrderController(viewsets.ViewSet):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OrderService()

    @extend_schema(
        summary="Listar todos los pedidos",
        responses={200: OrderSerializer(many=True)},
        tags=["Orders"]
    )
    def list(self, request):
        try:
            orders = self.service.get_all_orders()
            return Response({"success": True, "data": orders}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Obtener un pedido por UUID",
        parameters=[
            OpenApiParameter(name='id', type=str, location=OpenApiParameter.PATH, description='UUID del pedido (order_id)')
        ],
        responses={200: OrderSerializer, 404: ErrorResponseSerializer},
        tags=["Orders"]
    )
    def retrieve(self, request, pk=None):
        try:
            # Buscamos por el UUID (pk) usando el servicio
            order = self.service.get_order_by_id(pk)
            if not order:
                return Response({"error": f"Pedido {pk} no encontrado."}, status=status.HTTP_404_NOT_FOUND)
            return Response({"success": True, "data": order}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Crear un nuevo pedido",
        request=OrderSerializer,
        responses={201: OrderSerializer, 400: ErrorResponseSerializer},
        tags=["Orders"]
    )
    def create(self, request):
        try:
            data = request.data
            new_order = self.service.process_new_order(
                data.get('user_id'), 
                data.get('items'), 
                data.get('order_type')
            )
            return Response({"success": True, "data": new_order}, status=status.HTTP_201_CREATED)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Actualizar estado de un pedido",
        parameters=[
            OpenApiParameter(name='id', type=str, location=OpenApiParameter.PATH, description='UUID del pedido')
        ],
        request=OrderStatusUpdateSerializer,
        responses={200: OrderUpdateResponseSerializer, 404: ErrorResponseSerializer},
        tags=["Orders"]
    )
    def update(self, request, pk=None):
        serializer = OrderStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Enviamos el UUID (pk) al servicio
        actualizado = self.service.update_order_status(pk, serializer.validated_data.get('status'))

        if not actualizado:
            return Response({"error": f"No se pudo actualizar. UUID {pk} no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "message": f"Pedido {pk} actualizado con éxito",
            "datos_actualizados": serializer.validated_data
        }, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Eliminar pedido",
        parameters=[
            OpenApiParameter(name='id', type=str, location=OpenApiParameter.PATH, description='UUID del pedido')
        ],
        responses={204: None, 404: ErrorResponseSerializer},
        tags=["Orders"]
    )
    def destroy(self, request, pk=None):
        # Conectamos el borrado real por UUID
        eliminado = self.service.delete_order(pk)

        if not eliminado:
            return Response(
                {"error": f"No se encontró el pedido con UUID {pk}."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(status=status.HTTP_204_NO_CONTENT)