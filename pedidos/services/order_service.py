from .Factory import OrderFactory
from pedidos.repositories.mongo_client import OrderRepository

class OrderService:
    def __init__(self):
        # El Service solo debe hablar con el Repositorio
        self.repository = OrderRepository() 

    def process_new_order(self, user_id: str, items: list, order_type: str):
        created_order = OrderFactory.create_order(user_id, items, order_type)
        saved_order = self.repository.create_order(created_order)
        return saved_order.model_dump()

    def get_all_orders(self):
        orders = self.repository.get_all()
        return [order.model_dump() for order in orders]
    
    def update_order_status(self, order_id: str, new_status: str):
        # Aquí pasamos el UUID string directo al repositorio
        return self.repository.update_status(order_id, new_status)

    def get_order_by_id(self, order_id: str):
        order = self.repository.get_by_id(order_id)
        if order:
            return order.model_dump()
        return None
    
    def delete_order(self, order_id: str):
        return self.repository.delete(order_id)