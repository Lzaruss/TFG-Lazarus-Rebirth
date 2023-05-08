import { showErrorPopup, showSuccessPopup } from './utils.js';

// funcion para aclarar el color de los elementos del menu cuando cambias el color en la configuracion
function lightenColor(color, amount) {
    var r = parseInt(color.substring(1,3),16);
    var g = parseInt(color.substring(3,5),16);
    var b = parseInt(color.substring(5,7),16);
    r = Math.min(255, Math.round(r + amount));
    g = Math.min(255, Math.round(g + amount));
    b = Math.min(255, Math.round(b + amount));
    return '#' + r.toString(16).padStart(2, '0') + g.toString(16).padStart(2, '0') + b.toString(16).padStart(2, '0');
  }

function saveSettings(){
    let pickup_color = document.getElementById("pickup_color").value;
    let twofa = document.getElementById("twofa").checked; 
    twofa === true ? twofa = 1 : twofa = 0;
    let notify = document.getElementById("notify").checked; 
    notify === true ? notify = 1 : notify = 0;
    fetch('/saveSettings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            color: pickup_color,
            hover_color: lightenColor(pickup_color, 20),
            twofa: twofa,
            notify: notify
        })

    }).then(response => response.json())
    .then(data => {
        if(data.status === "success"){
            showSuccessPopup("Cambios guardados correctamente");
        }else{
            showErrorPopup("Error al guardar los cambios");
        }
    });
}

function deleteTransactions(){
    fetch('/deleteTransaction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => response.json())
    .then(data => {
        if(data.status === "success"){
            showSuccessPopup("Transacciones eliminadas correctamente!");
        }else{
            showErrorPopup("No se han podido eliminar las transacciones, inténtelo de nuevo más tarde");
        }       
    })
}

function changePassword(){
    fetch('/changePassword', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => response.json())
    .then(data => {
        if(data.status === "success"){
            showSuccessPopup("Se ha enviado el cambio a tu correo!");
        }else{
            showErrorPopup("No se ha podido enviar el cambio de contraseña, inténtelo de nuevo más tarde");
        }
    })
}


window.saveSettings = saveSettings;
window.deleteTransactions = deleteTransactions;
window.changePassword = changePassword;
