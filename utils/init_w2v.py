from gensim.models import KeyedVectors


from settings.settings import WORD2VEC_PATH


def init_word2vec(word2vec_path):
    word2vec_model = KeyedVectors.load(word2vec_path)
    word2vec_model.most_similar(positive=["初始化"], topn=1)

    return word2vec_model


def build_word2vec(doc):
    import gensim
    with open(doc, "r") as f:
        corpus = [i.strip().split("\t")[0] for i in f.readlines()]
    model = gensim.models.Word2Vec(corpus, size=200,
                           min_count=0, sg=1, hs=0, negative=6,
                           iter=10, workers=64, window=7, seed=2019)

    return model.wv


w2v = init_word2vec(WORD2VEC_PATH)

