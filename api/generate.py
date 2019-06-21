import json
import requests


from api.base import BaseHandler
from settings.settings import logger
from utils.data_generate import delete_randomly, swap_randomly, insert_randomly, replace_randomly, synonyms_run


func_dict = {
    "删除": delete_randomly,
    "交换": swap_randomly,
    "替换": replace_randomly,
    "插入": insert_randomly

}


class GenerateHandler(BaseHandler):

    async def post(self):
        field = self.get_body_argument("field")
        intent = self.get_body_arguments("intent")
        func = self.get_body_argument("func")
        split_rate = self.get_body_argument("split_rate", 0.5)
        file_metas = list(self.request.files.values())

        print(field, intent, func, len(file_metas))

        if len(file_metas) == 0 or not field or func not in func_dict:
            return self.response({"code": 1, "msg": "请上传文件，确定领域和增强方法！", "data": []})
        else:
            generate_func = func_dict[func]
            for metas in file_metas:
                meta = metas[0]
                filename = meta["filename"]
                logger.info("正在上传文件：{}".format(filename))
                # rename_prefix = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                # rename = "{}_{}".format(rename_prefix, file_name)
                save_path = "data/original_corpus/{}".format(filename)
                with open(save_path, 'w', encoding="utf-8") as f:
                    f.write(meta["body"].decode())

                with open(save_path, "r", encoding="utf-8") as f:
                    corpus = [i for i in f.readlines()]
                res, _ = generate_func(field=field,
                                       all_corpus=corpus,
                                       split_rate=split_rate,
                                       intent=intent)

                return self.response({"code": 0, "msg": "数据增强之同义词{}成功！".format(func), "data": res})


class SynonymsHandler(BaseHandler):

    async def post(self):
        field = self.get_body_argument("field")
        intent = self.get_body_arguments("intent")
        func = self.get_body_argument("func")
        ele_num = int(self.get_body_argument("ele_num", 3))
        file_metas = list(self.request.files.values())

        print(field, intent, func, len(file_metas))
        print(type(ele_num))

        if len(file_metas) == 0 or not field or func not in func_dict:
            return self.response({"code": 1, "msg": "请上传文件，确定领域和增强方法！", "data": []})
        else:
            generate_func = func_dict[func]
            for metas in file_metas:
                meta = metas[0]
                filename = meta["filename"]
                logger.info("正在上传文件：{}".format(filename))
                # rename_prefix = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                # rename = "{}_{}".format(rename_prefix, file_name)
                save_path = "data/original_corpus/{}".format(filename)
                with open(save_path, 'w', encoding="utf-8") as f:
                    f.write(meta["body"].decode())

                with open(save_path, "r", encoding="utf-8") as f:
                    corpus = [i for i in f.readlines()]
                res, _ = synonyms_run(field=field,
                                      all_corpus=corpus,
                                      method=generate_func,
                                      ele_num=ele_num,
                                      intent=intent)

                return self.response({"code": 0, "msg": "数据增强之同义词{}成功！".format(func), "data": res})


