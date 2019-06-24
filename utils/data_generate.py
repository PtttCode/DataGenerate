import os
import re
import time
import json
import jieba
import random
import jieba.analyse
import synonyms
import itertools
import jieba.analyse
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer, CountVectorizer

from settings.settings import logger, word_dep, field_dir, stop_words


def find_all_field():
    fields = [i for i in os.listdir(field_dir)]
    for field in fields:
        print(field)
        update_words(field_dir, field)


def update_words(work_dir, field, tfidf=3):
    work_dir = "{}/{}".format(work_dir, field)
    datas = []
    for parent, dirnames, filenames in os.walk(work_dir,  followlinks=True):
            for filename in filenames:
                with open("{}/{}".format(work_dir, filename), "r", encoding="utf-8") as f:
                    datas.extend([i.strip() for i in f.readlines()])

    with open("{}/{}.txt".format(word_dep, field), "w", encoding="utf-8") as f:
        datas = ["{} {}\n".format(i.strip(), tfidf) for i in datas if i]
        f.writelines(datas)


def load_field_dict(filed):
    sen = "查看stock"
    # tokenizer = jieba.analyse.default_tfidf
    tokenizer = jieba.Tokenizer()
    tokenizer.load_userdict("{}/{}.txt".format(word_dep, filed))
    # words = [i for i in tokenizer.cut(sen)]
    # ana = jieba.analyse.extract_tags(sen, withFlag=True, withWeight=True)
    # print(words)
    # print(ana)

    return tokenizer


def swap_ele(origin_words, permutations):
    for i, j in permutations:
        idx1 = origin_words.index(i)
        idx2 = origin_words.index(j)
        origin_words[idx1], origin_words[idx2] = j, i

        yield "".join(origin_words)


def get_corpus_label(datas, intent=None):
    if intent:
        datas = [i for i in datas if i.split("\t")[1].strip() in intent]

    corpus = [i.split("\t")[0].strip() for i in datas]
    labels = [i.split("\t")[1].strip() for i in datas]

    return corpus, labels


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
            print(words, sen)
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
            cp = "{}\t{}\n".format(sen.replace(i, ""), labels[idx])
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


def cal_tfidf():
    tfidf2 = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b", max_df=3)
    with open("jinrong0605.txt", "r", encoding="utf-8") as f:
        data = f.readlines()
    tokenizer = load_field_dict("金融")
    data = [" ".join([j for j in tokenizer.cut(i.split("\t")[0])]) for i in data]
    with open("tfidf.txt", "w", encoding="utf-8") as f:
        f.writelines([i + "\n" for i in data])
    data = ["".join(data).strip()]
    res = tfidf2.fit_transform(data).toarray()
    # vectorizer = CountVectorizer()
    #
    # transformer = TfidfTransformer()
    # tfidf = transformer.fit_transform(vectorizer.fit_transform(data))
    # print(words.vocabulary_)
    # print(res)
    word = tfidf2.get_feature_names()

    print(len(word))
    res = res[0]
    print(len(res))
    sorted(res)
    print(res)


def translation_generate(all_corpus, intent=None):
    from translation.youdao_trans import youdao_translate
    from translation.tc_api import tencent_translation, TencentCloud
    tc = TencentCloud()

    corpus, labels = get_corpus_label(all_corpus, intent)
    if not corpus:
        return [], {}

    new_corpus = []
    dic = {}

    for idx, sen in enumerate(corpus):
        if idx % 10 == 0:
            print(idx)

        trans_sen = [i for i in tencent_translation(tc, sen, ['en'])]
        # trans_sen = youdao_translate(youdao_translate(sen))

        print(trans_sen)
        screen_corpus = []
        for i in trans_sen:
            cp = "{}\t{}\n".format(i, labels[idx])
            if cp not in all_corpus and cp not in new_corpus:
                screen_corpus.append(cp)

        new_corpus.extend(screen_corpus)
        dic[sen] = screen_corpus

    return new_corpus, dic


def get_synonyms(word):
    return synonyms.nearby(word)[0]


def insert_randomly(words, n):
    new_words = words.copy()
    for _ in range(n):
        synonyms = []
        counter = 0
        while len(synonyms) < 1:
            random_word = new_words[random.randint(0, len(new_words)-1)]
            synonyms = get_synonyms(random_word)
            counter += 1
            if counter >= 10:
                return
        random_synonym = random.choice(synonyms)
        random_idx = random.randint(0, len(new_words)-1)
        new_words.insert(random_idx, random_synonym)
    return new_words


def replace_randomly(words, n):
    new_words = words.copy()
    random_word_list = list(set([word for word in words if word not in stop_words]))
    random.shuffle(random_word_list)
    num_replaced = 0
    for random_word in random_word_list:
        synonyms = get_synonyms(random_word)
        if len(synonyms) >= 1:
            synonym = random.choice(synonyms)
            new_words = [synonym if word == random_word else word for word in new_words]
            num_replaced += 1
        if num_replaced >= n:
            break

    sentence = ' '.join(new_words)
    new_words = sentence.split(' ')
    return new_words


def synonyms_run(field, all_corpus, method, ele_num=3, intent=None):
    tokenizer = load_field_dict(field)
    corpus, labels = get_corpus_label(all_corpus, intent)
    if not corpus:
        return [], {}

    new_corpus = []
    dic = {}
    for idx, sen in enumerate(corpus):
        words = [i for i in tokenizer.cut(sen)]
        if len(words) <= 3:
            # print(words, sen)
            continue

        word_list = method(words, ele_num)
        new_sen = "".join(word_list) if isinstance(word_list, list) else "".join([i for i in word_list])
        cp = "{}\t{}\n".format(new_sen, labels[idx])
        if cp not in all_corpus and cp not in new_corpus:
            new_corpus.append(cp)

        dic[sen] = cp

    return new_corpus, dic


if __name__ == '__main__':
    # update_words(work_dir="金融", tfidf=3)
    # load_field_dict(filed="金融")
    filename = "jinrong0614.txt"
    split_r = 0.5
    times = time.time()

    # find_all_field("data/field")

    # with open(filename, "r", encoding="utf-8") as f:
    #     data = [i for i in f.readlines()]

    # new_cor, dicc = replace_randomly(field="金融", all_corpus=data, split_rate=split_r)
    # with open("字典_替换_数据增强_{}_{}_{}_{}".format(str(times), split_r, len(new_cor), filename), "w", encoding="utf-8") as f:
    #     f.write(json.dumps(dicc, ensure_ascii=False, indent=2))
    # with open("语料_替换_数据增强_{}_{}_{}_{}".format(str(times), split_r, len(new_cor), filename), "w", encoding="utf-8") as f:
    #     f.writelines(new_cor)
    #
    # a, c = delete_randomly(field="金融", all_corpus=data, split_rate=split_r)
    # with open("字典_删除_数据增强_{}_{}_{}_{}".format(str(times), split_r, len(a), filename), "w", encoding="utf-8") as f:
    #     f.write(json.dumps(c, ensure_ascii=False, indent=2))
    # with open("语料_删除_数据增强_{}_{}_{}_{}".format(str(times), split_r, len(a), filename), "w", encoding="utf-8") as f:
    #     f.writelines(a)
    #
    # print(len(data), len(new_cor))
    # print(len(data), len(a))

    # res = translation_generate(data)
    # print(res)



