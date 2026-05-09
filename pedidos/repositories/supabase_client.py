import os
import requests
from typing import List, Optional
from pedidos.domain.entities import Order



class OrderRepository:
    def __init__(self):
        # Asegúrate de que en el .env esta variable tenga la URL que empieza con https://
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        # Validación de seguridad para que no vuelva a dar el error "None"
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("❌ ERROR: Faltan las variables SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en el .env")
        
        # URL final apuntando a la tabla 'order'. 
        # rstrip('/') evita problemas si pusiste un slash al final en el .env
        self.base_url = f"{self.supabase_url.rstrip('/')}/rest/v1/order"
        
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
            # 👇 ESTO ES MAGIA Pura: Le dice a PostgREST que use tu schema 'pedidos'
            "Accept-Profile": "pedidos",
            "Content-Profile": "pedidos"
        }

    def create_order(self, order: Order) -> Order:
        """Inserta la cabecera de la orden en la tabla pedidos.order"""
        order_dict = order.model_dump()
        
        payload = {
            "user_id": str(order_dict.get("user_id")),
            "order_type": order_dict.get("order_type"),
            "status": order_dict.get("status", "PENDING"),
            "total_price": order_dict.get("total", 0.0) # Asegúrate de mapear tu total si tu BD lo pide
        }

        response = requests.post(self.base_url, headers=self.headers, json=payload)
        
        if response.status_code in [200, 201]:
            # Pydantic a veces necesita recuperar el ID generado por la BD,
            # pero por ahora devolvemos la orden para no romper tu Service
            return order
        else:
            raise Exception(f"Error al crear orden en Supabase: {response.text}")

    def get_by_id(self, order_id: str) -> Optional[Order]:
        """Busca una orden por su ID en el schema pedidos"""
        # OJO: Si la columna primaria en Postgres se llama 'order_id' en lugar de 'id', cambia esto a ?order_id=eq.{order_id}
        url = f"{self.base_url}?id=eq.{order_id}&select=*"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                return Order(**data[0])
        return None

    def get_all(self) -> List[Order]:
        """Obtiene todas las órdenes de la tabla pedidos.order"""
        url = f"{self.base_url}?select=*"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return [Order(**doc) for doc in response.json()]
        return []

    def update_status(self, order_id: str, new_status: str) -> bool:
        """Actualiza el estado de una orden (PATCH)"""
        url = f"{self.base_url}?id=eq.{order_id}"
        payload = {"status": new_status}
        
        response = requests.patch(url, headers=self.headers, json=payload)
        return response.status_code in [200, 204]

    def delete(self, order_id: str) -> bool:
        """Elimina una orden (DELETE)"""
        url = f"{self.base_url}?id=eq.{order_id}"
        
        response = requests.delete(url, headers=self.headers)
        return response.status_code in [200, 204]