# %%
import re
from numba import jit
import numpy as np
from konlpy.tag import Okt, Komoran, Hannanum, Kkma, Mecab
mecab = Mecab()

import utils

re_var = re.compile(r'((@[ns]?|#|\$)[0-9]+)(\D|$)')
re_number = re.compile(r'[0-9]+([.][0-9]+)?(/[0-9]+([.][0-9]+)?)?')
re_numvar = re.compile(r'[A-Z]')
re_numexpr = re.compile(r'[0-9A-Z\(][0-9A-Z\(\)\.\+\-\*\/ ]*[0-9A-Z\)]')
re_string = re.compile(r'\(\w\)')
re_equation = re.compile('[0-9A-Z][0-9A-Z\.\+\-\*\/\(\)=<> ]*=[0-9A-Z\.\+\-\*\/\(\)=<> ]*[0-9A-Z]') # 등호(=)를 포함하는 식

def add_paddings(tags):
    return [('', 'PADDING', 0, 0), *tags, ('', 'PADDING', 0, 0)]

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

    for match in re_numvar.finditer(text):
        # print(match)
        tags = [tag for tag in tags if not(match.span()[0] <= tag[2] and tag[3] <= match.span()[1])]
        tags.append((match.group(), 'NUMBER', match.span()[0], match.span()[1]))

    for match in re_numexpr.finditer(text):
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

    for match in re.finditer('@numbers[0-9]', text):
        tags.append((match.group(), 'NUMBERS', match.span()[0], match.span()[1]))

    for match in re.finditer('@strings[0-9]', text):
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

    for tag in tags:
        if tag[0] == 'ml' and tag[1] == 'SL':
            tag[0] = '밀리리터'
            tag[1] = 'NNBC'
        if tag[0] == '㎖' and tag[1] == 'SY':
            tag[0] = '밀리리터'
            tag[1] = 'NNBC'
        if tag[0] == 'l' and tag[1] == 'SL':
            tag[0] = '리터'
            tag[1] = 'NNBC'
        if tag[0] == 'ℓ' and tag[1] == 'SY':
            tag[0] = '리터'
            tag[1] = 'NNBC'

        if tag[0] == 'cm' and tag[1] == 'SL':
            tag[0] = '센티미터'
            tag[1] = 'NNBC'
        if tag[0] == 'm' and tag[1] == 'SL':
            tag[0] = '미터'
            tag[1] = 'NNBC'
        if tag[0] == 'km' and tag[1] == 'SL':
            tag[0] = '킬로미터'
            tag[1] = 'NNBC'

        if tag[0] == '㎝' and tag[1] == 'SY':
            tag[0] = '센티미터'
            tag[1] = 'NNBC'
        if tag[0] == '㎠' and tag[1] == 'SY':
            tag[0] = '제곱센티미터'
            tag[1] = 'NNBC'
        if tag[0] == '㎤' and tag[1] == 'SY':
            tag[0] = '세제곱센티미터'
            tag[1] = 'NNBC'
        if tag[0] == '㎡' and tag[1] == 'SY':
            tag[0] = '제곱미터'
            tag[1] = 'NNBC'
        if tag[0] == '㎥' and tag[1] == 'SY':
            tag[0] = '세제곱미터'
            tag[1] = 'NNBC'

        if tag[0] == 'g' and tag[1] == 'SL':
            tag[0] = '그램'
            tag[1] = 'NNBC'
        if tag[0] == 'kg' and tag[1] == 'SL':
            tag[0] = '킬로그램'
            tag[1] = 'NNBC'

        if len(tag[0]) == 3 and tag[0][2] == '이' and tag[1] == 'NNP':
            tag[0] = tag[0][0:2]

    tags = [tuple(x) for x in tags]

    return tags


# pos tagging된 두 단어를 비교한 score를 계산, w1 = template tag, w2 = question tag
# w = (str, POS, start, end)의 형식, start, end는 문장에서의 span 시작과 끝 index
# 이상적으로는 str과 POS값을 모두 고려하여 score를 계산하여야 하지만 일단 POS값을 중요시하여 계산
# POS값에 따른 score matrix를 생각할 수 있고, 이것을 자동학습 할 수 있으면 좋을듯
important_words = [
    '왼쪽', '오른쪽',
    '꼭짓점', '꼭지점',
    '삼각형', '사각형', '오각형', '육각형', '칠각형', '팔각형', '직사각형', '마름모', '평행사변형', '사다리꼴', '원', '지름', '반지름', '길이', '둘레', '가로', '세로', '대각선',
    '정삼각형', '정사각형', '정오각형', '정육각형', '정칠각형', '정팔각형',
    '정사면체', '정육면체', '겉넓이', '넓이']
important_VV = [ '주', '받', '넣']
def match_word_tags(t_tag, q_tag):
    global important_words
    global important_VV
    s = 1.0
    if t_tag[1] == 'PADDING':
        s = -0.000001
    elif t_tag[1] == q_tag[1]: # POS가 같으면 페널티 없음
        if t_tag[0] == q_tag[0]:
            s = 0.0
        elif q_tag[1] == 'VV' and q_tag[0] in important_VV:
            s = 2
        elif q_tag[1] != 'VV' and q_tag[0] in important_words:
            s = 2
        else:
            s = 0.1
    elif t_tag[0] == q_tag[0]:
        s = 0.1
    elif t_tag[1] == 'NONE' or q_tag[1] == 'NONE': # 매칭되는 단어가 없어서 스킵할 경우
        s = 0.4
    elif t_tag[1] == 'WILDCARD':
        if q_tag[1][0] == 'N' or q_tag[1] == 'SL' or q_tag[1] == 'VA+ETM': # WILDCARD는 단어 또는 숫자에 매칭 가능
            s = 0.0
        else:
            s = 1000000.0
    elif t_tag[1] == 'WILDCARD_NUM':
        if q_tag[1] == 'NUMBER':
            s = 0.0
        else:
            s = 1000000.0
    elif t_tag[1] == 'WILDCARD_STR':
        if q_tag[1] != 'NUMBER' and (q_tag[1][0] == 'N' or q_tag[1] == 'SL' or q_tag[1] == 'VA+ETM'):
            s = 0.0
        else:
            s = 1000000.0
    elif t_tag[1].startswith('WILDCARD_OBJECT'):
        sp = t_tag[1].split('_')
        if q_tag[0].startswith(sp[2]) and q_tag[0].endswith(sp[4]):
            s = 0.0
        else:
            s = 1000000.0
    elif t_tag[1] == 'SF' or q_tag[1] == 'SF' or t_tag[1] == 'XSN' or q_tag[1] == 'XSN': # 마침표
        s = 0.1
    # POS가 다른 단어끼리 매칭
    else:
        s = 1.0
    return s

# 문장 비교, 비슷할 수록 낮은 값 리턴
@jit(nopython=True)
def match_to_template_tags_jit(len_t, len_q, score_table, scores, tracks1, tracks2):
    for i1 in range(0, len_t+1):
        for i2 in range(0, len_q+1):
            scores[i1,i2], tracks1[i1][i2], tracks2[i1][i2] = 1000000.0, -1000000, -1000000
            if i1>0 and i2>0 and scores[i1,i2] > scores[i1-1,i2-1] + max(score_table[i1][i2], 0.0): # (template tag - question tag) matched
                scores[i1,i2] = scores[i1-1,i2-1] + max(score_table[i1][i2], 0.0)
                tracks1[i1][i2] = i1-1
                tracks2[i1][i2] = i2-1
            if i2>0 and scores[i1,i2] > scores[i1,i2-1] and score_table[i1][i2] < 0: # template tag is PADDING
                scores[i1,i2] = scores[i1,i2-1]
                tracks1[i1][i2] = i1
                tracks2[i1][i2] = i2-1
            if i2>0 and scores[i1,i2] > scores[i1,i2-1] + score_table[0][i2]: # template tag skipped (matched to NONE)
                scores[i1,i2] = scores[i1,i2-1] + score_table[0][i2]
                tracks1[i1][i2] = i1
                tracks2[i1][i2] = i2-1
            if i1>0 and scores[i1,i2] > scores[i1-1,i2] + max(score_table[i1][0], 0.0): # question tag skipped (matched to NONE)
                scores[i1,i2] = scores[i1-1,i2] + max(score_table[i1][0], 0.0)
                tracks1[i1][i2] = i1-1
                tracks2[i1][i2] = i2
            if i1==0 and i2==0:
                scores[i1,i2], tracks1[i1][i2], tracks2[i1][i2] = 0.0, -1000000, -1000000
    return

# 문장 비교, 비슷할 수록 낮은 값 리턴
def match_to_template_tags(template_tags, question_tags, visualize=False):
    len_t, len_q = len(template_tags), len(question_tags)
    score_table = 1000000.0 * np.ones([len_t+1, len_q+1])

    for i1 in range(0, len(template_tags)+1):
        for i2 in range(0, len(question_tags)+1):
            t_tag = template_tags[i1-1] if i1>0 else ('', 'NONE', -1, -1)
            q_tag = question_tags[i2-1] if i2>0 else ('', 'NONE', -1, -1)
            score_table[i1][i2] = match_word_tags(t_tag, q_tag)
    
    scores = np.zeros([len_t+1, len_q+1])
    tracks1 = np.zeros([len_t+1, len_q+1], dtype=int)
    tracks2 = np.zeros([len_t+1, len_q+1], dtype=int)
    match_to_template_tags_jit(len_t, len_q, score_table, scores, tracks1, tracks2)

    assignments = dict()
    span = [None, None]
    
    correspondence = []
    i1, i2 = len_t, len_q
    while True:
        if i1 == -1000000 or i2 == -1000000:
            break
        if tracks1[i1][i2] == i1 - 1 and tracks2[i1][i2] == i2 - 1: # 실제 tags사이에 매칭이 일어난 경우 (None과 매칭되지 않고) WILDCARD에 대응되는 값을 assignments에 추가
            if template_tags[i1-1][1].startswith('WILDCARD'):
                # if template_tags[i1-1][1].startswith('WILDCARD_OBJECT'):
                    # q_tag = (object_to_num(question_tags[i2-1][0]), question_tags[i2-1]
                # else:
                    # q_tag = question_tags[i2-1]
                name = template_tags[i1-1][0]
                if name not in assignments:
                    assignments[name] = set()
                # assignments[name].add(q_tag)
                assignments[name].add(question_tags[i2-1])
                # assignments[name] = question_tags[i2-1]
        if i1 > 0 and template_tags[i1-1][1] != 'PADDING':
            span[0] = i2-1
            if span[1] == None:
                span[1] = i2
        correspondence.append((i1, i2, scores[i1,i2]))
        i1, i2 = tracks1[i1][i2], tracks2[i1][i2]
    span[0] = max(span[0], 0)

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
            if match[0] > last[0] or template_tags[match[0]-1][1] == 'PADDING':
                left = template_tags[match[0]-1]
            if match[1] > last[1] or question_tags[match[1]-1][1] == 'PADDING':
                right = question_tags[match[1]-1]
            print('{:0.2f}'.format(match[2] - last[2]) + ' (' + left[0] + ' ' + left[1] + ') --- (' + right[0] + ' ' + right[1] + ')')
            last = match
        print('matching score = {:0.2f}'.format(scores[-1][-1]))

    #return scores[-1][-1], assignments, correspondence, span
    return scores[-1][-1] / (len_t + len_q), assignments, correspondence, span

# %%
if __name__== "__main__": # 모듈 단독 테스트
    q = '지현이의 나이는 12살이고 동생은 지현이보다 3살 적습니다. 어머니의 나이는 동생의 나이의 5배보다 1살이 더 많습니다. 어머니의 나이는 몇 살인가요?'
    print(pos_tagging(q))

# %%
if __name__== "__main__": # 모듈 단독 테스트
    score, assignments, correspondence, span = match_to_template_tags(
        # add_paddings(pos_tagging('비행기에 #1명이 타고 있습니다.')),
        # add_paddings(pos_tagging('그 중 #1명이 내렸습니다.')),
        # add_paddings(pos_tagging('비행기에 타고 있는 인원은 얼마입니까?')),
        # pos_tagging('비행기에 351명이 타고 있습니다. 그 중 158명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?'),
        # add_paddings(pos_tagging('4명 중 가장 가벼운 사람은 누구입니까?')),
        # pos_tagging('학생들이 몸무게를 비교하고 있습니다. 석진이는 호석이보다 무겁고 지민이보다 가볍습니다. 남준이는 지민이보다 무겁습니다. 4명 중 가장 가벼운 사람은 누구입니까?'),
        pos_tagging('$1구슬과 $2구슬, $3구슬을 모두 합하면 #1개입니다. $4구슬은 $5구슬보다 #2개가 많고, $6구슬은 #3개일 때 $7구슬은 몇 개입니까?'),
        pos_tagging('빨간 구슬과 노란 구슬, 파란 구슬을 모두 합하면 100개입니다. 노란 구슬은 파란 구슬보다 5개가 많고, 파란 구슬은 23개일 때 빨간 구슬은 몇 개입니까?'),
        visualize=True)
    print(score)
    print(assignments)
    print(span)