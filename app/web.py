import json
import os
import time
from subprocess import PIPE, Popen

from flask import Blueprint, Response
from flask_login import current_user, login_required


blueprint = Blueprint('web', __name__)


@blueprint.route('/preview')  # Strona z oblsuga procesu kalibracji
def preview():
    # camera_model = {}
    # camera_model = camera_Model()
    return sessions.session_monitor('preview.html')
