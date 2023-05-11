from flask import Flask, session, render_template, request, redirect
import pyrebase 
import dbFunctions as ddbb
import json
import os

app = Flask(__name__)

app.secret_key = 'secret_key'

@app.route('/', methods=["POST", "GET"])
def index():
    if('user' in session):
        settings = ddbb.getSettings(ddbb.getUser(session['user']))
        return render_template('sendMoney.html', config=settings)
    
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        if ddbb.iniciar_sesion(email, password):
            session['user'] = email
            settings = ddbb.getSettings(ddbb.getUser(session['user']))
            return render_template('sendMoney.html', config=settings)
        else:
            return render_template('login.html', error=True)

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

        if ddbb.checkUsername(username) is None:
            return render_template('registrar.html', error="El nombre de usuario no es válido (Debe contener al menos 4 caracteres y no puede contener espacios ni caracteres especiales)")
        password = request.form.get("password")
        balance = 5

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
            ddbb.pushDataToUsers(username, {"uid": user['idToken'], "email": email, "username": user['email'], "balance": balance, "wallet": ddbb.createWallet(), "notifications": "", "transactions": "", "config":{"color": "#222", "hover_color":"#333", "twofa": "1", "notifys": "0"}, "friends":{}})
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
    
@app.route("/send", methods=["GET", "POST"])
def send():
    if('user' in session):
        settings = ddbb.getSettings(ddbb.getUser(session['user']))
        return render_template('sendMoney.html', config=settings)
    else:
        return redirect("/")
    
@app.route("/receive", methods=["GET", "POST"])
def receive():
    if('user' in session):
        settings = ddbb.getSettings(ddbb.getUser(session['user']))
        return render_template('requestMoney.html', config=settings)
    else:
        return redirect("/")
    
@app.route("/transactions", methods=["GET", "POST"])
def transactions():
    if('user' in session):
        settings = ddbb.getSettings(ddbb.getUser(session['user']))
        return render_template('transactions.html', config=settings)
    else:
        return redirect("/")
    
@app.route("/account")
def account():
    if('user' in session):
        settings = ddbb.getSettings(ddbb.getUser(session['user']))
        return render_template('account.html', config=settings)
    else:
        return redirect("/")

@app.route("/settings")
def configuracion():
    if('user' in session):
        settings = ddbb.getSettings(ddbb.getUser(session['user']))
        return render_template('settings.html', config=settings)
    else:
        return redirect("/")
    
@app.route("/friends", methods=["GET", "POST"])
def friends():
    if('user' in session):
        settings = ddbb.getSettings(ddbb.getUser(session['user']))
        return render_template('friends.html', config=settings)
    else:
        return redirect("/")


# API

@app.route("/saldo", methods=["GET"])
def saldo():
    try:
        return {"saldo" : str(ddbb.getBalance(ddbb.getUser(session['user'])))}
    except:
        return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

@app.route("/actualUser", methods=["GET"])  
def actualUser():
    try:
        return {"user" : ddbb.getUser(session['user'])}
    finally:
        pass


@app.route("/sendBalance", methods=["GET", "POST"])
def sendBalance():
    if request.method == "POST":
        userTo  = request.json.get("receiver")
        balance = request.json.get("amount")

        userFrom = ddbb.getUser(session['user'])

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
def sendNotification():
    if request.method == "POST":
        userTo  = request.json.get("receiver")
        balance = request.json.get("amount")
        message = request.json.get("message")
        userFrom = ddbb.getUser(session['user'])

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
def getHistory():
    try:
        return {"transactions" : ddbb.getTransactions(ddbb.getUser(session['user']))}
    except:
        return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

    
# get notifications
@app.route("/getNotifications", methods=["GET"])
def getNotifications():
    try:
        return {"notifys" : ddbb.getNotifications(ddbb.getUser(session['user']))}
    except:
        return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

@app.route("/deleteNotification", methods=["GET", "POST"])
def deleteNotification():
    try:
        ddbb.deleteNotification(ddbb.getUser(session['user']), request.form.get("position"))
        return {"status": "success", "message": "Se ha eliminado correctamente!"}

    except:
        return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}


@app.route("/deleteTransaction", methods=["GET", "POST"])
def deleteTransaction():
    try:
        ddbb.deleteTransaction(ddbb.getUser(session['user']))
        return {"status": "success", "message": "Se ha eliminado correctamente!"}
    except:
        return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

    
@app.route("/getAccount", methods=["GET"]) ###
def getAccount():
    try:
        return {"account" : ddbb.getAccount(ddbb.getUser(session['user']))}
    except:
        return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

@app.route("/saveSettings", methods=["POST"]) ###
def saveSettings():
    if request.method == "POST":
        try:
            ddbb.saveSettings(ddbb.getUser(session['user']), {"color": request.json['color'], "hover_color":request.json['hover_color'], "twofa": request.json['twofa'], "notifys": request.json['notify']})
            return {"status": "success", "message": "Se ha guardado correctamente!"}
        except:
            return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

@app.route("/changePassword", methods=["POST"]) 
def changePassword():
    if request.method == "POST":
        if ddbb.enviar_email_contrasena(session['user']):
            return {"status": "success", "message": "Se ha enviado un correo a tu cuenta de correo electrónico!"}
        else:
            return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}
    
@app.route("/getFriends")
def getFriends():
    try:
        return {"response" : ddbb.getFriends(ddbb.getUser(session['user']))}
    except:
        return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}
    
@app.route("/getMessages/<friend_name>")
def getMessages(friend_name):
    try:
        return {"response" : ddbb.getMessages(ddbb.getUser(session['user']), friend_name)}
    except:
        return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

@app.route("/sendMessage", methods=["POST"])
def sendMessage():
    if request.method == "POST":
        try:
            if request.json['message'] == "":
                return {"error": "No puedes enviar un mensaje vacío!"}
            if ddbb.addMessage(ddbb.getUser(session['user']), request.json['friend'], request.json['message'], request.json['timestamp']):
                return {"status": "success", "message": "Se ha enviado correctamente!"}
            return {"error": "No se ha podido enviar el mensaje"}
        except:
            return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

@app.route("/addFriend", methods=["POST"])
def addFriend():
    if request.method == "POST":
        try:
            if ddbb.addFriend(ddbb.getUser(session['user']), request.json['friend']):
                return {"status": "success", "message": "Se ha enviado la solicitud correctamente!"}
            return {"error": "No se ha encontrado al usuario!"}
        except:
            return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

@app.route("/deleteFriend", methods=["POST"])
def deleteFriend():
    if request.method == "POST":
        try:
            if ddbb.deleteFriend(ddbb.getUser(session['user']), request.json['friend']):
                return {"status": "success", "message": "Se ha eliminado correctamente!"}
            return {"error": "No se ha encontrado al usuario!"}
        except:
            return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}
        
@app.route("/deleteAccount", methods=["POST"])
def deleteAccount():
    if request.method == "POST":
        try:
            if ddbb.deleteAccount(ddbb.getUser(session['user'])):
                try:
                    session.pop('user')
                except:
                    pass
                return {"status": "success", "message": "Se ha eliminado correctamente!"}
            return {"error": "No se ha encontrado al usuario!"}
        except:
            return {"error": "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"}

if __name__ == '__main__':
    print("Server started")
    app.run(port=1111)