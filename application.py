from flask import Flask, flash, redirect, render_template, request, session
from tempfile import mkdtemp
import os
import requests
from requests.auth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import shutil

app = Flask(__name__)

# TODO: FIgure out how to hide: app secret_key, quizlet id, quizlet secret (app.config, pull info from config.py, put config.py as gitignore)
app.secret_key = "b'\xac\x88\xd5I\x02{\xda\x99(yN\xde?\xdf\xacA\x99\xf7h\xf7\xa98\x89\xc5'"
app.config['QUIZLET_ID'] = "XtkWJxXHWw"
app.config['QUIZLET_SECRET'] = "DbgGge2PQZrmUPy7wsnbcQ"

# Initialize a key in app.config with an empty string so the helper function (clear_folder) does not raise error
app.config["UPLOAD_FOLDER"] = ""

app.debug = True


# Route to show homepage
@app.route('/', methods=["GET"])
def index():
    # Upon redirect to homepage (from login), if user denies access to app from Quizlet login, return error
    if request.args.get("error") == "access_denied":
        flash("User denied access")
        return redirect("/")
    # If user is currently logged in and they visit the home page, clear the temporary folder
    if "user_id" in session:
        if app.config["UPLOAD_FOLDER"]:
            clear_folder()

    return render_template("homepage.html")


# Route to log user in
@app.route('/login')
def quizlet_authorize():
    # If user somehow tries to log in twice
    if "access_token" in session:
        flash("You are already logged in!")
        return redirect('/')
    # Generate random string for state (a string to be passed to Quizlet API, like a csrf token)
    state = os.urandom(24)
    # Set up where all uploaded images will go to (in static folder, within uploaded_files,
    # create temporary folder for each user)
    app.config["UPLOAD_FOLDER"] = mkdtemp(dir="static/uploaded_files")
    # Part 1 of quizlet's Oauth protocol: Get code that we can trade with API for an access code, scope is "write_set"
    return redirect("https://quizlet.com/authorize?response_type=code&client_id=XtkWJxXHWw&scope=read&scope=write_set"
                    "&state={}&redirect_uri=http://127.0.0.1:5000/authorized".format(state))


# Route to authorize user. From "/login" (through Quizlet), redirect to this route
# (that's what the redirect uri is in the long string in "/login")
@app.route('/authorized', methods=["GET", "POST"])
def authorized():
    # If user denies access, return to home page with error message
    if request.args.get("error") == "access_denied":
        flash("User denied access")
        return redirect('/')
    # If user tries to manually enter this route, return error
    if not request.args.get("code"):
        flash("Invalid request!")
        return redirect('/')
    # Part 2 of Quizlet's Oauth protocol: Take code from previous url (passed in trough the url parameter),
    # and post it to Quizlet api to get an access code we can make API calls with
    url = "https://api.quizlet.com/oauth/token?"
    code = request.args.get("code")
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": 'http://127.0.0.1:5000/authorized',
        "client_id": "XtkWJxXHWw"
    }
    # Create response object from a post request (using requests library, pass in data, and BASIC AUTH)
    res = requests.request('POST', url, data=data, auth=HTTPBasicAuth("XtkWJxXHWw", "DbgGge2PQZrmUPy7wsnbcQ"),
                           allow_redirects=True)
    # Get JSON form of the response
    res_data = res.json()
    # Store access token and user's id in session
    session["access_token"] = res_data["access_token"]
    session["user_id"] = res_data["user_id"]

    # Return to main page
    return redirect('/')


# Log user out (Clear session's auth token and delete temporary folder)
@app.route('/logout')
def logout():
    # Make sure user is logged in before the logout occurs
    if "user_id" in session:
        session.clear()
    # Delete the user's temporary storage folder
    if "UPLOAD_FOLDER" in app.config:
        shutil.rmtree(path=app.config["UPLOAD_FOLDER"])
    # Return to main page
    return redirect('/')


# Route that allows user to upload image to server (source: http://flask.pocoo.org/docs/0.12/patterns/fileuploads/)
@app.route('/upload_image', methods=["GET", "POST"])
def upload_image():
    # Check that user is logged in
    if "access_token" not in session:
        flash("Please log in first!")
        return redirect('/')
    # If request method is POST, save the provided file into the specified directory
    if request.method == 'POST':
        # Check if the POST request has the file input
        if 'image' not in request.files:
            flash('Please input a file')
            return redirect(request.url)
        file = request.files['image']
        # If user does not select a file, return error and render same page
        if file.filename == '':
            flash("Invalid file")
            return redirect(request.url)
        # Return error if file type not supported
        if not allowed_file(file.filename):
            flash('Unsupported image type')
            return redirect(request.url)
        # If file exists and extension is allowed, generate a secure file name using werkzeug.utils library
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Save the image's path into session to allow other app routes to access the path
            session["image_path"] = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Save file into user's temporary directory in static folder
            file.save(session["image_path"])
            # User proceeds to cropping image for terms
            return redirect('/term_crop')
    # If request is GET request, render the html
    else:
        return render_template("upload_image.html")


# Route that allows user to crop the uploaded image for the terms only
@app.route('/term_crop', methods=["GET", "POST"])
def term_crop():
    # If request is a POST, take in the cropped coordinates from the html
    if request.method == "POST":
        image = Image.open(session["image_path"])
        x1 = round(float(request.form.get("x1")))
        y1 = round(float(request.form.get("y1")))
        x2 = round(float(request.form.get("x2")))
        y2 = round(float(request.form.get("y2")))
        # Use Python Image Library (PIL) to crop image using specified coordinates
        box = (x1, y1, x2, y2)
        cropped_image = image.crop(box)
        # Save cropped image as terms.jpg
        cropped_image.save(os.path.join(app.config['UPLOAD_FOLDER'], "terms.jpg"))
        # User proceeds to cropping the definition image
        return redirect('/definition_crop')
    # If request is a GET, render the html, and pass in the image path (to display image on screen)
    else:
        return render_template("term_crop.html", path=session["image_path"])


# Route that allows user to crop uploaded image for the definitions only (same logic as term_crop)
@app.route('/definition_crop', methods=["GET", "POST"])
def definition_crop():
    # If request is POST, take in coordinate inputs and crop image
    if request.method == "POST":
        image = Image.open(session["image_path"])
        x1 = round(float(request.form.get("x1")))
        y1 = round(float(request.form.get("y1")))
        x2 = round(float(request.form.get("x2")))
        y2 = round(float(request.form.get("y2")))
        box = (x1, y1, x2, y2)
        cropped_image = image.crop(box)
        # Save cropped image as definitions.jpg
        cropped_image.save(os.path.join(app.config['UPLOAD_FOLDER'], "definitions.jpg"))
        # Send user to finalizing the set creation (such as setting title, setting term/definition languages)
        return redirect("/write_set")
    # If GET request, render template while passing in image path (to display image on screen)
    else:
        return render_template("definition_crop.html", path=session["image_path"])


# Route that writes the Quizlet set
@app.route('/write_set', methods=["GET", "POST"])
def write_set():
    # If route is visited when nobody is logged in, throw an error
    if "access_token" not in session:
        flash("Please Log in First!")
        return redirect('/')
    # If user tries to enter "/write_set" without having any images uploaded, return error
    if len(os.listdir(app.config["UPLOAD_FOLDER"])) == 0:
        flash("Invalid request! Please re-upload your image!")
        return redirect(request.url)
    # Handle POST request when images are properly cropped and title and term/definition languages are set properly
    if request.method == "POST":
        # Pass access token to Quizlet API in the header of a POST request to make an API call
        headers = {"Authorization": "Bearer " + session["access_token"]}
        # Retrieve user input for title, term/definition languages, checking to make sure each was filled out
        title = request.form.get("title")
        lang_terms = request.form.get("lang_terms")
        lang_definitions = request.form.get("lang_definitions")
        if not title:
            flash("Please enter a title!")
            return redirect(request.url)
        if not lang_terms or not lang_definitions:
            flash("Term and Definition Language Required!")
            return redirect(request.url)
        # Run the terms.jpg file through tesseract and save the resulting string as term_text
        term_text = pytesseract.image_to_string(
            Image.open(os.path.join(app.config['UPLOAD_FOLDER'], "terms.jpg")), lang=lang_terms)
        # Run the definitions.jpg through tesseract and save resulting string as definitions_text
        definition_text = pytesseract.image_to_string(
            Image.open(os.path.join(app.config['UPLOAD_FOLDER'], "definitions.jpg")), lang=lang_definitions)
        # Get an array of all the terms, removing any blank spaces the OCR may have recognized
        terms = term_text.split("\n")
        for term in terms:
            if term == "":
                terms.remove(term)
        # Get array of all definitions
        definitions = definition_text.split("\n")
        for definition in definitions:
            if definition == "":
                definitions.remove(definition)

        # The language codes that tesseract and quizlet use are different, so convert tesseract language codes into
        # quizlet codes using a dictionary (for fast lookup)
        quizlet_languages = {
            "eng": "en",
            "chi_sim": "zh-CN",
            "chi_tra": "zh-TW",
            "fra": "fr",
            "spa": "es",
            "rus": "ru",
            "jpn": "ja",
            "kor": "ko",
            "hin": "hi",
            "deu": "de",
            "ita": "it"
        }
        # Construct a data dict that is passed into the api call (POST request), along with the API url
        data = {
            "title": title,
            "terms[]": terms,
            "definitions[]": definitions,
            "lang_terms": quizlet_languages[lang_terms],
            "lang_definitions": quizlet_languages[lang_definitions]
        }
        url = "https://api.quizlet.com/2.0/sets"
        # Make POST request, passing in the headers (access token) and relevant data
        requests.post(url, data=data, headers=headers)
        # Let user know the set has been created
        flash("Your set {} has been successfully created!".format(title))
        # Clear user's temporary folder (but don't delete the folder itself)
        clear_folder()
        # Return to home
        return redirect("/")

    # If request is get, render the create a set page
    if request.method == "GET":
        return render_template("write_set.html")


# Route to display How To gifs and images
@app.route('/how_to')
def how_to():
    return render_template("how_to.html")


# Route to display About page
@app.route('/about')
def about():
    return render_template("about.html")


# Create a set of allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


# Helper function that checks a file name to make sure its extension is allowed, and returns true if it is allowed.
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Helper function that clears user's temporary folder
def clear_folder():
    folder = app.config["UPLOAD_FOLDER"]
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
