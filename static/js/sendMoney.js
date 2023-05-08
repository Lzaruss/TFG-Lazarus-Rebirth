import { showErrorPopup, showSuccessPopup } from './utils.js';

fetch('/actualUser')
  .then(response => response.text())
  .then(data => {
    document.getElementById('sender-input').placeholder = JSON.parse(data).user;
  })

function sendMoney(){

    let receiver = document.getElementById('name-input').value;
    let amount = document.getElementById('amount-input').value;
    
    let data = {
        receiver: receiver,
        amount: amount
    }
    
    
    fetch('/sendBalance', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        if(data.status == 'success'){
            showSuccessPopup(data.message);
        } else {
            showErrorPopup(data.error)
        }
    })
}

window.sendMoney = sendMoney;