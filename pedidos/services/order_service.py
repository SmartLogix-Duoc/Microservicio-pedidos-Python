from pedidos.database.mongo_connection import db
from .Factory import OrderFactory
# IMPORTANTE: Asegúrate de importar tu repositorio real aquí
from pedidos.repositories.mongo_client import OrderRepository

class OrderService:
    """Capa de Servicio (CSR) - Contiene la lógica de negocio"""

    def __init__(self):
        # Seleccionamos la colección en Mongo (equivalente a la tabla). 
        # La cambié a 'orders' para mantener el inglés, pero si tu BD 
        # ya creó 'test_pedidos' o 'pedidos', puedes dejarla así.
        self.collection = db['orders'] 
        
        # Instanciamos el repositorio pasándole la conexión a la BD
        self.repository = OrderRepository() 

    def process_new_order(self, user_id: str, items: list, order_type: str):
        # 1. Usamos el Factory Method para crear y validar el pedido
        created_order = OrderFactory.create_order(user_id, items, order_type)
        
        # 2. Usamos el Repositorio para guardarlo en MongoDB
        saved_order = self.repository.create_order(created_order)
        
        # 3. Devolvemos el resultado en formato diccionario para el Controller
        return saved_order.model_dump()

    def get_all_orders(self):
        # Le pedimos al repositorio todos los pedidos
        orders = self.repository.get_all()
        
        # Los devolvemos como una lista de diccionarios
        return [order.model_dump() for order in orders]
    
    def update_order_status(self, order_id: str, new_status: str):
        # 1. Validamos que el estado sea correcto según nuestro Enum (opcional aquí o en modelo)
        # 2. Llamamos al repositorio para actualizarlo en MongoDB
        updated_order = self.repository.update_status(order_id, new_status)
        return updated_order

    def delete_order(self, order_id: str):  
        # 1. Le decimos al repositorio que lo borre
        result = self.repository.delete(order_id)
        return result