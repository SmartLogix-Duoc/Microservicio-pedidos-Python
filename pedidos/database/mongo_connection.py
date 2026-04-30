import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

# 1. Calculamos la ruta EXACTA a la raíz de tu proyecto
# __file__ es este archivo. Subimos 3 niveles: database -> pedidos -> Raíz
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / '.env'

# 2. Prints de diagnóstico (luego los borramos)
print(f"DEBUG - Buscando archivo .env exactamente en: {ENV_PATH}")
print(f"DEBUG - ¿El archivo físico realmente existe ahí?: {ENV_PATH.exists()}")

# 3. Forzamos a dotenv a leer ese archivo específico
load_dotenv(dotenv_path=ENV_PATH)

# 4. Extraemos la variable
mi_uri_secreta = os.getenv("MONGO_URI")
print(f"DEBUG - URI CARGADA: {mi_uri_secreta}")

if not mi_uri_secreta:
    raise ValueError("¡Error! Variable MONGO_URI no encontrada")

# 5. Conexión a Mongo
try:
    client = MongoClient(mi_uri_secreta)
    db = client['ecommerce_pedidos']
except Exception as e:
    print(f"Error al conectar a MongoDB: {e}")