import random
import synonyms

from settings.settings import logger, stop_words, ask_words
from utils.init_w2v import w2v
from utils.utils import load_field_dict, get_corpus_label


def get_synonyms(word):
    return synonyms.nearby(word)[0]


def insert_randomly(words, n, useless_word=None):
    """
    随机插入同义词
    :param words:   切词后的列表
    :param n:   插入次数
    :return:
    """
    new_words = words.copy()
    res = []

    for _ in range(n):
        synonyms = []
        counter = 0
        while len(synonyms) < 1:
            random_word = new_words[random.randint(0, len(new_words)-1)]
            try:
                synonyms = w2v.most_similar(positive=[random_word], topn=1)[0][0]
            except KeyError as e:
                logger.info("词向量无此词：{}".format(random_word))

            counter += 1
            if counter >= 10:
                return []
        random_synonym = random.choice(synonyms)
        random_idx = random.randint(0, len(new_words)-1)
        new_words.insert(random_idx, random_synonym)
        res.append(new_words)
    return res


def replace_randomly(words, n, useless_words=None):
    new_words = words.copy()
    random_word_list = list(set([word for word in words if word not in stop_words]))
    random.shuffle(random_word_list)
    num_replaced = 0
    res = []

    for random_word in random_word_list:
        try:
            synonyms = w2v.most_similar(positive=[random_word], topn=1)[0][0]
        except KeyError as e:
            logger.info("词向量无此词：{}".format(random_word))
            continue
        if len(synonyms) >= 1:
            synonym = random.choice(synonyms)
            new_words = [synonym if word == random_word else word for word in new_words]
            res.append(new_words)
            num_replaced += 1
        if num_replaced >= n:
            break

    # sentence = ' '.join(new_words)
    # new_words = sentence.split(' ')
    return res


def insert_stop_words(words, n, useless_words=None):
    if n not in [-1, 0, 1]:
        return []

    insert_idx = random.randint(1, len(words)-1) if n == -1 else n*(len(words)-1)
    useless_words = ask_words if not useless_words else useless_words

    new_words = []
    for word in useless_words:
        new_sen = words.copy()
        if new_sen[insert_idx] not in word and word not in new_sen[insert_idx]:
            ins_idx = insert_idx + 1 if len(new_sen) - 1 == insert_idx else insert_idx
            new_sen.insert(ins_idx, word)
        new_words.append(new_sen)

    return new_words


def synonyms_run(field, all_corpus, method, ele_num=3, intent=None, useless_words=None):
    tokenizer = load_field_dict(field)
    corpus, labels = get_corpus_label(all_corpus, intent)
    if not corpus:
        return [], {}

    new_corpus = []
    dic = {}
    for idx, sen in enumerate(corpus):
        words = [i for i in tokenizer.cut(sen)]
        if len(words) <= 3:
            # logger.info(words, sen)
            continue

        word_list = ["".join(i) for i in method(words, ele_num, useless_words)]
        if not word_list:
            continue
        for new_sen in word_list:
            # new_sen = "".join(new_sen) if isinstance(word_list, list) else "".join([i for i in word_list])
            cp = "{}\t{}\n".format(new_sen, labels[idx])

            if cp not in all_corpus and cp not in new_corpus:
                new_corpus.append(cp)
        dic[sen] = [list(set(word_list))]

    return new_corpus, dic