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
    