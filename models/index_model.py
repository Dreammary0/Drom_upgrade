import pandas
import datetime
from sqlite3 import Error


# функция изменения базы данных
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def get_cities(conn):
    return pandas.read_sql(
        '''
        SELECT CityName FROM City where CountryName='Россия'
    ''', conn)


def get_brands(conn):
    return pandas.read_sql(
        '''
        SELECT BrandName FROM Brand
        ''', conn)


def get_models(conn):
    return pandas.read_sql(f'''
        SELECT * FROM Model
        ''', conn)


def get_transmissions(conn):
    return pandas.read_sql('''
        SELECT TransmissionType FROM Transmission
        ''', conn)


def get_drives(conn):
    return pandas.read_sql('''
        SELECT DriveType FROM Drive
        ''', conn)


def get_fuels(conn):
    return pandas.read_sql('''
        SELECT FuelType FROM Fuel
        ''', conn)


def get_selling(conn, city=None, brand=None, model=None, min_price=None, max_price=None,
                min_year=None, max_year=None, transmission=None, drive=None,
                min_hp=None, max_hp=None, user_id=None, selling_id=None, user_autho=None):
    check_actuality(conn)
    df = pandas.read_sql(f'''
    select Car.IDUser, BodyOrVinNumber, StateNumber, BrandName, ModelName,
    E.IDEngine, Capacity, HP, FuelType, ReleaseDate, TransmissionType, DriveType, IDEquip,
    Actuality, Price, Description, AdditionDate, ExpirationDate, CityName, IDSelling, PhoneNumber
    from Car
    join Selling S on Car.IDCar = S.IDCar
    join Engine E on E.IDEngine = Car.IDEngine
    join User U on U.IDUser = Car.IDUser
    ''', conn)
    if selling_id:
        df = df.where(df['IDSelling'] == int(selling_id)).dropna(how='any')
    if city and city != 'Все регионы':
        df = df.where(df['CityName'] == city).dropna(how='any')
    if brand:
        df = df.where(df['BrandName'] == brand).dropna(how='any')
    if model:
        df = df.where(df['ModelName'] == model).dropna(how='any')
    if min_price:
        df = df.where(df['Price'] >= min_price).dropna(how='any')
    if max_price:
        df = df.where(df['Price'] <= max_price).dropna(how='any')
    if min_year:
        df = df.where(df['ReleaseDate'] >= min_year).dropna(how='any')
    if max_year:
        df = df.where(df['ReleaseDate'] <= max_year).dropna(how='any')
    if transmission:
        df = df.where(df['TransmissionType'] == transmission).dropna(how='any')
    if drive:
        df = df.where(df['DriveType'] == drive).dropna(how='any')
    if min_hp:
        df = df.where(df['HP'] >= min_hp).dropna(how='any')
    if max_hp:
        df = df.where(df['HP'] <= max_hp).dropna(how='any')
    if user_id:
        df = df.where(df['IDUser'] == user_id).dropna(how='any')

    df = df.sort_values(by='Actuality', ascending=False)
    # Добавим столбец с избранным
    df1 = pandas.read_sql(f'''
       select * from User_Selling where user_id = '{user_autho}';
       ''', conn)
    df1.rename(columns={'selling_id': 'IDSelling', 'user_id': 'Like'}, inplace=True)
    result = pandas.merge(df, df1, on='IDSelling', how='left')
    result['Like'] = result['Like'].fillna(0)

    # Добавим столбец с количеством добавлений в избранное
    likes_count = pandas.read_sql('''
       select selling_id as IDSelling, count(user_id) as likes_count from User_Selling group by selling_id;''', conn)
    result = pandas.merge(result, likes_count, on='IDSelling', how='left')
    result['likes_count'] = result['likes_count'].fillna(0)

    return result


def get_favourite_selling(conn, df):
    df = df.drop(df[df['Like'] == 0].index)
    return df


# Проверить актуальность и отметить как устаревшее, если его время пришло
def check_actuality(conn):
    today = datetime.date.today()
    df = pandas.read_sql(f"""
    Select * from Selling
     WHERE ExpirationDate < '{today}' and Actuality = 1;
    """, conn)
    isempty = df.empty
    if not isempty:
        Update_actuality = f"""
                UPDATE Selling
                SET Actuality = '0'
                WHERE ExpirationDate < '{today}';
                """
        execute_query(conn, Update_actuality)


def remove_selling(conn, user_id, selling_id, act):
    df = pandas.read_sql('''
    select IDUser, IDSelling from Selling
    join Car C on C.IDCar = Selling.IDCar
    ''', conn)
    df = df.where(df['IDUser'] == user_id).dropna(how='any')
    df = df.where(df['IDSelling'] == float(selling_id)).dropna(how='any')
    if not df.empty:
        cursor = conn.cursor()
        cursor.executescript(f'''
        update Selling set Actuality={act}
        where IDSelling={selling_id}
        ''')
        if act:
            cursor.executescript(f'''
            update Selling set ExpirationDate=date('now', '+3 month')
            where IDSelling={selling_id}
            ''')
        else:
            cursor.executescript(f'''
                        update Selling set ExpirationDate=date('now')
                        where IDSelling={selling_id}
                        ''')
        conn.commit()


def get_town(conn, IDUser):
    df = pandas.read_sql(
        f'''
        SELECT CityName FROM User where IDUser='{IDUser}'
    ''', conn)
    return df['CityName'].values[0]


def edit_favourite_selling(conn, idSelling, idUser):
    df = pandas.read_sql(
        f'''
        SELECT * FROM User_Selling where user_id='{idUser}' and selling_id='{idSelling}'
    ''', conn)
    isempty = df.empty
    if isempty:
        edit_favourite = f"""
            INSERT INTO User_Selling('user_id', 'selling_id')
            VALUES ('{idUser}','{idSelling}')
        """
    else:
        edit_favourite = f"""
        DELETE from User_Selling where user_id='{idUser}' and selling_id='{idSelling}'
                """
    execute_query(conn, edit_favourite)


def get_likes_count(conn):
    likes = pandas.read_sql('''
    select selling_id, count(user_id) as likes_count from User_Selling group by selling_id;''', conn)
    return likes
