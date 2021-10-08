# %%
# 풀이 과정에 해당하는 python code가 제한 시간안에 종료되지 않아서 다음 문제를 못 풀게 되는 상황을 방지하기 위하여
# 시간 제한을 둘 수 있도록 필요한 모듈
import signal
from contextlib import contextmanager
from sympy import Symbol, symbols
import sympy
import re

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

# sympy에서 풀 수 있는 형태로 수식 변경
# ['귤+자몽=42', '귤=자몽-16'] -> ['귤+자몽-(42)', '귤-(자몽+16)']
def equation_substitution(equations):
    substitued_equations = []
    for equation in equations:
        left_eq, right_eq = equation.split('=')
        substitued_eq = left_eq + '-(' + right_eq + ')'
        substitued_equations.append(substitued_eq)

    return substitued_equations

# sympy를 이용한 답 구하기
def find_answer_using_sympy(substitued_equations):
    variables = set()
    for equation in substitued_equations:
         # 한글 단어들을 변수로 설정
         vars = re.compile('[가-힣]+|[A-Za-z]').findall(equation)
         variables.update(vars)

    var_symbol_list = []
    for var in variables:
        var_symbol_list.append(Symbol(var))

    # sympy를 이용한 방정식 풀이
    eq_dict = sympy.solve(substitued_equations, var_symbol_list, dict=True)[0]

    return eq_dict

def solution_code_generate(equations, eq_dict, objective):
    answer_str = "vars = dict()\n"
    for key, value in eq_dict.items():
        answer_str+= "vars['" + str(key) + "']" + "=" + str(value) + "\n"
    answer_str += "if "
    for index, equation in enumerate(equations):
        replaced_str = equation.replace("=","==")

        vars = re.compile('[가-힣]+|[A-Za-z]').findall(replaced_str)
        for var in vars:
            replaced_str = replaced_str.replace(var, "vars['" + var + "']")
        answer_str += replaced_str

        if index != (len(equations)-1):
            answer_str += " and "
    answer_str +=":\n    "
    answer_str +="print("+ objective + ")"
    # answer_str +="print("+ "vars['" + objective + "']" + ")"

    return answer_str

# 주어진 statements(equation, code 등)에서 실행가능한 python 코드를 생성하고, 실행해서 얻어진 답을 반환한다.
# statements: equation, code, objective
def do_math(statements):
    derivation = []
    objective = 'x'

    if 'equation' in statements:
        pass

    if len(statements['equation']) > 0 and len(statements['objective']) > 0:
        equations = statements['equation'][0].split('\r\n')
        objective = statements['objective'][0]
        # 수식을 좌변으로 모음
        substitued_equations = equation_substitution(equations)
        # sympy를 이용해서 정답을 찾음
        eq_dict = find_answer_using_sympy(substitued_equations)
        # 정답을 기반으로 solution 코드를 생성
        answer_str = solution_code_generate(equations, eq_dict, objective)
        print(answer_str)

    derivation = statements['code']
    # if 'objective' in statements:
    if len(statements['objective']) > 0:
        objective = statements['objective'][0]

    env = dict()
    try:
        exec(answer_str, env, env)
        answer = eval(objective, env, env)
        print(answer_str)
        return answer, answer_str

        # exec('\n'.join(derivation), env, env)
        # answer = eval(objective, env, env)
        # if answer != None:
        #     if type(answer) == str:
        #         objective_in_string = objective
        #     elif type(answer) == int or (type(answer) == float and int(answer) == round(answer, 5)):
        #         objective_in_string = '"{0:.0f}".format(' + objective + ')'
        #     elif type(answer) == float:
        #         objective_in_string = '"{0:.2f}".format(' + objective + ')'
        #     derivation.append('print(' + objective_in_string + ')')
        #     answer = eval(objective_in_string, env, env)
                
        #     return answer, derivation
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
    except Exception as e:
        print("do_math() exception!")
    return answer, derivation
# %%
