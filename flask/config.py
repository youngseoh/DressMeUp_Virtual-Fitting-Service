from flask import Flask
import pymysql

app = Flask(__name__)

def connection():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='1234',
        database='dressmeup',
        cursorclass=pymysql.cursors.DictCursor  # 결과를 Dictionary 형태로 받기 위해 설정
    )

def close(cursor, db_connection):
    cursor.close()
    db_connection.close()