from airflow.hooks.base import BaseHook
import requests
import json
from minio import Minio
from io import BytesIO


def _get_stock_prices(url, symbol):
    url = f"{url}{symbol}?metrics=high?&interval=1d&range=1y"
    api = BaseHook.get_connection('stock_api')
    reponse = requests.get(url, headers=api.extra_dejson['headers'])
    return json.dumps(reponse.json()['chart']['result'][0])


def _store_prices(stock):
    #minio = BaseHook.get_connection('minio').extra_dejson
    minio = BaseHook.get_connection('minio')
    print(minio)
    client = Minio(
        # after print, these two attributes could not be gotten, change to login and password
        #endpoint=minio['endpoint_url'].split('//')[1],
        #access_key=minio['aws_access_key_id'],
        #secret_key=minio['aws_secret_access_key'],
        endpoint=minio.extra_dejson['endpoint_url'].split('//')[1],
        access_key=minio.login,
        secret_key=minio.password,
        secure=False
    )
    bucket_name = 'stock-market'
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
    stock = json.loads(stock)
    symbol = stock['meta']['symbol']
    data = json.dumps(stock, ensure_ascii=False).encode('utf8')
    objw = client.put_object(
        bucket_name=bucket_name,
        object_name=f'{symbol}/prices.json',
        data=BytesIO(data),
        length=len(data)
    )
    return f'{objw.bucket_name}/{symbol}'