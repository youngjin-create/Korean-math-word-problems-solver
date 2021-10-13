# %%
import json
import csv
import time
start_time = time.time()

import utils
import template
import rulebased
import dataset
import math_solver

# %%
def solve_mwp(problem):
    # 문제 전처리
    problem['question_preprocessed'] = utils.preprocess(problem['question'])

    # 여러가지 방법을 이용하여 자연어로 된 문제를 수학적 표현으로 변환
    distance, statements = rulebased.match(problem)
    if distance == None:
        distance, statements = template.find_template(problem)

    # 변환된 수학적 표현을 풀어서 python code 형태로 답을 구함
    # answer, derivation = math_solver.solve(statements, time_limit_sec=99999)

    # if answer != None:
        # return answer, derivation
    return '0', ['print(0)'] # if failed, print 0

# %%
csvfile = open('debugsheet.csv', 'w', newline='')
csvfile.close()

def debug_one_question(question, q_number=0):
    global csvfile
    problem_time = time.time()

    problem = { "question": question, "id": q_number }
    answer, derivation, code = 0, [], ''
    # try:
    print(f'\033[92mQ{q_number}: {question}\033[0;0m')
    answer, derivation = solve_mwp(problem)
    if type(derivation) == list:
        code = '\n'.join(derivation)
    else:
        code = derivation

    print(f'\033[33mcode:\n{code}\033[0;0m')
    print(f'\033[33mA: {answer}\033[0;0m')
    # except Exception as e:
    #     print(e)

    with open('debugsheet.csv', 'a', newline='') as csvfile:
        closest_k = ''
        for k in problem['closest_k']:
            closest_k += k[1]['id'] + ' ({:.2f}) '.format(k[0]) + k[1]['template'] + '\n'
        writer = csv.writer(csvfile, delimiter=',', quotechar='"')
        writer.writerow([problem['question'], problem['question_preprocessed'], problem['extracted_lists'], problem['extracted_equations'],
            problem['best_template_distance'], problem['best_template']['template'], problem['best_template_assignment'], problem['statements'],
            problem['id'], closest_k,
            '{0:.0f}'.format(time.time() - problem_time)])

def debug_all_questions():
    for q_number, q in enumerate(dataset.dataset_csv):
        # if q_number % 10 != 0:
            # continue
        debug_one_question(q['question'], q['id'])
        print('elapsed time = {0:.0f} seconds.'.format(time.time() - start_time))

debug_all_questions()
# debug_one_question('A는 B보다 먼저 교실에 도착했습니다. C는 A보다 먼저 교실에 도착했습니다. B는 D보다 늦게 교실에 도착했습니다. D는 A보다 늦게 교실에 도착했습니다. 교실에 가장 빨리 온 것은 누구입니까?')
# debug_one_question('비행기에 351명이 타고 있습니다. 그 중 158명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?')
# debug_one_question('상자에는 사과가 10개 있습니다. 이 중에 5개를 먹었을 때, 남아있는 사과는 몇 개입니까?') # 하율이는 팽이가 12개 있습니다. 친구들에게 7개를 빌려주려고 합니다. 빌려주고 남는 팽이는 몇 개일까요?