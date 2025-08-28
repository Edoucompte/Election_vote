import jwt

def createToken(userId, email, secretKey):
    return jwt.encode(
        {"sub": userId, "email": email},
        secretKey,
        algorithm="HS256",
        #expiration
    )

def decodeToken(jwtToken, secretKey):
    return jwt.decode(jwtToken, secretKey, algorithm="HS256"  )#expiration