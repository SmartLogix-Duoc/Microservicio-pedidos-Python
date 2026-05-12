# pedidos/services/order_service.py
from pedidos.repositories.OrderRepository import OrderRepository
from pedidos.clients.inventory_client import InventoryApiClient
import requests
import jwt
from pedidos.domain.enums import OrderState
from datetime import datetime, timedelta, timezone


ENVIOS_MS_URL = "http://localhost:8004"
class OrderService:
    def __init__(self):
        self.repository = OrderRepository()
        self.inventory_api = InventoryApiClient()

    def get_all_orders(self):
        return self.repository.get_all()

    def get_order_by_id(self, order_id: str):
        return self.repository.get_by_id(order_id)

    #Actualizado para conectar con el MS Envíos al pasar a SHIPPED
    def update_order_status(self, order_id: str, new_status: str):
        # Actualizar estado en BD
        result = self.repository.update_status(order_id, new_status)

        # Si el pedido pasa a SHIPPED → crear envío automáticamente
        if new_status == OrderState.SHIPPED.value:
            try:
                order = self.repository.get_by_id(order_id)
                print(f"DEBUG order: {order}")  # ← agregar
                if order:
                    payload = {
                        "order_id": order_id,
                        "warehouse_id": order.get("warehouse_id", 1),
                        "order_type": order.get("order_type", "NATIONAL"),
                    }
                    print(f"DEBUG payload enviado a MS Envios: {payload}")  # ← agregar
                    response = requests.post(
                        f"{ENVIOS_MS_URL}/api/shipments/from-order",
                        json=payload,
                        headers={
                            "Authorization": f"Bearer {self._get_service_token()}"
                        },
                        timeout=5,
                    )
                    print(f"DEBUG respuesta MS Envios: {response.status_code} {response.text}")  # ← agregar
            except Exception as e:
                print(f"Warning: No se pudo crear el envío automáticamente: {e}")
                # No bloqueamos el flujo si el MS Envíos falla
        return result

    def _get_service_token(self) -> str:
        """
        Token JWT para comunicación entre microservicios.
        Debe ser el mismo JWT_SECRET_KEY que usa el MS Envíos.
        """
        payload = {
            "sub": "ms-pedidos",
            "role": "ADMIN",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
            }
        return jwt.encode(payload, "91896272b47078739308e151776c91314b6e7a543ed405cac938f17e30b92c16", algorithm="HS256")

    def delete_order(self, order_id: str):
        self.repository.delete(order_id)
        return {"success": True, "message": f"Orden {order_id} eliminada correctamente"}

    def process_new_order(self, user_id: str, items_raw: list, order_type: str, token: str):
        validated_items = []
        total_order_price = 0.0

        # 1. POR CADA ITEM: buscar bodega automáticamente, validar stock y obtener precio
        for item in items_raw:
            product_id = item.get('product_id')
            qty = int(item.get('amount', 1))

            # Java busca en qué bodega hay stock suficiente (lógica Amazon)
            warehouse_id = self.inventory_api.find_warehouse(product_id, qty, token)

            # Validar stock y obtener precio desde esa bodega
            stock_info = self.inventory_api.check_stock(product_id, warehouse_id, qty, token)
            unit_price = float(stock_info.get('unit_price', 0.0))
            total_order_price += unit_price * qty

            validated_items.append({
                "product_id": product_id,
                "amount": qty,
                "unit_price": unit_price,
                "warehouse_id": warehouse_id  # cada item sabe desde qué bodega sale
            })

        # Recargo del 15% para pedidos internacionales
        total_final = round(total_order_price * 1.15, 2) if order_type.upper() == "INTERNATIONAL" else round(total_order_price, 2)

        # 2. GUARDAR CABECERA — sin warehouse_id fijo, cada item tiene el suyo
        order_payload = {
            "user_id": user_id,
            "order_type": order_type,
            "total": total_final,
            "status": "WAITING",
        }
        saved_order = self.repository.create_order(order_payload)
        supabase_order_id = saved_order.get('order_id')

        # 3. GUARDAR ITEMS con su bodega correspondiente
        items_payload = [
            {
                "order_id": supabase_order_id,
                "product_id": v_item["product_id"],
                "amount": v_item["amount"],
                "unit_price": v_item["unit_price"],
                "warehouse_id": v_item["warehouse_id"]
            }
            for v_item in validated_items
        ]
        self.repository.create_order_items(items_payload)

        # 4. DESCONTAR STOCK desde la bodega correcta de cada item
        for item in validated_items:
            try:
                self.inventory_api.deduct_stock(
                    product_id=item['product_id'],
                    warehouse_id=item['warehouse_id'],
                    qty=item['amount'],
                    token=token
                )
            except Exception as e:
                self.repository.update_status(supabase_order_id, "CANCELED")
                raise Exception(
                    f"Pedido {supabase_order_id} cancelado por fallo al descontar stock: {str(e)}"
                )

        return {
            "success": True,
            "order_id": supabase_order_id,
            "total": total_final,
            "items": validated_items,
            "message": "Pedido procesado y stock descontado exitosamente"
        }