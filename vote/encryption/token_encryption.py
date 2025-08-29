import jwt
from datetime import datetime, timedelta, timezone

def createToken(userId, email, secretKey, delay):
    payload = {
        "sub": userId, 
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
    return jwt.decode(jwtToken, secretKey, algorithm="HS256",  )#expiration