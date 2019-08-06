from settings.logger import Logger
from utils.syntax_generate import init_word2vec


WORD_DEP = "data/word_depository"
FIELD_DIR = "data/field"
WORD2VEC_PATH = "small_cc_zh.vec"
PRIORITY_DEFAULT = ["v", "n", "vn", "a", "t", "d", "eng", "r", "m", "uj", "c", "p", "q", "l"]

logger = Logger()

stop_words = list()
ask_words = list()
with open('data/stop/HIT.txt', "r", encoding="utf-8") as f:
    for stop_word in f.readlines():
        stop_words.append(stop_word[:-1])

with open('data/stop/ask_words.txt', "r", encoding="utf-8") as f:
    ask_words = [i.strip() for i in f.readlines()]

w2v = init_word2vec(word2vec_path=WORD2VEC_PATH)

