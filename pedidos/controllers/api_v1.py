from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from pedidos.services.order_service import OrderService
from rest_framework.permissions import IsAuthenticated

# 1. Definimos cómo se ve un "Item" (El sub-producto)
class ItemOrderSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    amount = serializers.IntegerField()
    unit_price = serializers.FloatField()

# 2. Definimos cómo se ve el Pedido completo
class OrderSerializer(serializers.Serializer):
    order_id = serializers.CharField(read_only=True)
    user_id = serializers.CharField(max_length=100)
    order_type = serializers.CharField()
    total = serializers.FloatField(read_only=True) # El total lo calcula el backend, el usuario no debe enviarlo
    status = serializers.CharField(default="WAITING")
    # AQUI ESTA LA MAGIA: Le decimos a Swagger que esto es una lista de la clase de arriba
    items = ItemOrderSerializer(many=True) 

class OrderController(APIView):
    
    """
    Controller Layer (CSR). 
    Receives HTTP requests (JSON), passes them to the Service layer, 
    and returns HTTP responses to the Frontend.
    """

    #permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OrderService()

    @extend_schema(
        summary="Listar todos los pedidos",
        description="Obtiene una lista completa de los pedidos almacenados en MongoDB.",
        responses={200: OrderSerializer(many=True)}, # Le decimos a Swagger: "Devolveré una lista de OrderSerializer"
        tags=["Orders"]
    )
    def get(self, request):
        """Maneja las peticiones GET (Leer)"""
        try:
            orders = self.service.get_all_orders()
            return Response({"success": True, "data": orders}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Crear un nuevo pedido",
        request=OrderSerializer, # Le decimos a Swagger: "El usuario me tiene que mandar este formato"
        responses={201: OrderSerializer},
        examples=[
            OpenApiExample(
                'Ejemplo de Pedido Correcto',
                value={
                    "user_id": "usr_987654",
                    "order_type": "INTERNATIONAL", # ACTUALIZADO: Para que ya no te dé el 400
                    "items": [
                        {"product_id": "prod_001", "amount": 2, "unit_price": 75.50},
                        {"product_id": "prod_002", "amount": 1, "unit_price": 120.00}
                    ]
                }
            )
        ],
        tags=["Orders"]
    )
    def post(self, request):
        """Maneja las peticiones POST (Crear)"""
        try:
            data = request.data
            user_id = data.get('user_id')
            items = data.get('items')
            order_type = data.get('order_type')

            new_order = self.service.process_new_order(user_id, items, order_type)
            
            return Response(
                {"success": True, "message": "Pedido creado", "data": new_order}, 
                status=status.HTTP_201_CREATED
            )
        except ValueError as ve:
            return Response({"success": False, "error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Actualizar estado de un pedido",
        parameters=[
            # OpenApiParameter le dice a Swagger que ponga una cajita de texto en la URL para pedir el ID
            OpenApiParameter(name='order_id', description='ID único del pedido en MongoDB', required=True, type=str)
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["WAITING", "PENDING", "SHIPPED", "DELIVERED"]}
                }
            }
        },
        responses={
            200: OpenApiExample('Respuesta Exitosa', value={"message": "Pedido actualizado", "data": {"status": "SHIPPED"}}),
            404: OpenApiExample('No encontrado', value={"error": "Pedido no encontrado"})
        },
        tags=["Orders"]
    )
    def put(self, request, order_id):
        """Actualiza el estado de un pedido existente."""
        new_status = request.data.get('status')
        if not new_status:
            return Response({"error": "El campo 'status' es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)
        
        updated_order = self.service.update_order_status(order_id, new_status)
        
        if updated_order:
            return Response({"message": "Pedido actualizado", "data": updated_order}, status=status.HTTP_200_OK)
        return Response({"error": "Pedido no encontrado"}, status=status.HTTP_404_NOT_FOUND)  
    
    @extend_schema(
        summary="Eliminar pedido",
        parameters=[
            OpenApiParameter(name='order_id', description='ID único del pedido', required=True, type=str)
        ],
        responses={204: None, 404: OpenApiExample('Error', value={"error": "No se pudo eliminar el pedido"})},
        tags=["Orders"]
    )
    def delete(self, request, order_id):
        """Elimina un pedido del sistema."""
        success = self.service.delete_order(order_id)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "No se pudo eliminar el pedido"}, status=status.HTTP_404_NOT_FOUND)