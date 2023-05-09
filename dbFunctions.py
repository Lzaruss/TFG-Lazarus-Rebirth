import re
import pyrebase
import random
import string
import datetime

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

def getActualHour():
    fecha_hora_actual = datetime.datetime.now()

    # Obtener los componentes de fecha y hora
    hora = fecha_hora_actual.strftime("%H:%M:%S")
    dia = fecha_hora_actual.strftime("%d")
    mes_abr = fecha_hora_actual.strftime("%b")
    anio = fecha_hora_actual.strftime("%Y")

    # Formatear la fecha y hora en el formato deseado
    return "[{}/{}/{} {}]".format(dia, mes_abr, anio, hora)


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
        if user.val()["wallet"] == wallet:
            return True
    return False

# Crea una direccion de wallet de 10 caracteres empiece con dos letras y el restante números
def createWallet():
    wallet = ""
    for i in range(2):
        wallet += random.choice(string.ascii_letters)
    for i in range(8):
        wallet += random.choice(string.digits)
    return wallet
# Comprobar que la wallet es correcta, que empiece por dos letras y 8 números
def checkWalletFormat(wallet : str):
    regex = r'^[a-zA-Z]{2}[0-9]{8}$'
    return re.search(regex, wallet)

# Comprobar que el usuario tiene saldo suficiente para realizar la compra
def checkBalance(user : str, price : int):
    return getBalance(user) >= price

# Enviar balance de un usuario a otro
def sendBalance(userFrom : str, userTo : str, amount : int) -> bool:
    if checkWalletFormat(userTo) is not None:
        userTo = getUserByWallet(userTo)
    if checkBalance(userFrom, amount) & checkUser(userFrom) & checkUser(userTo) & (userFrom != userTo):
        changeBalance(userTo, getBalance(userTo) + amount)
        changeBalance(userFrom, getBalance(userFrom) - amount)
        addTransaction(userFrom, userTo, amount)
        addNotification(userTo, userFrom, amount, message="Te ha enviado {}€".format(amount))
        return True
    return False

def addNotification(FROM : str, TO : str, AMOUNT : int, message : str):
    try:
        if checkUser(FROM):
            db.child(FROM).child("notifications").push({'FROM': TO, 'TO': FROM, 'AMOUNT': AMOUNT, 'message':message, 'TIME': getActualHour()})
            return True
    except Exception as e:
        print(e)

# añadir transacciones pero con formato de diccionario con los campos FROM, TO, AMOUNT, TIME
def addTransaction(user : str, TO : str, AMOUNT : int):
    if checkUser(user):
        db.child(user).child("transactions").push({'FROM': user, 'TO': TO, 'AMOUNT': AMOUNT, 'TIME': getActualHour()})

def getTransactions(user: str):
    if checkUser(user):
        transactions = db.child(user).child("transactions").get().val().values()
        return {i: transaction for i, transaction in enumerate(transactions)}
    return None

def getNotifications(user: str):
    if checkUser(user):
        notifications = db.child(user).child("notifications").get().val().values()
        return {i: notification for i, notification in enumerate(notifications)}
    return None

def deleteNotification(user:str, pos:int):
    try:
        if checkUser(user):
            n = db.child(user).child("notifications").get().val()
            notifications_keys = list(n.keys())
            notifications = list(n.values())
            del notifications[int(pos)], notifications_keys[int(pos)]
            diccionario = dict(zip(notifications_keys, notifications))
            # Hacer un push con el nuevo diccionario
            db.child(user).child("notifications").set(diccionario)
            if len(diccionario) == 0:
                db.child(user).child("notifications").push({})
    except Exception as e:
        pass

# Esta funcion eliminará todas las transacciones de un usuario
def deleteTransaction(user:str):
    try:
        if checkUser(user):
            db.child(user).child("transactions").remove()
    except Exception as e:
        pass

# Sacar el nombre de usuario, el email, el balance y la wallet de un usuario
def getAccount(user:str):
    if checkUser(user):
        OrderedDict = db.child(user).get().val()
        return {"username":OrderedDict["username"], "email":OrderedDict["email"], "balance":OrderedDict["balance"], "wallet":OrderedDict["wallet"]}
    return None


# recuperar la configuracion de un usuario
def getSettings(user:str):
    if checkUser(user):
        return dict(db.child(user).child("config").get().val())
    return None

def saveSettings(user:str, settings:dict):
    if checkUser(user):
        db.child(user).child("config").set(settings)

#print(saveSettings("Lzaruss", {"color": "#222", "2fa": "0", "notifys": "0"}))