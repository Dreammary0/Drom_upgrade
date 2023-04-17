import flask
import pandas

from app import app
from flask import render_template, request, session
from utils import get_db_connection
from models.index_model import get_brands, get_models, get_drives, get_transmissions, get_fuels, get_selling
from models.edit_selling_model import update_selling


@app.route('/edit_selling', methods=['get'])
def edit_selling():
    conn = get_db_connection()
    selling_id = session.get('edit_selling')

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

    if selling_id:
        selling_df = get_selling(conn, selling_id=int(selling_id))
    else:
        return flask.redirect(flask.url_for('account'))

    if session.get('user_id') is None:
        session['user_id'] = 0

    if get_selling(conn, user_id=session['user_id'], selling_id=selling_id).empty:
        session['edit_selling'] = None
        return flask.redirect(flask.url_for('account'))

    # description не обязательно
    if request.values.get('submitted') is not None and not get_selling(conn, user_id=session['user_id'],
                                                                       selling_id=selling_id).empty:
        update_selling(conn, vin, state_number, brand, model, engine_id, capacity, hp,
                       fuel, year, transmission, drive, equip_id, price, selling_id, description)
        return flask.redirect(flask.url_for('account'))

    html = render_template(
        'edit_selling.html',
        user_id=session['user_id'],
        brands=get_brands(conn),
        models=get_models(conn),
        drives=get_drives(conn),
        transmissions=get_transmissions(conn),
        fuels=get_fuels(conn),
        selling_id=selling_id,
        vin=selling_df['BodyOrVinNumber'].values[0],
        state_number=selling_df['StateNumber'].values[0],
        brand=selling_df['BrandName'].values[0],
        model=selling_df['ModelName'].values[0],
        engine_id=selling_df['IDEngine'].values[0],
        capacity=selling_df['Capacity'].values[0],
        hp=selling_df['HP'].values[0],
        fuel=selling_df['FuelType'].values[0],
        year=selling_df['ReleaseDate'].values[0],
        transmission=selling_df['TransmissionType'].values[0],
        drive=selling_df['DriveType'].values[0],
        equip_id=selling_df['IDEquip'].values[0],
        price=selling_df['Price'].values[0],
        description=selling_df['Description'].values[0],
        iterrows=pandas.DataFrame.iterrows,
        int=int,
        str=str
    )
    return html
