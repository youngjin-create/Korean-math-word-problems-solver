# %%
from multiprocessing import Pool
import csv
import re
import time
start_time = time.time()
from datetime import datetime

import utils
import template
import rulebased
import dataset
import math_solver
import dataset_google_sheets

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

    closest_k = ''
    for k in problem['closest_k']:
        closest_k += k[1]['id'] + ' ({:.2f}) '.format(k[0]) + k[1]['template'] + '\n'
    result_row = [problem['id'], problem['question'], problem['question_preprocessed'], problem['extracted_lists'], problem['extracted_mapping'], problem['extracted_equations'],
        problem['best_template_distance'], problem['best_template']['template'], problem['best_template_assignment'], problem['statements'], closest_k,
        code, answer, '{0:.0f}'.format(time.time() - problem_time)]

    with open('test_results.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"')
        writer.writerow(result_row)

    return result_row

def f(arg1, arg2):
    print(arg1)
    print(arg2)
    return arg1 + arg2

def debug_all_questions():
    # with Pool(4) as p:
    #     print(p.starmap(f, [(1, 2), (2, 3), (3, 4)]))
    # return
    test = dataset.dataset_google_drive#[:40]
    with Pool(32) as p:
        results = p.starmap(debug_one_question, [(q['question_original'], q['id']) for q in test])
    print('elapsed time = {0:.0f} seconds.'.format(time.time() - start_time))

    dataset_google_sheets.save_results(datetime.now().strftime("%m/%d %H;%M;%S"), results)

    return results

    # for q_number, q in enumerate(dataset.dataset_csv):
    #     # if q_number % 10 != 0:
    #         # continue
    #     debug_one_question(q['question_original'], q['id'])
    #     print('elapsed time = {0:.0f} seconds.'.format(time.time() - start_time))

# results = debug_all_questions()

debug_one_question('50m 달리기 시합에서 상희는 7초, 민아는 13초, 선호는 5초를 기록했습니다. 민아는 몇 등인가요?')
# %%
