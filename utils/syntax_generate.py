# coding:utf-8
import json
import time
import thulac
import itertools
import numpy as np
import pandas as pd

from keras.preprocessing.text import Tokenizer
from jieba import posseg as pseg
from gensim.models import KeyedVectors


thu1 = thulac.thulac()  # 默认模式


def time_cal(func):

    def run(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print("函数{0}的运行时间为： {1}".format(func.__name__, time.time() - start))
        return result
    return run


def init_word2vec(word2vec_path):
    word2vec_model = KeyedVectors.load(word2vec_path)
    word2vec_model.most_similar(positive=["初始化"], topn=1)

    return word2vec_model


@time_cal
def get_product(*args):
    return itertools.product(*args)


@time_cal
def load_words(filename):
    data = pd.read_excel(filename)
    data = data[["word1", "word1_pos", "word2"]].values.tolist()
    # with open(filename, "r", encoding="utf-8") as f:
    #     data = json.loads(f.read())
    word_dict = {}
    synonym_dict = {}

    for i in data:
        key = "{}_{}".format(i[0], i[1])
        if key not in synonym_dict:
            synonym_dict.setdefault(key, set())
        if i[1] not in word_dict:
            word_dict.setdefault(i[1], set())
        synonym_dict[key].add(i[2])
        word_dict[i[1]].add(i[0])

    return word_dict, synonym_dict


@time_cal
def run_func(corpus, filename, args):
    res = []
    sents = [i.strip().split("\t")[0].split(" ") for i in corpus]
    syntaxs = [i.strip().split("\t")[1].split(" ") for i in corpus]
    labels = [i.strip().split("\t")[2] for i in corpus]
    word_syntax = [["_".join(k) for k in zip(sents[i], syntaxs[i])] for i in range(len(sents))]
    word_dict, synonym_dict = load_words(filename)

    for idx, words in enumerate(word_syntax):
        length = len(words)
        split_num = max(int(length / args["limit"]), args["min_rep_num"])
        indexs = []

        for i in range(split_num):
            for j in args["priority"]:
                pos = syntaxs[idx].index(j) if j in syntaxs[idx] else 0
                if (j in syntaxs[idx]) and (words[pos] in synonym_dict):
                    indexs.append(pos)
                    break

        new_sents = synonym_replace(words, sents[idx], indexs, synonym_dict)
        res.extend(["{}\t{}\n".format(i, labels[idx]) for i in new_sents])
        res.append("----------------------------------------------------------------------\n")
    return res


def synonym_replace(word_syntax, sent_list, idxs, synonym_dict):
    res = []
    sent = "".join(sent_list)
    # print(word_syntax, sent_list, idxs)
    for idx in idxs:
        synonym_list = synonym_dict[word_syntax[idx]]
        for j in synonym_list:
            res.append(sent.replace(sent_list[idx], j))
    return res


def _cut(x, use_thulac=True):
    if use_thulac:
        x = thu1.cut(x)
        words, flags = list(zip(*x))
    else:
        x = pseg.cut(x)
        words, flags = list(zip(*[(e.word, e.flag) for e in x]))
    # words = [word + ''+ flag for word, flag in zip(words, flags)]
    words = " ".join(words)
    flags = " ".join(flags)
    return words, flags


def get_pos(words, postags):
    d = {}
    for word, pos in zip(words, postags):
        # print(word, pos)
        for w, p in zip(word.split(" "), pos.split(" ")):
            if w not in d:
                d[w] = [p]
            else:
                if not p in d[w]:
                    d[w].append(p)
    return d


@time_cal
def token_corpus(filename):
    df = pd.read_excel(filename)
    df["words"], df["flags"] = list(zip(*df.apply(lambda x: _cut(x["语料"], use_thulac=True), axis=1)))

    all_char_list = list(df["words"])
    token = Tokenizer()

    token.fit_on_texts(all_char_list)
    word_index = token.word_index
    word2pos = get_pos(df["words"].tolist(), df["flags"].tolist())
    df.to_excel("thulac_output.xlsx")
    corpus = ["\t".join(i)+"\n" for i in zip(df["words"], df["flags"], df["意图"])]
    del token
    return word_index, word2pos, corpus


def get_most_similar(model, pos_word, vocab, topn=20, pos_tag=None, word2pos=None):
    try:
        res = model.most_similar(positive=[pos_word], negative=[], topn=topn * 20)
    except KeyError as e:
        print("[!] Not in vocab pos_word = {}".format(pos_word))
        yield []
    res = [(e1, e2) for e1, e2 in res if e1 in vocab and e1 in word2pos]
    res = [(e1, e2) for e1, e2 in res if pos_tag in word2pos[e1]]
    yield res[:topn]


@time_cal
def write_excel(word_index, word2pos, word2vec_model, filename, thresholds):
    x = []
    for word in word_index:
        if word in word2pos:
            for pos_ in word2pos[word]:
                # print(word, pos_)
                values_obj = get_most_similar(word2vec_model, pos_word=word, vocab=word_index, topn=20, pos_tag=pos_, word2pos=word2pos)
                similars = next(values_obj)
                x.extend([[word, pos_, e[0], round(e[1], 6)] for e in similars if e[1] >= thresholds])
    df = pd.DataFrame(np.array(x), columns=['word1', "word1_pos", 'word2', 'similar'])
    df.to_excel(filename, encoding="utf8")


def syntax_generate(word2vec_model, corpus_filename, words_filename, args):
    word_index, word_pos, corpus = token_corpus(corpus_filename)
    write_excel(word_index, word_pos, word2vec_model, words_filename, args["thresholds"])
    res = run_func(corpus, words_filename, args)

    return res
















