fetch('/getAccount').then(response => {response.json()
    .then(data => {
        document.getElementById("username-account").placeholder = data["username"];
        document.getElementById("wallet-account").placeholder = data["wallet"];
        document.getElementById("email-account").placeholder = data["email"];
        document.getElementById("balance-account").placeholder = data["balance"];
});});