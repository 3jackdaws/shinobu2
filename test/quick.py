from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import HTTPError
from base64 import b64encode
ANON_CHANNEL = None
WEBHOOK_URL = 'https://discordapp.com/api/webhooks/253225447230406657/MEEc4eJB0HJnm9HsjejN1WVDRugmWl8wDJvuEoicthDKE05ijAs0Dn55i8C9DCO_yumm'
WEBHOOK_ID = None
USER_MAPPING = ''
HEADERS = {
    'User-Agent':'ShinobuBot (http://github.com/3jackdaws/shinobu2, v2.5.0)',
    'Content-Type': 'multipart/form-data',
    'Content-Encoding':'base64'
}

def webhook_send_message(*, content=None, file_url=None, username=None, avatar_url=None):
    data = {}
    if content:
        data['content'] = content
    if file_url:
        req = Request(file_url, headers=HEADERS)
        file = urlopen(req).read()
        data['file'] = file
        request = Request(WEBHOOK_URL, data=b64encode(urlencode(data)).encode(), headers=HEADERS, method='POST')
        urlopen(request).read()
        # print(file)
        data['files'] = file



if __name__ == '__main__':
    webhook_send_message(content='hello', file_url='http://www.qygjxz.com/data/out/179/5054311-picture.png')