
# %%
import re
from gensim import models

print('loading word embeddings...', end=' ')
# ko_model = models.fasttext.load_facebook_model('../../../word2vec/gensim_fasttext/cc.ko.300.bin')
# ko_model = models.fasttext.load_facebook_model('fasttext/cc.ko.300.bin')
ko_model = models.fasttext.load_facebook_model('fasttext/ko_Kyobong.200.bin')
print('done.')

similarity_cache = dict()
def clear_cache():
    global similarity_cache
    similarity_cache = dict()

def word_similiarty(w1, w2):
    global similarity_cache
    key = w1 + ' ' + w2
    if not(key in similarity_cache):
        similarity_cache[key] = ko_model.wv.similarity(w1, w2)
    return similarity_cache[key]

re_var_ending = re.compile(r'(@[0-9]+)(\D*)')
def word_distance_template(w1, w2): # w1 = template word, w2 = question word
    global re_var_ending
    match = re_var_ending.fullmatch(w1)
    if match: # template 단어가 wildcard를 포함하고 있으면
        ending = match[2]
        if w2[len(w2)-len(ending):] == ending:
            return 0, w2[:len(w2)-len(ending)]
        return 1-ko_model.wv.similarity(w1, w2), w2
    else: # 단순 단어 비교
        if w1 == w2:
            return 0, None
        return 1-ko_model.wv.similarity(w1, w2), None
    return

# # 문장 비교, 비슷할 수록 낮은 값 리턴
# def phrase_similarity(s1, s2):
#     # return ko_model.wv.wmdistance(s1, s2)
#     w1, w2 = s1.split(' '), s2.split(' ')
#     table = [[None for i in range(len(w2))] for j in range(len(w1))]
#     def score(l1, l2):
#         if l1 < 0 and l2 < 0:
#             return 0
#         if l1 < 0 or l2 < 0:
#             return float('inf')
#         if table[l1][l2] == None:
#             # table[l1][l2] = min(score(l1, l2-1), score(l1-1, l2), score(l1-1, l2-1)) + (1-ko_model.wv.similarity(w1[l1], w2[l2]))
#             table[l1][l2] = min(score(l1, l2-1), score(l1-1, l2), score(l1-1, l2-1)) + (1-word_similiarty(w1[l1], w2[l2]))
#         return table[l1][l2]
#     # print(score(len(w1)-1, len(w2)-1))
#     # print(table)
#     # print(w1)
#     # print(w2)
#     return score(len(w1)-1, len(w2)-1) # / (len(w1) + len(w2))

# %%
word_distance_template('@4', '국어')