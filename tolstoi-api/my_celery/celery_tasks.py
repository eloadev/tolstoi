import pdb

import redis
import json

from .celery_config import celery_app

from solving_services.recaptchav2.recaptchav2audiosolver import ReCaptchaV2AudioSolver
from solving_services.image_captcha.imagecaptchasolver import ImageCaptchaSolver


redis_client = redis.StrictRedis(host='redis', port=6379, decode_responses=True)


@celery_app.task
def solve_imagecaptcha(token, content):
    print('Solving image captcha...')
    data = redis_client.get(token)
    data_json = json.loads(data)
    captcha_response = None

    try:
        solver = ImageCaptchaSolver()
        captcha_response = solver.solve(content)
        status = 'CAPTCHA_SOLVED'
        data_json['response'] = captcha_response
    except:
        status = 'CAPTCHA_FAILED'

    data_json['status'] = status
    data_json['response'] = captcha_response

    new_data_json = json.dumps(data_json)
    redis_client.set(token, new_data_json)

@celery_app.task
def solve_recaptchav2(token, url, site_key):
    print('Solving recaptcha v2...')
    data = redis_client.get(token)
    data_json = json.loads(data)
    captcha_response = None

    try:
        solver = ReCaptchaV2AudioSolver()
        captcha_response = solver.solve(url, site_key)
        status = 'CAPTCHA_SOLVED'
        data_json['response'] = captcha_response
    except:
        status = 'CAPTCHA_FAILED'

    data_json['status'] = status
    data_json['response'] = captcha_response

    new_data_json = json.dumps(data_json)
    redis_client.set(token, new_data_json)


