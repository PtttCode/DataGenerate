import re
import jieba
import jieba.analyse
import itertools
import jieba.analyse

from settings.settings import logger
from utils.utils import load_field_dict, get_corpus_label


def swap_ele(origin_words, permutations):
    for i, j in permutations:
        idx1 = origin_words.index(i)
        idx2 = origin_words.index(j)
        origin_words[idx1], origin_words[idx2] = j, i

        yield "".join(origin_words)


def swap_randomly(field, all_corpus, split_rate=0.5, intent=None):
    tokenizer = load_field_dict(field)
    new_corpus = []
    dic = {}
    corpus, labels = get_corpus_label(all_corpus, intent)
    all_corpus = [i.strip().split("\t")[0] for i in all_corpus]
    if not corpus:
        return [], split_rate, {}

    for idx, sen in enumerate(corpus):
        words = [i for i in tokenizer.cut(sen)]
        if len(words) <= 3:
            logger.info(words, sen)
            continue
        tfidf = jieba.analyse.extract_tags(sen, withWeight=True)

        replace_rate = int(len(tfidf) * split_rate)
        tfidf = [t[0] for t in tfidf[:replace_rate]]

        minus_ele = list(set(tfidf) - set(words))
        if minus_ele:
            # 删除tfidf列表与切词结果列表中不同的部分
            _ = [tfidf.remove(i) for i in minus_ele]
        if len(tfidf) <= 1:
            continue
        # 获取排列组合
        permutations = [i for i in itertools.permutations(tfidf, 2)]
        added_corpus = swap_ele(words, permutations)

        screen_corpus = []
        for i in added_corpus:
            cp = "{}\t{}\n".format(i, labels[idx])
            if cp not in all_corpus and cp not in new_corpus:
                screen_corpus.append(cp)

        # intent_corpus = ["{}\t{}\n".format(i, labels[idx]) for i in added_corpus
        #                  if i not in all_corpus and i not in new_corpus]
        # intent_corpus = list(set(intent_corpus))

        new_corpus.extend(screen_corpus)
        dic[sen] = screen_corpus

    new_corpus = list(set(new_corpus))
    del tokenizer
    return new_corpus, dic


def delete_randomly(field, all_corpus, split_rate=0.5, intent=None):
    """
    随机删除词频低的词和切分出的所有字，得到新增的语料
    :param field:   领域 -> str
    :param all_corpus:  语料集 -> list
    :param split_rate:  切分率 -> float
    :param intent:  激活意图列表 -> list
    :return: new_corpus:    新增的语料 -> list
    :return: dic:    原句为key，新增语料为value的字典 -> dic
    """
    split_rate = 1 - split_rate
    tokenizer = load_field_dict(field)
    corpus, labels = get_corpus_label(all_corpus, intent)
    if not corpus:
        return [], split_rate, {}

    new_corpus = []
    dic = {}

    for idx, sen in enumerate(corpus):
        words = [i for i in tokenizer.cut(sen)]
        if len(words) <= 3:
            logger.info(words, sen)
            continue
        tfidf = jieba.analyse.extract_tags(sen, withWeight=True)

        replace_rate = int(len(tfidf) * split_rate)
        tfidf = [t[0] for t in tfidf[replace_rate:]]
        minus_ele = list(set(tfidf) - set(words))
        if minus_ele:
            # 删除tfidf列表与切词结果列表中不同的部分
            _ = [tfidf.remove(i) for i in minus_ele]
        single_words = list(set([i for i in words if len(i) == 1]))

        screen_corpus = []
        for i in tfidf:
            cp = "{}\t{}\n".format(sen.replace(i, ""), labels[idx])
            if cp not in all_corpus and cp not in new_corpus:
                screen_corpus.append(cp)

        pattern = "|".join(single_words)
        try:
            cp = "{}\t{}\n".format(re.sub(pattern, "", sen), labels[idx])
            if cp not in all_corpus and cp not in new_corpus:
                screen_corpus.append(cp)
        except Exception as e:
            logger.info(e.args)

        new_corpus.extend(screen_corpus)
        dic[sen] = screen_corpus

    del tokenizer
    return new_corpus, dic
