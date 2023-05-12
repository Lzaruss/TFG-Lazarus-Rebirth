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

const codeInput = document.getElementById("code-guest");

const url = window.location.href;
const regex = /[?&]code=([^&#]*)/g;
const code = regex.exec(url)[1];

codeInput.value = code;