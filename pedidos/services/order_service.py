from pedidos.database.mongo_connection import db
from .Factory import OrderFactory

class OrderService:
    #Capa de servicio CSR

    def __init__(self):
        # Instanciamos la conexión a la base de datos
        self.connection = db['pedidos']

    def procesar_nuevo_pedido(self, user_id: str, items: list, tipo: str):
        # 1. Usamos el Factory Method para crear y validar el pedido
        pedido_creado = OrderFactory.crear_pedido(user_id, items, tipo)
        
        # 2. Usamos el Repositorio para guardarlo en MongoDB
        pedido_guardado = self.repository.crear_pedido(pedido_creado)
        
        # 3. Devolvemos el resultado en formato diccionario para el Controller
        return pedido_guardado.model_dump()

    def obtener_todos_los_pedidos(self):
        # Le pedimos al repositorio todos los pedidos
        pedidos = self.repository.obtener_todos()
        # Los devolvemos como una lista de diccionarios
        return [p.model_dump() for p in pedidos]
    
    def actualizar_estado_pedido(self, pedido_id: str, nuevo_estado: str):
        # 1. Validamos que el estado sea correcto según nuestro Enum
        # 2. Llamamos al repositorio para actualizarlo en MongoDB
        pedido_actualizado = self.repository.actualizar_estado(pedido_id, nuevo_estado)
        return pedido_actualizado

    def eliminar_pedido(self, pedido_id: str):  
        # 1. Le decimos al repositorio que lo borre
        resultado = self.repository.eliminar(pedido_id)
        return resultado