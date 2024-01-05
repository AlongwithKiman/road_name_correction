import argparse
import random
import string
from flask import Flask, request, jsonify
import pandas as pd
import json
import asyncio
from juso import process_juso_api
import time
import nest_asyncio

from model.model_server import ModelforServer



app = Flask(__name__)

nest_asyncio.apply()
def get_args():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    return args

args = get_args()
model = ModelforServer(args)
session_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

@app.route('/api', methods=['POST'])
def process_request():
    # request로부터 온 데이터 --> string list

        request_data = request.get_json()
        
        request_list = request_data.get('requestList', [])
        juso_list = [x["requestAddress"] for x in request_list]
        seq = [x["seq"] for x in request_list]
        
        data = {
        "id": session_key,
        'query': juso_list[0:5000],
        'client_args': args.__dict__,
    }
        #model generation
        print("모델 돌리는 중..")
        result = model.get_response(data)
        print("모델 아웃풋 완료.")



        #juso.go.kr api
        print("API돌리는중...")
        juso_list = process_juso_api(result)
        print("API완료.")


        # construct response
        response_body = []
        for idx, result_address in enumerate(juso_list):
            response_body.append({
                'seq': seq[idx],
                'resultAddress': result_address
            })

        response = {
            'HEADER': {
                'RESULT_CODE': 'S',
                'RESULT_MSG': 'Success'
            },
            'BODY': response_body
        }

        return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)
