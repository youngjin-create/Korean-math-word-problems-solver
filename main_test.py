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
    distance, statements = template.match(problem)
    if distance != None:
        # 변환된 수학적 표현을 풀어서 python code 형태로 답을 구함
        answer, derivation = math_solver.solve(statements, time_limit_sec=15)
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
        rb_answer, rb_derivation = math_solver.solve(statements, time_limit_sec=15)
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

# debug_one_question('한 변이 12/5cm인 정삼각형의 둘레는 몇 cm입니까? ')
# debug_one_question('학생들이 몸무게를 비교하고 있습니다. 석진이는 호석이보다 무겁고 지민이보다 가볍습니다. 남준이는 지민이보다 무겁습니다. 4명 중 가장 가벼운 사람은 누구입니까?')
# debug_one_question('비행기에 351명이 타고 있습니다. 그 중 158명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?')
# debug_one_question('(가)는 삼각뿔의 모서리의 개수, (나)는 사각기둥의 옆면의 개수, (다)는 오각뿔의 밑면의 개수 입니다. 이 중 가장 작은 것은 어느 것입니까?')
# debug_one_question('1,0,4,8 수 카드 4장 중에서 3장을 골라 한 번씩만 사용하여 세 자리 수를 만들려고 합니다. 만들 수 있는 세 자리 수 중에서 두 번째로 큰 수와 두 번째로 작은 수의 차를 구하시오.')
# debug_one_question('민수는 10살입니다. 민수의 누나는 민수보다 3살이 더 많습니다. 엄마의 나이는 누나보다 3배 더 많고, 이모의 나이는 민수보다 3배 더 많습니다. 아빠의 나이는 민수보다 4배 더 많습니다. 두번째로 나이가 많은 사람은 누구입니까?')
# debug_one_question('(가) 그릇에 6l의 물이 들어 있었습니다. (가)에서 들이가 1.2l인 (나) 그릇으로 물을 가득 채워 3번 덜어 냈다면 (가)에 남은 물은 몇 l인가요?')
# debug_one_question('유정이는 가지고 있던 사탕 중에서 언니에게 7개를 주고 동생에게 6개를 주었더니 15개가 남았습니다. 처음에 유정이가 가지고 있던 사탕은 몇 개입니까?')
# debug_one_question('흰색 구슬, 검은색 구슬, 보라색 구슬, 초록색 구슬, 빨간색 구슬이 1개씩 있습니다. 이 구슬 중 서로 다른 2개의 구슬을 고르는 방법은 모두 몇 가지입니까?')
# debug_one_question('6에 어떤 수를 더해야 하는데 잘못하여 어떤 수를 6로 나누었더니 9이 되었습니다. 바르게 계산한 결과를 구하시오.')
# debug_one_question('덧셈식 AB+55=78에서 A에 해당하는 숫자를 쓰시오.')
# debug_one_question('지민이는 주스를 0.7l 마셨습니다. 은지는 지민이보다 1/10l 더 적게 마셨습니다. 윤기는 4/5l 마셨고, 유나는 지민이보다 0.2l 더 많이 마셨습니다. 주스를 가장 많이 마신 사람은 누구입니까?')
# debug_one_question('두 자리 수의 덧셈식 A4+2B=69에서 A+B에 해당하는 숫자를 쓰시오.')
# debug_one_question('A, B는 한 자리 수입니다. A는 2보다 4 큰 수이고, B보다 3 작은 수는 1입니다. A와 B의 합을 구하시오.')
# debug_one_question('친구들이 마리오 게임을 하고 있습니다. 9라운드 현재 호석이는 120점, 석진이는 100점, 정섭이는 90점을 얻었습니다. 마지막 10라운드에서 정섭이는 문제를 맞춰 10점을 얻었고, 보물카드에서 뽑은 카드에서 자신을 제외한 나머지 학생 -30점 카드가 나왔습니다. 10라운드가 끝났을 때 가장 높은 점수를 얻은 친구는 누구입니까?')
# debug_one_question('재석이의 모둠 학생은 재석, 수현, 은지, 민기입니다. 재석이의 키는 수현이보다 작고 은지보다 큽니다. 수현이는 은지보다 키가 크고 민기보다는 키가 작습니다. 재석이의 키는 모둠에서 몇번째로 작은가요?')
# debug_one_question('우리 반 대표로 가을 운동회에 나갈 수 있는 계주 선수는 3명입니다. 우리 반에서 달리기 실력이 좋은 정민, 진희, 기영, 유영, 은비가 예선을 치뤘더니 기영, 진희, 유영, 은비, 정민 순으로 도착하였습니다. 기영, 진희와 함께 반 대표로 나갈 수 있는 친구는 누구일까요?')
# debug_one_question('민지는 한 변의 길이가 12cm인 2cm 정사각형의 철사, 규영이는 한 변의 길이가 13cm인 정삼각형의 철사, 우진이는 한 변의 길이가 8cm인 정팔각형의 철사를 가지고 있다고 할 때, 가장 긴 철사를 가지고 있는 사람은 누구일까요?')
# debug_one_question('양팔저울로 사과와 배의 무게를 측정했더니 사과 쪽으로 저울이 기울었습니다. 사과와 감을 저울에 올렸더니 사과 쪽으로 저울이 기울었습니다. 사과, 배, 감 중 가장 무거운 과일은 무엇인가요?')
# debug_one_question('병진, 석우, 영수가 쪽지시험을 봤습니다. 10개의 문제 중 병진이는 영수는 3개 틀렸고 석우는 8개를 맞추었습니다. 누가 시험을 가장 잘 봤습니까?')
# debug_one_question('A원은 지름이 4cm, B원은 반지름이 3cm 입니다. A,B중 어느 원이 더 큰가요?')
# debug_one_question('어떤 수 (가)는 235962A794, (나)는 235B705012, (다)는 23598C7860입니다. A, B, C 안에는 0부터 9까지 어느 숫자를 넣어도 될 때, (가)~(다) 중에서 가장 큰 수는 무엇인지 기호를 쓰세요.')
# debug_one_question('지은이는 포도 원액 24 mL를 넣어 포도주스 60 mL를 만들었고 은성이는 포도 원액 27 mL를 넣어 포도주스 90 mL를 만들었습니다. 누가 만든 포도주스가 더 진할까요?')
# debug_one_question('수학여행을 갈 때 기차를 타는 것에 찬성하는 학생 수를 조사하였습니다. A반은 25명 학생중 13명이 찬성, B반은 24명 학생 중 12명이 찬성했습니다. 두 반 중 찬성률이 더 높은 반은 어느 반인가요?')
debug_one_question('구슬을 6명에게 똑같이 나누어 주어야 할 것을 잘못하여 4명에게 똑같이 나누어 주었더니 한 사람당 19개씩이고 3개가 남았습니다. 이 구슬을 6명에게 될 수 있는 대로 많이 똑같이 나누어 주면 한 사람당 A개씩 가지고 B개가 남습니다. A와 B의 합을 구하세요.')
# %%
