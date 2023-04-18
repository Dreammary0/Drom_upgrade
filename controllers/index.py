import flask
import pandas

from app import app
from flask import render_template, request, session
from utils import get_db_connection
from models.index_model import get_brands, get_models, get_transmissions, get_drives, get_selling, remove_selling, \
    get_cities, get_town, edit_favourite_selling, get_likes_count


def check_min_max(min_v, max_v):
    if min_v > max_v:
        min_v, max_v = max_v, min_v
    return min_v, max_v


@app.route('/', methods=['get'])
def index():
    conn = get_db_connection()
    brand = None
    df_brands = get_brands(conn)
    if request.values.get('brand'):
        brand = request.values.get('brand')

    model = None
    df_models = get_models(conn)
    if request.values.get('model'):
        model = request.values.get('model')

    min_price = None
    max_price = None
    if request.values.get('minprice'):
        min_price = int(request.values.get('minprice'))
    if request.values.get('maxprice'):
        max_price = int(request.values.get('maxprice'))
    if min_price and max_price:
        min_price, max_price = check_min_max(min_price, max_price)

    min_year = None
    max_year = None
    if request.values.get('minyear'):
        min_year = int(request.values.get('minyear'))
    if request.values.get('maxyear'):
        max_year = int(request.values.get('maxyear'))
    if min_year and max_year:
        min_year, max_year = check_min_max(min_year, max_year)

    transmission = None
    df_transmissions = get_transmissions(conn)
    if request.values.get('transmission'):
        transmission = request.values.get('transmission')

    drive = None
    df_drives = get_drives(conn)
    if request.values.get('drive'):
        drive = request.values.get('drive')

    min_hp = None
    max_hp = None
    if request.values.get('minhp'):
        min_hp = int(request.values.get('minhp'))
    if request.values.get('maxhp'):
        max_hp = int(request.values.get('maxhp'))
    if min_hp and max_hp:
        min_hp, max_hp = check_min_max(min_hp, max_hp)

    if request.values.get('city'):
        session['city'] = request.values.get('city')

    if session.get('user_id') is not None and session.get('user_id') != 0 and session.get('city') is None:
        selected_city = str(get_town(conn, session['user_id']))
    elif session.get('city') is not None:
        selected_city = session['city']
    else:
        selected_city = 'Владивосток'

    df_selling = get_selling(conn, selected_city, brand, model, min_price, max_price,
                             min_year, max_year, transmission, drive, min_hp, max_hp, user_autho=session['user_id'])

    if session.get('user_id') is None:
        session['user_id'] = 0

    if request.values.get('remove'):
        remove_selling(conn, session['user_id'], request.values.get('remove'), act=0)
        return flask.redirect(flask.url_for('index'))
    if request.values.get('restore'):
        remove_selling(conn, session['user_id'], request.values.get('restore'), act=1)
        return flask.redirect(flask.url_for('index'))

    if request.values.get('favourites'):
        edit_favourite_selling(conn, request.values.get('favourites'), session['user_id'])
        return flask.redirect(flask.url_for('index'))

    df_city = get_cities(conn)
    # выводим форму

    df_likes = get_likes_count(conn)

    html = render_template(
        'index.html',
        user_id=session['user_id'],
        brand=brand,
        model=model,
        brands=df_brands,
        models=df_models,
        min_price=min_price,
        max_price=max_price,
        min_year=min_year,
        max_year=max_year,
        transmissions=df_transmissions,
        transmission=transmission,
        drives=df_drives,
        drive=drive,
        min_hp=min_hp,
        max_hp=max_hp,
        df_selling=df_selling,
        iterrows=pandas.DataFrame.iterrows,
        len=len,
        str=str,
        int=int,
        round=round,
        cities=df_city,
        selected_city=selected_city,
        df_likes=df_likes
    )
    return html
