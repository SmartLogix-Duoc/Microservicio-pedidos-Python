from pedidos.domain.entities import Order, ItemOrder
from pedidos.domain.enums import OrderType

class OrderFactory:
    #Patron factory
    @staticmethod
    def create_order(user_id: str, items_data : list, tipo_str: str) -> Order :
        #1 Convertimos los diccionarios de items a entidades de pydantic
            items = [ItemOrder(**item) for item in items_data]
        #2 creamos el pedido base 
            new_order = Order(
                  userId=user_id,
                  items=items,
                  tipo=OrderType(tipo_str.upper())
            )

        #3. Calculamos el total base (precio * cantidad de los items)
            new_order.calcular_total()
        
        #4. Reglas del Factory Method según el tipo 
            if new_order == OrderType.INTERNATIONAL:
                  #Ejemplo de regla de negocio le multiplica al total el 15% aduanero 
                  new_order.total = new_order.total*1.15
            elif new_order.tipo == OrderType.NATIONAL:
                  #Pedido Nacional no tiene cargas extra por ahora
                  pass
            return new_order        