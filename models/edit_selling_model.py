import pandas


def update_selling(conn, vin, state_number, brand, model, engine_id, capacity, hp,
                   fuel, year, transmission, drive, equip_id, price, selling_id, description=None):
    cursor = conn.cursor()
    cursor.executescript(f'''
    update Engine set Capacity={capacity},
    HP={hp}, FuelType='{fuel}' where IDEngine='{engine_id}';''')

    cursor.executescript(f'''
    insert or ignore into Engine values
    ('{engine_id}', {capacity}, {hp}, '{fuel}');''')

    car_id = pandas.read_sql(f'''
    select IDCar from Selling where IDSelling={selling_id};''', conn).values[0][0]

    cursor.executescript(f'''
    update Car set BodyOrVinNumber='{vin}', StateNumber='{state_number}', BrandName='{brand}',
    ModelName='{model}', IDEngine='{engine_id}', ReleaseDate={year}, TransmissionType='{transmission}',
    DriveType='{drive}', IDEquip='{equip_id}' where IDCar={car_id};''')

    cursor.executescript(f'''
    update Selling set Price={price}, Description='{description}' where IDSelling={selling_id};''')
