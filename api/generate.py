import json
import time


from api.base import BaseHandler
from settings.settings import logger, PRIORITY_DEFAULT
from utils.data_generate import delete_randomly, swap_randomly, insert_randomly, replace_randomly, synonyms_run
from utils.syntax_generate import syntax_generate, _cut


func_dict = {
    "删除": delete_randomly,
    "交换": swap_randomly,
    "替换": replace_randomly,
    "插入": insert_randomly,
    "句式生成": syntax_generate,

}


class GenerateHandler(BaseHandler):

    async def post(self):
        field = self.get_body_argument("field")
        intent = self.get_body_arguments("intent")
        func = self.get_body_argument("func")
        split_rate = self.get_body_argument("split_rate", 0.5)
        file_metas = list(self.request.files.values())
        
        logger.info(self.request.remote_ip)
        logger.info(field, intent)

        if len(file_metas) == 0 or not field or func not in func_dict:
            return self.response({"code": 1, "msg": "请上传文件，确定领域和增强方法！", "data": []})
        else:
            generate_func = func_dict[func]
            for metas in file_metas:
                meta = metas[0]
                filename = meta["filename"]
                logger.info("正在上传文件：{}".format(filename))
                rename_prefix = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                # rename = "{}_{}".format(rename_prefix, file_name)
                save_path = "data/original_corpus/generate/{}_{}".format(str(rename_prefix), filename)
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

        logger.info(field, intent)
        logger.info(type(ele_num))

        if len(file_metas) == 0 or not field or func not in func_dict:
            return self.response({"code": 1, "msg": "请上传文件，确定领域和增强方法！", "data": []})
        else:
            generate_func = func_dict[func]
            for metas in file_metas:
                meta = metas[0]
                filename = meta["filename"]
                logger.info("正在上传文件：{}".format(filename))
                rename_prefix = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                # rename = "{}_{}".format(rename_prefix, file_name)
                save_path = "data/original_corpus/synonyms_generate/{}_{}".format(str(rename_prefix), filename)
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


class SyntaxHandler(BaseHandler):
    async def get(self):
        body = self.json_request
        sentences = body.get("sentences")
        res = [_cut(i) for i in sentences]

        logger.info(res)
        return self.response({"code": 0, "data": res})

    async def post(self):
        params = eval(self.get_body_argument("params"))
        priority = params.get("priority", PRIORITY_DEFAULT)
        min_rep_num = params.get("min_rep_num", 1)
        thresholds = params.get("thresholds", 0.49)
        limit = params.get("limit", 2)
        topn = params.get("topn", 20)
        restrict_vocab = params.get("restrict_vocab", 2000000)
        abandon_dict = params.get("abandon_dict", {})
        func = params.get("func", "句式生成")
        file_metas = list(self.request.files.values())

        args_list = ["priority", "min_rep_num", "thresholds", "limit", "topn", "restrict_vocab", "abandon_dict"]
        args = {}
        for i in args_list:
            args[i] = eval(i)

        logger.info(args)

        if len(file_metas) == 0 or func not in func_dict:
            return self.response({"code": 1, "msg": "请上传文件，确定领域和增强方法！", "data": []})
        else:
            generate_func = func_dict[func]
            for metas in file_metas:
                meta = metas[0]
                filename = meta["filename"]
                logger.info("正在上传文件：{}".format(filename))
                rename_prefix = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                # rename = "{}_{}".format(rename_prefix, file_name)
                save_path = "data/original_corpus/syntax_generate/{}_{}".format(str(rename_prefix), filename)
                words_filename = "data/original_corpus/syntax_generate/{}_words_properties.xlsx".format(str(rename_prefix))
                with open(save_path, 'wb') as f:
                    f.write(meta["body"])

                res = generate_func(self.w2v, save_path, words_filename, args)

                return self.response({"code": 0, "msg": "数据增强之同义词{}成功！".format(func), "data": res})



