# -*-coding:utf-8-*-

BLACK_WORDS_PATH = '/home/xnr1/xnr_0429/xnr/timed_python_files/daily_interest_classify/dict/black.txt'

def load_black_words():
    black_words = set([line.strip('\r\n') for line in file(BLACK_WORDS_PATH)])
    return black_words

black_words = load_black_words()

