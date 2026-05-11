from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import uuid
from .enums import OrderType, OrderState

class ItemOrder(BaseModel):
    product_id: str
    amount: int = Field(gt=0, description="La cantidad debe ser mayor a 0")
    unit_price: float = Field(ge=0, description="El precio no puede ser negativo")

class Order(BaseModel):
    # Tu lógica de UUID para IDs únicos en MongoDB
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[ItemOrder] 
    total: float = 0.0
    order_type: OrderType
    status: str = OrderState.WAITING.value
    created_at: datetime = Field(default_factory=datetime.utcnow)
    warehouse_id: int = Field(default=1, description="ID de la bodega de origen")

    def calculate_total(self):
        suma = sum(item.unit_price * item.amount for item in self.items)
        self.total = suma