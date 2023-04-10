import('./clearInteval.js').then((module) => {
  module.detenerTodosLosIntervalos();
});

const saldo = document.querySelector('.saldo');
const wallet = document.querySelector('#wallet');
const welcomeDiv = document.querySelector('#welcomeDiv');
const dateDiv = document.querySelector('#date');

function getFormattedDate() {
  const date = new Date();
  const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  return date.toLocaleDateString('es-ES', options);
}

function updateUser() {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/actualUser');
  xhr.onload = function() {
      welcomeDiv.innerHTML = "Bienvenido/a " + xhr.responseText;
      console.log("Bienvenido/a " + xhr.responseText)
  };
  xhr.send();
}

function updateWallet() {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/wallet');
  xhr.onload = function() {
      wallet.innerHTML = xhr.responseText;
  };
  xhr.send();
}

function updateSaldo() {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/saldo');
  xhr.onload = function() {
      var data = JSON.parse(xhr.responseText);
      saldo.innerHTML = data + "€";
  };
  xhr.send();
}

function copyToClipboard() {
  var text = document.getElementById("wallet").innerText;
  navigator.clipboard.writeText(text);
  console.log("Copiado al portapapeles: " + text);
}

function mostrarRecuadro(enviar=true) {
  var recuadro = document.getElementById("input-container");
  document.getElementById("error").innerHTML="";
  recuadro.style.display = recuadro.style.display === "none" ? "block" : "none";
}

function enviarDatosAlServidor(parametro1, parametro2) {
  console.log("userTo=" + parametro1 + "&balance=" + parametro2);
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById("error").innerHTML = this.responseText;
    }
  };
  xhttp.open("POST", "/sendBalance", true);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("userTo=" + parametro1 + "&balance=" + parametro2);
}

document.getElementById("enviarBalance").addEventListener("click", function(){
  let walletPlaceholder = document.getElementById("walletPlaceholder").value;
  let balancePlaceholder = document.getElementById("balancePlaceholder").value;
  enviarDatosAlServidor(walletPlaceholder, balancePlaceholder);
});

dateDiv.innerHTML = getFormattedDate();
updateWallet();
updateSaldo();
updateUser();
setInterval(updateSaldo, 10000)
