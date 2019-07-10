# coding:utf-8
import itertools
import thulac
import numpy as np
import pandas as pd

from keras.preprocessing.text import Tokenizer
from jieba import posseg as pseg
from gensim.models import KeyedVectors


def time_cal(func):
    import time

    def run(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print("函数{0}的运行时间为： {1}".format(func.__name__, time.time() - start))
        return result
    return run


@time_cal
def get_product(*args):
    return itertools.product(*args)


@time_cal
def synonym_replace(word_syntax, sent_list, idxs, synonym_dict):
    res = []
    sent = "".join(sent_list)
    print(word_syntax, sent_list, idxs)
    for idx in idxs:
        synonym_list = synonym_dict[word_syntax[idx]]
        for j in synonym_list:
            res.append(sent.replace(sent_list[idx], j))
    return res


@time_cal
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


@time_cal
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


def token_corpus(filename):
    df = pd.read_excel(filename)
    df["words"], df["flags"] = list(zip(*df.apply(lambda x: _cut(x["语料"], use_thulac=True), axis=1)))

    all_char_list = list(df["words"])
    token = Tokenizer()

    token.fit_on_texts(all_char_list)
    word_index = token.word_index
    word2pos = get_pos(df["words"].tolist(), df["flags"].tolist())
    df.to_excel("thulac_output.xlsx")
    return word_index, word2pos


@time_cal
def get_most_similar(model, pos_word, vocab, topn=20, pos_tag=None, word2pos=None):
    try:
        res = model.most_similar(positive=[pos_word], negative=[], topn=topn * 1000)
    except KeyError as e:
        print("[!] Not in vocab pos_word = {}".format(pos_word))
        return []
    res = [(e1, e2) for e1, e2 in res if e1 in vocab and e1 in word2pos]
    res = [(e1, e2) for e1, e2 in res if pos_tag in word2pos[e1]]
    return res[: topn]


@time_cal
def write_excel(word_index, word2pos, word2vec_model, filename):
    x = []
    for word in word_index:
        if word in word2pos:
            for pos_ in word2pos[word]:
                # print(word, pos_)
                for e in get_most_similar(word2vec_model, pos_word=word, topn=20, pos_tag=pos_, word2pos=word2pos):
                    x.append([word, pos_, e[0], round(e[1], 6)])
    df = pd.DataFrame(np.array(x), columns=['word1', "word1_pos", 'word2', 'similar'])
    df.to_excel(filename, encoding="utf8")


if __name__ == '__main__':

    thu1 = thulac.thulac()  # 默认模式
    filename = "../中德安联意图语料V5.0.4_0709.xlsx"
    word2vec_path = "../cc.zh.300.vec"
    word2vec_model = KeyedVectors.load_word2vec_format(word2vec_path, binary=False)

    word_index, word_pos = token_corpus(filename)
    write_excel(word_index, word_pos, word2vec_model, "res.xlsx")

    print(1/0)





    excel_name = "../同义词库（词性）.xlsx"
    data = pd.read_excel(excel_name)
    data = data[["word1", "word1_pos", "word2"]].values.tolist()

    priority = ["v", "n", "vn", "a", "t", "d", "eng", "r", "m", "uj", "c", "p", "q", "l"]
    limit = 2
    min_rep_num = 1

    with open("corpus.txt", "r", encoding="utf-8") as f:
        corpus = f.readlines()
        sents = [i.strip().split("\t")[0].split(" ") for i in corpus]
        syntaxs = [i.strip().split("\t")[1].split(" ") for i in corpus]
        labels = [i.strip().split("\t")[2] for i in corpus]
        word_syntax = [["_".join(k) for k in zip(sents[i], syntaxs[i])] for i in range(len(sents))]

    # print(labels)


    # syntax_name = "../句式.xlsx"
    # syntax = pd.read_excel(syntax_name)
    # syntax = [i[0].split(" ") for i in syntax[["flags1"]].values.tolist()]
    # print(len(syntax))

    # print(syntax)

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

    res = []
    for idx, words in enumerate(word_syntax):
        length = len(words)
        split_num = max(int(length/limit), min_rep_num)
        indexs = []

        for i in range(split_num):
            for j in priority:
                pos = syntaxs[idx].index(j) if j in syntaxs[idx] else 0
                if (j in syntaxs[idx]) and (words[pos] in synonym_dict):
                    indexs.append(pos)
                    break
        # try:
        #     all_words = [list(word_dict[k]) for k in i]
        # except KeyError as e:
        #     print("Error:{}{}".format(e.args, " ".join(i)))
        #     continue
        # product = [j for j in get_product(*all_words)]
        # product = ["".join(s) for s in product]
        new_sents = synonym_replace(words, sents[idx], indexs, synonym_dict)
        res.extend(["{}\t{}\n".format(i, labels[idx]) for i in new_sents])
        res.append("----------------------------------------------------------------------\n")
    with open("句式生成.txt", "w", encoding="utf-8") as f:
        f.writelines(list(set(res)))















