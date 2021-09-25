
import re
import wordsim
import utils
import dataset

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

def find_template(question):
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
            equation.append(line)
    code = []
    if 'template_code' in q:
        for line in q['template_code']:
            for idx, v in enumerate(values):
                line = re.compile(f'\\bvar{idx}\\b').sub(v, line)
            code.append(line)

    print('equation substituted')
    print(equation)
    print('code substituted')
    print(code)

    return distance, dict(equation=equation, code=code)
