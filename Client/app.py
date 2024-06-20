from flask import Flask, jsonify, request, url_for, redirect, render_template, session, current_app, flash
from werkzeug.security import generate_password_hash
from PIL import Image
import requests
import secrets
import os

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}
ALLOWED_CATEGORIES = {'Technology', 'Science', 'Health', 'Music', 'Politics', 'Sports', 'Entertainment', 'Travel', 'Art'}

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 # Limita el peso de la imagen a 2mb
app.secret_key = "secretkey"

API_URL = 'http://localhost:5000'


@app.route("/")
def index():
    if 'user' in session:
        username = session['user']['username']
        return render_template("index.html", username = username)
    return render_template("index.html")


"""FUNCIONES DE USUARIOS"""

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        security_answer_one = request.form.get('security_answer_one')
        security_answer_two = request.form.get('security_answer_two')
        passhash = generate_password_hash(password)
        user = {'username': username, 'password': passhash, 'security_answer_one': security_answer_one, 'security_answer_two': security_answer_two}
        if (username and password and security_answer_one and security_answer_two):
            response = requests.post(API_URL + "/register_user", json=user)
            if response.status_code == 201:
                flash("Registro exitoso!", "success")
                return redirect(url_for('login'))
            else:
                flash("Registro fallido!", "error")
                return render_template('signup.html')
    return render_template('signup.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user_credentials = {'username': username, 'password': password}
        if username and password:
            response = requests.post(API_URL + "/login_user", json=user_credentials)
            if response.status_code == 200:
                user_data = response.json()
                session['user'] = user_data
                flash("Login exitoso!", "success")
                return redirect(url_for('index'))
            else:
                flash("Login fallido!", "error")
                return redirect(url_for('login'))
    return render_template('login.html')


@app.route("/delete-account", methods=['GET', 'POST'])
def delete_account():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user_credentials = {'username': username, 'password': password}
        if username and password:
            response = requests.delete(API_URL + "/delete_user", json=user_credentials)
            if response.status_code == 200:
                session.pop('user', None)
                return redirect(url_for('index'))
            else:
                flash("No se pudo eliminar la cuenta!", "error")
                return redirect(url_for('index'))
    return render_template('delete-account.html')


@app.route('/recovery', methods=['GET', 'POST'])
def recovery():
    if request.method == "POST":
        username = request.form.get('user')
        new_password = request.form.get('newpword')
        security_answer_1 = request.form.get('secquestions1')
        security_answer_2 = request.form.get('secquestions2')
        new_password_hashed = generate_password_hash(new_password)
        user_credentials = {'username': username, 'password': new_password_hashed, 'security_answer_one': security_answer_1 , 'security_answer_two': security_answer_2 }
        if username and new_password and security_answer_1 and security_answer_2:
            respone = requests.patch(API_URL + '/update_password', json = user_credentials)
            if respone.status_code == 200:
                flash("Se cambio la contraseña exitosamente!", "success")
                return redirect(url_for('login'))
            elif respone.status_code == 401:
                error_msj = "Las respuestas a las preguntas de seguridad son incorrectas."
                flash(f"{error_msj}", "error")
                return render_template('recovery.html')
            elif respone.status_code == 404:
                error_msj = "El usuario no existe."
                flash(f"{error_msj}", "error")
                return render_template('recovery.html')
            else:
                error_msj = "Hubo un problema al cambiar la contraseña"
                flash(f"{error_msj}", "error")
                return render_template('recovery.html')
    return render_template('recovery.html')


@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route("/user_data", methods=['GET'])
def get_user_data():
    if 'user' in session:
        user_id = session['user']['id']
        response = requests.get(API_URL + f"/user/{user_id}")
        if response.status_code == 200:
            user_data = response.json()
            return render_template("user.html", user_data=user_data)
        else:
            return render_template("user.html", user_data={"username": "Usuario no autenticado", "password": "Usuario no autenticado"})
    else:
        return render_template("user.html", user_data={"username": "Usuario no autenticado", "password": "Usuario no autenticado"})


"""FUNCIONES DE POSTEOS"""

@app.route("/categories", methods=['GET'])
def categories():
    return render_template("categories.html")


@app.route("/c/<selected_category>")
def category(selected_category):
    if selected_category not in ALLOWED_CATEGORIES:
        return page_not_found(404)
    response = requests.get(API_URL + f"/get_posts/{selected_category}")
    posts = response.json()
    return render_template("category.html", posts=posts, category=selected_category)


@app.route('/send_post', methods=['POST'])
def send_post():
    post_title = request.form.get("post-title")
    post_content = request.form.get("post-content")
    post_category = request.form.get("post-category")
    post_image = request.files['post-image']
    if not 'user' in session:
        flash("Necesita iniciar session para publicar un post!", "error")
        return redirect(url_for('category', selected_category=post_category))
    username = session['user']['username']
    if not (username and post_title and post_content and post_category):
        flash("El envio del post a fallado, no se recibieron los datos esperados!", "error")
        return redirect(url_for('category', selected_category=post_category))
    if not post_image:
        filename = ""
    else:
        post_image = request.files['post-image']
        filename = save_image(post_image)
        if not filename:
            flash("La imagen que selecciono es invalida!", "error")
            return redirect(url_for('category', selected_category=post_category))
    post = {'username': username, 'title': post_title, 'post': post_content, 'category': post_category, 'image_link': filename}
    response = requests.post(API_URL + "/create_post", json=post)
    if response.status_code == 201:
        flash("Post enviado exitosamente!", "success")
    else:
        flash("El envio del post a fallado!", "error")
    return redirect(url_for('category', selected_category=post_category))


def save_image(image):
    _, f_ext = os.path.splitext(image.filename) #divide el nombre de la imagen en 2, el nombre puro que no nos interesa y la extencion
    if f_ext not in ALLOWED_EXTENSIONS: # verifica que la extencion esta permitida
        return None
    random_hex = secrets.token_hex(8) #crea un nombre random para la imagen
    image_fn = random_hex + f_ext #une el nombre random con la extension
    image_path = os.path.join(current_app.root_path, 'static', 'images', 'posts-images', image_fn) #crea la ruta completa de la imagen
    image.save(image_path)
    try:
        Image.open(image_path) #verifica que es una imagen valida
        return image_fn
    except IOError:
        os.remove(image_path)
        return None
    

@app.route("/delete_request_post/<category>/<id_post>")
def delete_request_post(id_post, category):
    try:
        if not 'user' in session:
            flash("Necesita iniciar session para publicar un post!", "error")
            return redirect(url_for('category', selected_category=category))
        username = {'username': session['user']['username']}
        response = requests.delete(API_URL + f"/delete_post/{id_post}", json=username)
        if (response.status_code >= 200) and (response.status_code < 300):
            _, image_link = response.json()
            if image_link['image_link']:
                image_path = os.path.join(current_app.root_path, 'static', 'images', 'posts-images', image_link['image_link'])
                if os.path.exists(image_path):
                    os.remove(image_path)
            flash("Se ha eliminado exitosamente!", "success")
            return redirect(url_for('category', selected_category=category))
        else:
            flash("Error al intentar eliminar el post.", "error")
            return redirect(url_for('category', selected_category=category))
    except Exception as e:
        flash(f"Error al eliminar el post: {e}", "error")
        return redirect(url_for('category', selected_category=category))
    

@app.route('/c/<category>/edit_post/<id_post>', methods = ['GET', 'POST'])
def edit_post(category, id_post):
    if not 'user' in session:
        flash("Necesita iniciar sesion para editar el post!", "error")
        return redirect(url_for('category', selected_category=category))
    if request.method == 'POST':
        title = request.form.get('post-title')
        post_content = request.form.get('post-content')

        data = {"title": title, "post": post_content, "username": session['user']['username']}
        response = requests.patch(API_URL + '/update_post/' + str(id_post), json=data)
        if response.status_code == 200:
            flash("El post se ha editado correctamente.", "success")
            return redirect(url_for('category', selected_category=category))
        else:
            flash("No se pudo editar el post.", "error")
            
    return render_template("edit_post.html", category = category, id_post = id_post)


@app.route("/latest_posts", methods=['GET'])
def latest_posts():
    response = requests.get(API_URL + "/get_last_posts")
    if response.status_code == 200:
        posts = response.json()
        return render_template("latest_posts.html", posts=posts)
    return jsonify({"error": "No se pudieron obtener los posts"}), 400
    

"""FUNCIONES DE RESPUESTAS"""

@app.route("/c/<selected_category>/post/<id_post>")
def responses(selected_category, id_post):
    response = requests.get(API_URL + f"/get_complete_post/{id_post}")
    post, responses = response.json()
    return render_template("post.html", post=post, responses=responses)


@app.route("/send_response", methods=['GET', 'POST'])
def send_response():
    if request.method == 'POST':
        response_content = request.form.get('response-content')
        post_id = request.form.get('post-id')
        post_category = request.form.get('post-category')
        if not 'user' in session:
            flash("Necesita iniciar session para responder a un post!", "error")
            return redirect(url_for('responses', selected_category=post_category, id_post=post_id))
        username = session['user']['username']
        response = {"username": username, "post": response_content, "id_post": post_id}
        post_response = requests.post(API_URL + "/create_response", json=response)
        if post_response.status_code == 201:
            flash("Respuesta enviada exitosamente!", "success")
        else:
            flash("El envio la respuesta ha fallado!", "error")
    return redirect(url_for('responses', selected_category=post_category, id_post=post_id))
    

@app.route('/c/<post_category>/post/<id_post>/update_response/<id_response>', methods=['GET', 'POST'])
def update_response(post_category, id_post, id_response):
    if not 'user' in session:
        flash("Necesita iniciar sesion para editar este comentario!", "error")
        return redirect(url_for('responses', selected_category=post_category, id_post=id_post))
    if request.method == 'POST':
        id_response = request.form.get('id_response')
        post = request.form.get('post')
        response_data = {
            'id_response': id_response,
            'post': post,
            "username": session['user']['username']
        }
        response = requests.patch(API_URL + '/update_response', json=response_data)
        if response.status_code == 200:
            message = "La respuesta se ha actualizado correctamente."
            flash(message, "success")
            return redirect(url_for('responses', selected_category=post_category, id_post=id_post))
        else:
            error = "No se pudo actualizar la respuesta."
            flash(error, "error")
            
    return render_template('update_response.html', post_category = post_category, id_post = id_post, id_response = id_response)


@app.route('/remove_response')
def remove_response():
    id_response = request.args.get('id_response')
    id_post = request.args.get('id_post')
    post_category = request.args.get('post_category')
    if not 'user' in session:
        flash("Necesita iniciar session para borrar un comentario!", "error")
        return redirect(url_for('responses', selected_category=post_category, id_post=id_post))
    username = session['user']['username']
    data = {"username": username, "id_response": id_response}
    response = requests.delete(API_URL + '/delete_response/' + id_response, json=data)
    if response.status_code == 200:
        flash("La respuesta se ha borrado correctamente.", "success")
    else:
        flash("No se pudo borrar la respuesta.", "error")
    return redirect(url_for('responses', selected_category=post_category, id_post=id_post))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run("127.0.0.1", port="5001", debug=True)
