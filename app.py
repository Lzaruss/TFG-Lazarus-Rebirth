from flask import Flask, session, render_template, request, redirect
from functools import wraps
import dbFunctions as ddbb
import json

app = Flask(__name__)

app.secret_key = 'secret_key'

@app.route('/', methods=["POST", "GET"])
def index():
    if('user' in session):
        settings = ddbb.getSettings(session['user'])
        return render_template('home.html', config=settings)
    
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        if ddbb.iniciar_sesion(email, password):
            session['user'] = ddbb.getUser(email)
            settings = ddbb.getSettings(session['user'])
            return render_template('sendMoney.html', config=settings)
        else:
            return render_template('login.html', error=True)
    try:
        session.pop('user')
    except:
        pass
    return render_template('login.html')

@app.route("/recovery", methods=["POST", "GET"])
def recovery():
    if request.method == 'POST':
        email = request.form.get("email")
        if ddbb.enviar_email_contrasena(email):
            return render_template('recovery.html', enviado=True)
        else:
            return render_template('recovery.html', error="El correo electrónico no está registrado")
    return render_template('recovery.html')

@app.route("/registrar", methods=["POST", "GET"])
def registrar():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        code = request.form.get("code-guest")
        balance = 5

        if ddbb.checkCode(code) is not None:
            userGuest = ddbb.checkCodeInDB(code)
            if userGuest is not False:
                balance = 25
                ddbb.changeBalance(userGuest, ddbb.getBalance(userGuest) + balance)
                ddbb.updateUserGuest(userGuest)

        if ddbb.checkUsername(username) is None:
            return render_template('registrar.html', error="El nombre de usuario no es válido (Debe contener al menos 4 caracteres y no puede contener espacios ni caracteres especiales)")
        password = request.form.get("password")

        if ddbb.checkEmail(email) is None:
            return render_template('registrar.html', error="El correo electrónico no es válido")
        if ddbb.checkPassword(password) is None:
            return render_template('registrar.html', error="La contraseña no es válida (Debe contener al menos 6 caracteres y un número)")
        if ddbb.checkUser(username):
            return render_template('registrar.html', error="El nombre de usuario ya está en uso")
        try:
            user = ddbb.registrar_usuario(email, password)
            if user is False:
                return render_template('registrar.html', error="Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador")
            ddbb.pushDataToUsers(username, {"uid": user['idToken'], "email": user['email'], "username": username, "balance": balance, "wallet": ddbb.createWallet(), "notifications": "", "transactions": "", "config":{"color": "#222", "hover_color":"#333", "twofa": "1", "notifys": "0"}, "friends":{}, "code":ddbb.createCode(), "guest": "0"})
            return render_template('registrar.html', usuario=True)
        except Exception as e:
            
            # Convierte el error en un json para poder leer los datos de una manera sencilla.
            dataError = json.loads(e.args[1])

            if dataError["error"]["message"] == 'EMAIL_EXISTS':
                return render_template('registrar.html', error="El correo electrónico ya está registrado")
            
            if dataError["error"]["message"] == 'OPERATION_NOT_ALLOWED':
                return render_template('registrar.html', error="El registro de usuarios está deshabilitado")
            
            if dataError["error"]["message"] == 'TOO_MANY_ATTEMPTS_TRY_LATER':
                return render_template('registrar.html', error="Demasiados intentos, vuelve a intentarlo en unos minutos")
            
            if dataError["error"]["message"] == 'INVALID_EMAIL':
                return render_template('registrar.html', error="El correo electrónico no es válido")
    
            if dataError["error"]["message"] == 'INVALID_PASSWORD':
                return render_template('registrar.html', error="La contraseña no es válida")

            return render_template('registrar.html', error="Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador")
        
    return render_template('registrar.html')

@app.route("/logout")
def logout():
    try:
        session.pop('user')
    finally:
        return redirect("/")

# DECORATORS
def check_user_in_session_routes(parameter):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user' in session:
                settings = ddbb.getSettings(session['user'])
                return render_template(parameter, config=settings)
            else:
                return redirect("/")
        return wrapper
    return decorator

def check_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user' in session:
            return func(*args, **kwargs)
        else:
            return redirect("/")
    return wrapper


# DEFAULT ROUTES

@app.route("/send", methods=["GET", "POST"])
@check_user_in_session_routes('sendMoney.html')
def send():
    pass

@app.route("/receive", methods=["GET", "POST"])
@check_user_in_session_routes('requestMoney.html')
def receive():
    pass

@app.route("/transactions", methods=["GET", "POST"])
@check_user_in_session_routes('transactions.html')
def transactions():
    pass
    
@app.route("/account")
@check_user_in_session_routes('account.html')
def account():
    pass

@app.route("/settings")
@check_user_in_session_routes('settings.html')
def configuracion():
    pass
    
@app.route("/friends", methods=["GET", "POST"])
@check_user_in_session_routes('friends.html')
def friends():
    pass

# API

@app.route("/saldo", methods=["GET"])
@check_login
def saldo():
    try:
        return {"saldo" : str(ddbb.getBalance(session['user']))}
    except:
        return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

@app.route("/actualUser", methods=["GET"])  
@check_login
def actualUser():
    try:
        return {"user" : session['user']}
    finally:
        pass

@app.route("/sendBalance", methods=["GET", "POST"])
@check_login
def sendBalance():
    if request.method == "POST":
        userTo  = request.json.get("receiver")
        balance = request.json.get("amount")

        userFrom = session['user']

        if not ddbb.checkUser(userTo) and not ddbb.checkWallet(userTo): 
            return {"error": "El usuario no existe"}

        try:
            if int(balance) <= 0:
                return {"error": "La cantidad debe ser mayor que 0"}
            if not ddbb.checkBalance(userFrom, int(balance)):
                return {"error": "No tienes suficiente saldo para realizar la transacción!"}
            if ddbb.sendBalance(userFrom, userTo, int(balance)):
                return {"status": "success", "message": "Se ha enviado correctamente!"}
            return {"error": "No se ha podido enviar la petición"}
        except ValueError:
            return {"error": "Comprueba la cantidad enviada!"}
        except Exception as e:
            return {"error": "No se ha podido enviar la petición, comprueba que los datos estan correctos!"}
    
@app.route("/sendNotification", methods=["GET", "POST"])
@check_login
def sendNotification():
    if request.method == "POST":
        userTo  = request.json.get("receiver")
        balance = request.json.get("amount")
        message = request.json.get("message")
        userFrom = session['user']

        if not ddbb.checkUser(userTo) and not ddbb.checkWallet(userTo): 
            return {"error": "El usuario no existe"}

        try:
            if ddbb.addNotification(userTo, userFrom, int(balance), message):
                return {"status": "success", "message": "Se ha enviado correctamente!"}
            return {"error": "No se ha podido enviar la petición"}
        except ValueError:
            return {"error": "Comprueba la cantidad enviada!"}
        except Exception as e:
            return {"error": "No se ha podido enviar la petición, comprueba que los datos estan correctos!"}
    
# get History of transactions
@app.route("/getHistory", methods=["GET"])
@check_login
def getHistory():
    try:
        return {"transactions" : ddbb.getTransactions(session['user'])}
    except:
        return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

    
# get notifications
@app.route("/getNotifications", methods=["GET"])
@check_login
def getNotifications():
    try:
        return {"notifys" : ddbb.getNotifications(session['user'])}
    except:
        return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

@app.route("/deleteNotification", methods=["GET", "POST"])
@check_login
def deleteNotification():
    try:
        ddbb.deleteNotification(session['user'], request.form.get("position"))
        return {"status": "success", "message": "Se ha eliminado correctamente!"}

    except:
        return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}


@app.route("/deleteTransaction", methods=["GET", "POST"])
@check_login
def deleteTransaction():
    try:
        ddbb.deleteTransaction(session['user'])
        return {"status": "success", "message": "Se ha eliminado correctamente!"}
    except:
        return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}


@app.route("/getAccount", methods=["GET"]) ###
@check_login
def getAccount():
    try:
        return {"account" : ddbb.getAccount(session['user'])}
    except:
        return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

@app.route("/saveSettings", methods=["POST"]) ###
@check_login
def saveSettings():
    if request.method == "POST":
        try:
            ddbb.saveSettings(session['user'], {"color": request.json['color'], "hover_color":request.json['hover_color'], "twofa": request.json['twofa'], "notifys": request.json['notify']})
            return {"status": "success", "message": "Se ha guardado correctamente!"}
        except:
            return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

@app.route("/changePassword", methods=["POST"]) 
@check_login
def changePassword():
    if request.method == "POST":
        if ddbb.enviar_email_contrasena(session['user']):
            return {"status": "success", "message": "Se ha enviado un correo a tu cuenta de correo electrónico!"}
        else:
            return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}
    
@app.route("/getFriends")
@check_login
def getFriends():
    try:
        return {"response" : ddbb.getFriends(session['user'])}
    except:
        return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}
    
@app.route("/getMessages/<friend_name>")
@check_login
def getMessages(friend_name):
    try:
        return {"response" : ddbb.getMessages(session['user'], friend_name)}
    except:
        return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

@app.route("/sendMessage", methods=["POST"])
@check_login
def sendMessage():
    if request.method == "POST":
        try:
            if request.json['message'] == "":
                return {"error": "No puedes enviar un mensaje vacío!"}
            if ddbb.addMessage(session['user'], request.json['friend'], request.json['message'], request.json['timestamp']):
                return {"status": "success", "message": "Se ha enviado correctamente!"}
            return {"error": "No se ha podido enviar el mensaje"}
        except:
            return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

@app.route("/addFriend", methods=["POST"])
@check_login
def addFriend():
    if request.method == "POST":
        try:
            if ddbb.addFriend(session['user'], request.json['friend']):
                return {"status": "success", "message": "Se ha enviado la solicitud correctamente!"}
            return {"error": "No se ha encontrado al usuario!"}
        except:
            return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

@app.route("/deleteFriend", methods=["POST"])
@check_login
def deleteFriend():
    if request.method == "POST":
        try:
            if ddbb.deleteFriend(session['user'], request.json['friend']):
                return {"status": "success", "message": "Se ha eliminado correctamente!"}
            return {"error": "No se ha encontrado al usuario!"}
        except:
            return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}
        
@app.route("/deleteAccount", methods=["POST"])
@check_login
def deleteAccount():
    if request.method == "POST":
        try:
            if ddbb.deleteAccount(session['user']):
                try:
                    session.pop('user')
                except:
                    pass
                return {"status": "success", "message": "Se ha eliminado correctamente!"}
            return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}
        except:
            return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

if __name__ == '__main__':
    print("Server started")
    app.run(port=1111)