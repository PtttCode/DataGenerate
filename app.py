import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import ptttloggg


from api.generate import GenerateHandler, SynonymsHandler
from settings.settings import logger
from utils.data_generate import find_all_field


urls = [(r"/generate", GenerateHandler),
        (r"/synonyms", SynonymsHandler),
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
        find_all_field()
        ptttloggg.initLogConf()


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.bind(PORT)
    http_server.start()
    logger.info("server start, listen at {}".format(PORT))
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()

