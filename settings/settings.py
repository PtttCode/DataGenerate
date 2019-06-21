from settings.logger import Logger


word_dep = "data/word_depository"
field_dir = "data/field"

logger = Logger()

stop_words = list()
with open('data/stop/HIT.txt', "r", encoding="utf-8") as f:
    for stop_word in f.readlines():
        stop_words.append(stop_word[:-1])

