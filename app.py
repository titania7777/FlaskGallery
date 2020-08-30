import os, io
from datetime import datetime

from flask import Flask, session, redirect, url_for, request, render_template, send_from_directory
from markupsafe import escape

import mysql.connector as connector
from mysql.connector import Error

from utils.settings import page_name, host, database, user, password, img_root_path
from utils.AESCipher import encrypt, decrypt
from utils.img_compressor import img_compressor_byte, remove_image

app = Flask(__name__)

app.secret_key = encrypt("this is a session secret key")
rootsign = 'i am root'
num_image = 30

def connect():
    conn = None
    try:
        conn = connector.connect(
            host = host,
            database = database,
            user = user, 
            password = password,
        )
    except Error as e:
        print("[connect error: {}]".format(e))
    return conn

@app.route('/')
@app.route('/', methods=['GET', 'POST'])
def index():
    page_config = {}
    page_config['title'] = page_name + " - EXHIBITION"
    page_config['login'] = None
    page_config['db'] = True
    page_config['images'] = None
    page_config['page_length'] = 0
    page_config['first'] = False

    # config session['login']
    if session.get('login') and session['login'] == rootsign:
        page_config['login'] = session['login']
    
    # config check db
    conn = connect()
    if conn is None:
        page_config['db'] = False
        return render_template("index.html", page_config=page_config)
    cursor = conn.cursor()

    if request.method == 'POST' and page_config['login'] == rootsign:
        image_id = request.form['image_id']
        image_name = request.form['image_name']

        # delete image
        if request.form['action'] == 'delete':
            sql = "DELETE FROM post_gallery WHERE pgid=%s"
            cursor.execute(sql, (image_id,))
            conn.commit()

            remove_image(image_name)

        if request.form['action'] == 'modify':
            pass

    # get images from database
    sql = "SELECT * FROM post_gallery ORDER BY created DESC"
    cursor.execute(sql)
    images = cursor.fetchall()

    # config page_length, unsigned integer(fixed number of images=30)
    page_length = int((len(images)-1)/num_image)
    if page_length < 0:
        page_length += 1
    page_config['page_length'] = page_length
    
    if page_length == 0:
        sql = "SELECT * FROM users WHERE root=true"
        cursor.execute(sql)
        if cursor.fetchone() is None:
            page_config['first'] = True
    cursor.close(); conn.close()

    # check page and convert to integer
    query_page = request.args.get('page')
    try:
        query_page = int(query_page)
        if query_page < 0:
            query_page = 0
        if query_page >= page_length:
            query_page = page_length
    except (ValueError, TypeError):
        page_config['images'] = images[:num_image]
        return render_template("index.html", page_config=page_config)

    # select page
    page_config['images'] = images[num_image * query_page:num_image * (query_page+1)]

    return render_template("index.html", page_config=page_config)

@app.route('/board')
def board():
    page_config = {}
    page_config['title'] = page_name + " - BOARD"
    page_config['db'] = True

    return render_template("board.html", page_config=page_config)

@app.route('/post')
@app.route('/post/<mode>', methods=['GET', 'POST'])
def post(mode=None):
    page_config = {}
    page_config['title'] = page_name + " - WRITE"
    page_config['check'] = True
    page_config['db'] = True
    
    if mode == None:
        return redirect(url_for('index'))
    
    if not session.get('login'):
        return redirect(url_for('login'))

    # only use root user
    if session['login'] != rootsign:
        return redirect(url_for('index'))

    # connect to database
    conn = connect()
    if conn is None:
        page_config['db'] = False
        return render_template("write.html", page_config=page_config)
    
    if mode == 'write':
        # POST request
        if request.method == 'POST':
            title = request.form['title']
            image = request.files['image']
            image_name = str(datetime.now().strftime('%Y%m%d%H%M%S%f')) + '-' + image.filename
            
            # allow only image file
            if image.content_type.split('/')[0] != 'image':
                page_config['check'] = False
                conn.close()
                return render_template("write.html", page_config=page_config)

            # save image path and title
            cursor = conn.cursor()
            sql = "INSERT INTO post_gallery (image, title, created, updated) values (%s, %s, %s, %s)"
            cursor.execute(sql, (os.path.join(img_root_path, image_name), title, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit(); cursor.close(); conn.close()

            # compress image and save
            img_compressor_byte(io.BytesIO(image.read()), image_name)
            return redirect(url_for('index'))

        return render_template("write.html", page_config=page_config)
    
    if mode == 'modify':
        # POST request
        return render_template("modify.html", db=True)
        if request.method == 'POST':
            pass

# login, logout method
@app.route('/login', methods=['GET', 'POST'])
def login():
    page_config = {}
    page_config['title'] = page_name + " - LOGIN"
    page_config['check'] = True
    page_config['db'] = True

    # POST request
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # check user information
        conn = connect()
        if conn is None:
            page_config['db'] = False
            return render_template("login.html", page_config=page_config)
        
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE email=%s"
        cursor.execute(sql, (email,))
        result = cursor.fetchone()
        cursor.close(); conn.close()

        if result is None:
            page_config['check'] = False
            return render_template("login.html", page_config=page_config)
        elif decrypt(result[2]).decode("utf-8") == password:
            session['login'] = request.form['email']
            if result[0] == 1:
                session['login'] = rootsign
            return redirect(url_for('index'))
        else:
            page_config['check'] = False
            return render_template("login.html", page_config=page_config)

    return render_template("login.html", page_config=page_config)

@app.route('/logout')
def logout():
    session.pop('login', None)
    return redirect(url_for('index'))

# first signup for root(only one)
@app.route('/rootsignup', methods=['GET', 'POST'])
def rootsignup():
    page_config = {}
    page_config['title'] = page_name + " - ROOTSIGNUP"
    page_config['check'] = True
    page_config['db'] = True

    # ignore root signup when root exist
    conn = connect()
    if conn is None:
        page_config['db'] = False
        return render_template("rootsignup.html", page_config=page_config)

    cursor = conn.cursor()
    sql = "SELECT * FROM users WHERE root=true"
    cursor.execute(sql)
    if cursor.fetchone() is not None:
        cursor.close(); conn.close()
        return redirect(url_for('index'))

    # POST request
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        passwordcheck = request.form['passwordcheck']
        
        # check password
        if password != passwordcheck:
            page_config['check'] = False
            cursor.close(); conn.close()
            return render_template("rootsignup.html", page_config=page_config)
        
        # encrypt password
        password = encrypt(password)
        
        # insert root account into database
        sql = "INSERT INTO users (root, email, password) values (true, %s, %s)"
        cursor.execute(sql, (email, password))
        conn.commit(); cursor.close(); conn.close()
        
        # make session
        session['login'] = rootsign
        return redirect(url_for('index'))
    
    return render_template("rootsignup.html", page_config=page_config)