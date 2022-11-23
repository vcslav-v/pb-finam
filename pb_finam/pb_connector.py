import json
import os

import requests

from pb_finam import schemas


def get_subscriptions() -> schemas.SubsStat:
    with requests.sessions.Session() as session:
        session.auth = (os.environ.get('PB_LOGIN'), os.environ.get('PB_TOKEN'))
        resp = session.get(os.environ.get('PB_END_POINT'))
        data_json = json.loads(resp.text)

        return schemas.SubsStat(
            year=data_json['year'],
            month=data_json['month'],
            lifetime=data_json['permanent'],
        )
