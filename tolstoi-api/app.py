import json
import pdb
import secrets

import redis
from flask import Flask, request, jsonify

from my_celery.celery_tasks import solve_recaptchav2, solve_imagecaptcha


flask_app = Flask(__name__)
redis_client = redis.StrictRedis(host='redis', port=6379, decode_responses=True)


def generate_unique_token():
    token = secrets.token_urlsafe(16)

    while redis_client.get(token):
        token = secrets.token_urlsafe(16)

    return token


@flask_app.route('/in', methods=['POST'])
def in_request():
    method = request.json['method']
    token = generate_unique_token()

    if method == 'image':
        file_info = request.json['file']
        file_content = file_info['content']

        redis_client.set(token,
                         json.dumps({
                             "method": method,
                             "data": {
                                 "file": {
                                     "content": file_content
                                 }
                             },
                             "status": "CAPTCHA_NOT_READY",
                             "response": None
                         }))

        solve_imagecaptcha.apply_async(args=[token, file_content])
    elif method == 'recaptchav2':
        site_key = request.json['sitekey']
        url = request.json['url']

        redis_client.set(token,
                         json.dumps({
                             "method": method,
                             "data": {
                                 "site_key": site_key,
                                 "url": url
                             },
                             "status": "CAPTCHA_NOT_READY",
                             "response": None
                         }))

        solve_recaptchav2.apply_async(args=[token, url, site_key])
    else:
        response = {'message': 'Invalid captcha method'}
        redis_client.delete(token)
        return jsonify(response), 400

    response = {
        'message': 'CAPTCHA solving initiated successfully',
        'token': token
    }

    return jsonify(response), 200


@flask_app.route('/res', methods=['GET'])
def res_request():
    token = request.json['token']

    captcha_data = json.loads(redis_client.get(token))

    match captcha_data['status']:
        case 'CAPTCHA_NOT_READY':
            response = {
                'message': captcha_data['status'],
            }
            return jsonify(response), 202
        case 'CAPTCHA_SOLVED':
            response = {
                'message': captcha_data['status'],
                'response': captcha_data['response']
            }
            return jsonify(response), 200
        case 'CAPTCHA_FAILED':
            response = {
                'message': captcha_data['status']
            }
            return jsonify(response), 500


if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', debug=True, port=5000)
