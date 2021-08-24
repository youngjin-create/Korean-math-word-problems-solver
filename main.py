# %%
# imports

import json
# import re
import time

# import dataset
import nl_regularizer
import nl_to_fr
import fr_solver

# %%
def solve_mwp(question):
    q = nl_regularizer.regularize(question)

    best_answer, best_derivation, best_score = None, [], float('inf')
    # 질문을 여러가지 방법으로 파싱해서 각각의 경우를 풀어본다.
    for fr, score in nl_to_fr.generate(q):
        # fr.print()
        print(fr)
        print(f'parse_score = {score}')
        answer, derivation = fr_solver.solve(fr, time_limit=30)

        if answer != None and derivation:
            # 정답이 나오는 경우가 여러가지가 있으면 가장 파싱이 잘 된 경우의 답을 정답으로 채택
            if score < best_score:
                best_answer, best_derivation, best_score = answer, derivation, score

    if best_answer != None:
        return best_answer, best_derivation
    return '0', ['print(0)'] # if failed, guess answer

# %%
start_time = time.time()

# with open('/home/agc2021/dataset/problemsheet.json') as infile: # 1차 대회
with open('sample.json') as infile: # 샘플 문제
    problemsheet = json.load(infile)

answersheet = dict()
for q_number in problemsheet:
    q = problemsheet[q_number]['question']
    answer, derivation, code = 0, [], ''
    try:
        print(f'\033[92mQ{q_number}: {q}\033[0;0m')
        answer, derivation = solve_mwp(q)
        print(f'\033[33mA: {answer}\033[0;0m')
        code = '\n'.join(derivation)
        print(f'\033[33mderivation:\n{code}\033[0;0m')
    except Exception as e:
        print(e)

    # 한 문제씩 풀 때마다 파일에 기록
    if time.time() - start_time < 3600*2-60:
        code = code.replace('"', "'")
        answersheet[q_number] = { "answer": answer, "equation": code }
        with open('answersheet.json', 'w', encoding='utf-8') as outfile:
            json.dump(answersheet, outfile, ensure_ascii=False, indent=4)

print('execution time = {0:.0f} seconds.'.format(time.time() - start_time))
