from pedidos.domain.entities import Order, ItemOrder
from pedidos.domain.enums import OrderType

class OrderFactory:
    @staticmethod
    def create_order(user_id: str, items_entities: list, order_type_str: str) -> Order:
        # 1. Determinamos el tipo usando el Enum
        try:
            o_type = OrderType(order_type_str.upper())
        except ValueError:
            o_type = OrderType.NATIONAL # Default o manejo de error

        # 2. Creamos el pedido base con los items ya transformados
        new_order = Order(
            user_id=user_id,
            items=items_entities,
            order_type=o_type
        )

        # 3. Calculamos el total base (precio * cantidad)
        new_order.calculate_total()
        
        # 4. Reglas del Factory Method: Aplicación de impuestos
        if new_order.order_type == OrderType.INTERNATIONAL:
            # Multiplicamos por 1.15 (15% aduanero)
            new_order.total = round(new_order.total * 1.15, 2)
            
        return new_order