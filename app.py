import os
from datetime import datetime

from flask import Flask, session, redirect, url_for, request, render_template, send_from_directory
from markupsafe import escape


from utils.Settings import app_secret_key, root_signal, img_root_path
from utils.Users import Users
from utils.PageConfig import PageConfig
from utils.Post import GalleryPost, BoardPost
from utils.AESCipher import encrypt

app = Flask(__name__)
app.secret_key = encrypt(app_secret_key)

# session['user_info'] = email
# session['root_signal'] = root signal

@app.route('/')
@app.route('/', methods=['GET', 'POST'])
def index():
    page_config = PageConfig('Exhibition')

    users = Users(page_config)

    # check db_connection
    if not users.db_connection:
        return render_template("index.html", page_config=page_config)

    # check first root user
    if not users.root_exist():
        page_config.set(comm_root_first = True)
        return render_template("index.html", page_config=page_config)
        
    # check user info
    if session.get("user_info") is not None:
        page_config.set(comm_user_signin=True)
        if session.get("root_signal")  is not None and session["root_signal"] == root_signal:
            page_config.set(comm_root_signin=True)
    gallery_post = GalleryPost(page_config)
    
    # root area
    #======================================================
    # request post write and delete
    if request.method == "POST" and page_config.get("comm_root_signin"):
        image_id = request.form['image_id']
        image_path = request.form['image_path']

        # delete image
        if request.form['action'] == 'delete':
            gallery_post.delete(image_id, image_path)

        # modify image
        if request.form['action'] == 'modify':
            page = request.args.get("page")
            if page is None:
                page = '1'
            return redirect("/gallerypost/modify?image_id=" + image_id + "&page=" + page)
    #======================================================

    # get page length
    page_length = gallery_post.get_page_length()
    page_config.set(data_page_length=page_length)

    # page query validate process
    query_page = request.args.get("page")
    try:
        query_page = int(query_page)
        if query_page < 1:
            query_page = 1
        if query_page > page_length:
            query_page = page_length
    except (ValueError, TypeError):
        query_page = 1
    page_config.set(data_page_last_query = query_page)
    
    # get images
    images = gallery_post.read_page(query_page)
    page_config.set(data_images=images)

    return render_template("index.html", page_config=page_config)

@app.route('/board')
def board():
    page_config = PageConfig('Board')

    users = Users(page_config)

    # check db_connection
    if not users.db_connection:
        return render_template("board.html", page_config=page_config)

    return render_template("board.html", page_config=page_config)

@app.route('/gallerypost')
@app.route('/gallerypost/<mode>', methods=['GET', 'POST'])
def post(mode=None):
    page_config = PageConfig('Write')

    gallery_post = GalleryPost(page_config)

    # check db_connection
    if not gallery_post.db_connection:
        return render_template("write.html", page_config=page_config)

    # check user info
    if session.get("user_info") is not None:
        page_config.set(comm_user_signin=True)
        if session.get("root_signal")  is not None and session["root_signal"] == root_signal:
            page_config.set(comm_root_signin=True)

    page_config.set(data_page_last_query = request.args.get("page"))
    if mode == 'view':
        result = gallery_post.read(request.args.get("image_id"))
        page_config.set(data_image = result)
        # root area
        #======================================================
        if request.method == "POST" and page_config.get("comm_root_signin"):
            data_page_last_query = request.form['data_page_last_query']
            # delete image
            if request.form['action'] == 'delete':
                gallery_post.delete(str(result[0]), result[1])
                return redirect('/?page=' + str(data_page_last_query))

            # modify image
            if request.form['action'] == 'modify':
                return redirect('/gallerypost/modify?image_id=' + str(result[0]) + "&page=" + str(data_page_last_query))
        #======================================================
        return render_template("gallerypost.html", page_config=page_config)

    if not page_config.get("comm_root_signin"):
        return redirect(url_for('index'))

    # root area
    #======================================================
    if mode == 'write':
        # POST request
        if request.method == 'POST':
            title = request.form['title']
            image = request.files['image']
            image_name = str(datetime.now().strftime('%Y%m%d%H%M%S%f')) + '-' + image.filename
            image_path = os.path.join(img_root_path, image_name)
            created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated = created

            # allow only image file
            if image.content_type.split('/')[0] != 'image':
                page_config.set(message = "can't load image, please check the format !!")
                return render_template("write.html", page_config=page_config)

            # save image path and title
            gallery_post.write(image, image_path, title, created, updated)
            return redirect(url_for('index'))
        return render_template("write.html", page_config=page_config)

    if mode == 'modify':
        result = gallery_post.read(request.args.get("image_id"))
        if result is None:
            return redirect(url_for('index'))
        page_config.set(data_image=result)

        # POST request
        if request.method == 'POST':
            title = request.form['title']
            image = request.files['image']
            image_name = str(datetime.now().strftime('%Y%m%d%H%M%S%f')) + '-' + image.filename
            image_path = os.path.join(img_root_path, image_name)
            updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # allow only image file
            if image.content_type.split('/')[0] != 'image':
                page_config.set(message = "can't load image, please check the format !!")
                return render_template("modify.html", page_config=page_config)
            
            # save image path and title
            gallery_post.modify(image, result[0], result[1], image_path, title, updated)
            if request.args.get("page") is not None:
                return redirect('/gallerypost/view?image_id=' + str(result[0]) + "&page=" + request.args.get("page"))
            return redirect(url_for('index'))

        return render_template("modify.html", page_config=page_config)

    return redirect(url_for('index'))
    #======================================================

# signin, logout method
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    page_config = PageConfig('Sign In')

    if session.get("user_info") is not None:
        return redirect(url_for('index')) 
    
    users = Users(page_config)
    
    # check db_connection
    if not users.db_connection:
        return render_template("signin.html", page_config=page_config)

    # POST request
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user_signin, root_signin = users.signin(email, password)

        if user_signin:
            session['user_info'] = request.form['email']
            if root_signin:
                session['root_signal'] = root_signal
            return redirect(url_for('index'))
        else:
            page_config.set(message="account information is not matched !!")

    return render_template("signin.html", page_config=page_config)

@app.route('/signout')
def logout():
    session.pop('user_info', None)
    return redirect(url_for('index'))

# first signup for root(only one)
@app.route('/rootsignup', methods=['GET', 'POST'])
def rootsignup():
    page_config = PageConfig("Root Sign Up")

    users = Users(page_config)

    # check db_connection
    if not users.db_connection:
        return render_template("rootsignup.html", page_config=page_config)

    if users.root_exist():
        return redirect(url_for("index"))

    # root area
    #======================================================
    # POST request
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        passwordcheck = request.form["passwordcheck"]
        
        if password != passwordcheck:
            page_config.set(message = "Password is different !!")
            return render_template("rootsignup.html", page_config=page_config)
        
        # sign up root user
        users.signup(True, email, password)
        
        # make session
        session['user_info'] = request.form['email']
        session['root_signal'] = root_signal
        return redirect(url_for('index'))
    #======================================================
    return render_template("rootsignup.html", page_config=page_config)