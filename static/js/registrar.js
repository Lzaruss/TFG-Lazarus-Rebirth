import('./utils.js').then((module) => {
    module.detenerTodosLosIntervalos();
  });

const password = document.getElementById("password");
const confirmPassword = document.getElementById("confirm-password");
const submitButton = document.getElementById("submit");
const error = document.getElementById("passwords");

submitButton.disabled = true;

const checkPassword = () => {
  if (password.value === confirmPassword.value) {
    submitButton.disabled = false;
    error.innerHTML = "";
  } else {
    error.innerHTML = "Las contraseñas no coinciden";
    submitButton.disabled = true;
  }
};

password.addEventListener("keyup", checkPassword);
confirmPassword.addEventListener("keyup", checkPassword);