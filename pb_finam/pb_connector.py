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
            year_count=data_json['countYearsSubscriptions'],
            month_count=data_json['countMonthSubscriptions'],
            lifetime_count=data_json['countPermanentSubscriptions'],
            year_sum=int(data_json['sumYearsSubscriptions'] * 100),
            month_sum=int(data_json['sumMonthSubscriptions'] * 100),
            lifetime_sum=int(data_json['sumPermanentSubscriptions'] * 100),
        )
