export function showErrorPopup(message) {
    const popup = document.getElementById('error-popup');
    popup.textContent = message;
    popup.style.display = 'block';
    setTimeout(() => {
      popup.style.display = 'none';
    }, 3000); // Ocultar el popup después de 3 segundos (3000 milisegundos)
}

export function showSuccessPopup(message) {
    const popup = document.getElementById('success-popup');
    popup.textContent = message;
    popup.style.display = 'block';
    setTimeout(() => {
      popup.style.display = 'none';
    }, 3000); // Ocultar el popup después de 3 segundos (3000 milisegundos)
  }

// Creamos una matriz global para almacenar los intervalos activos
var intervalosActivos = [];

// Sobrescribimos la función setInterval para almacenar los identificadores de los intervalos activos en la matriz
var originalSetInterval = window.setInterval;
window.setInterval = function() {
  var intervalID = originalSetInterval.apply(this, arguments);
  intervalosActivos.push(intervalID);
  return intervalID;
};

// Creamos una función personalizada que detiene todos los intervalos activos
export function detenerTodosLosIntervalos() {
  for (var i = 0; i < intervalosActivos.length; i++) {
    clearInterval(intervalosActivos[i]);
  }
  // limpiar la matriz de intervalosActivos 
  intervalosActivos = [];
}

const loadingContainer = document.getElementById('loading-container');

export function showLoading() {
  loadingContainer.style.display = 'flex';
}

export function hideLoading() {
  loadingContainer.style.display = 'none';
}