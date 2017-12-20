
from urllib.request import Request, urlopen
from urllib.parse import urlencode


def get(url, parameters=None, raw=False):
    if parameters:
        url = url + urlencode(parameters)
    result = urlopen(url).read()
    if not raw:
        result = result.decode('utf-8')
    return result


def get_resource(url, parameters=None):
    if parameters:
        url = url + urlencode(parameters)
    return urlopen(url)


def iso_api_request(url, params=None):
    return urlopen()


