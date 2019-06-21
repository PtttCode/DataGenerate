from datetime import datetime
import binascii
import hashlib
import hmac
import sys
import requests
import urllib.request
import time
import random


class TencentCloud(object):

    '''准备好的secretId和secretKey,
    可以在 https://console.cloud.tencent.com/capi 获取'''
    def __init__(self):

        # 在此处定义一些必须的内容

        self.secretId = "AKIDxkJcS8xpeFDzWqlqUu87sjPvFJDutl03"
        self.secretKey = "1OZLwSq4BAuQHR9fy3wZ0MdmfNI47R1g"
        self.timeData = str(int(time.time()))  # 时间戳
        self.nonceData = int(random.random() * 10000)  # Nonce，官网给的信息：随机正整数，与 Timestamp 联合起来， 用于防止重放攻击
        self.actionData = "TextTranslate"  # Action一般是操作名称
        self.uriData = "tmt.tencentcloudapi.com"  # uri，请参考官网
        self.signMethod = "HmacSHA256"  # 加密方法
        self.requestMethod = "GET"  # 请求方法，在签名时会遇到，如果签名时使用的是GET，那么在请求时也请使用GET
        self.regionData = "ap-hongkong"  # 区域选择
        self.versionData = '2018-03-21'  # 版本选择

    def sign(self,secretKey, signStr, signMethod):
        '''
        该方法主要是实现腾讯云的签名功能
        :param secretKey: 用户的secretKey
        :param signStr: 传递进来字符串，加密时需要使用
        :param signMethod: 加密方法
        :return:
        '''
        if sys.version_info[0] > 2:
            signStr = signStr.encode("utf-8")
            secretKey = secretKey.encode("utf-8")

        # 根据参数中的signMethod来选择加密方式
        if signMethod == 'HmacSHA256':
            digestmod = hashlib.sha256
        elif signMethod == 'HmacSHA1':
            digestmod = hashlib.sha1

        # 完成加密，生成加密后的数据
        hashed = hmac.new(secretKey, signStr, digestmod)
        base64 = binascii.b2a_base64(hashed.digest())[:-1]

        if sys.version_info[0] > 2:
            base64 = base64.decode()

        return base64

    def dictToStr(self,dictData):
        '''
        本方法主要是将Dict转为List并且拼接成字符串
        :param dictData:
        :return: 拼接好的字符串
        '''
        tempList = []
        for eveKey, eveValue in dictData.items():
            tempList.append(str(eveKey) + "=" + str(eveValue))
        return "&".join(tempList)



    def get_result(self,text='hello',target ='zh'):
        signDictData = {
            'Action' : self.actionData,
            'Nonce' : self.nonceData,
            'ProjectId':0,
            'Region' : self.regionData,
            'SecretId' : self.secretId,
            'SignatureMethod':self.signMethod,
            'Source': 'auto',
            'SourceText': text,
            'Target': target,
            'Timestamp' : int(self.timeData),
            'Version':self.versionData ,
        }
        requestStr = "%s%s%s%s%s" % (self.requestMethod, self.uriData, "/", "?", self.dictToStr(signDictData))

        signData = urllib.parse.quote(self.sign(self.secretKey, requestStr, self.signMethod))

        # 上述操作是实现签名，下面即进行请求
        # 先建立请求参数, 此处参数只在签名时多了一个Signature
        actionArgs = signDictData
        print(signData)
        actionArgs["Signature"] = signData

        # 根据uri构建请求的url
        requestUrl = "https://%s/?" % (self.uriData)

        # 将请求的url和参数进行拼接
        requestUrlWithArgs = requestUrl + self.dictToStr(actionArgs)


        # 获得response
        response = requests.get(requestUrlWithArgs)
        json_r = response.json()
        print(json_r)
        try:
            if 'Error' not in json_r:
                response = response.json()['Response']['TargetText']
                return response
        except Exception as e:
            print(e)


if __name__ == '__main__':
    tc = TencentCloud()
    langs = [ 'en', 'jp', 'kr', 'de', 'fr', 'es', 'it', 'tr', 'ru', 'pt', 'vi', 'id', 'ms', 'th']
    for lang in langs:
        text = tc.get_result('为什么庞桐掉不了', lang)
        time.sleep(0.21)
        print(text)
        _text = tc.get_result(text)
        time.sleep(0.2)
        print(_text)
        # return _text
