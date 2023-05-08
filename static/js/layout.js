import('./utils.js').then((module) => {
  module.detenerTodosLosIntervalos();
});

const popup = document.querySelector('.popup');
const badge = document.querySelector('.badge');
function notifyInterval(){
  fetch('/getNotifications')
    .then(response => response.json())
    .then(notifications => {
      if (notifications.error) {
        badge.textContent = "0";
        const link = document.createElement('a');
        link.textContent = "No tienes notificaciones";
        popup.appendChild(link);
      }else{
        badge.textContent = notifications.length;

        notifications.forEach(notification => {
          const link = document.createElement('a');
          link.textContent = "De: " + notification.FROM + " | Mensaje: " + notification.message + " | Cantidad: " + notification.AMOUNT + "€" + " - " + notification.TIME;
          popup.appendChild(link);
        });
      }
    });
}
notifyInterval()
setInterval(notifyInterval, 120000)