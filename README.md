# Foro "Los Flaskonautas"

Trabajo práctico para la materia "Introducción al desarrollo de software" de la Facultad de Ingeniería de la Universidad de Buenos Aires.

## Presentation

This project is a practical work for the "Introduction to Software Development" course at the Faculty of Engineering, University of Buenos Aires. It involves creating a full-fledged web application using Flask.

## Features

- Complete API functionality
- User-friendly client interface
- Database initialization and management

## Front End Installation Guide

1. Clone the repository:
    ```bash
    git clone https://github.com/TarabayIvan/tp-introds-flaskonautas.git
    cd tp-introds-flaskonautas
    cd Client
    ```

2. create virtual environment with pipenv:
    ```bash
    mkdir .venv
    pipenv install
    pipenv shell
    ```

3. Run app:
    ```bash
    python app.py
    ```

## Back End Installation Guide

1. Clone the repository:
    ```bash
    git clone https://github.com/TarabayIvan/tp-introds-flaskonautas.git
    cd tp-introds-flaskonautas
    cd API
    ```

2. create virtual environment with pipenv:
    ```bash
    mkdir .venv
    pipenv install
    pipenv shell
    ```

3. Run app:
    ```bash
    python app.py
    ```

## DB Installation Guide Docker

1. Create the container:
    ```bash
    cd Database_initializer
    cd docker
    docker compose up --build -d
    ```

2. Connect to the MySQL database:
    ```bash
    docker exec -it docker-db-1 mysql -u root -p
    ```

## Dependencies

- Flask
- SQLAlchemy
- Pillow
- Werkzeug
- requests
- python-dotenv

## API Endpoints

- `POST /register_user`: Registrar un nuevo usuario.
- `POST /login_user`: Iniciar sesión de usuario.
- `POST /get_user`: Obtener información de usuario.
- `POST /update-password`: Actualizar la contraseña del usuario.
- `POST /create_post`: Crear una nueva publicación.
- `POST /get_posts`: Obtener todas las publicaciones.
- `POST /get_last_posts`: Obtener las publicaciones más recientes.
- `POST /create_response`: Crear una nueva respuesta a una publicación.
- `POST /get_complete_post`: Obtener una publicación con todas sus respuestas.(corregir no envia un erorr si un post es invalido).
- `POST /delete_user`: Eliminar un usuario.
- `PUT /update_post`: Actualizar una publicación.
- `PATCH /update_response`: Actualizar una respuesta.
- `DELETE /delete_post`: Eliminar una publicación.
- `DELETE /delete_response`: Eliminar una respuesta.

## Preview

[Home Page](assets/home_page.png) 
[Categories Page](assets/categories_page.png) 
[Technology Page](assets/technology_page.png) 
[Login Page](assets/signin_page.png) 
[Sign up Page](assets/signup_page.png) 
[Post Page](assets/post_page.png) 
[Latest Posts Page](assets/latest_post_page.png) 
[User Page](assets/user_page.png)
