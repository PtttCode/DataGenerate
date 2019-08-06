from gensim.models import KeyedVectors


from settings.settings import WORD2VEC_PATH


def init_word2vec(word2vec_path):
    word2vec_model = KeyedVectors.load(word2vec_path)
    word2vec_model.most_similar(positive=["初始化"], topn=1)

    return word2vec_model


w2v = init_word2vec(WORD2VEC_PATH)

