
import re
import wordsim
import utils
import dataset
# from node import Node

# %%
def get_sentences(question):
    end_of_phrases = '[^0-9a-zA-Z\(\)][\.\?][ ]'
    phrases = []
    pos = 0
    for x in re.compile(end_of_phrases).finditer(question):
        phrases.append(question[pos:x.span()[1]])
        pos = x.span()[1]
    if pos != len(question):
        phrases.append(question[pos:])
    return [x.strip() for x in phrases]

def get_phrases(question):
    # end_of_phrases = '.+면,|.+며,|.+고,|.+때,|.+다\. |.+오\.|.+\. |.+$'
    # end_of_phrases = '.+?면,|.+?며,|.+?고,|.+?때,|.+?다\.|.+?오\.|.+?\. |.+?$'
    end_of_phrases = '[^0-9a-zA-Z\(\)][\,\.\?][ ]'
    phrases = []
    pos = 0
    for x in re.compile(end_of_phrases).finditer(question):
        phrases.append(question[pos:x.span()[1]])
        pos = x.span()[1]
    if pos != len(question):
        phrases.append(question[pos:])
    return [x.strip() for x in phrases]

# %%

def word_similarity(w1, w2): # w1 = template word, w2 = question word
    t = re.compile('(var[0-9]+)(\w+)').findall(w1)
    # var = re.compile('(var[0-9]+)(*)').findall(w1)
    if t: # template 단어가 wildcard를 포함하고 있으면
        ending = t[0][1]
        if w2[-len(ending):] == ending:
            return 0, w2[:-len(ending)]
        return 1, w2
    else: # 단순 단어 비교
        if w1 == w2:
            return 0, None
        return 1, None
    return

# # 문장 비교, 비슷할 수록 낮은 값 리턴
# def match_to_template(t, s, v): # template, question sentence, values
#     # v = [''] * len(v)
#     w1, w2 = t.split(' '), s.split(' ')

#     varnum = [None] * len(w1)
#     for i in range(0, len(w1)):
#         var = re.compile('var[0-9]+').findall(w1[i])
#         varnum[i] = int(var[0][3:])
#         # print(var)

#     beams = 5
#     scores = [[[float('inf')] * beams for i in range(len(w2+1))] for j in range(len(w1+1))]
#     scores[0][0] = [0] * beams
#     assigns = [[[[''] * len(v)] * beams for i in range(len(w2+1))] for j in range(len(w1+1))]

#     for i1 in range(0, len(w1)):
#         for i2 in range(0, len(w2)):
#             if varnum[i1] != None:
#                 s, a = word_similarity(w1[i1], w2[i2])
#                 for k in range(0, beams):
#                     if a is consistent with assigns[i1][i2]
#                     scores[i1+1][i2+1] = scores[i1][i2] + s
#             else:
#                 s, a = word_similarity(w1[i1], w2[i2])


#             # word_similarity(w1[i1], w2[i2])
#             table[i1][i2] 


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

# 문장 비교, 비슷할 수록 낮은 값 리턴
def match_to_template(t, s, v): # template, question sentence, values
    skip_penalty = 0.6

    # v = [''] * len(v)
    w1, w2 = t.split(' '), s.split(' ')

    varnum = [None] * len(w1)
    for i in range(0, len(w1)):
        var = re.compile('var[0-9]+').findall(w1[i])
        if var:
            varnum[i] = int(var[0][3:])
        # print(var)

    score_table = [[float('inf') for i in range(len(w2))] for j in range(len(w1))]
    assign_table = [['' for i in range(len(w2))] for j in range(len(w1))]
    for i1 in range(0, len(w1)):
        for i2 in range(0, len(w2)):
            score_table[i1][i2], assign_table[i1][i2] = wordsim.word_distance_template(w1[i1], w2[i2])

    scores = [[float('inf') for i in range(len(w2)+1)] for j in range(len(w1)+1)]
    for i in range(len(w2)+1):
        scores[0][i] = i * skip_penalty
    scores[0][0] = 0
    for j in range(1, len(w1)+1):
        if varnum[j-1] != None:
            scores[j][0] = float('inf')
        else:
            scores[j][0] = scores[j-1][0] + skip_penalty
    tracks = [[(None, None) for i in range(len(w2)+1)] for j in range(len(w1)+1)]
    # assigns = [['' for i in range(len(w2)+1)] for j in range(len(w1)+1)]

    for i1 in range(0, len(w1)):
        for i2 in range(0, len(w2)):
            # score = None
            # score_add, assign = word_similarity(w1[i1], w2[i2])
            # score_add, assign = score_table[i1][i2], assign_table[i1][i2]#wordsim.word_distance_template(w1[i1], w2[i2])
            if varnum[i1] != None:
                scores[i1+1][i2+1] = scores[i1][i2] + score_table[i1][i2]
                tracks[i1+1][i2+1] = (i1, i2)
                # assigns[i1+1][i2+1] = assign
            else:
                scores[i1+1][i2+1] = scores[i1][i2] + score_table[i1][i2]
                tracks[i1+1][i2+1] = (i1, i2)
                if scores[i1+1][i2+1] > scores[i1+1][i2] + skip_penalty:
                    scores[i1+1][i2+1] = scores[i1+1][i2] + skip_penalty
                    tracks[i1+1][i2+1] = (i1+1, i2)
                if scores[i1+1][i2+1] > scores[i1][i2+1] + skip_penalty:
                    scores[i1+1][i2+1] = scores[i1][i2+1] + skip_penalty
                    tracks[i1+1][i2+1] = (i1, i2+1)
            # scores[i1+1][i2+1] = score

    assignments = [set() for i in range(len(v))]
    def backtrack(i1, i2):
        if i1 < 0 or i2 < 0:
            return
        if varnum[i1] != None and assign_table[i1][i2]:
            assignments[varnum[i1]].add(assign_table[i1][i2])
        backtrack(tracks[i1+1][i2+1][0]-1, tracks[i1+1][i2+1][1]-1)
    backtrack(len(w1)-1, len(w2)-1)

    return scores[len(w1)][len(w2)], assignments
    # print(score(len(w1)-1, len(w2)-1))
    # print(table)
    # print(w1)
    # print(w2)
    # return score(len(w1)-1, len(w2)-1) # / (len(w1) + len(w2))

def find_closest(question):
    closest_distance, best_pattern, best_assignments = float('inf'), None, None
    for p in dataset.dataset_json:
        distance, assignments = match_to_template(p['template'], question, p['template_values'])
        if distance < closest_distance:
            closest_distance, best_pattern, best_assignments = distance, p, assignments
    # if pattern:
        # print(pattern)
    return closest_distance, best_pattern, best_assignments

# %%
# 문장에서 가능한 파싱을 계속 yield해주는 함수
# 일단 단순하게 몇 가지 경우로 구현
def generate(question):

    # 1. 문장 전체로 매칭
    distance, q, assignments = find_closest(question)
    print(f'best matching distance = {distance}')
    # print(distance)
    print(q)
    print(assignments)
    values = q['template_values']
    for idx, valueset in enumerate(assignments):
        if len(valueset) > 0:
            values[idx] = list(valueset)[0]
    print(values)

    equation = []
    if 'template_equation' in q:
        for line in q['template_equation']:
            for idx, v in enumerate(values):
                line = re.compile(f'\\bvar{idx}\\b').sub(v, line)
            # for idx, strset in enumerate(assignments):
                # eq = re.compile(f'\\bvar{idx}\\b').sub(list(strset)[0], eq)
                # eq = re.compile('\\b' + str + '\\b').sub(f'var{idx}', eq)
                # eq = re.sub(r'\b' + str + r'\b', f'<{idx}>', eq)
            equation.append(line)
    code = []
    if 'template_code' in q:
        for line in q['template_code']:
            for idx, v in enumerate(values):
                line = re.compile(f'\\bvar{idx}\\b').sub(v, line)
            # for idx, strset in enumerate(assignments):
                # if len(strset) > 0:
                    # eq = re.compile(f'\\bvar{idx}\\b').sub(list(strset)[0], eq)
                # eq = re.compile('\\b' + str + '\\b').sub(f'var{idx}', eq)
                # eq = re.sub(r'\b' + str + r'\b', f'<{idx}>', eq)
            code.append(line)

    print('equation substituted')
    print(equation)
    print('code substituted')
    print(code)
    # literals = utils.find_literals(question)

    # yield 
    # root = Node(question)
    # root.match_predefined()
    # _, matching_score = root.do_pattern_match()
    # yield root, matching_score

    yield distance, equation, code
    return

    # 2. 일단 문장별로 나누고 문장을 쪼개서 매칭
    matching_score = 0
    root = Node(question)
    for sentence in get_sentences(question):
        best_nodes, best_score = [], float('inf')

        # sentence 전체로 매칭
        whole = Node(sentence)
        whole.match_predefined()
        pattern, score = whole.do_pattern_match()
        # print(f'whole {sentence} {score}')
        if pattern:
            best_nodes, best_score = [whole], score

        # sentence를 나누어서 매칭
        words = sentence.split(' ')
        for i in range(1, len(words)):
            left = Node(' '.join(words[:i]))
            left.match_predefined()
            _, score_left = left.do_pattern_match()
            right = Node(' '.join(words[i:]))
            right.match_predefined()
            _, score_right = right.do_pattern_match()
            if score_left + score_right < best_score:
                best_nodes, best_score = [left, right], score_left + score_right

        # 최적의 매칭을 파싱 트리에 추가
        for node in best_nodes:
            root.children.append([None, 0, 0, node])
        matching_score = matching_score + best_score

    yield root, matching_score

    # 3. 일단 phrase별로 나누고 그 안에서 다시 쪼개서 매칭
    matching_score = 0
    root = Node(question)
    for phrase in get_phrases(question):
        best_nodes, best_score = [], float('inf')

        # phrase 전체로 매칭
        whole = Node(phrase)
        whole.match_predefined()
        pattern, score = whole.do_pattern_match()
        if pattern:
            best_nodes, best_score = [whole], score

        # phrase를 나누어서 매칭
        words = phrase.split(' ')
        for i in range(1, len(words)):
            left = Node(' '.join(words[:i]))
            left.match_predefined()
            _, score_left = left.do_pattern_match()
            right = Node(' '.join(words[i:]))
            right.match_predefined()
            _, score_right = right.do_pattern_match()
            if score_left + score_right < best_score:
                best_nodes, best_score = [left, right], score_left + score_right

        # 최적의 매칭을 파싱 트리에 추가
        for node in best_nodes:
            root.children.append([None, 0, 0, node])
        matching_score = matching_score + best_score

    yield root, matching_score
