# %%
from multiprocessing import Pool
import json
import time
start_time = time.time()

import utils
import rulebased
import template
import math_solver

# %%
def solve_mwp(problem):
    # 문제 전처리
    problem['question_preprocessed'] = utils.preprocess(problem['question'])


    # 여러가지 방법을 이용하여 자연어로 된 문제를 수학적 표현으로 변환

    # distance, statements = template.match(problem, no_predefined=True)
    # distance_pd, statements_pd = template.match(problem)
    # if distance == None or distance_pd < distance:
    #     distance, statements = distance_pd, statements_pd

    distance, statements = template.match(problem)
    if distance != None:
        # 변환된 수학적 표현을 풀어서 python code 형태로 답을 구함
        answer, derivation = math_solver.solve(statements, time_limit_sec=60)
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
            
    # fallback = True
    if fallback:
        distance, statements = rulebased.match(problem)
        rb_answer, rb_derivation = math_solver.solve(statements, time_limit_sec=60)
        if rb_answer != None:
            return rb_answer, rb_derivation

    if answer != None:
        return answer, derivation

    # # 여러가지 방법을 이용하여 자연어로 된 문제를 수학적 표현으로 변환
    # # distance_rb, statements_rb = rulebased.match(problem)
    # # if distance == None:
    # distance, statements = template.match(problem)
    # if distance != None:
    #     # 변환된 수학적 표현을 풀어서 python code 형태로 답을 구함
    #     answer, derivation = math_solver.solve(statements, time_limit_sec=60)
    #     # if answer != None:
    #         # return answer, derivation

    # fallback = False
    # if answer == None or distance > 0.15:
    #     fallback = True
    # else:
    #     expected_type, _ = rulebased.classify_question_type(problem)
    #     answer_type = 'number' if answer[0].isnumeric() else 'string'
    #     if expected_type != None and expected_type != answer_type:
    #         fallback = True

    # if fallback:
    #     distance, statements = rulebased.match(problem)
    #     rb_answer, rb_derivation = math_solver.solve(statements, time_limit_sec=60)
    #     if rb_answer != None:
    #         return rb_answer, rb_derivation

    # if answer != None:
    #     return answer, derivation

    return '0', 'print(0)' # if failed, print 0

    # # 여러가지 방법을 이용하여 자연어로 된 문제를 수학적 표현으로 변환
    # distance, statements = rulebased.match(problem)
    # if distance == None:
    #     distance, statements = template.match(problem)

    # if distance != None:
    #     # 변환된 수학적 표현을 풀어서 python code 형태로 답을 구함
    #     answer, derivation = math_solver.solve(statements, time_limit_sec=10)
    #     if answer != None:
    #         return answer, derivation

    # return '0', 'print(0)' # if failed, print 0

# %%

# with open('/home/agc2021/dataset/problemsheet.json') as infile: # 1차 대회
# with open('sample.json') as infile: # 샘플 문제
# with open('problemsheet.json') as infile: # 테스트 문제
# with open('/home/agc2021/dataset/problemsheet.json', encoding='utf-8-sig') as infile: # 2차 대회
with open('/home/agc2021/dataset/problemsheet_5_00.json', encoding='utf-8-sig') as infile: # 2차 대회
    problemsheet = json.load(infile)
utils.preprocess_sheet(problemsheet)

answersheet = dict()

def one_question(question, q_number=0, right_answer=''):
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

    return dict(q_number=q_number, answer=answer, equation=code)

with Pool(4) as p:
    results = p.starmap(one_question, [(problemsheet[q_number]['question'], q_number) for q_number in problemsheet])
print('elapsed time = {0:.0f} seconds.'.format(time.time() - start_time))

answersheet = {}
for r in results:
    answersheet[r['q_number']] = dict(answer=r['answer'], equation=r['equation'])

# answersheet[q_number] = { "answer": answer, "equation": code }
with open('answersheet_5_00_everdoubling.json', 'w', encoding='utf-8') as outfile:
# with open('answersheet.json', 'w', encoding='utf-8') as outfile:
    json.dump(answersheet, outfile, ensure_ascii=False, indent=4)

print('execution time = {0:.0f} seconds.'.format(time.time() - start_time))

# %%
