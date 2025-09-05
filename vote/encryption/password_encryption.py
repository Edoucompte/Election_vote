import bcrypt

def hashPassword(password):
    #convert password in bytes
    bytes = password.encode('utf-8')

    #generate the salt, special key to hash the password
    salt = bcrypt.gensalt()

    strPass = str(bcrypt.hashpw(bytes, salt))[2:-1]
    return strPass

def checkPassword(password, hashedPassword):
    bytes = password.encode('utf-8')
    # hashedPassword[2:-1]
    return bcrypt.checkpw(bytes, hashedPassword.encode('utf-8'))