# pedidos/repositories/order_repository.py
import requests
from .supabase_client import SupabaseClient

class OrderRepository(SupabaseClient):
    def __init__(self):
        super().__init__()
        
        # Headers exclusivos para conectarse a Pedidos (Ya no hay rastro de inventario)
        self.headers_pedidos = self.headers.copy()
        self.headers_pedidos['Accept-Profile'] = 'pedidos'
        self.headers_pedidos['Content-Profile'] = 'pedidos'

    # --- MÉTODOS DE PEDIDOS (Única responsabilidad de este archivo) ---
    
    def get_all(self):
        url = f"{self.supabase_url}/rest/v1/orders?select=*"
        response = requests.get(url, headers=self.headers_pedidos, timeout=5)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Supabase GET Error: {response.text}")

    def get_by_id(self, order_id: str):
        url = f"{self.supabase_url}/rest/v1/orders?order_id=eq.{order_id}&select=*"
        response = requests.get(url, headers=self.headers_pedidos, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
        raise Exception(f"Supabase GET Error: {response.text}")

    def create_order(self, payload: dict):
        url = f"{self.supabase_url}/rest/v1/orders"
        response = requests.post(url, headers=self.headers_pedidos, json=payload, timeout=5)
        if response.status_code in [200, 201]:
            return response.json()[0]
        raise Exception(f"Supabase POST Order Error: {response.text}")

    def create_order_items(self, payload: list):
        url = f"{self.supabase_url}/rest/v1/order_items"
        response = requests.post(url, headers=self.headers_pedidos, json=payload, timeout=5)
        if response.status_code not in [200, 201]:
            raise Exception(f"Supabase POST Items Error: {response.text}")
        return response.json()

    def update_status(self, order_id: str, new_status: str):
        url = f"{self.supabase_url}/rest/v1/orders?order_id=eq.{order_id}"
        payload = {"status": new_status}
        response = requests.patch(url, headers=self.headers_pedidos, json=payload, timeout=5)
        if response.status_code in [200, 204]:
            return response.json()[0] if response.json() else None
        raise Exception(f"Supabase UPDATE Error: {response.text}")

    def delete(self, order_id: str):
        url = f"{self.supabase_url}/rest/v1/orders?order_id=eq.{order_id}"
        response = requests.delete(url, headers=self.headers_pedidos, timeout=5)
        if response.status_code in [200, 204]:
            return True
        raise Exception(f"Supabase DELETE Error: {response.text}")