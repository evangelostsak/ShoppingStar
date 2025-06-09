import os
import logging
from flask import Flask, request, render_template, redirect, flash, url_for
from data_manager.sqlite_manager import SQLiteDataManager
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
    """Login an existing User."""
    
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
        
    