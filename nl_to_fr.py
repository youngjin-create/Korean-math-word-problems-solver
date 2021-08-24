
# from gensim import models

print('loading model...')
# ko_model = models.fasttext.load_facebook_model('../../../word2vec/gensim_fasttext/cc.ko.300.bin')
# ko_model = models.fasttext.load_facebook_model('fasttext/cc.ko.300.bin')
# ko_model = models.fasttext.load_facebook_model('fasttext/ko_Kyobong.200.bin')
print('done.')

similarity_cache = dict()
def word_similiarty(w1, w2):
    global similarity_cache
    key = w1 + ' ' + w2
    if not(key in similarity_cache):
        similarity_cache[key] = ko_model.wv.similarity(w1, w2)
    return similarity_cache[key]

def clear_cache():
    global similarity_cache
    similarity_cache = dict()

# 문장 비교, 비슷할 수록 낮은 값 리턴
def semantic_similarity(s1, s2):
    # return ko_model.wv.wmdistance(s1, s2)
    w1, w2 = s1.split(' '), s2.split(' ')
    table = [[None for i in range(len(w2))] for j in range(len(w1))]
    def score(l1, l2):
        if l1 < 0 and l2 < 0:
            return 0
        if l1 < 0 or l2 < 0:
            return float('inf')
        if table[l1][l2] == None:
            # table[l1][l2] = min(score(l1, l2-1), score(l1-1, l2), score(l1-1, l2-1)) + (1-ko_model.wv.similarity(w1[l1], w2[l2]))
            table[l1][l2] = min(score(l1, l2-1), score(l1-1, l2), score(l1-1, l2-1)) + (1-word_similiarty(w1[l1], w2[l2]))
        return table[l1][l2]
    # print(score(len(w1)-1, len(w2)-1))
    # print(table)
    # print(w1)
    # print(w2)
    return score(len(w1)-1, len(w2)-1) # / (len(w1) + len(w2))

random_var_name = 0
def get_random_var_name():
    global random_var_name
    random_var_name = random_var_name + 1
    return f'var{random_var_name:03d}'

# %%
# '<x:숫자>'와 같은 입력이 들어왔을 때 (x, 숫자)를 리턴
def get_name_and_type(item):
    # str_types = ['숫자', '수열', '지시자', '지시자들', '미지수', '미지수들', '사람', '사람들', '과목', '과목들']
    pos = item.find(':')
    first, second = (item[1:pos], item[pos+1:-1]) if pos != -1 else ('', item[1:-1])
    return (first, second) if second.upper() == second.lower() else (second, first)

# %%
# mapping = { '$a': 'var22', '$b': 'var33' }
def variable_substitute(statement, mapping):
    # print(statement)
    # print(mapping)
    for m in mapping:
        statement = statement.replace(m, str(mapping[m]))
    return statement

# %%
def generate(q):
    statements = []
    score = 0
    yield statements, score
