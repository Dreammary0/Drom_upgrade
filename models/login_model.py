import pandas
import uuid
import hashlib
from sqlite3 import Error

def hash_password(password):
    # uuid используется для генерации случайного числа
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()


#функция изменения базы данных
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def get_user_id(conn, login, password):
    df = pandas.read_sql('''
    select IDUser, Login, HashPassword from User
    ''', conn)
    ID = df.where(df['Login'] == login).dropna(how='any')
    if not ID.empty:
        hashed_password = ID['HashPassword'].values[0]
        if check_password(hashed_password, password):
            return int(ID['IDUser'].values[0])



def add_user(conn,Login,HashPassword,FIO,PhoneNumber,EmailAddress,CityName):
    Add_user = f"""
    INSERT INTO User('Login','FIO','PhoneNumber','EmailAddress','CityName', 'HashPassword') 
    VALUES ('{Login}','{FIO}','{PhoneNumber}','{EmailAddress}','{CityName}', '{HashPassword}')
    """
    execute_query(conn, Add_user)

# Проверить, есть ли user в базе, если нет - добавить. Вернуть его айди.
def reg_user(conn,Login,Password,FIO,PhoneNumber,EmailAddress,CityName):
    hashed_password = hash_password(Password)
    df = pandas.read_sql(f"""    
    select * from User 
    where Login='{Login}'
    """,conn)
    isempty = df.empty
    if isempty:
        add_user(conn,Login,hashed_password,FIO,PhoneNumber,EmailAddress,CityName)
        return get_user_id(conn, Login, Password)

def get_cities(conn):
    return pandas.read_sql(
        '''
        SELECT CityName FROM City where CountryName='Россия'
    ''',conn)



#Удалить user после тестирования
def DeleteTestUsers(con):
    D_User=f"""
    DELETE FROM User;
    UPDATE SQLITE_SEQUENCE SET seq = 0 WHERE name = 'User';
    """
    execute_query(con, D_User)