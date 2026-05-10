# pedidos/clients/inventory_client.py
import dotenv
import requests

class InventoryApiClient:
    def __init__(self):
        # URL base del microservicio de tu compañero (Spring Boot)
        self.base_url = dotenv.get("INVENTORY_SERVICE_URL")

    def get_headers(self, token: str):
        # Como mencionaste, ambos deben compartir el JWT para que Java te deje pasar
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

    def check_stock(self, product_id: int, warehouse_id: int, qty: int, token: str):
        # Hace el GET al Spring Boot: /inventory/check?prod=1&wh=2&qty=5
        url = f"{self.base_url}/check?prod={product_id}&wh={warehouse_id}&qty={qty}"
        
        response = requests.get(url, headers=self.get_headers(token), timeout=5)
        
        if response.status_code == 200:
            return response.json() # Asumimos que devuelve la info del producto o True
        elif response.status_code == 400:
            raise Exception(f"Stock insuficiente para el producto {product_id}")
        else:
            raise Exception(f"Error comunicándose con el inventario: {response.status_code}")

    def deduct_stock(self, product_id: int, warehouse_id: int, qty: int, token: str):
        # Hace el POST al Spring Boot para registrar la VENTA
        url = f"{self.base_url}/movements"
        payload = {
            "productId": product_id,
            "warehouseId": warehouse_id,
            "quantity": qty,
            "movementType": "VENTA"
        }
        
        response = requests.post(url, headers=self.get_headers(token), json=payload, timeout=5)
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Error al descontar stock del producto {product_id}")
        return True