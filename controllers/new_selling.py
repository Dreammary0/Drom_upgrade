import flask
import pandas

from app import app
from flask import render_template, request, session
from utils import get_db_connection
from models.new_selling_model import create_new_selling
from models.index_model import get_brands, get_models, get_drives, get_transmissions, get_fuels


@app.route('/new_selling', methods=['get'])
def new_selling():
    conn = get_db_connection()

    vin = request.values.get('vin')
    state_number = request.values.get('state_number')
    brand = request.values.get('brand')
    model = request.values.get('model')
    engine_id = request.values.get('engine_id')
    capacity = request.values.get('capacity')
    hp = request.values.get('hp')
    fuel = request.values.get('fuel')
    year = request.values.get('year')
    transmission = request.values.get('transmission')
    drive = request.values.get('drive')
    equip_id = request.values.get('equip_id')
    price = request.values.get('price')
    if request.values.get('description'):
        description = request.values.get('description')
    else:
        description = None

    if session.get('user_id') is None:
        session['user_id'] = 0

    # description не обязательно
    if session['user_id'] and vin and state_number and brand and model and engine_id and capacity and hp \
            and fuel and year and transmission and drive and equip_id and price:
        create_new_selling(conn, session['user_id'], vin, state_number, brand, model, engine_id, capacity, hp,
                           fuel, year, transmission, drive, equip_id, price, description)
        return flask.redirect(flask.url_for('index'))

    html = render_template(
        'new_selling.html',
        user_id=session['user_id'],
        brands=get_brands(conn),
        models=get_models(conn),
        drives=get_drives(conn),
        transmissions=get_transmissions(conn),
        fuels=get_fuels(conn),
        iterrows=pandas.DataFrame.iterrows,
        int=int,
        str=str
    )
    return html
