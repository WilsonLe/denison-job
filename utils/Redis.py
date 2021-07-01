import redis
import json
import os
from dotenv import load_dotenv
load_dotenv()


class Redis():
    def __init__(self, host, port, password, db=0, decode_response=True):
        self.HOST = host
        self.PORT = port
        self.PASSWORD = password
        self.DB = db
        self.DECODE_REPONSE = decode_response
        self.CHARSET = 'utf-8'
        self.ERRORS = 'strict'

        self.client = self.connect()

    def connect(self):
        """connect to redis server. INTERNAL USE ONLY!

        Returns:
            redis.client.Redis: Redis client that is connected to redis server
        """
        client = redis.StrictRedis(
            host=self.HOST,
            port=self.PORT,
            db=self.DB,
            password=self.PASSWORD,
            charset=self.CHARSET,
            errors=self.ERRORS)

        try:
            client.ping()
            print('connected to redis server')
            return client
        except Exception as e:
            raise e

    def set_key(self, key, value):
        """set key value pair to database

        Args:
            key (string): name of key to set value to
            value (string or dict or list): value that is assigned to key

        Raises:
            ValueError: input key parameter must be a string
            ValueError: input value parameter must be a string, list, or dict

        Returns:
            bool: True if value is successfully set to db
        """

        if type(key) != str:
            raise ValueError('key parameter must be a string')

        if type(value) == str:
            return self.client.set(key, value)
        elif type(value) == dict or type(value) == list:
            self.client.set(key, json.dumps(value))
        else:
            raise ValueError(
                'invalid value parameter. Must be a string, list, or dict')

    def get_key(self, key):
        """get value of key from database

        Args:
            key (string): name of key to get value from

        Raises:
            ValueError: input key parameter must be a string

        Returns:
            string, list, or dict: value at specified key
        """
        if type(key) != str:
            raise ValueError('key parameter must be a string')
        value = self.client.get(key).decode('utf-8')
        if value.startswith('{') and value.endswith('}'):
            value = json.loads(value)
        return value

    def exist_key(self, key):
        """check if a key exists in current server

        Args:
            key (string): name of key to check for existence

        Raises:
            ValueError: key parameter must be a string

        Returns:
            bool: True if key exist, else False
        """
        if type(key) != str:
            raise ValueError('key parameter must be a string')
        return self.client.exists(key)

    def get_all_keys(self):
        """get all keys from database

        Returns:
            list: list of all keys of database
        """
        return list(map(lambda key: key.decode('utf-8'), self.client.keys()))

    def get_db(self):
        """get all database as a JSON Dict

        Returns:
            Didct: entire database as json dict
        """
        db = {}
        all_keys = self.get_all_keys()
        for key in all_keys:
            db[key] = self.get_key(key)
        return db

    def del_key(self, key):
        """delete specified key from database

        Args:
            key (string): name of key to be removed from database

        Raises:
            ValueError: key parameter must be a string

        Returns:
            int: 1 if key exist and deleted, 0 if key does not exist
        """
        if type(key) != str:
            raise ValueError('key parameter must be a string')
        return self.client.delete(key)
