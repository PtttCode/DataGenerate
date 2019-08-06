import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import ptttloggg
import os


from api.generate import GenerateHandler, SynonymsHandler, SyntaxHandler
from settings.settings import logger, w2v
from utils.data_generate import find_all_field


urls = [(r"/generate", GenerateHandler),
        (r"/synonyms", SynonymsHandler),
        (r"/syntax", SyntaxHandler),
        ]
PORT = 8080


class Application(tornado.web.Application):

    def __init__(self):
        handlers = urls
        settings = dict(
            debug=True,
            # static_path=os.path.join(os.path.dirname(__file__), "resource"),
            # static_url_prefix='/test/',
        )
        super(Application, self).__init__(handlers, **settings)
        self.w2v = w2v
        find_all_field()
        ptttloggg.initLogConf()


def main():
    oc_path = "data/original_corpus/"
    if not os.path.exists(oc_path):
        os.makedirs(oc_path + "generate")
        os.makedirs(oc_path + "synonyms_generate")
        os.makedirs(oc_path + "syntax_generate")

    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.bind(PORT)
    http_server.start()
    logger.info("server start, listen at {}".format(PORT))
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()

