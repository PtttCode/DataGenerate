from settings.logger import Logger


WORD_DEP = "data/word_depository"
FIELD_DIR = "data/field"
WORD2VEC_PATH = "small_cc_zh.vec"
PRIORITY_DEFAULT = ["v", "n", "vn", "a", "t", "d", "eng", "r", "m", "uj", "c", "p", "q", "l"]

logger = Logger()

stop_words = list()
with open('data/stop/HIT.txt', "r", encoding="utf-8") as f:
    for stop_word in f.readlines():
        stop_words.append(stop_word[:-1])

