# pedidos/services/order_service.py
from pedidos.repositories.OrderRepository import OrderRepository
from pedidos.clients.inventory_client import InventoryApiClient

class OrderService:
    def __init__(self):
        self.repository = OrderRepository()
        self.inventory_api = InventoryApiClient()

    # --- MÉTODOS CRUD SIMPLES ---
    def get_all_orders(self):
        return self.repository.get_all()

    def get_order_by_id(self, order_id: str):
        return self.repository.get_by_id(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        return self.repository.update_status(order_id, new_status)

    def delete_order(self, order_id: str):
        self.repository.delete(order_id)
        return {"success": True, "message": f"Orden {order_id} eliminada correctamente"}

    # --- MÉTODO COMPLEJO DE PROCESAMIENTO ---
    def process_new_order(self, user_id: str, items_raw: list, order_type: str, token: str):
        validated_items = []
        total_order_price = 0
        
        # Mapeamos el tipo de orden a un ID de bodega (como acordaron)
        warehouse_id = 1 if order_type.lower() == "nacional" else 2

        # 1. VALIDAR STOCK CON LA API DE JAVA (GET)
        for item in items_raw:
            product_id = item.get('product_id')
            qty = item['amount']
            
            # Aquí le tocamos la puerta a Spring Boot
            # OJO: Necesitamos que Java nos devuelva el PRECIO aquí para poder sumar el total
            product_data = self.inventory_api.check_stock(product_id, warehouse_id, qty, token)
            
            # Asumimos que product_data trae el unit_price desde Java
            unit_price = float(product_data.get('price', item.get('price', 0))) 
            total_order_price += (unit_price * qty)
            
            validated_items.append({
                "product_id": product_id,
                "amount": qty,
                "unit_price": unit_price
            })

        # 2. GUARDAR CABECERA (Tu BD vía Supabase)
        order_payload = {
            "user_id": user_id,
            "order_type": order_type,
            "total": total_order_price,
            "status": "PENDING"
        }
        saved_order = self.repository.create_order(order_payload)
        supabase_order_id = saved_order.get('order_id')

        # 3. GUARDAR DETALLES (Tu BD vía Supabase)
        items_payload = [{
            "order_id": supabase_order_id,
            "product_id": v_item["product_id"],
            "amount": v_item["amount"],
            "unit_price": v_item["unit_price"]
        } for v_item in validated_items]
        
        self.repository.create_order_items(items_payload)

        # 4. DESCONTAR STOCK EN LA API DE JAVA (POST)
        for item in validated_items:
            self.inventory_api.deduct_stock(
                product_id=item['product_id'],
                warehouse_id=warehouse_id,
                qty=item['amount'],
                token=token
            )

        return {
            "success": True,
            "order_id": supabase_order_id,
            "message": "Pedido procesado y stock descontado exitosamente"
        }