fetch('/getAccount').then(response => {response.json()
    .then(data => {
        document.getElementById("username-account").placeholder = data.account["username"];
        document.getElementById("wallet-account").placeholder = data.account["wallet"];
        document.getElementById("email-account").placeholder = data.account["email"];
        document.getElementById("balance-account").placeholder = data.account["balance"] + "€";
        document.getElementById("code-account").placeholder = data.account["code"] + "                   Usuarios invitados: " + data.account["guest"];
        document.getElementById("code-link").href = "lzarusss.pythonanywhere.com/registrar?code=" + data.account["code"]; 
});});