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
    # distance_rb, statements_rb = rulebased.match(problem)
    # if distance == None:
    distance, statements = template.match(problem, no_predefined=True)
    distance_pd, statements_pd = template.match(problem)
    if distance == None or distance_pd < distance:
        distance, statements = distance_pd, statements_pd

    if distance != None:
        # 변환된 수학적 표현을 풀어서 python code 형태로 답을 구함
        answer, derivation = math_solver.solve(statements, time_limit_sec=20)
        # if answer != None:
            # return answer, derivation

    fallback = False
    if answer == None or distance > 0.15:
        fallback = True
    else:
        expected_type, _ = rulebased.classify_question_type(problem)
        answer_type = 'number' if answer[0].isnumeric() else 'string'
        if expected_type != None and expected_type != answer_type:
            fallback = True

    if fallback:
        distance, statements = rulebased.match(problem)
        rb_answer, rb_derivation = math_solver.solve(statements, time_limit_sec=20)
        if rb_answer != None:
            return rb_answer, rb_derivation

    if answer != None:
        return answer, derivation

    return '0', 'print(0)' # if failed, print 0

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
            closest_k += k[1]['id'] + ' ({:.4f}) '.format(k[0]) + k[1]['template'] + '\n'
    tags = [(x[0], x[1], x[4], x[5], x[6]) for x in problem['question_tags']]
    result_row = [problem['id'], problem['question'], tags, #problem['question_preprocessed'],
        problem['question_predefined_patterns'],
        problem['best_template_distance'], problem['best_template'], problem['best_template_assignment'], problem['statements'], closest_k,
        code, answer, right_answer, '{0:.2f}'.format(time.time() - problem_time)]

    # with open('test_results.csv', 'a', newline='') as csvfile:
    #     writer = csv.writer(csvfile, delimiter=',', quotechar='"')
    #     writer.writerow(result_row)

    return result_row

def debug_all_questions():
    # test = dataset.dataset_google_sentences_teacher#[:40]
    test = dataset.dataset_sentences
    with Pool(32) as p:
        results = p.starmap(debug_one_question, [(q['question_original'], q['id'], q['answer']) for q in test])
    print('elapsed time = {0:.0f} seconds.'.format(time.time() - start_time))

    dataset_google_sheets.save_results(datetime.now().strftime("%m/%d %H;%M;%S"), results)

    return results

# results = debug_all_questions()

debug_one_question('295 * A < 1000 일 때, A에 들어갈 수 있는 자연수 중에서 가장 큰 수는 얼마일까요?')
# debug_one_question('윤기는 네 자리 수와 두 자리 수의 뺄셈을 하려 합니다. 윤기는 네 자리 수의 일의 자리 숫자 9를 6으로 잘못 보았고, 두 자리 수의 십의 자리 숫자와 일의 자리 숫자를 바꾸어 75라고 잘못 보았습니다. 윤기가 구한 차는 1821 일 때, 바르게 계산한 결과를 구하시오.')
