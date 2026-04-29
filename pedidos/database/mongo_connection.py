import os
from dotenv import load_dotenv
from pymongo import MongoClient


# Buscamos el .env en la raíz (dos niveles arriba de este archivo)
load_dotenv()

class MongoDBClient:
    """Clase Singleton para gestionar la conexión a MongoDB"""
    _client = None

    @classmethod
    def get_db(cls):
        if cls._client is None:
            uri = os.getenv("MONGO_URI")
            if not uri:
                raise ValueError("Variable MONGO_URI no encontrada")
            cls._client = MongoClient(uri)
        
        # Retornamos la base de datos específica
        return cls._client['ecommerce_pedidos']

# Instancia lista para usar
db = MongoDBClient.get_db()