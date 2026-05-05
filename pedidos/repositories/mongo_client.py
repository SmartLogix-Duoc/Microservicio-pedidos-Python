from typing import List
from pedidos.database.mongo_connection import db
from pedidos.domain.entities import Order

class OrderRepository:
    def __init__(self):
        self.collection = db['orders']

    def create_order(self, order: Order) -> Order:
        order_dict = order.model_dump()
        self.collection.insert_one(order_dict)
        return order

    def get_by_id(self, order_id: str):
        # Buscamos STRING contra STRING en la columna 'order_id'
        documento = self.collection.find_one({"order_id": order_id})
        if documento:
            documento.pop('_id', None) # Quitamos el ObjectId de Mongo para que Pydantic no explote
            return Order(**documento)
        return None

    def get_all(self) -> List[Order]:
        cursor = self.collection.find()
        orders = []
        for doc in cursor:
            doc.pop('_id', None)
            orders.append(Order(**doc))
        return orders

    def update_status(self, order_id: str, new_status: str) -> bool:
        # IMPORTANTE: Aquí NO debe haber nada de ObjectId
        filtro = {"order_id": order_id} 
        resultado = self.collection.update_one(
            filtro, 
            {"$set": {"status": new_status}}
        )
        return resultado.matched_count > 0

    def delete(self, order_id: str) -> bool:
        filtro = {"order_id": order_id} 
        resultado = self.collection.delete_one(filtro)
        return resultado.deleted_count > 0