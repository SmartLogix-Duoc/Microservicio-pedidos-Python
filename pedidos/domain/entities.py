from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .enums import OrderState, OrderType
import uuid

class ItemOrder(BaseModel):
    productId : str
    amount: int = Field(gt=0, description="La cantidad debe ser mayor a 0")
    unitPrice : float = Field(gt=0, descriptition="La cantidad no puede ser negativa.")

class Order(BaseModel):
    #Entidad principal (Aggregate Root). Representa el pedido en si
    #BaseModel (pydantic) nos da todo lo que lombok (@Data) hace en java
    # uuid4 genera un ID único automático tipo '123e4567-e89b-12d3-a456-426614174000'
    orderId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    items: List[ItemOrder] # Una lista de la sub-entidad que creamos arriba
    total: float = 0.0
    tipo: OrderType
    estado: OrderState = OrderState.WAITING
    createdAt: datetime = Field(default_factory=datetime.utcnow)    


    # Definición Técnica - Método de Instancia:
    # Una función que le pertenece solo a esta clase para calcular cosas propias.
    def calculate_total(self):
        suma = sum(item.unitPrice * item.amount for item in self.items)
        self.total = suma

