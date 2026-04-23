from enum import Enum

class OrderState(str, Enum):
# Definiremos los estados estrictos por los que un pedido va a pasar
# Heredaremos de Str y Enum nos permitira que python lo trate como un texto
#  pero validando que solo existen estas opciones

    PROCCESING = "Procesando"
    WAITING = "Pendiente"
    CANCELED = "Cancelado"
    DELIVERED = "Entregado"
    SHIPPED = "Enviado"

class OrderType(str, Enum):
    #Define los tipos de pedidos para nuestro Factory Method Posterior
    NATIONAL = "Nacional"
    INTERNATIONAL = "Internacional"