import os
import requests
from .Factory import OrderFactory
from pedidos.repositories.supabase_client import OrderRepository

class OrderService:
    def __init__(self):
        self.repository = OrderRepository()
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        # Headers base para Supabase (usando Service Role para evitar el 403)
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    # --- MÉTODOS DE CONSULTA (RESTURADOS) ---

   # Dentro de class OrderService en pedidos/services/order_service.py

    def get_all_orders(self):
        # Llama al nuevo repositorio de Supabase
        orders = self.repository.get_all()
        return [o.model_dump() for o in orders]

    def get_order_by_id(self, order_id: str):
        order = self.repository.get_by_id(order_id)
        return order.model_dump() if order else None

    def update_order_status(self, order_id: str, new_status: str):
        # Llama al update_status del repositorio que creamos antes
        return self.repository.update_status(order_id, new_status)

    def delete_order(self, order_id: str):
        # Llama al delete del repositorio
        return self.repository.delete(order_id)

    # --- MÉTODO DE PROCESAMIENTO (ACTUALIZADO) ---

    def process_new_order(self, user_id: str, items_raw: list, order_type: str, token: str):
        validated_items = []
        total_order_price = 0

        # 1. VALIDAR PRODUCTOS EN SUPABASE (Schema public)
        for item in items_raw:
            product_id = item.get('product_id')
            url_get = f"{self.supabase_url}/rest/v1/products?id=eq.{product_id}&select=*"

            response = requests.get(url_get, headers=self.headers, timeout=5)
            if response.status_code == 200 and response.json():
                p = response.json()[0]
                unit_price = float(p['price'])
                subtotal = unit_price * item['amount']
                total_order_price += subtotal
                
                validated_items.append({
                    "product_id": str(p['id']),
                    "name": p.get('name'),
                    "amount": item['amount'],
                    "unit_price": unit_price
                })
            else:
                raise Exception(f"Producto {product_id} no válido o no encontrado en Supabase.")

        # 2. GUARDAR EN SUPABASE (Schema: pedidos)
        # 2a. Cabecera (pedidos.order)
        try:
            url_order = f"{self.supabase_url}/rest/v1/pedidos/order"
            order_payload = {
                "user_id": user_id,
                "order_type": order_type,
                "total_price": total_order_price
            }
            res_order = requests.post(url_order, headers=self.headers, json=order_payload)
            
            if res_order.status_code in [200, 201]:
                supabase_order_id = res_order.json()[0]['id']
                
                # 2b. Detalles (pedidos.itemorder)
                url_items = f"{self.supabase_url}/rest/v1/pedidos/itemorder"
                items_payload = [{
                    "order_id": supabase_order_id,
                    "product_id": v_item["product_id"],
                    "quantity": v_item["amount"],
                    "unit_price": v_item["unit_price"]
                } for v_item in validated_items]
                
                requests.post(url_items, headers=self.headers, json=items_payload)
        except Exception as e:
            print(f"Error opcional al guardar en SQL: {e}")

        # 3. GUARDAR EN MONGODB (Persistencia principal de pedidos)
        created_order = OrderFactory.create_order(user_id, validated_items, order_type)
        saved_order = self.repository.create_order(created_order)
        
        return saved_order.model_dump()