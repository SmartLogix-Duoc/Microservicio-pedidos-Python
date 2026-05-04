from typing import List, Optional
from pedidos.database.mongo_connection import db
from pedidos.domain.entities import Order

class OrderRepository:
    """
    Capa de Repositorio (CSR).
    Se encarga ÚNICAMENTE de la persistencia en MongoDB.
    """
    def __init__(self):
        # Usamos la colección 'orders' (en inglés para mantener el estándar)
        self.collection = db['orders']

    # ==========================================
    # C - CREATE
    # ==========================================
    def create_order(self, order: Order) -> Order:
        # Convertimos la Entidad Pydantic a diccionario
        order_dict = order.model_dump()
        
        # Insertamos en MongoDB
        self.collection.insert_one(order_dict)
        return order

    # ==========================================
    # R - READ
    # ==========================================
    def get_by_id(self, order_id: str) -> Optional[Order]:
        # Buscamos por el campo order_id (definido en nuestra entidad)
        data = self.collection.find_one({"order_id": order_id})
        
        if data:
            # Eliminamos el _id de Mongo si Pydantic no lo espera o lo manejamos
            data.pop('_id', None) 
            return Order(**data)
        return None

    def get_all(self) -> List[Order]:
        cursor = self.collection.find()
        orders = []
        for doc in cursor:
            doc.pop('_id', None) # Limpiamos el ID interno de Mongo
            orders.append(Order(**doc))
        return orders

    # ==========================================
    # U - UPDATE
    # ==========================================
    def update_status(self, order_id: str, new_status: str) -> bool:
        # Actualizamos el campo 'status' (alineado con la entidad)
        result = self.collection.update_one(
            {"order_id": order_id},
            {"$set": {"status": new_status}}
        )
        return result.modified_count > 0

    # ==========================================
    # D - DELETE
    # ==========================================
    def delete_order(self, order_id: str) -> bool:
        result = self.collection.delete_one({"order_id": order_id})
        return result.deleted_count > 0