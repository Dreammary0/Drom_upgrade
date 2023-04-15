import flask

from app import app
import pandas
from flask import render_template, request, session
from utils import get_db_connection
from models.login_model import get_user_id, reg_user, get_cities

@app.route('/login', methods=['get'])
def login():
    conn = get_db_connection()
    # Получаем ID пользователя
    ID = get_user_id(conn, request.values.get('login'), request.values.get('password'))

    if request.values.get('fullname'):
        ID = reg_user(conn, request.values.get('new_login'), request.values.get('new_password'),
                 request.values.get('fullname'), request.values.get('phone'), request.values.get('email'),
                 request.values.get('city'))

    if ID:
        session['user_id'] = ID
        return flask.redirect(flask.url_for('index'))
    mistake = False
    if request.values.get('login') or request.values.get('password') and not ID:
        mistake = True
    df_city = get_cities(conn)

    # выводим форму
    html = render_template(
        'login.html',
        mistake=mistake,
        cities=df_city,
        iterrows=pandas.DataFrame.iterrows
    )
    return html
