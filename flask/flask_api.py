import numpy as np
from flask import Flask, jsonify, request
import person_segmentation
import sys

sys.path.append("../cloth-segmentation")

from clothsegmentation import check_colors_in_image_cv, run_commands
from clothremovebackground import process_cloth_image
from long_short_classification import predict_class
from dressmenup_top import top
from dressmeup_longdress import longdress
from dressmeup_shortdress import shortdress
from dressmeup_shortpants_skirt import shortpants_skirt
from dressup_longpants_skirt import longpants_skirt

from config import connection
import boto3
from PIL import Image
from io import BytesIO
import uuid
import logging
import cv2

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


def upload_image_to_s3_with_path(image_data, file_name):
    try:
        # 이미지 데이터를 Pillow의 Image 객체로 변환
        image = Image.fromarray(image_data)

        # 이미지를 BytesIO 객체에 저장
        image_buffer = BytesIO()
        image.save(image_buffer, format='JPEG')
        image_buffer.seek(0)

        # S3에 파일 업로드
        s3_client.upload_fileobj(image_buffer, S3_BUCKET_NAME, file_name)

        # 업로드된 파일의 URL 생성
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
        # file = request.files['file'].read()  # 전송받은 파일 데이터 읽어서
        # 유저 id같이 넘어옴(body에 이미지랑 같이 담겨서)
        # data = request.json
        # person_image = data['file']
        # userId = data['userId']

        person_image = request.files['file']
        userId = request.form['userId']

        print("userId :" + str(userId))

        # ml 사람 누끼따는 함수. 이미지 바이트로 변환
        image_pil = person_segmentation.segment_person(person_image)
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
        return s3_url, 200
    except Exception as e:
        return str(e), 500



# 옷 이미지 받아서 db에 insert
@app.route('/cloth', methods=['POST'])
def clothImage():
    try:
        app.logger.info('/cloth /cloth /cloth ')

        cloth_image = request.files['file']
        userId = request.form['userId']
        image_path = f"C:/Users/kate2/PycharmProjects/DressMeUp-CV/flask/{uuid.uuid4().hex}_cloth_image.jpg"  # 적절한 경로로 변경하세요
        cloth_image.save(image_path)

        run_commands(image_path)
        app.logger.info('run_commands')
        print("run_commands")

        clothType = check_colors_in_image_cv(
            "C:/Users/kate2/PycharmProjects/DressMeUp-CV/flask/output/cloth_seg/final_seg.png")
        app.logger.info('clothType : ' + clothType)

        print('clothType : ' + clothType)

        # 누끼딴 이미지 반환
        image_np = process_cloth_image(
            "C:/Users/kate2/PycharmProjects/DressMeUp-CV/flask/output/cloth_seg/final_seg.png", image_path, clothType)
        print("image_np")
        image_pil = Image.fromarray(cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB))
        print("image_pil")

        # 이미지 모드를 RGB로 변환
        if image_pil.mode == 'RGBA':
            image_pil = image_pil.convert('RGB')

        image_bytes_io = BytesIO()
        print("BytesIO")
        image_pil.save(image_bytes_io, format='JPEG')  # 이미지 형식에 따라 format을 조절하세요
        print("save")

        image_bytes_io.seek(0)
        print("seek")
        s3_url = upload_image_to_s3(image_bytes_io, f"{userId}_cloth_image_{uuid.uuid4().hex}.jpg")
        print("upload_image_to_s3")
        
        if clothType == 'DRESS,SKIRT':
            clothType = 'DRESS'
            
        if clothType != 'TOP':
            original = predict_class(cloth_image)

            print("clothType : " + str(clothType))
        else:
            clothType = 6


        if s3_url:
            db_connection = connection()
            cursor = db_connection.cursor()
            clothType = clothType.upper()  # 모두 대문자로 변경
            query = 'INSERT INTO cloth (user_id, image, clothType) VALUES (%s, %s, %s)'

            cursor.execute(query, (userId, s3_url, clothType))
            db_connection.commit()

            # 연결 닫기
            cursor.close()
            db_connection.close()
            clothType = clothType.upper()
        return jsonify({'s3_url': s3_url, 'clothType': clothType, 'original': str(original)}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/dress-up', methods=['POST'])
def dressUp():
    try:
        dressUp_model = request.files['file']
        dressUp_cloth = request.files['cloth_file']
        clothId = request.form['clothId']  # 옷 타입'
        clothType = request.form['original']  # 숫자
        print("request")

        model_image_path = f"C:/Users/kate2/PycharmProjects/DressMeUp-CV/flask/{uuid.uuid4().hex}_model_image.jpg"
        cloth_image_path = f"C:/Users/kate2/PycharmProjects/DressMeUp-CV/flask/{uuid.uuid4().hex}_cloth_image.jpg"
        dressUp_model.save(model_image_path)
        dressUp_cloth.save(cloth_image_path)

        print(clothId)
        # if clothId != 'TOP':
        #     clothType = predict_class(dressUp_cloth)

        #     print("clothType : " + str(clothType))
        # else:
        #     clothType = 6


        # clothType = predict_class(dressUp_cloth)
        # print(clothType)

        if clothType == "2" or clothType == "1":
            print("dressUpImage 이전")
            dressUpImage = longpants_skirt(model_image_path, cloth_image_path)
            print("dressUpImage 완료")
        elif clothType == "5" or clothType == "4":
            dressUpImage = shortpants_skirt(model_image_path, cloth_image_path)
        elif clothType == "0":
            dressUpImage = longdress(model_image_path, cloth_image_path)
        elif clothType == "3":
            dressUpImage = shortdress(model_image_path, cloth_image_path)
        else:
            print("dressUpImage 이전")
            dressUpImage = top(model_image_path, cloth_image_path)
            print("dressUpImage 완료")

        s3_url = upload_image_to_s3_with_path(dressUpImage, f"dressUp_image_{uuid.uuid4().hex}.jpg")

        print(s3_url)
        return s3_url, 200
    except Exception as e:
        return str(e), 500



if __name__ == '__main__':
    logging.basicConfig(filename='app.log', level=logging.INFO)
    app.run(debug=True)