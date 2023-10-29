# Lazarus Rebirth

![Screenshot of the Application](screenshot.png)

## Description

Lazarus Rebirth is a web application developed in Python using the Flask framework. It utilizes Firebase as a non-relational database to manage user data. This application focuses on providing secure and efficient online financial management and payment solutions.

## Project Structure

- `static/` contains static files such as CSS, JavaScript, and images.
  - `css/` contains style files.
  - `js/` contains JavaScript scripts.
  - `img/` contains images used in the application.
- `templates/` contains HTML templates used for rendering pages.
- `app.py` contains the Flask application logic and defines the API endpoints.
- `dbFunctions.py` provides functions to interact with the Firebase database.
- `config.json` contains the application configuration.

## Database

The application uses Firebase as a non-relational database. It is structured into user nodes, each with subnodes containing various valuable data such as balance, reward code, wallet address, configurations, and more.

For more details on the database structure, refer to [CONFIG.md](CONFIG.md).

## Technologies Used

- Python
- Flask
- Pyrebase
- Firebase
- HTML
- Jinja
- CSS
- JavaScript
- HTTP

## Product Deployment

The application is deployed on PythonAnywhere. To access the production version, visit https://www.lzarusss.pythonanywhere.com
