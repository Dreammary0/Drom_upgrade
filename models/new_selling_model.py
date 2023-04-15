import pandas


def create_new_selling(conn, user_id, vin, state_number, brand, model, engine_id, capacity, hp,
                       fuel, year, transmission, drive, equip_id, price, description=None):
    cursor = conn.cursor()
    cursor.executescript(f'''
    insert into Engine values
    ('{engine_id}', {capacity}, {hp}, '{fuel}')
    on conflict do nothing;
    ''')

    car_exists = pandas.read_sql(f'''
        select IDCar from Car
        where BodyOrVinNumber='{vin}'
        ''', conn)
    if car_exists.empty:
        max_curr_car_id = pandas.read_sql('''
        select max(IDCar) from Car
        ''', conn).values[0][0]
        car_id = max_curr_car_id + 1
    else:
        car_id = car_exists.values[0][0]
    cursor.executescript(f'''
        insert into Car values
        ({car_id}, {user_id}, '{vin}', '{state_number}', '{brand}',
         '{model}', '{engine_id}', {year}, '{transmission}', '{drive}', '{equip_id}')
        on conflict do nothing;
    ''')

    max_curr_selling_id = pandas.read_sql('''
        select max(IDSelling) from Selling
        ''', conn).values[0][0]
    selling_id = max_curr_selling_id + 1
    cursor.executescript(f'''
    insert into Selling values
    ({selling_id}, {car_id}, 1, {price}, '{description}', date('now'), date('now', '+3 month'))
        on conflict do nothing;
    ''')
