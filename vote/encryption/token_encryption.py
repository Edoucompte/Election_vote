import jwt
from jwt.exceptions import InvalidKeyError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone

def createToken(userId, email, secretKey, delay):
    payload = {
        "sub": str(userId), 
        "email": email,
        "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=delay)
    }

    return jwt.encode(
        payload,
        secretKey,
        algorithm="HS256",
        #expiration
    )

def decodeToken(jwtToken, secretKey):
    token = jwtToken[7:]
    try:
        return jwt.decode(token, secretKey, algorithms=["HS256"] )#expiration
    except InvalidKeyError:
        raise ValueError('Invalid key')
    except ExpiredSignatureError:
        raise ValueError("token exprired")
    except Exception as e:
        raise ValueError(f"Invalid :")

