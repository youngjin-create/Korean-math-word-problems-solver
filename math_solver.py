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

# 주어진 statements(equation, code 등)에서 실행가능한 python 코드를 생성하고, 실행해서 얻어진 답을 반환한다.
def do_math(statements):

    derivation = statements['code']
    objective = 'x'# statements['code']

    env = dict()
    try:
        exec('\n'.join(derivation), env, env)
        answer = eval(objective, env, env)
        if answer != None:
            if type(answer) == str:
                objective_in_string = objective
            elif type(answer) == int or (type(answer) == float and int(answer) == round(answer, 5)):
                objective_in_string = '"{0:.0f}".format(' + objective + ')'
            elif type(answer) == float:
                objective_in_string = '"{0:.2f}".format(' + objective + ')'
            derivation.append('print(' + objective_in_string + ')')
            answer = eval(objective_in_string, env, env)
                
            return answer, derivation
    except Exception as e:
        print(e)

    return None, []

# %%
def solve(statements, time_limit_sec):
    answer, derivation = None, []
    try:
        with time_limit(time_limit_sec):
            answer, derivation = do_math(statements)
    except TimeoutException as e:
        print("do_math() timed out!")
    return answer, derivation
