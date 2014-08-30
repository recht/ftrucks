import os

class BaseConfig(object):

    DEBUG = True
    TESTING = False
    # the hostname to use when connecting to ElasticSearch
    ESHOST = os.environ.get('BONSAI_URL', 'localhost:9200')

    # the ElasticSearch index to use for truck info
    ESINDEX = 'trucks'

    # Control if the truck data indexer should run periodically
    SLURP = True

    # Control if vehicle locations should be polled for at regular intervals
    WATCH = True

class TestConfig(BaseConfig):
    TESTING = True
    ESINDEX = 'trucks_test'
    SLURP = False
    WATCH = False
