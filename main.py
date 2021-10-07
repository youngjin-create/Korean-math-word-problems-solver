# %%
import json
import time
start_time = time.time()

import utils
import template
import rulebased
import math_solver
# import fr_solver

# %%
def solve_mwp(question):
    # 문제 전처리
    q = utils.preprocess(question)

    # 여러가지 방법을 이용하여 자연어로 된 문제를 수학적 표현으로 변환
    distance, statements = rulebased.match(q)
    if distance == None:
        distance, statements = template.find_template(q)

    # 변환된 수학적 표현을 풀어서 python code 형태로 답을 구함
    answer, derivation = math_solver.solve(statements, time_limit_sec=30)

    if answer != None:
        return answer, derivation
    return '0', ['print(0)'] # if failed, print 0

# %%

# with open('/home/agc2021/dataset/problemsheet.json') as infile: # 1차 대회
# with open('sample.json') as infile: # 샘플 문제
    # problemsheet = json.load(infile)
with open('problemsheet.json') as infile: # 테스트 문제
    problemsheet = json.load(infile)

answersheet = dict()
for q_number in problemsheet:
    print('elapsed time = {0:.0f} seconds.'.format(time.time() - start_time))

    q = problemsheet[q_number]['question']
    answer, derivation, code = 0, [], ''
    # try:
    print(f'\033[92mQ{q_number}: {q}\033[0;0m')
    answer, derivation = solve_mwp(q)
    print(f'\033[33mA: {answer}\033[0;0m')
    code = '\n'.join(derivation)
    print(f'\033[33mderivation:\n{code}\033[0;0m')
    # except Exception as e:
    #     print(e)

    # 한 문제씩 풀 때마다 파일에 기록
    if time.time() - start_time < 3600*2-60:
        code = code.replace('"', "'")
        answersheet[q_number] = { "answer": answer, "equation": code }
        with open('answersheet.json', 'w', encoding='utf-8') as outfile:
            json.dump(answersheet, outfile, ensure_ascii=False, indent=4)

print('execution time = {0:.0f} seconds.'.format(time.time() - start_time))
