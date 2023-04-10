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