import pandas
import uuid
import hashlib
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


def hash_password(password):
    # uuid используется для генерации случайного числа
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt


def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()


def get_user_account_info(conn, userID):
    df = pandas.read_sql(f"""    
        select * from User 
        where IDUser='{userID}';
        """, conn)
    return [df['Login'].values[0], df['FIO'].values[0], df['PhoneNumber'].values[0], df['EmailAddress'].values[0],
            df['CityName'].values[0]]


def update_password(conn, IDUser, old_password, new_password):
    df = pandas.read_sql('''
        select IDUser, HashPassword from User
        ''', conn)
    ID = df.where(df['IDUser'] == IDUser).dropna(how='any')
    if not ID.empty:
        hashed_password = ID['HashPassword'].values[0]
        if check_password(hashed_password, old_password):
            HashPassword = hash_password(new_password)
            Update_pwd = f"""
                    UPDATE User
                    SET HashPassword = '{HashPassword}'
                    WHERE IDUser = {IDUser};"""
            execute_query(conn, Update_pwd)
            return True
        else:
            return False


def update_user_info(conn, userID, Login, FIO, PhoneNumber, EmailAddress, CityName):
    df = pandas.read_sql(f"""    
        select * from User 
        where Login='{Login}' and IDUser != '{userID}'
        """, conn)
    isempty = df.empty
    if isempty:
        Update_user = f"""
            UPDATE User
            SET Login='{Login}',
            FIO = '{FIO}',
            PhoneNumber = '{PhoneNumber}',
            EmailAddress = '{EmailAddress}',
            CityName = '{CityName}'
            WHERE IDUser = {userID};
            """
        execute_query(conn, Update_user)
    else:
        print('логин занят')


def get_cities(conn):
    return pandas.read_sql(
        '''
        SELECT CityName FROM City where CountryName='Россия'
    ''', conn)


