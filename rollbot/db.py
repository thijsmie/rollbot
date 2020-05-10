import redis
from urllib.parse import urlparse


def make_db(url):
    url = urlparse(url)
    return redis.Redis(host=url.hostname, port=url.port, password=url.password)
