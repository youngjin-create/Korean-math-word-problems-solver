# %%
# 풀이 과정에 해당하는 python code가 제한 시간안에 종료되지 않아서 다음 문제를 못 풀게 되는 상황을 방지하기 위하여
# 시간 제한을 둘 수 있도록 필요한 모듈
import signal
from contextlib import contextmanager

class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

# %%
# def compute(scope, unknowns):
#     pass

# 실제 산술 연산을 해서 답을 구하는 함수:
# 문제에서 뽑아낸 statements가 입력으로 주어지면,
# 이를 실행가능한 python 코드로 변환한 다음 exec로 실행해서 답을 구하고, 답과 코드를 반환한다.
def do_math(statements):
    print('statements:')
    print(statements)

    # scope = dict()
    # # reference resolution
    # scope['it'] = None
    # # world knowledge
    values = dict()
    # scope['people'] = set()
    # scope['subjects'] = set()
    # scope['indicators'] = set()
    # scope['objects'] = set()
    # mathematics
    inits = []
    assignments = []
    conditions = []
    thens = []
    # scope['solutions'] = set()
    objective = ''

    for s in statements:
        # do actions according to the type of s
        if s.startswith('init:'):
            # print(s[len('init:'):])
            # exec(s[len('init:'):], scope, scope)
            inits.append(s[len('init:'):])
        elif s.startswith('values:'):
            values[s[len('values:'):]] = None
        elif s.startswith('condition:'):
            conditions.append(s[len('condition:'):])
        elif s.startswith('then:'):
            thens.append(s[len('then:'):])
        elif s.startswith('objective:'):
            objective = s[len('objective:'):]
        else:
            assignments.append(s)

    # print('inits:')
    # print(inits)
    # print('values:')
    # print(values)
    # print('assignments:')
    # print(assignments)
    # print('conditions:')
    # print(conditions)
    # print('then:')
    # print(thens)
    # print('objective:')
    # print(objective)

    if not objective:
        return None, []

        
    answer, derivation = None, []

    # derivation.append('import math')
    derivation.append('it, values, people, indicators, solutions, reg = [], dict(), set(), set(), set(), lambda x: x')

    for init in inits:
        derivation.append(init)
    if len(values) >= 1:
        range_max = int(pow(10, 5/len(values)))
        derivation.append(f'range_max = {range_max}')
        derivation.append('for numr in range(-1000,100000):')
        derivation.append('    if numr < 0:')
        for key in values:
            derivation.append(f'        values["{key}"] = -numr')
        derivation.append('    else:')

        for key in values:
            derivation.append(f'        values["{key}"], numr = numr % range_max, numr // range_max')
    else:
        derivation.append('for dummy in range(1):')
    for op in assignments:
        derivation.append('    ' + op)
    tabs = 1
    for cond in conditions:
        derivation.append('    '*tabs + f'if {cond}:')
        tabs += 1
    for op in thens:
        derivation.append('    '*tabs + op)
    if not thens:
        derivation.append('    '*tabs + 'break')
    # derivation.append('print(' + objective + ')')

    # print(derivation)
    # for line in derivation:
    #     print(line)

    #     if 'math' in line:
    #         derivation.insert(0, 'import math')
    #         print('import math')
    #         break
    # for line in derivation:
    #     if 'itertools' in line:
    #         derivation.insert(0, 'import itertools')
    #         break

    # print('\n'.join(derivation))
    env = dict()
    try:
        exec('\n'.join(derivation), env, env)
        # print(objective)
        answer = eval(objective, env, env)
        if answer != None:
            if type(answer) == str:
                objective_in_string = objective
                # derivation.append('print(' + objective + ')')
            elif type(answer) == int or (type(answer) == float and int(answer) == round(answer, 5)):
                objective_in_string = '"{0:.0f}".format(' + objective + ')'
                # derivation.append('print("{0:.0f}".format(' + objective + '))')
                # answer = "{0:.0f}".format(answer)
            elif type(answer) == float:
                objective_in_string = '"{0:.2f}".format(' + objective + ')'
                # derivation.append('print("{0:.2f}".format(' + objective + '))')
                # answer = "{0:.2f}".format(answer)
            derivation.append('print(' + objective_in_string + ')')
            answer = eval(objective_in_string, env, env)
                
            return answer, derivation
    except Exception as e:
        print(e)

    return None, []

# %%
def solve(root, time_limit_sec):

    statements = root.resolve_statements('sol')

    answer, derivation = None, []
    try:
        with time_limit(time_limit_sec):
            answer, derivation = do_math(statements)
    except TimeoutException as e:
        print("do_math() timed out!")
    # return None, []
    return answer, derivation
