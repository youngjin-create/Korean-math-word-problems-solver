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
        distance, statements = template.match(problem)

    if distance != None:
        # 변환된 수학적 표현을 풀어서 python code 형태로 답을 구함
        answer, derivation = math_solver.solve(statements, time_limit_sec=999999)
        if answer != None:
            return answer, derivation

    return '0', ['print(0)'] # if failed, print 0

# %%
csvfile = open('test_results.csv', 'w', newline='')
csvfile.close()

def debug_one_question(question, q_number=0, right_answer=''):
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
    if 'closest_k' in problem:
        for k in problem['closest_k']:
            closest_k += k[1]['id'] + ' ({:.2f}) '.format(k[0]) + k[1]['template'] + '\n'
    result_row = [problem['id'], problem['question'], problem['question_preprocessed'], problem['question_predefined_patterns'],
        problem['best_template_distance'], problem['best_template'], problem['best_template_assignment'], problem['statements'], closest_k,
        code, answer, right_answer, '{0:.2f}'.format(time.time() - problem_time)]

    with open('test_results.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"')
        writer.writerow(result_row)

    return result_row

def f(arg1, arg2):
    print(arg1)
    print(arg2)
    return arg1 + arg2

def debug_all_questions():
    test = dataset.dataset_google_sentences_teacher#[:40]
    with Pool(32) as p:
        results = p.starmap(debug_one_question, [(q['question_original'], q['id'], q['answer']) for q in test])
    print('elapsed time = {0:.0f} seconds.'.format(time.time() - start_time))

    dataset_google_sheets.save_results(datetime.now().strftime("%m/%d %H;%M;%S"), results)

    return results

results = debug_all_questions()

# debug_one_question('한 변이 12/5cm인 정삼각형의 둘레는 몇 cm입니까? ')
# debug_one_question('학생들이 몸무게를 비교하고 있습니다. 석진이는 호석이보다 무겁고 지민이보다 가볍습니다. 남준이는 지민이보다 무겁습니다. 4명 중 가장 가벼운 사람은 누구입니까?')
# debug_one_question('비행기에 351명이 타고 있습니다. 그 중 158명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?')
# debug_one_question('(가)는 삼각뿔의 모서리의 개수, (나)는 사각기둥의 옆면의 개수, (다)는 오각뿔의 밑면의 개수 입니다. 이 중 가장 작은 것은 어느 것입니까?')
# debug_one_question('1,0,4,8 수 카드 4장 중에서 3장을 골라 한 번씩만 사용하여 세 자리 수를 만들려고 합니다. 만들 수 있는 세 자리 수 중에서 두 번째로 큰 수와 두 번째로 작은 수의 차를 구하시오.')
# debug_one_question('민수는 10살입니다. 민수의 누나는 민수보다 3살이 더 많습니다. 엄마의 나이는 누나보다 3배 더 많고, 이모의 나이는 민수보다 3배 더 많습니다. 아빠의 나이는 민수보다 4배 더 많습니다. 두번째로 나이가 많은 사람은 누구입니까?')
# debug_one_question('(가) 그릇에 6l의 물이 들어 있었습니다. (가)에서 들이가 1.2l인 (나) 그릇으로 물을 가득 채워 3번 덜어 냈다면 (가)에 남은 물은 몇 l인가요?')

# %%
