from flask import Flask, jsonify, request
from config import connection
import boto3
from PIL import Image
from io import BytesIO
import uuid
import logging
import pymysql

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB까지 허용 (원하는 크기로 조절 가능)

# 로깅 설정
logging.basicConfig(filename='app.log', level=logging.DEBUG)

# AWS S3 관련 설정
AWS_ACCESS_KEY = 'AKIAQ5IEBH3LNNBYDBND'
AWS_SECRET_KEY = '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'
S3_BUCKET_NAME = 'dressmeup-user'
S3_REGION = 'ap-northeast-2'

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=S3_REGION
)

def upload_image_to_s3(file_data, file_name):
    try:
        s3_client.upload_fileobj(file_data, S3_BUCKET_NAME, file_name)
        s3_url = f'https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{file_name}'
        return s3_url
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None


@app.route('/')
def home():
    return 'Hello, DressMeUp!'


# 모델 이미지 받아서 db 저장
@app.route('/model', methods=['PATCH'])
def modelImage():
    try:
        app.logger.info('This is an info message.')
        app.logger.info(request.json)
        app.logger.info(request.files)
        # file = request.files['file'].read()  # 전송받은 파일 데이터 읽어서
        # 유저 id같이 넘어옴(body에 이미지랑 같이 담겨서)
        # data = request.json
        # person_image = data['file']
        # userId = data['userId']

        person_image = request.files['file'].read()
        userId = request.form['userId']

        # ml 사람 누끼따는 함수. 이미지 바이트로 변환
        image_pil = Image.fromarray(person_image.astype(np.uint8))
        image_bytes_io = BytesIO()
        image_pil.save(image_bytes_io, format='JPEG')  # 이미지 형식에 따라 format을 조절하세요
        image_bytes_io.seek(0)

        # s3에 업로드하고 url 받아오기
        s3_url = upload_image_to_s3(image_bytes_io, f"{userId}_model_image_{uuid.uuid4().hex}.jpg")

        if s3_url:
            db_connection = connection()
            cursor = db_connection.cursor()
            query = 'UPDATE user_model SET image = %s WHERE user_id = %s'

            cursor.execute(query, (s3_url, userId))
            db_connection.commit()

            # 연결 닫기
            cursor.close()
            db_connection.close()
        return jsonify({'image': s3_url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 옷 이미지 받아서 db에 insert
@app.route('/cloth', methods=['POST'])
def clothImage():
    try:
        cloth_image = request.files['file'].read()
        userId = request.form['userId']
        clothType = request.form['clothType']


        # 이미지 바이트로 변환(아래 옷 누끼따는 함수로 수정)
        image_pil = Image.fromarray(cloth_image.astype(np.uint8))
        image_bytes_io = BytesIO()
        image_pil.save(image_bytes_io, format='JPEG')  # 이미지 형식에 따라 format을 조절하세요
        image_bytes_io.seek(0)
        s3_url = upload_image_to_s3(image_bytes_io, f"{userId}_cloth_image_{uuid.uuid4().hex}.jpg")

        if s3_url:
            db_connection = connection()
            cursor = db_connection.cursor()
            query = 'INSERT INTO cloth (user_id, image, cloth_type) VALUES (%s, %s, %s)'

            cursor.execute(query, (userId, s3_url, clothType))
            db_connection.commit()

            # 연결 닫기
            cursor.close()
            db_connection.close()
        return jsonify({'image': s3_url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dress-up', methods=['POST'])
def dressUp():
    try:
        dressUp_image = request.files['file'].read()
        userId = request.form['userId']

        # 이미지 바이트로 변환(옷 입히는 함수 불러오기)
        image_pil = Image.fromarray(dressUp_image.astype(np.uint8))
        image_bytes_io = BytesIO()
        image_pil.save(image_bytes_io, format='JPEG')  # 이미지 형식에 따라 format을 조절하세요
        image_bytes_io.seek(0)
        s3_url = upload_image_to_s3(image_bytes_io, f"{userId}_dressUp_image_{uuid.uuid4().hex}.jpg")

        if s3_url:
            db_connection = connection()
            cursor = db_connection.cursor()
            query = 'INSERT INTO album (user_id, image, image_like) VALUES (%s, %s, %s)'

            cursor.execute(query, (userId, s3_url, 0))
            db_connection.commit()

            # 연결 닫기
            cursor.close()
            db_connection.close()
        return jsonify({'image': s3_url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logging.basicConfig(filename='app.log', level=logging.INFO)
    app.run(debug=True)
