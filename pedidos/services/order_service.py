# pedidos/services/order_service.py
from pedidos.repositories.OrderRepository import OrderRepository
from pedidos.clients.inventory_client import InventoryApiClient


class OrderService:
    def __init__(self):
        self.repository = OrderRepository()
        self.inventory_api = InventoryApiClient()

    def get_all_orders(self):
        return self.repository.get_all()

    def get_order_by_id(self, order_id: str):
        return self.repository.get_by_id(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        return self.repository.update_status(order_id, new_status)

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