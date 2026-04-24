# pedidos/controllers/api_v1.py
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from pedidos.services.order_service import OrderService

class OrderSerializer(serializers.Serializer):  
    id = serializers.CharField(read_only=True)
    customer_name = serializers.CharField(max_length=100)
    total = serializers.FloatField()
    status = serializers.CharField(default="WAITING")
    items = serializers.ListField(child=serializers.CharField())
    
class PedidoController(APIView):
    """
    Capa de Controlador (CSR). 
    Su única función es recibir la petición HTTP (JSON), 
    pasársela al Servicio y devolver una respuesta HTTP al Frontend.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Instanciamos nuestro servicio
        self.service = OrderService()

    @extend_schema(
        summary="Listar todos los pedidos",
        description="Obtiene una lista completa de los pedidos almacenados en MongoDB.",
        responses={200: OrderSerializer(many=True)},
        tags=["Pedidos"]
    )
    def get(self, request):
        """Maneja las peticiones GET (Leer)"""
        try:
            pedidos = self.service.obtener_todos_los_pedidos()
            return Response({"success": True, "data": pedidos}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @extend_schema(
        summary="Crear un nuevo pedido",
        request=OrderSerializer,
        responses={201: OrderSerializer},
        examples=[
            OpenApiExample(
                'Ejemplo de Pedido',
                value={
                    "customer_name": "Maxi Olguin",
                    "total": 150.50,
                    "items": ["Laptop", "Mouse"]
                }
            )
        ],
        tags=["Pedidos"]
    )
    def post(self, request):
        """Maneja las peticiones POST (Crear)"""
        try:
            # Extraemos los datos del JSON que envía React
            datos = request.data
            user_id = datos.get('userId')
            items = datos.get('items')
            tipo = datos.get('tipo')

            # Llamamos al servicio para que haga toda la magia
            nuevo_pedido = self.service.procesar_nuevo_pedido(user_id, items, tipo)
            
            return Response(
                {"success": True, "message": "Pedido creado", "data": nuevo_pedido}, 
                status=status.HTTP_201_CREATED
            )
        # Si Pydantic detecta un error de validación, lo capturamos aquí
        except ValueError as ve:
            return Response({"success": False, "error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Actualizar estado de un pedido",
        parameters=[
            OpenApiParameter(name='order_id', description='ID único del pedido en MongoDB', required=True, type=str)
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["PENDING", "SHIPPED", "DELIVERED"]}
                }
            }
        },
        responses={
            200: OpenApiExample('Respuesta Exitosa', value={"message": "Pedido actualizado", "id": "123"}),
            404: OpenApiExample('No encontrado', value={"error": "Pedido no existe"})
        },
        tags=["Pedidos"]
    )
    def put(self, request, order_id):
        """
        Actualiza el estado de un pedido existente.
        """
        new_status = request.data.get('status')
        if not new_status:
            return Response({"error": "El campo 'status' es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delegamos la lógica al servicio
        updated_order = self.service.update_order_status(order_id, new_status)
        
        if updated_order:
            return Response({"message": "Pedido actualizado", "data": updated_order}, status=status.HTTP_200_OK)
        return Response({"error": "Pedido no encontrado"}, status=status.HTTP_404_NOT_FOUND)  

    
    @extend_schema(
        summary="Eliminar pedido",
        parameters=[
            OpenApiParameter(name='order_id', description='ID único del pedido', required=True, type=str)
        ],
        responses={204: None, 404: OpenApiExample('Error', value={"error": "ID inválido"})},
        tags=["Pedidos"]
    )
    def delete(self, request, order_id):
        #Elimina pedidos
        #Delegamos la eliminacion al serivicio 
        success = self.service.delete_order(order_id)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "No se pudo eliminar el pedido"}, status=status.HTTP_404_NOT_FOUND)