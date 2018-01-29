#!/usr/bin/python3
import os
import json
import requests
import configparser

PROJECT_ROOT_DIR = os.getcwd()
config = configparser.ConfigParser()
configFilePath = os.path.join(PROJECT_ROOT_DIR, 'config.cfg')
config.read(configFilePath)


class Config:
    username = config.get('info', 'username')
    password = config.get('info', 'password')
    client_id = config.get('info', 'client_id')


class RobinHood():
    def __init__(self, user, password):
        self.username = user
        self.password = password
        self.base_url = 'https://api.robinhood.com'
        self.headers = {
            'Host': 'api.robinhood.com',
            'Content-Type': 'application/json',
            'X-Robinhood-API-Version': '1.196.3',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'User-Agent': 'Robinhood/6.0.0 (com.robinhood.release.Robinhood; build:4430; iOS 10.2.0) Alamofire/4.5.1',
            'Accept-Language': 'en-US;q=1.0',
            'Accept-Encoding': 'gzip;q=1.0, compress;q=0.5',
            'X-Midlands-API-Version': '1.48.1'
        }
        self.authorization = None
        self.user_id = None
        self.logged_in = False

    def _make_request(self, method, endpoint, **kwargs):
        data = kwargs.get('data', None)
        json = kwargs.get('json', None)
        params = kwargs.get('params', None)
        added_headers = kwargs.get('headers', None)
        if added_headers is not None:
            for key, value in kwargs.get('headers', None).items():
                self.headers[key] = value
        return requests.request(method, f'{self.base_url}{endpoint}', params=params, data=data, json=json,
                                headers=self.headers)

    def login(self):
        client_id = Config().client_id
        login_response = self._make_request('POST', '/oauth2/token/', json={
            'client_id': client_id,
            'grant_type': 'password',
            'password': self.password,
            'scope': 'internal',
            'username': self.username
        })
        self.authorization = f'{login_response.json()["token_type"]} {login_response.json()["access_token"]}'
        del self.headers['Content-Type']
        self.headers['Authorization'] = self.authorization
        self.logged_in = True

    def get_user(self):
        if self.logged_in is False:
            self.login()
        user_info_response = self._make_request('GET', '/user/')
        self.user_id = user_info_response.json()['id']

    def get_cryptos(self):
        if self.logged_in is False:
            self.get_user()
        crypto_search_response = self._make_request('GET', '/midlands/search/', params={
            'active_instruments_only': '1',
            'query': 'Cryptocurrenci'
        })
        crypto_ids = []
        for coin in crypto_search_response.json()['currency_pairs']:
            crypto_ids.append(coin['id'])
        id_string = ''
        for id in crypto_ids:
            id_string += f'{id},'
        crypto_price_search_response = self._make_request('GET', '/marketdata/forex/quotes/',
                                                          params={'ids': id_string[:-1]})
        print(json.dumps(crypto_price_search_response.json(), indent=4))


RobinHood(Config().username, Config().password).get_cryptos()
