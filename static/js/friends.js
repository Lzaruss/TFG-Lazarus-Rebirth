import { showErrorPopup, showSuccessPopup, detenerTodosLosIntervalos, showLoading, hideLoading } from './utils.js';

function mostrarChat(friendName) {
    showLoading();
    const chatHistory = document.getElementById('container');

    if (chatHistory.style.display  === 'none') {
        setInterval(() => {getMessages(friendName)}, 10000);
        hideLoading();
    }else{
        chatHistory.style.display = 'none';
        detenerTodosLosIntervalos();
    }
}

function getMessages(friendName){
    showLoading();
    const chatHistory = document.getElementById('container');
    
    chatHistory.style.display = 'block';
    const chatHeader = document.getElementById('amigo-seleccionado');
    const chatMessages = document.querySelector('.chat-messages');
    // Obtener los mensajes del amigo
    fetch(`/getMessages/${friendName}`)
    .then(response => response.json())
    .then(data => {
        hideLoading();
        //vaciamos el chat
        chatMessages.innerHTML = '';
        chatHeader.textContent = friendName;
        // clase para el amigo: friend-message
        // clase para mis mensajes: my-message
        // Mostrar los mensajes
        for (const key in data.response) {
            const message = data.response[key];
                if (message.sender !== "") {
                const p = document.createElement('p');
                p.classList.add('message');
                if (message.sender === friendName) {
                    p.classList.add('friend-message');
                } else {
                    p.classList.add('my-message');
                }
        
                const pSender = document.createElement('p');
                pSender.classList.add('sender');
                pSender.textContent = message.sender;
                p.appendChild(pSender);
        
                const pContent = document.createElement('p');
                pContent.classList.add('contentChat');
                pContent.textContent = message.message;
                p.appendChild(pContent);
        
                const pTimestamp = document.createElement('p');
                pTimestamp.classList.add('timestamp');
                pTimestamp.textContent = message.timestamp;
                p.appendChild(pTimestamp);
        
                chatMessages.appendChild(p);
            }
        }
    });
}
  
function ocultarHistorial(){
    var chatHistory = document.getElementById("container");
    chatHistory.style.display === "block" ? chatHistory.style.display = "none" : chatHistory.style.display = "block";
}



function getCurrentTime() {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const date = new Date();
    const day = date.getDate();
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');
    const timeString = `[${day}/${month}/${year} ${hours}:${minutes}:${seconds}]`;
    return timeString;
  }

function sendMessage(){
    showLoading();
    const actualTime = getCurrentTime();
    const inputMessage = document.getElementById('sendMessage');
    const friendName = document.getElementById('amigo-seleccionado').textContent;
    fetch('/sendMessage', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            friend: friendName,
            message: inputMessage.value,
            timestamp: actualTime
        })
    })
        .then(response => response.json()).then(data => {
            hideLoading();
            if (data.error) {
                showErrorPopup("Ha ocurrido un error al enviar el mensaje");
            }else{
                const chatMessages = document.querySelector('.chat-messages');
                const p = document.createElement('p');
                p.classList.add('message');
                p.classList.add('my-message');
                
                const pContent = document.createElement('p');
                pContent.classList.add('contentChat');
                pContent.textContent = inputMessage.value;
                p.appendChild(pContent);
                
                const pTimestamp = document.createElement('p');
                pTimestamp.classList.add('timestamp');
                pTimestamp.textContent = getCurrentTime();
                p.appendChild(pTimestamp);
                
                chatMessages.appendChild(p);
                inputMessage.value = '';
            }
    });
}


function searchContact(){
    showLoading();
    const friendName = document.getElementById('searchContact');
    fetch('/addFriend', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            friend: friendName.value,
        })
    }).then(response => response.json()).then(data => {
        hideLoading();
        if (data.error) {
            showErrorPopup(data.error);
        } else {
            showSuccessPopup("Usuario añadido correctamente!");
        }
        friendName.value = '';
    });
}

function deleteFriend(){
    showLoading();
    const friendName = document.getElementById('amigo-seleccionado').textContent;
    fetch('/deleteFriend', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            friend: friendName,
        })
    }).then(response => response.json()).then(data => {
        hideLoading();
        if (data.error) {
            showErrorPopup(data.error);
        } else {
            showSuccessPopup("Usuario eliminado correctamente!");
            location.reload();
        }
    });
}

fetch('/getFriends')
    .then(function (response) {
        showLoading();
        return response.json();
    }).then(function (data) {
        hideLoading();
        const friendsList = document.querySelector('.friends-list ul');
        let idCount = 0;
        for (const friendName of Object.keys(data.response)) {
        
            // Crear el elemento <li> y añadirlo a la lista de amigos
            const li = document.createElement('li');
            li.classList.add('friend');
            li.id = idCount;
            idCount++;
            li.onclick = () => mostrarChat(friendName);
            
            const img = document.createElement('img');
            img.src = 'static/img/friends.png';
            img.alt = friendName;
            li.appendChild(img);
            
            const h3 = document.createElement('h3');
            h3.textContent = friendName;
            li.appendChild(h3);
            
            const p = document.createElement('p');
            p.classList.add('friend-info');
            p.textContent = data.response[friendName].wallet;
            li.appendChild(p);
            
            friendsList.appendChild(li);
        } 
    });

document.getElementById('searchContact').addEventListener('keydown', function(event) {if (event.keyCode === 13)searchContact();});
document.getElementById('sendMessage').addEventListener('keydown', function(event) {if (event.keyCode === 13)sendMessage();});

window.searchContact = searchContact;
window.sendMessage = sendMessage;
window.ocultarHistorial = ocultarHistorial;
window.deleteFriend = deleteFriend;