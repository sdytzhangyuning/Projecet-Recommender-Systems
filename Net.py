import urllib.requests
import json
import os
import base64
import binascii
from Crypto.Cipher import AES
class NetEaseAPI:
    def __init__(self):
        self.header = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/search/',
            'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'  # NOQA
        }
        self.cookies = {'appver': '1.5.2'}
        self.playlist_class_dict = {}
        self.session = requests.Session()
    def httpRequest(self, method, action, query=None, urlencoded=None, callback=None, timeout=None):
        connection = json.loads(self.rawHttpRequest(method, action, query, urlencoded, callback, timeout))
        return connection
    def rawHttpRequest(self, method, action, query=None, urlencoded=None, callback=None, timeout=None):
        if method == 'GET':
            url = action if query is None else action + '?' + query
            connection = self.session.get(url)
        elif method == 'POST':
            connection = self.session.post(action, query, self.header)
        elif method == 'Login_POST':
            connection = self.session.post(action,  query, self.header)
            self.session.cookies.save()
        connection.encoding = 'UTF-8'
        return connection.text
    def search(self, s, stype=1, offset=0, total='true', limit=1):
        action = 'http://music.163.com/api/search/get'
        data = {
            's': s,
            'type': stype,
            'offset': offset,
            'total': total,
            'limit': limit
        }
        return self.httpRequest('POST', action, data)
    def aesEncrypt(self, text, secKey):
        pad = 16 - len(text) % 16
        text = text + chr(pad) * pad
        encryptor = AES.new(secKey, 2, '0102030405060708')
        ciphertext = encryptor.encrypt(text)
        ciphertext = base64.b64encode(ciphertext).decode('utf-8')
        return ciphertext
    def rsaEncrypt(self, text, pubKey, modulus):
        text = text[::-1]
        rs = pow(int(binascii.hexlify(text), 16), int(pubKey, 16), int(modulus, 16))
        return format(rs, 'x').zfill(256)
    def createSecretKey(self,size):
        return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))))[0:16]
    def encrypted_request(self, text):
        modulus = ('00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7'
           'b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280'
           '104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932'
           '575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b'
           '3ece0462db0a22b8e7')
        nonce = '0CoJUm6Qyw8W8jud'
        pubKey = '010001'
        text = json.dumps(text)
        secKey = binascii.hexlify(os.urandom(16))[:16]
        encText = self.aesEncrypt(self.aesEncrypt(text, nonce), secKey)
        encSecKey = self.rsaEncrypt(secKey, pubKey, modulus)
        data = {'params': encText, 'encSecKey': encSecKey}
        return data
    def getComment(self, songId, offset=0, total='fasle', limit=100):
        action = 'http://music.163.com/api/v1/resource/comments/R_SO_4_{}/?rid=R_SO_4_{}&\
        offset={}&total={}&limit={}'.format(songId, songId, offset, total, limit)
        comments = self.httpRequest('GET', action)
        return comments['hotComments']
    def getPlaylist(self, uid):
        text = {
            'uid': uid,
            'limit':100
        }
        text = json.dumps(text)
        nonce = '0CoJUm6Qyw8W8jud'
        pubKey = '010001'
        modulus = ('00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7'
           'b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280'
           '104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932'
           '575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b'
           '3ece0462db0a22b8e7')
        secKey = self.createSecretKey(16)
        encText = self.aesEncrypt(self.aesEncrypt(text, nonce), secKey)
        encSecKey = self.rsaEncrypt(secKey, pubKey, modulus)
        data = {
            'params': encText,
            'encSecKey': encSecKey
        }
        action = 'http://music.163.com/weapi/user/playlist?csrf_token='
        playlist = self.httpRequest('POST', action, data)
        res = list()
        for play in playlist['playlist']:
            res.append({'id':play['id'],'subscribedCount':play['subscribedCount'],'playCount':play['playCount']})
        return res
    def getPlaylistDetail(self, id):
        text = {
            'id': id,
            'limit':100,
            'total':True
        }
        text = json.dumps(text)
        nonce = '0CoJUm6Qyw8W8jud'
        pubKey = '010001'
        modulus = ('00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7'
           'b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280'
           '104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932'
           '575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b'
           '3ece0462db0a22b8e7')
        secKey = self.createSecretKey(16)
        encText = self.aesEncrypt(self.aesEncrypt(text, nonce), secKey)
        encSecKey = self.rsaEncrypt(secKey, pubKey, modulus)
        data = {
            'params': encText,
            'encSecKey': encSecKey
        }
        action = 'http://music.163.com/weapi/v3/playlist/detail?csrf_token='
        playlistDetail = self.httpRequest('POST', action, data)
        music = list()
        musicCount = dict()
        for count in playlistDetail['playlist']['trackIds']:
            musicCount[count['id']] = count['v']
        for detail in playlistDetail['playlist']['tracks']:
            singer = ''
            for author in detail['ar']:
                singer += author['name']+','
            music.append({'id':detail['id'],'name':detail['name'],'singer':singer, 'playCount':musicCount[detail['id']]})
        return music
