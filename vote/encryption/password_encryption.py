import bcrypt

def hashPassword(password):
    #convert password in bytes
    bytes = password.encode('utf-8')

    #generate the salt, special key to hash the password
    salt = bcrypt.gensalt()

    return bcrypt.hashpw(bytes, salt)

def checkPassword(password, hashedPassword):
    bytes = password.encode('utf-8')

    return bcrypt.checkpw(bytes, hashedPassword)