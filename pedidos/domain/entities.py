from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .enums import OrderState, OrderType
import uuid

class ItemOrder(BaseModel):
    productId : str
    amount: int = Field(gt=0, description="La cantidad debe ser mayor a 0")
    