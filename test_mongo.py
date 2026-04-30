# test_mongo.py
from pedidos.database.mongo_connection import db

def probar_conexion():
    try:
        # 1. Creamos un pedido de prueba
        pedido_test = {
            "usuario_id": 1,
            "producto": "Laptop Gamer",
            "cantidad": 1,
            "estado": "pago_pendiente"
        }
        
        # 2. Insertamos en una colección llamada 'test_pedidos'
        resultado = db.test_pedidos.insert_one(pedido_test)
        
        print(f"✅ ¡Conexión exitosa! ID del pedido insertado: {resultado.inserted_id}")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")

if __name__ == "__main__":
    probar_conexion()