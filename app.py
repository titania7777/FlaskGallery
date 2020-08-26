from flask import Flask, session, redirect, url_for, request, render_template
from markupsafe import escape

from utils.settings import page_name
from utils.AESCipher import encrypt, decrypt
from utils.img_compressor import img_compressor

app = Flask(__name__)

app.secret_key = encrypt("i can hide your password with AES block Cipher")

@app.route('/')
def index():
    # set a section and logo image
    title = page_name + " - EXHIBITION"
    
    # get images from database
    images = []
    for i in range(30):
        images.append(url_for("static", filename="images/1.jpg"))

    # check session
    if 'login' in session:
        login = True
    else:
        login = False
    
    return render_template("index.html", title=title, images=images, login=login)


# login logout methods
@app.route('/login', methods=['GET', 'POST'])
def login():
    # set a section
    title = page_name + " - login"

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == 'test@gmail.com' and password == '1234':
            session['login'] = request.form['email']
        return redirect(url_for('index'))
    return render_template("login.html", title=title)

@app.route('/logout')
def logout():
    session.pop('login', None)
    return redirect(url_for('index'))
