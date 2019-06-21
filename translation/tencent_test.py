import re
import time
import requests
# from dataclasses import dataclass
import linecache
import os



def get_qtv_qtk():
    api_url = 'https://fanyi.qq.com/'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, '
                      'like Gecko) Chrome/73.0.3683.86 Safari/537.36', }

    res = requests.get(api_url, headers=headers)
    data = res.text

    fy_guid = res.cookies.get('fy_guid')

    reg = re.compile(r'var qtv = "(.*?)"')
    qtv = reg.search(data).group(1)

    reg = re.compile(r'var qtk = "(.*?)"')
    qtk = reg.search(data).group(1)

    return fy_guid, qtv, qtk


# @dataclass
class SougoTrans(object):

    def __init__(self, tolang, fromlang="auto"):
        self.api_url = 'https://fanyi.qq.com/api/translate'
        self.headers = {
            'Cookie': 'fy_guid=605ead81-f210-47eb-bd80-ac6ae5e7a2d8; '
                      'qtv=ed286a053ae88763; '
                      'qtk=wfMmjh3k/7Sr2xVNg/LtITgPRlnvGWBzP9a4FN0dn9PE7L5jDYiYJnW03MJLRUGHEFNCRhTfrp/V+wUj0dun1KkKNUUmS86A/wGVf6ydzhwboelTOs0hfHuF0ndtSoX+N3486tUMlm62VU4i856mqw==; ',
            'Host': 'fanyi.qq.com',
            'Origin': 'https://fanyi.qq.com',
            'Referer': 'https://fanyi.qq.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/73.0.3683.86 Safari/537.36', }

        self.fromlang = "auto"
        self.tolang = tolang
        if not self.fromlang:
            self.fromlang = 'auto'
        if not self.tolang:
            self.tolang = 'en'  # 设置默认为英语
        self.sessionUuid = str(int(time.time() * 1000))

        self.fy_guid, self.qtv, self.qtk = get_qtv_qtk()

        self.headers['Cookie'] = self.headers['Cookie'].replace(
            '605ead81-f210-47eb-bd80-ac6ae5e7a2d8', self.fy_guid)

        self.headers['Cookie'] = self.headers['Cookie'].replace(
            'ed286a053ae88763', self.qtv)
        self.headers['Cookie'] = self.headers['Cookie'].replace(
            'wfMmjh3k/7Sr2xVNg/LtITgPRlnvGWBzP9a4FN0dn9PE7L5jDYiYJnW03MJLRUGHEFNCRhTfrp/V+wUj0dun1KkKNUUmS86A/wGVf6ydzhwboelTOs0hfHuF0ndtSoX+N3486tUMlm62VU4i856mqw==',
            self.qtk)

    def get_trans_result(self,text):
        data = {
            'source': self.fromlang,
            'target': self.tolang,
            'sourceText': text,
            'qtv': self.qtv,
            'qtk': self.qtk,
            'sessionUuid': self.sessionUuid, }

        trans_result = requests.post(
            self.api_url, data=data, headers=self.headers)

        try:
            datas = trans_result.json()['translate']['records']
            trans_result = ''.join([data['targetText'] for data in datas])
        except:
            print(trans_result.text)
            trans_result = ''

        return trans_result


def save_to_file(file_name, contents):
    fh = open(file_name, 'w', encoding='utf-8')
    fh.write(contents)
    fh.close()


def run(number):
    Flag = True
    a = number
    while (Flag):
        if (a <= 14927):
            start = time.clock()
            a = a + 1
            fromlang = ''
            tolang = 'en'
            text = ''
            reqs = linecache.getlines('./原始数据/' + str(a) + '.csv')
            for i in reqs:
                i = i.strip()
                while i.startswith('"') or i.startswith("'"):
                    i = i[1:]
                while i.endswith('"') or i.endswith("'"):
                    i = i[:-1]
                i = i + "\n"
                text = text + i
            try:
                Sougou = SougoTrans(fromlang, tolang, text)
                res = Sougou.get_trans_result()
            except TimeoutError:
                run(a - 1)
                print(a)
            fileout_name = './英文数据/' + str(a) + '.txt'
            save_to_file(fileout_name, res)
            end = time.clock()
            print('Running time: %s Seconds' % (end - start))
            print(a)
            time.sleep(1)
        else:
            Flag = False


if __name__ == '__main__':

    text = "我日"
    Sougou = SougoTrans(tolang="es")
    res = Sougou.get_trans_result(text)
    print(res)
    Sougou.tolang = "en"
    res = Sougou.get_trans_result(text)
    print(res)