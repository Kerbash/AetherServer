import traceback
from flask import make_response, Blueprint, render_template, current_app
import os

_dir = os.path.dirname(os.path.abspath(__file__))
html_blueprint = Blueprint('html', __name__, template_folder="templates")

@html_blueprint.app_errorhandler(404)
def not_found(e):
    return "EORROR", 404

@html_blueprint.route('/')
def home():
    return render_template('main_page.html', version = current_app.config["VERSION"])