# -*- coding: utf-8 -*-
import tornado.web
import json
import re


class BaseHandler(tornado.web.RequestHandler):

    @property
    def w2v(self):
        return self.application.w2v

    def json_dumps(self, obj):
        # return json.dumps(obj, default=alchemyencoder,
        # ensure_ascii=False).encode("utf-8")
        return json.dumps(obj, ensure_ascii=False)

    def response(self, result):
        self.write(self.json_dumps(result))

    @property
    def json_request(self):
        body = self.request.body.decode("utf-8")
        data = json.loads(body) if body else {}
        return data

    def args_get(self, name):
        return self.get_body_argument(name)




