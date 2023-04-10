from flask import Flask, session, render_template, request, redirect
import pyrebase 
import dbFunctions as ddbb
import json
app = Flask(__name__)

with open('config.json') as config_file:
    config = json.load(config_file)

firebase = pyrebase.initialize_app(config) 
auth = firebase.auth()
app.secret_key = 'secret_key'

@app.route('/', methods=["POST", "GET"])
def index():
    if('user' in session):
        return redirect("/home")
    
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            auth.sign_in_with_email_and_password(email, password)
            session['user'] = email
            return redirect("/home")
        except Exception as e:
            return render_template('login.html', error=True)

    return render_template('login.html')

@app.route("/registrar.html", methods=["POST", "GET"])
def registrar():
    
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirm-password")
        balance = 5

        if ddbb.checkEmail(email) is None:
            return render_template('registrar.html', error="El correo electrónico no es válido")
        if ddbb.checkPassword(password) is None:
            return render_template('registrar.html', error="La contraseña no es válida (Debe contener al menos 6 caracteres y un número)")
        if not ddbb.checkSamePassword(password, confirmPassword):
            return render_template('registrar.html', error="Las contraseñas no coinciden")
        if ddbb.checkUser(username):
            return render_template('registrar.html', error="El nombre de usuario ya está en uso")
        
        try:
            auth.create_user_with_email_and_password(email, password)
            ddbb.pushDataToUsers(username, {"email": email, "username": username, "balance": balance, "wallet": ddbb.createWallet()})
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
    
    
@app.route("/home", methods=["GET", "POST"])
def home():
    if('user' in session):
        return render_template('home.html')
    else:
        return redirect("/")
    

@app.route("/saldo", methods=["GET"], )
def saldo():
    try:
        return str(ddbb.getBalance(ddbb.getUser(session['user'])))
    except:
        return "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"
    

@app.route("/wallet", methods=["GET"], )
def wallet():
    try:
        return str(ddbb.getWallet(ddbb.getUser(session['user'])))
    except:
        return "Ha ocurrido un error, vuelve a intentarlo en unos minutos o contacta con el administrador"


@app.route("/actualUser", methods=["GET"])  
def actualUser():
    try:
        return str(ddbb.getUser(session['user']))
    finally:
        pass


@app.route("/sendBalance", methods=["GET", "POST"])
def sendBalance():
    userTo = request.form.get("userTo")
    balance = request.form.get("balance")
    userFrom = ddbb.getUser(session['user'])

    try:
        if not ddbb.checkBalance(userFrom, int(balance)):
            return render_template("home.html", error="No tienes suficiente saldo para realizar la transacción!")
        ddbb.sendBalance(userFrom, userTo, int(balance))
        return "Se ha enviado correctamente!"
    except ValueError:
        return "Comprueba la cantidad enviada!"
    except Exception as e:
        return "No se ha podido enviar la petición, comprueba que los datos estan correctos!"


if __name__ == '__main__':
    app.run(port=1111)