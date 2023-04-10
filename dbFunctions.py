import re
import pyrebase
import random
import string

config = {
            'apiKey': "AIzaSyAyOFO875u8wYYbFbjpyZBDzAEuUQtICYM",
            'authDomain': "tfg-launcher.firebaseapp.com",
            'databaseURL': "https://tfg-launcher-default-rtdb.firebaseio.com",
            'projectId': "tfg-launcher",
            'storageBucket': "tfg-launcher.appspot.com",
            'messagingSenderId': "364319578115",
            'appId': "1:364319578115:web:1b344ae37a3e6926a25636",
            'measurementId': "G-2GGEX0L1N6",
        }
firebase = pyrebase.initialize_app(config)
db = firebase.database()

def checkEmail(email):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.search(regex, email)

def checkPassword(password):
    regex = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$'
    return re.search(regex, password)

def checkSamePassword(a, b):
    return a == b

# Crea los datos de un usuario en la base de datos
def pushDataToUsers(user : str, dataUser):
    db.child(user).set(dataUser)

# comprueba que el usuario existe en la base de datos
def checkUser(user : str):
    return db.child(user).get().val() is not None

# cambiar el balance de un usuario
def changeBalance(user : str, balance : int):
    db.child(user).update({"balance": balance})

# obtener el balance de un usuario
def getBalance(user : str):
    return db.child(user).get().val()["balance"]

# obtener la direccion de wallet de un usuario
def getWallet(user : str):
    return db.child(user).get().val()["wallet"]

# obtener el usuario a través de su wallet
def getUserByWallet(wallet : str):
    users = db.get()
    for user in users.each():
        if user.val()["wallet"] == wallet:
            return user.key()
    return None

# obtener el usuario pasandole el email
def getUser(email : str):
    users = db.get()
    for user in users.each():
        if user.val()["email"] == email:
            return user.key()
    return None

# Comprobar que la wallet que le pase por parametro, no la contiene ningun usuario en sus datos de la base de datos
def checkWallet(wallet : str):
    users = db.get()
    for user in users.each():
        if user.val()== wallet:
            return False
    return True

# Crea una direccion de wallet de 10 caracteres empiece con dos letras y el restante números
def createWallet():
    wallet = ""
    for i in range(2):
        wallet += random.choice(string.ascii_letters)
    for i in range(8):
        wallet += random.choice(string.digits)

    return wallet if checkWallet(wallet) else createWallet()

# Comprobar que la wallet es correcta, que empiece por dos letras y 8 números
def checkWalletFormat(wallet : str):
    regex = r'^[a-zA-Z]{2}[0-9]{8}$'
    return re.search(regex, wallet)

# Comprobar que el usuario tiene saldo suficiente para realizar la compra
def checkBalance(user : str, price : int):
    return getBalance(user) >= price

# Enviar balance de un usuario a otro
def sendBalance(userFrom : str, userTo : str, amount : int) -> bool:
    if checkBalance(userFrom, amount) & checkUser(userFrom) & checkUser(userTo):
        changeBalance(userTo, getBalance(userTo) + amount)
        changeBalance(userFrom, getBalance(userFrom) - amount)
        return True
    return False

#Enviar balance de una direccion de cartera a otra
def sendBalanceWallet(walletFrom : str, walletTo : str, amount : int) -> bool:
    userFrom = getUserByWallet(walletFrom)
    userTo = getUserByWallet(walletTo)
    if userFrom is not None and userTo is not None:
        return sendBalance(userFrom, userTo, amount)
    return False