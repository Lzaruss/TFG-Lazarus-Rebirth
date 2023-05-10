import('./utils.js').then((module) => {
  module.detenerTodosLosIntervalos();
});

const popup = document.querySelector('.popup');
const badge = document.querySelector('.badge');


function notifyInterval(){
  fetch('/getNotifications')
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      badge.textContent = "0";
      const link = document.createElement('a');
      link.textContent = "No tienes notificaciones";
      popup.appendChild(link);
    } else {
      badge.textContent = Object.keys(data.notifys).length;

      Object.entries(data.notifys).forEach(([index, notification]) => {
        const link = document.createElement('a');
        link.textContent = `De: ${notification.FROM} | Mensaje: ${notification.message} | Cantidad: ${notification.AMOUNT}€ - ${notification.TIME}`;
        popup.appendChild(link);
      });
    }
  });
}
const twofa = document.getElementById('twofa').className

if(twofa === '1'){
  window.addEventListener('beforeunload', function(event) {
    // Hacer petición para cerrar la sesión del usuario
    fetch('/logout')
      .then(response => {
        if (!response.ok) {
          throw new Error('Error al cerrar la sesión');
        }
      })
      .catch(error => {
        console.error(error);
      });
  });
}
notifyInterval()

const notifys = document.getElementById('twofa').className
if(notifys === '0')
  setInterval(notifyInterval, 1000)