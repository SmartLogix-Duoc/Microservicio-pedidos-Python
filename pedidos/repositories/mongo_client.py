# pedidos/repositories/mongo_client.py
from pymongo import MongoClient
from pedidos.domain.entities import Order
from typing import List, Optional

class MongoPedidoRepository:
    """
    Esta clase se encarga ÚNICAMENTE de hablar con MongoDB.
    No toma decisiones de negocio, solo obedece órdenes de guardar, leer, etc.
    """
    def __init__(self):
        # Nos conectamos a MongoDB (esto luego se pone en variables de entorno)
        self.collection = self.db['pedidos']

    # ==========================================
    # C - CREATE (Crear)
    # ==========================================
    def crear_pedido(self, pedido: Order) -> Order:
        # Convertimos nuestra Entidad Pydantic a un diccionario (JSON) que Mongo entienda
        pedido_dict = pedido.model_dump()
        
        # Insertamos en la base de datos
        self.collection.insert_one(pedido_dict)
        return pedido

    # ==========================================
    # R - READ (Leer)
    # ==========================================
    def obtener_por_id(self, order_id: str) -> Optional[Order]:
        # Buscamos en Mongo el documento que coincida con el orderId
        data = self.collection.find_one({"orderId": order_id})
        
        if data:
            # Si lo encontramos, lo volvemos a convertir en nuestra Entidad Pedido
            return Order(**data)
        return None

    def obtener_todos(self) -> List[Order]:
        # Traemos todos los pedidos
        cursor = self.collection.find()
        # Convertimos la lista de diccionarios a una lista de Entidades Pedido
        return [Order(**doc) for doc in cursor]

    # ==========================================
    # U - UPDATE (Actualizar)
    # ==========================================
    def actualizar_estado(self, order_id: str, nuevo_estado: str) -> bool:
        # Actualizamos solo el campo "estado" de un pedido específico
        resultado = self.collection.update_one(
            {"orderId": order_id},
            {"$set": {"estado": nuevo_estado}}
        )
        return resultado.modified_count > 0

    # ==========================================
    # D - DELETE (Eliminar)
    # ==========================================
    def eliminar_pedido(self, order_id: str) -> bool:
        # Borramos el pedido de la base de datos
        resultado = self.collection.delete_one({"orderId": order_id})
        return resultado.deleted_count > 0