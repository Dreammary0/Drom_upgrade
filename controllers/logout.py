import flask

from app import app
from flask import session


@app.route('/logout', methods=['get'])
def logout():
    session['user_id'] = 0
    return flask.redirect(flask.url_for('index'))
