import flask

from app import app
import pandas
from flask import render_template, request, session
from utils import get_db_connection
from models.login_model import get_user_id
from models.account_model import get_user_account_info, update_user_info, update_password, get_cities
from models.index_model import get_selling, remove_selling


@app.route('/account', methods=['get'])
def account():
    conn = get_db_connection()

    if session.get('user_id') is None:
        session['user_id'] = 0

    info = get_user_account_info(conn, session['user_id'])

    if request.values.get('update_account_info'):
        update_user_info(conn, session['user_id'], request.values.get('login'),
                         request.values.get('name'),
                         request.values.get('phone'), request.values.get('email'),
                         request.values.get('city'))
        info = get_user_account_info(conn, session['user_id'])

    if request.values.get('new_password'):
        update_password(conn, session['user_id'], request.values.get('old_password'),
                        request.values.get('new_password'))

    if request.values.get('remove'):
        remove_selling(conn, session['user_id'], request.values.get('idSelling'), act=0)
        return flask.redirect(flask.url_for('account'))
    if request.values.get('restore'):
        remove_selling(conn, session['user_id'], request.values.get('idSelling'), act=1)
        return flask.redirect(flask.url_for('account'))

    if request.values.get('edit_selling'):
        session['edit_selling'] = request.values.get('idSelling')
        return flask.redirect(flask.url_for('edit_selling'))

    df_city = get_cities(conn)

    df_selling = get_selling(conn, user_id=session.get('user_id'))
    # выводим форму
    html = render_template(
        'account.html',
        user_id=session['user_id'],
        fio=info[1],
        phone=info[2],
        town=info[4],
        email=info[3],
        login=info[0],
        iterrows=pandas.DataFrame.iterrows,
        cities=df_city,
        int=int,
        str=str,
        round=round,
        df_selling=df_selling
    )
    return html
