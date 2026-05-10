# pedidos/repositories/supabase_client.py
import os

class SupabaseClient:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("❌ ERROR: Faltan las variables SUPABASE en el .env")
        
        # Quitamos el slash final si existe para evitar errores en las URLs
        self.supabase_url = self.supabase_url.rstrip('/')
        
        # Headers genéricos (sin especificar esquema aún)
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }