from pydantic import BaseModel
from decimal import Decimal

class InventoryItemDTO(BaseModel):
    def __init__(self, id, name, price, stock):
        self.id = id
        self.name = name
        self.price = Decimal(str(price)) # Transformación de seguridad
        self.stock = stock