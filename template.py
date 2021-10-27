# %%
import re
import numpy as np

import utils
import dataset
import tagging

def find_closest(problem):
    closest_distance, best_pattern, best_assignments = float('inf'), None, None
    dists = []
    for template in dataset.dataset_sentences:
        if len(template['objective']) == 0 or (len(template['objective']) == 1 and template['objective'][0] == ''):
            continue

        if utils.is_pruning(template['question_pruning'], problem['pruning_vector']):
            continue
        if template['question_predefined_patterns']['lists'].keys() != problem['question_predefined_patterns']['lists'].keys():
            continue
        if (template['question_predefined_patterns']['mapping'] == {}) != (problem['question_predefined_patterns']['mapping'] == {}):
            continue
        if (len(template['question_predefined_patterns']['equations']) > 0) != (len(problem['question_predefined_patterns']['equations']) > 0):
            continue
        # distance, assignments = match_to_template(problem['question_preprocessed'], template)
        distance, assignments, _, _ = tagging.match_to_template_tags(template['template_tags'], problem['question_tags'])
        if distance < closest_distance:
            closest_distance, best_pattern, best_assignments = distance, template, assignments

        dists.append([distance, template, assignments])

    problem['closest_k'] = sorted(dists, key=lambda x: x[0])[:10]

    return closest_distance, [(best_pattern, best_assignments)]

def find_phrases(problem):
    len_q = len(problem['question_tags'])
    matches = [[(float('inf'), None, None) for i in range(0, len_q+1)] for j in range(0, len_q+1)]
    for template in dataset.dataset_phrases:
        distance, assignments, _, span = tagging.match_to_template_tags(template['template_tags'], problem['question_tags'])
        distance *= (len(template['template_tags']) + len(problem['question_tags']))
        # distance *= 2 * (span[1]-span[0]) / len(problem['question_tags'])
        if distance < matches[span[0]][span[1]][0]:
            matches[span[0]][span[1]] = (distance, template, assignments)

    scores = np.zeros([len_q+1])
    tracks = np.zeros([len_q+1], dtype=int)

    scores[0] = 0
    tracks[0] = -1
    for e in range(1, len_q+1):
        scores[e] = scores[e-1] + 0.6
        tracks[e] = e-1
        for s in range(0, e):
            if scores[e] > scores[s] + matches[s][e][0]:
                scores[e] = scores[s] + matches[s][e][0]
                tracks[e] = s

    template_assignment_list = []

    pos = len_q
    while pos >= 0 and tracks[pos] >= 0:
        # print(pos)
        # print(scores[pos])
        # print(matches[tracks[pos]][pos])
        if matches[tracks[pos]][pos][0] != float('inf'):
            # print(matches[tracks[pos]][pos][1]['template'], matches[tracks[pos]][pos][2])
            template_assignment_list.append((matches[tracks[pos]][pos][1], matches[tracks[pos]][pos][2]))
        pos = tracks[pos]

    return scores[-1] / (2*len_q), template_assignment_list
    # return closest_distance, best_pattern, best_assignments

# 매칭된 템플릿을 이용하여 statements(lists, equation, code, objective) 구성
# statements는 풀이과정과 답안을 구하기 위한 충분정보가 포함되어야 한다.
def compile_statements(problem, template_assignment_list):
    statements = dict()
    field_names = ['equation', 'code', 'objective']
    for fn in field_names:
        statements[fn] = []
    mapping = dict()
    if problem['question_predefined_patterns']:
        for key in problem['question_predefined_patterns']['lists']:
            statements['code'].append(key + '=' + str(problem['question_predefined_patterns']['lists'][key]))
        if 'mapping' in problem['question_predefined_patterns'] and problem['question_predefined_patterns']['mapping'] != {}:
            statements['code'].append('mapping=' + str(problem['question_predefined_patterns']['mapping']))
            mapping = problem['question_predefined_patterns']['mapping']
        for eq in problem['question_predefined_patterns']['equations']:
            statements['equation'].append(eq)
    for item in reversed(template_assignment_list):
        matched, assignments = item[0], item[1]
        for fn in field_names:
            if 'template_'+fn not in matched:
                continue
            for line in matched['template_'+fn]:
                if 'mapping' in line:
                    for key in mapping:
                        statements[fn].append('{}={}'.format(key, mapping[key]))
                    continue
                for key in assignments:
                    st = list(assignments[key])[0][0] if type(assignments[key]) == set else assignments[key]
                    if key.startswith('@n'):# and not(st[0].isnumeric()):
                        st = utils.object_to_number(st)
                    # line = re.sub(f'({re.escape(key)})($|\D)', assignments[key] + '\\g<2>', line)
                    line = re.sub(f'({re.escape(key)})($|\D)', st + '\\g<2>', line)
                if line != '':
                    statements[fn].append(line)
    return statements

def match(problem):
    problem['pruning_vector'] = utils.pruning_vector(problem['question_preprocessed'])

    problem['question_predefined_patterns'], problem['question_preprocessed'] = utils.extract_predefined_patterns(problem['question_preprocessed'])

    problem['question_tags'] = tagging.pos_tagging(problem['question_preprocessed'])

    print('extracted predefined patterns = ' + str(problem['question_predefined_patterns']))

    print(f'\033[33mbest match sentence\033[0;0m')
    distance, matches = find_closest(problem)
    print(f'{distance} {matches}')

    if len(problem['question']) > 30:
        print(f'\033[33mbest match phrases\033[0;0m')
        distance_phrases, matches_phrases = find_phrases(problem)
        print(f'{distance_phrases} {matches_phrases}')

        if distance_phrases < distance:
            distance = distance_phrases
            matches = matches_phrases

    if matches == None or matches[0][0] == None:
        return None, []

    problem['best_template_distance'] = distance
    problem['best_template'] = [x[0]['template'] for x in matches]
    problem['best_template_assignment'] = [x[1] for x in matches]

    statements = compile_statements(problem, matches)

    print(f'\033[33mstatements = {statements}\033[0;0m')
    problem['statements'] = statements

    return distance, statements

