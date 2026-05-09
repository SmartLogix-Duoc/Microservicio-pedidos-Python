import jwt
import os
from django.conf import settings

def decode_token(token: str):
    try:
        secret = os.getenv("JWT_SECRET_KEY")
        algo = os.getenv("ALGORITHM", "HS256")
        payload = jwt.decode(token, secret, algorithms=[algo])
        return payload # Aquí viene el sub (user_id), roles, etc.
    except jwt.ExpiredSignatureError:
        raise Exception("El token ha expirado")
    except jwt.InvalidTokenError:
        raise Exception("Token inválido")