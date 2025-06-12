import os
import logging
from flask import Flask, request, render_template, redirect, flash, url_for
from backend.data_manager.sqlite_manager import SQLiteDataManager
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.exceptions import NotFound
from werkzeug.utils import secure_filename

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backend/logs/app.log"),  # Log to a file
        logging.StreamHandler()  # Log to console
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Configure file upload settings
UPLOAD_FOLDER = "../static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Configure DATABASE_URI handling sqlite and postgres
base_dir = os.path.abspath(os.path.dirname(__file__))
if os.getenv("FLASK_ENV") == "development":
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{base_dir}/data/db.sqlite"
else:
    POSTGRES_URI = os.getenv("POSTGRES_URI")
    app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URI

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize DataManager
data_manager = SQLiteDataManager(app)

# Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = "error"


@login_manager.user_loader
def load_user(user_id):
    user = data_manager.get_user(user_id)
    return user


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new User."""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'GET':
        return render_template('register.html')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
    if not username or not password or not email:
        flash("All fields are required!", "error")
        return redirect(url_for('register'))
    
    try:
        message = data_manager.register(username, password, email)
        if "already exists" in message:
            flash(f"{message}", "error")
            logger.warning(f"Registration failed: {message}")
            return render_template("register.html")
        
        flash(f"{message}", "success")
        logger.info(f"New user registered: {username}")
        return redirect(url_for('login'))
    
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        flash("Error while adding the user, please try again!", "error")
        return render_template("register.html")
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login route, Login a registered User."""
    
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

    correct_user = data_manager.authenticate_user(username=username, password=password)

    if correct_user:
        login_user(correct_user)
        flash("Welcome back, {correct_user.username}!", "success")
        logger.info(f"User logged in: {username}")
        return redirect(url_for('home'))

    else:
        flash("Invalid username or password", "error")
        logger.warning(f"Login failed for user: {username}")
        return redirect(url_for('login'))
        

@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    """Logout route, Ending session for the current user."""

    user = data_manager.get_user(current_user.id)
    if request.method == "POST":
        logout_user()
        flash("You have been logged out.", "success")
        logger.info(f"User logged out: {user.username}")
        return redirect(url_for('login'))

    return render_template("logout.html")


@app.route("/<user_id>/profile", methods=["GET"])
@login_required
def user_profile(user_id):
    """Display Specific User's profile data."""

    if int(current_user.id) != int(user_id):
        flash("You can only view your own profile!", "error")
        return redirect(url_for('home'))
    
    user = data_manager.get_user(user_id)
    if not user:
        raise NotFound
    
    return render_template("profile.html", user=user, user_id=user_id)
    

@app.route("/<user_id>/profile/update_user", methods=["GET", "POST"])
@login_required
def update_user(user_id):
    """Update Specific User's profile data."""
    
    if int(current_user.id) != int(user_id):
        flash("You can only update your own profile!", "error")
        return redirect(url_for('home'))
    user = data_manager.get_user(user_id)
    if not user:
        raise NotFound("User not found")        
    
    if request.method == "GET":
        return render_template("update_user.html", user=user, user_id=user_id)
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        profile_picture = request.files.get("profile_picture")
        remove_profile_picture = request.form.get("remove_profile_picture")
        filename = None

        try:
            if remove_profile_picture:
                filename = "default.png"
            elif profile_picture and allowed_file(profile_picture.filename):
                filename = secure_filename(profile_picture.filename)
                file_path = os.path.join(os.getcwd(), app.config["UPLOAD_FOLDER"], filename)
                profile_picture.save(file_path)

            # Update  user details
            update_details = data_manager.update_user(
                user_id=user_id,
                username=username if username else user.username,
                password=password if password else user.password,
                email=email if email else user.email,
                profile_picture=filename if (profile_picture or remove_profile_picture) else user.profile_picture)
            
        except Exception as e:
            flash(f"Error updating user, try that again!", "error")
            return redirect(f"/{user_id}/profile/update_user")
        
        flash(f"{update_details}", "success")
        logger.info(f"User details updated: {user.username}")
        return redirect(f"/{user_id}/profile")
    

@app.route("/<user_id>/profile/delete_user", methods=["GET", "POST"])
@login_required
def delete_user(user_id):
    """Delete Specific User's profile."""
    if int(current_user.id) != int(user_id):
        flash("You can only delete your own profile!", "error")
        return redirect(url_for('home'))
    user = data_manager.get_user(user_id)
    if not user:
        raise NotFound("User not found")
    
    if request.method == "GET":
        return render_template("delete_user.html", user=user, user_id=user_id)
    
    if request.method == "POST":

        try:
            user_id = current_user.id
            delete_user = data_manager.delete_user(user_id)

            if not delete_user:
                flash(f"User with ID {user_id} couldn't be found.", "error")
                return redirect('home')
            flash(f"User {user_id} deleted successfully!", "success")
            logout_user()
            logger.info(f"User deleted: {user.username}")
            return redirect(url_for('login'))
        
        except Exception as e:
            flash(f"Error deleting user, try that again!", "error")
            logger.error(f"Error deleting user {user_id}: {e}")
            return redirect(url_for('home'))


@app.route("/", methods=["GET"])
def home():
    """Home route, home.html gets rendered"""
    return render_template("home.html")
    