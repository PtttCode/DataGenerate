import urllib.request
import urllib.parse
import json


# 有道翻译方法
def youdao_translate(content):
    '''实现有道翻译的接口'''
    youdao_url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule'
    data = {}

    data['i'] = content
    data['from'] = 'AUTO'
    data['to'] = 'de'

    data['smartresult'] = 'dict'
    data['client'] = 'fanyideskweb'
    data['salt'] = '15604167649822'
    data['sign'] = 'ad260a722fde1d1562707ea453fb83bd'
    data['doctype'] = 'json'
    data['version'] = '2.1'
    data['keyfrom'] = 'fanyi.web'
    data['action'] = 'FY_BY_CLICKBUTTION'
    data['typoResult'] = 'false'
    data = urllib.parse.urlencode(data).encode('utf-8')


    youdao_response = urllib.request.urlopen(youdao_url, data)
    youdao_html = youdao_response.read().decode('utf-8')

    target = json.loads(youdao_html)
    # print(target)

    trans = target['translateResult']
    ret = ''
    for i in range(len(trans)):
        line = ''
        for j in range(len(trans[i])):
            line = trans[i][j]['tgt']
        ret += line + '\n'

    return ret


if __name__ == '__main__':
    print(youdao_translate("hello"))
