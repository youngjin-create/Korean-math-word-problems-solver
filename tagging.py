import re
from numba import jit
import numpy as np
from konlpy.tag import Okt, Komoran, Hannanum, Kkma, Mecab
mecab = Mecab()

re_var = re.compile(r'((@[ns]?|#|\$)[0-9]+)(\D|$)')
re_number = re.compile(r'[0-9]+([.][0-9]+)?(/[0-9]+([.][0-9]+)?)?')
re_string = re.compile(r'\(\w\)')
re_equation = re.compile('[0-9A-Z][0-9A-Z\.\+\-\*\/\(\)=<> ]*=[0-9A-Z\.\+\-\*\/\(\)=<> ]*[0-9A-Z]') # 등호(=)를 포함하는 식

# 템플릿 매칭을 위한 사용자 정의 태그 : WILDCARD, WILDCARD_NUM, WILDCARD_STR, NUMBER, STRING, EQUATION, NUMBERS, STRINGS, MAPPING
def pos_tagging(text, join=None):
    global re_number

    tags = mecab.pos(text, join=join)
    new_tags = []
    position = 0
    for tag in tags:
        position = text.find(tag[0], position)
        new_tags.append((tag[0], tag[1], position, position+len(tag[0])))
    tags = new_tags

    for match in re_var.finditer(text):
        # print(match)
        tags = [tag for tag in tags if not(match.span(1)[0] <= tag[2] and tag[3] <= match.span(1)[1])]
        if match.group(2) in ['@n', '#']:
            cl = 'WILDCARD_NUM'
        elif match.group(2) in ['@s', '$']:
            cl = 'WILDCARD_STR'
        else:
            cl = 'WILDCARD'
        tags.append((match.group(1), cl, match.span(1)[0], match.span(1)[1]))

    for match in re_number.finditer(text):
        # print(match)
        tags = [tag for tag in tags if not(match.span()[0] <= tag[2] and tag[3] <= match.span()[1])]
        tags.append((match.group(), 'NUMBER', match.span()[0], match.span()[1]))

    for match in re_string.finditer(text):
        # print(match)
        tags = [tag for tag in tags if not(match.span()[0] <= tag[2] and tag[3] <= match.span()[1])]
        tags.append((match.group(), 'STRING', match.span()[0], match.span()[1]))

    for match in re_equation.finditer(text):
        # print(match)
        tags = [tag for tag in tags if not(match.span()[0] <= tag[2] and tag[3] <= match.span()[1])]
        tags.append((match.group(), 'EQUATION', match.span()[0], match.span()[1]))

    for match in re.finditer('@numbers', text):
        tags.append((match.group(), 'NUMBERS', match.span()[0], match.span()[1]))

    for match in re.finditer('@strings', text):
        tags.append((match.group(), 'STRINGS', match.span()[0], match.span()[1]))

    for match in re.finditer('@mapping', text):
        tags.append((match.group(), 'MAPPING', match.span()[0], match.span()[1]))

    tags.sort(key=lambda x:x[2]*10000-x[3])

    new_tags = []
    position = 0
    for tag in tags:
        if tag[2] < position:
            continue
        new_tags.append(list(tag))
        position = tag[3]
    tags = new_tags

    # for i in range(0, len(tags)):
    #     if tags[i][0] == '이' and (tags[i][1] == 'NR' or tags[i][1] == 'XSN' or tags[i][1] == 'JKS'):
    #         tags[i][1] = 'IGNORE'

    # for i in range(1, len(tags)-1):
    #     if tags[i][0] == '이' and tags[i][1] == 'NR':
    #         if tags[i-1][1].startswith('WILDCARD') and tags[i+1][1] == 'JX':
    #             tags[i][1] = 'XSN'

    tags = [tuple(x) for x in tags]

    return tags


# pos tagging된 두 단어를 비교한 score를 계산, w1 = template tag, w2 = question tag
# w = (str, POS, start, end)의 형식, start, end는 문장에서의 span 시작과 끝 index
# 이상적으로는 str과 POS값을 모두 고려하여 score를 계산하여야 하지만 일단 POS값을 중요시하여 계산
# POS값에 따른 score matrix를 생각할 수 있고, 이것을 자동학습 할 수 있으면 좋을듯
def match_word_tags(t_tag, q_tag):
    s = 1.0
    if t_tag[1] == q_tag[1]: # POS가 같으면 페널티 없음
        if t_tag[0] == q_tag[0]:
            s = 0.0
        else:
            s = 0.1
    elif t_tag[0] == q_tag[0]:
        s = 0.1
    elif t_tag[1] == 'NONE' or q_tag[1] == 'NONE': # 매칭되는 단어가 없어서 스킵할 경우
        s = 0.6
    elif t_tag[1] == 'WILDCARD':
        if q_tag[1][0] == 'N' or q_tag[1] == 'SL': # WILDCARD는 단어 또는 숫자에 매칭 가능
            s = 0.0
        else:
            s = 1000000.0
    elif t_tag[1] == 'WILDCARD_NUM':
        if q_tag[1] == 'NUMBER':
            s = 0.0
        else:
            s = 1000000.0
    elif t_tag[1] == 'WILDCARD_STR':
        if q_tag[1] != 'NUMBER' and (q_tag[1][0] == 'N' or q_tag[1] == 'SL'):
            s = 0.0
        else:
            s = 1000000.0
    elif t_tag[1] == 'SF' or q_tag[1] == 'SF': # 마침표
        s = 0.1
    # POS가 다른 단어끼리 매칭
    else:
        s = 1.0
    return s
    # score_table[i1][i2] = s

    # if w1[1] == w2[1]: # POS가 같으면 페널티 없음
    #     return 0.0
    # if w1[1] == 'NONE' or w2[1] == 'NONE': # 매칭되는 단어가 없어서 스킵할 경우
    #     return 0.6
    # if w1[1] == 'WILDCARD':
    #     if w2[1][0] == 'N' or w2[1] == 'SL': # WILDCARD는 단어 또는 숫자에 매칭 가능
    #         return 0.0
    #     else:
    #         return float('inf')
    # if w1[1] == 'SF' or w2[1] == 'SF': # 마침표
    #     return 0.1
    # # POS가 다른 단어끼리 매칭
    # return 1.0


# 문장 비교, 비슷할 수록 낮은 값 리턴
@jit(nopython=True)
def match_to_template_tags_jit(len_t, len_q, score_table, scores, tracks1, tracks2):
    for i1 in range(0, len_t+1):
        for i2 in range(0, len_q+1):
            scores[i1,i2], tracks1[i1][i2], tracks2[i1][i2] = 1000000.0, -1000000, -1000000
            if i1>0 and i2>0 and scores[i1,i2] > scores[i1-1,i2-1] + score_table[i1][i2]:
                scores[i1,i2] = scores[i1-1,i2-1] + score_table[i1][i2]
                tracks1[i1][i2] = i1-1
                tracks2[i1][i2] = i2-1
            if i2>0 and scores[i1,i2] > scores[i1,i2-1] + score_table[0][i2]:
                scores[i1,i2] = scores[i1,i2-1] + score_table[0][i2]
                tracks1[i1][i2] = i1
                tracks2[i1][i2] = i2-1
            if i1>0 and scores[i1,i2] > scores[i1-1,i2] + score_table[i1][0]:
                scores[i1,i2] = scores[i1-1,i2] + score_table[i1][0]
                tracks1[i1][i2] = i1-1
                tracks2[i1][i2] = i2
            if i1==0 and i2==0:
                scores[i1,i2], tracks1[i1][i2], tracks2[i1][i2] = 0.0, -1000000, -1000000
    return #scores, tracks1, tracks2

# 문장 비교, 비슷할 수록 낮은 값 리턴
def match_to_template_tags(template_tags, question_tags, visualize=False):
    len_t, len_q = len(template_tags), len(question_tags)
    score_table = 1000000.0 * np.ones([len_t+1, len_q+1])

    # for i1 in range(0, len(template_tags)+1):
    #     for i2 in range(0, len(question_tags)+1):
    #         score_table[i1][i2] = match_word_tags(
    #             template_tags[i1-1] if i1>0 else ('', 'NONE', None, None),
    #             question_tags[i2-1] if i2>0 else ('', 'NONE', None, None))

    for i1 in range(0, len(template_tags)+1):
        for i2 in range(0, len(question_tags)+1):
            t_tag = template_tags[i1-1] if i1>0 else ('', 'NONE', -1, -1)
            q_tag = question_tags[i2-1] if i2>0 else ('', 'NONE', -1, -1)
            # if t_tag[1] == q_tag[1]: # POS가 같으면 페널티 없음
            #     if t_tag[0] == q_tag[0]:
            #         s = 0.0
            #     else:
            #         s = 0.1
            # elif t_tag[0] == q_tag[0]:
            #     s = 0.1
            # elif t_tag[1] == 'NONE' or q_tag[1] == 'NONE': # 매칭되는 단어가 없어서 스킵할 경우
            #     s = 0.6
            # elif t_tag[1] == 'WILDCARD':
            #     if q_tag[1][0] == 'N' or q_tag[1] == 'SL': # WILDCARD는 단어 또는 숫자에 매칭 가능
            #         s = 0.0
            #     else:
            #         s = 1000000.0
            # elif t_tag[1] == 'WILDCARD_NUM':
            #     if q_tag[1] == 'NUMBER':
            #         s = 0.0
            #     else:
            #         s = 1000000.0
            # elif t_tag[1] == 'WILDCARD_STR':
            #     if q_tag[1] != 'NUMBER' and (q_tag[1][0] == 'N' or q_tag[1] == 'SL'):
            #         s = 0.0
            #     else:
            #         s = 1000000.0
            # elif t_tag[1] == 'SF' or q_tag[1] == 'SF': # 마침표
            #     s = 0.1
            # # POS가 다른 단어끼리 매칭
            # else:
            #     s = 1.0
            # score_table[i1][i2] = s
            score_table[i1][i2] = match_word_tags(t_tag, q_tag)
            
    
    scores = np.zeros([len_t+1, len_q+1])
    tracks1 = np.zeros([len_t+1, len_q+1], dtype=int)
    tracks2 = np.zeros([len_t+1, len_q+1], dtype=int)
    match_to_template_tags_jit(len_t, len_q, score_table, scores, tracks1, tracks2)

    correspondence = []
    assignments = dict()
    i1, i2 = len_t, len_q
    while True:
        if i1 == -1000000 or i2 == -1000000:
            break
        if tracks1[i1][i2] == i1 - 1 and tracks2[i1][i2] == i2 - 1: # 실제 tags사이에 매칭이 일어난 경우 (None과 매칭되지 않고) WILDCARD에 대응되는 값을 assignments에 추가
            if template_tags[i1-1][1].startswith('WILDCARD'):
                name = template_tags[i1-1][0]
                if name not in assignments:
                    assignments[name] = set()
                assignments[name].add(question_tags[i2-1])
                # assignments[name] = question_tags[i2-1]
        correspondence.append((i1, i2, scores[i1,i2]))
        i1, i2 = tracks1[i1][i2], tracks2[i1][i2]

    # def backtrack(i1, i2):
    #     if i1 == -1000000 or i2 == -1000000:
    #         return
    #     if tracks1[i1][i2] == i1 - 1 and tracks2[i1][i2] == i2 - 1: # 실제 tags사이에 매칭이 일어난 경우 (None과 매칭되지 않고) WILDCARD에 대응되는 값을 assignments에 추가
    #         if template_tags[i1-1][1] == 'WILDCARD':
    #             name = template_tags[i1-1][0][1:]
    #             if name not in assignments:
    #                 assignments[name] = set()
    #             assignments[name].add(question_tags[i2-1])
    #     correspondence.append((i1, i2, scores[i1][i2]))
    #     backtrack(tracks1[i1][i2], tracks2[i1][i2])
    # backtrack(len(template_tags), len(question_tags))

    # correspondence = reversed(correspondence)
    # for match in correspondence:
    #     print(match)
    if visualize:
        last = (0, 0, 0)
        for match in reversed(correspondence):
            left, right = ('', 'NONE', None, None), ('', 'NONE', None, None)
            if match[0] > last[0]:
                left = template_tags[match[0]-1]
            if match[1] > last[1]:
                right = question_tags[match[1]-1]
            print('{:0.2f}'.format(match[2] - last[2]) + ' (' + left[0] + ' ' + left[1] + ') --- (' + right[0] + ' ' + right[1] + ')')
            last = match
        print('matching score = {:0.2f}'.format(scores[-1][-1]))

    return scores[-1][-1], assignments, correspondence

# match_to_template_tags(utils.pos_tagging('상자 안에 5개의 감이 있습니다.'), utils.pos_tagging('상자 안에 5개의 감이 있습니다.'))
# match_to_template_tags(utils.pos_tagging('상자 안에 @0개의 감이 있습니다.'), utils.pos_tagging('박스 안에 5개의 과일이 있다.'))


# %%
if __name__== "__main__": # 모듈 단독 테스트
    q = '#1에서 22를 뺀 값은 11입니다. $1이는 지민이보다 무겁습니다. 이 사람보다 무거운 사람은?'
    print(pos_tagging(q))

# %%

# %%
# score, assignments = match_to_template_tags(
#     utils.pos_tagging('비행기에 @0명이 타고 있습니다. 그 중 @1명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?'),
#     utils.pos_tagging('버스에 22명이 타고 있습니다. 그 중 118명이 내렸을 때, 버스에 남아있는 있는 사람은 얼마입니까?'),
#     visualize=True)
# start_time = time.time()
# for i in range(1000):
#     # utils.pos_tagging('비행기에 @0명이 타고 있습니다. 그 중 @1명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?')
#     # utils.pos_tagging('@strings 각각 1개씩 있습니다. 이 중 3개를 택하여 한 개의 접시에 담으려고 합니다. 감과 귤을 함께 담지 않는 방법은 모두 몇 가지입니까?')
#     # score, assignments = match_to_template_tags(
#     #     utils.pos_tagging('비행기에 @0명이 타고 있습니다. 그 중 @1명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?'),
#     #     utils.pos_tagging('@strings 각각 1개씩 있습니다. 이 중 3개를 택하여 한 개의 접시에 담으려고 합니다. 감과 귤을 함께 담지 않는 방법은 모두 몇 가지입니까?'))
#     score, assignments = match_to_template_tags(
#         utils.pos_tagging('비행기에 @0명이 타고 있습니다. 그 중 @1명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?'),
#         utils.pos_tagging('버스에 22명이 타고 있습니다. 그 중 118명이 내렸을 때, 버스에 남아있는 있는 사람은 얼마입니까?'))
# print(time.time() - start_time)

if __name__== "__main__": # 모듈 단독 테스트
    score, assignments, _ = match_to_template_tags(
        pos_tagging('@s0이는 @s2이보다 무겁고 @s1이보다 가볍습니다. $1이는 $2이보다 가볍습니다. 4명 중 가장 가벼운 사람은 누구입니까?'),
        pos_tagging('석진이는 호석이보다 무겁고 지민이보다 가볍습니다. 남준이는 호석이보다 가볍습니다. 4명 중 가장 가벼운 사람은 누구입니까?'),
        visualize=True)
    print(score)
    print(assignments)