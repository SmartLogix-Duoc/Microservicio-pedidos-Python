

from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import uuid
from .enums import OrderType # Asegúrate de importar bien tu enum
from .enums import OrderState
class ItemOrder(BaseModel):
    product_id: str
    amount: int = Field(gt=0, description="La cantidad debe ser mayor a 0")
    unit_price: float = Field(ge=0, description="El precio no puede ser negativo")

class Order(BaseModel):
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[ItemOrder] 
    total: float = 0.0
    order_type: OrderType
    status: str = OrderState.WAITING.value
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def calculate_total(self):
        suma = sum(item.unit_price * item.amount for item in self.items)
        self.total = suma