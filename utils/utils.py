import os
import jieba
import jieba.analyse
from sklearn.feature_extraction.text import TfidfVectorizer

from settings.settings import logger, WORD_DEP, FIELD_DIR


def find_all_field():
    fields = [i for i in os.listdir(FIELD_DIR)]
    for field in fields:
        logger.info(field)
        update_words(FIELD_DIR, field)


def update_words(work_dir, field, tfidf=3):
    work_dir = "{}/{}".format(work_dir, field)
    datas = []
    for parent, dirnames, filenames in os.walk(work_dir,  followlinks=True):
            for filename in filenames:
                with open("{}/{}".format(work_dir, filename), "r", encoding="utf-8") as f:
                    datas.extend([i.strip() for i in f.readlines()])

    with open("{}/{}.txt".format(WORD_DEP, field), "w", encoding="utf-8") as f:
        datas = ["{} {}\n".format(i.strip(), tfidf) for i in datas if i]
        f.writelines(datas)


def load_field_dict(field):
    # sen = "查看stock"
    # tokenizer = jieba.analyse.default_tfidf
    tokenizer = jieba.Tokenizer()
    tokenizer.load_userdict("{}/{}.txt".format(WORD_DEP, field))
    # words = [i for i in tokenizer.cut(sen)]
    # ana = jieba.analyse.extract_tags(sen, withFlag=True, withWeight=True)
    # logger.info(words)
    # logger.info(ana)

    return tokenizer


def get_corpus_label(datas, intent=None):
    if intent:
        datas = [i for i in datas if i.split("\t")[1].strip() in intent]

    corpus = [i.split("\t")[0].strip() for i in datas]
    labels = [i.split("\t")[1].strip() for i in datas]

    return corpus, labels


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
    # logger.info(words.vocabulary_)
    # logger.info(res)
    word = tfidf2.get_feature_names()

    logger.info(len(word))
    res = res[0]
    logger.info(len(res))
    sorted(res)
    logger.info(res)


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
            logger.info(idx)

        trans_sen = [i for i in tencent_translation(tc, sen, ['en'])]
        # trans_sen = youdao_translate(youdao_translate(sen))

        logger.info(trans_sen)
        screen_corpus = []
        for i in trans_sen:
            cp = "{}\t{}\n".format(i, labels[idx])
            if cp not in all_corpus and cp not in new_corpus:
                screen_corpus.append(cp)

        new_corpus.extend(screen_corpus)
        dic[sen] = screen_corpus

    return new_corpus, dic


