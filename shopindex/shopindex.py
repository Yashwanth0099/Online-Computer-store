
from flask import Blueprint, render_template, flash, redirect, url_for, current_app
from sql.db import DB

from flask_login import login_required, current_user
shopindex = Blueprint('shopindex', __name__, url_prefix='/',template_folder='templates')

@shopindex.route("/")
def index():
    return render_template("index.html")