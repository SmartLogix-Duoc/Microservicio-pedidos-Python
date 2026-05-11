# pedidos/clients/inventory_client.py
import requests
import dotenv
import os

dotenv.load_dotenv()

class InventoryApiClient:
    def __init__(self):
        self.base_url = os.getenv("INVENTORY_API_URL")

    def get_headers(self, token: str):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

    def find_warehouse(self, product_id: int, qty: int, token: str) -> int:
        """Pregunta a Java en qué bodega hay stock suficiente para este producto."""
        url = f"{self.base_url}/find-warehouse"
        params = {"productId": product_id, "quantity": qty}

        response = requests.get(url, headers=self.get_headers(token), params=params, timeout=5)

        if response.status_code == 200:
            return int(response.json().get('warehouse_id'))
        elif response.status_code == 404:
            raise Exception(f"Sin stock disponible para el producto {product_id} en ninguna bodega")
        else:
            raise Exception(f"Error buscando bodega para producto {product_id}: {response.status_code}")

    def check_stock(self, product_id: int, warehouse_id: int, qty: int, token: str) -> dict:
        """Valida stock y obtiene precio unitario desde Java."""
        url = f"{self.base_url}/check"
        params = {"productId": product_id, "warehouseId": warehouse_id, "quantity": qty}

        response = requests.get(url, headers=self.get_headers(token), params=params, timeout=5)

        print("=" * 50)
        print(f"URL: {response.url} | STATUS: {response.status_code}")
        print("=" * 50)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            raise Exception(f"Stock insuficiente para el producto {product_id}")
        else:
            raise Exception(f"Error comunicándose con el inventario (Check): {response.status_code}")

    def deduct_stock(self, product_id: int, warehouse_id: int, qty: int, token: str) -> bool:
        """Descuenta stock desde la bodega indicada."""
        url = f"{self.base_url}/update"
        params = {
            "productId": product_id,
            "warehouseId": warehouse_id,
            "quantity": qty,
            "movementType": "SALIDA"
        }

        response = requests.post(url, headers=self.get_headers(token), params=params, timeout=5)

        if response.status_code not in [200, 201]:
            raise Exception(f"Error al descontar stock del producto {product_id}: {response.status_code}")
        return True