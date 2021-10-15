# %%
from multiprocessing import Pool
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
    answer, derivation = math_solver.solve(statements, time_limit_sec=99999)

    if answer != None:
        return answer, derivation
    return '0', ['print(0)'] # if failed, print 0

# %%
csvfile = open('test_results.csv', 'w', newline='')
csvfile.close()

def debug_one_question(question, q_number=0):
    global csvfile
    problem_time = time.time()

    problem = { "question": question, "id": q_number }
    answer, derivation, code = 0, [], ''
    # try:
    print(f'\033[92mQuestion {q_number}: {question}\033[0;0m')
    answer, derivation = solve_mwp(problem)
    if type(derivation) == list:
        code = '\n'.join(derivation)
    else:
        code = derivation

    print(f'\033[33mcode:\n{code}\033[0;0m')
    print(f'\033[33mA: {answer}\033[0;0m')
    # except Exception as e:
    #     print(e)

    with open('test_results.csv', 'a', newline='') as csvfile:
        closest_k = ''
        for k in problem['closest_k']:
            closest_k += k[1]['id'] + ' ({:.2f}) '.format(k[0]) + k[1]['template'] + '\n'
        writer = csv.writer(csvfile, delimiter=',', quotechar='"')
        writer.writerow([problem['id'], problem['question'], problem['question_preprocessed'], problem['extracted_lists'], problem['extracted_equations'],
            problem['best_template_distance'], problem['best_template']['template'], problem['best_template_assignment'], problem['statements'], closest_k,
            '{0:.0f}'.format(time.time() - problem_time)])

def f(arg1, arg2):
    print(arg1)
    print(arg2)
    return arg1 + arg2

def debug_all_questions():
    # with Pool(4) as p:
    #     print(p.starmap(f, [(1, 2), (2, 3), (3, 4)]))
    # return
    # dataset.dataset_csv = dataset.dataset_csv[:40]
    with Pool(32) as p:
        results = p.starmap(debug_one_question, [(q['question_original'], q['id']) for q in dataset.dataset_csv])
    print('elapsed time = {0:.0f} seconds.'.format(time.time() - start_time))

    # for q_number, q in enumerate(dataset.dataset_csv):
    #     # if q_number % 10 != 0:
    #         # continue
    #     debug_one_question(q['question_original'], q['id'])
    #     print('elapsed time = {0:.0f} seconds.'.format(time.time() - start_time))

# debug_all_questions()
# debug_one_question('A는 B보다 먼저 교실에 도착했습니다. C는 A보다 먼저 교실에 도착했습니다. B는 D보다 늦게 교실에 도착했습니다. D는 A보다 늦게 교실에 도착했습니다. 교실에 가장 빨리 온 것은 누구입니까?')
# debug_one_question('비행기에 351명이 타고 있습니다. 그 중 158명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?')
# debug_one_question('상자에는 사과가 10개 있습니다. 이 중에 5개를 먹었을 때, 남아있는 사과는 몇 개입니까?') # 하율이는 팽이가 12개 있습니다. 친구들에게 7개를 빌려주려고 합니다. 빌려주고 남는 팽이는 몇 개일까요?
# debug_one_question('사과, 배, 복숭아, 감, 귤이 각각 1개씩 있습니다. 이 중 3개를 택하여 한 개의 접시에 담으려고 합니다. 감과 귤을 함께 담지 않는 방법은 모두 몇 가지입니까?')
# debug_one_question('파란 컵, 빨간 컵, 노란 컵이 각각 한 개씩 있습니다. 컵 3개를 한 줄로 놓는 방법은 모두 몇 가지입니까?')
# debug_one_question('4개의 수 53, 98, 69, 84가 있습니다. 그 중에서 가장 큰 수와 가장 작은 수의 차는 얼마입니까?')
# debug_one_question('형과 나의 나이의 합은 37살입니다. 형이 나보다 3살 많다면 나의 나이는 얼마입니까?')
# debug_one_question('색종이를 4명에게 똑같이 나누어 주어야 할 것을 잘못하여 5명에게 똑같이 나누어 주었더니 한 사람당 15장씩 주고 2장이 남았습니다. 이 색종이를 4명에게 똑같이 나누어 주면 한 사람당 최대한 몇 장씩 가지게 됩니까?')
# debug_one_question('비행기에 351명이 타고 있습니다. 그 중 158명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?')
debug_one_question('박세리는 한유미보다 나이가 많고, 한유미는 남현희보다 어리고 정유인보다는 나이가 많습니다. 네 명 중 가장 나이가 어린 사람은 누구입니까?')
# %%
