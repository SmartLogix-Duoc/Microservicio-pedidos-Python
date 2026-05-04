from pedidos.domain.entities import Order, ItemOrder
from pedidos.domain.enums import OrderType

class OrderFactory:
    """Factory Pattern para creación y aplicación de reglas de negocio en Pedidos"""
    
    @staticmethod
    def create_order(user_id: str, items_data: list, order_type_str: str) -> Order:
        # 1. Convertimos los diccionarios de items a entidades de Pydantic
        items = [ItemOrder(**item) for item in items_data]
        
        # 2. Creamos el pedido base (Usando los nombres exactos del Pydantic Model)
        new_order = Order(
            user_id=user_id,
            items=items,
            order_type=OrderType(order_type_str.upper()).value # Usamos .value si order_type espera un string
        )

        # 3. Calculamos el total base (precio * cantidad de los items)
        new_order.calculate_total()
        
        # 4. Reglas del Factory Method según el tipo 
        if new_order.order_type == OrderType.INTERNATIONAL.value:
            # Ejemplo de regla de negocio: se le multiplica al total el 15% aduanero 
            new_order.total = new_order.total * 1.15
            
        elif new_order.order_type == OrderType.NATIONAL.value:
            # Pedido Nacional no tiene cargas extra por ahora
            pass
            
        return new_order