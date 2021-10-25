# %%
# 풀이 과정에 해당하는 python code가 제한 시간안에 종료되지 않아서 다음 문제를 못 풀게 되는 상황을 방지하기 위하여
# 시간 제한을 둘 수 있도록 필요한 모듈
import signal
from contextlib import contextmanager
from sympy import Symbol, symbols
import sympy
import re
import string
import parser

# 전역 변수
additional_conditions = []

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
        if equation == '':
            continue
        left_eq, right_eq = equation.split('=')
        substitued_eq = left_eq + '-(' + right_eq + ')'
        substitued_equations.append(substitued_eq)

    return substitued_equations

# sympy를 이용한 답 구하기
def find_answer_using_sympy(substitued_equations):
    variables = set()
    for equation in substitued_equations:
         # 한글 단어들을 변수로 설정
         vars = re.compile('[가-힣]+|[A-Za-z]+').findall(equation)
         variables.update(vars)

    var_symbol_list = []
    for var in variables:
        var_symbol_list.append(Symbol(var))

    # sympy를 이용한 방정식 풀이
    sol = sympy.solve(substitued_equations, var_symbol_list, dict=True)
    eq_dict = sol[0] if sol != [] else {}

    return eq_dict

# 메소드
def find_pos_right(field, a, b, range_max):
  try:
    if max(field, key=field.get) == a:
      return (range_max - field[a]) / 2 + field[a]
    else:
      ranges = sorted(list(field.values()))
      idx = ranges.index(field[a])
      ret = []
      for i in range(idx, len(ranges)):
        if i+1 < len(ranges):
          ret.append((ranges[i],ranges[i+1]))
        if i+1 == len(ranges):
          ret.append((ranges[i],range_max))
      return ret
  except:
    return None

def find_ordering(inequal, field, range_max, verbose=False):
  for i in inequal:
    (a, b) = i
    if len(field) == 0:
      field[a] = range_max / 2
    if a in field and not isinstance(field[a], list):
      if b not in field:
        pos = find_pos_right(field, a, b, range_max)
        if pos != None:
          field[b] = pos
      elif isinstance(field[b], list):
        candidates = []
        for r in field[b]:
          if field[a] <= r[0]:
            candidates.append(r)
        if len(candidates) == 1:
          field[b] = (candidates[0][1]-candidates[0][0]) / 2 + candidates[0][0]
    elif a in field and isinstance(field[a], list) and b in field and not isinstance(field[b], list):
      candidates = []
      for r in field[a]:
        if r[1] <= field[b]:
          candidates.append(r)
      if len(candidates) == 1:
        field[a] = (candidates[0][1]-candidates[0][0]) / 2 + candidates[0][0]
    # elif a not in field:
    #   if b in field:
    #     pos = find_pos_left(field, b, a)
    #     if pos != None:
    #       field[a] = pos
    if verbose:
      print(i)
      print(field)

# 부등식 답 구하기
# equations : 호석<석진<지민<남준
def find_answer_in_inequality(equations, order_symbol):
    if order_symbol == '<':
        ascending_ordered_list = equations.split(order_symbol)
    elif order_symbol == '>':
        ascending_ordered_list = equations.split(order_symbol)[::-1]

    '''
    # 입력 : 심볼 가나다순 정렬
    inequal = [('호석', '석진'), ('호석', '지민'), ('호석', '남준'), ('석진', '지민'), ('석진', '남준'),
               ('지민', '남준')]  # 왼쪽 < 오른쪽 (예: 가 < 나)
    '''
    inequal = []
    for index, item in enumerate(ascending_ordered_list):
        if index < (len(ascending_ordered_list)-1):
            ascending_tuple = (ascending_ordered_list[index], ascending_ordered_list[index + 1])
            inequal.append(ascending_tuple)

    # 전역변수
    symbols = sorted(list(set([x[0] for x in inequal] + [x[1] for x in inequal])))
    range_max = float(2 ** len(symbols))
    field = dict()

    while True:
        if len(field) == len(symbols):
            count = 0
            for k in field:
                if isinstance(field[k], list):
                    count = count + 1
            if count == 0:
                break
        find_ordering(inequal, field, range_max, verbose=True)
        print()

    print("Result:")
    print(field)
    print("최소: " + min(field, key=field.get))
    print("최대: " + max(field, key=field.get))

    return field



import itertools
# import time
def find_answer_in_inequality2(equations):
    # start = time.time()
    field = {}
    equations = list(map(lambda x: x.replace(' ', ''), equations))
    whole_variable_list = set(itertools.chain.from_iterable( map(lambda x: re.split('>|<|=', x), equations))) 

    # 부등호 refinement
    expressions = ['(' + x.replace('=','==') +')' for x in equations]
    for i in range(0,len(expressions)): 
        for v in whole_variable_list:
            expressions[i] = expressions[i].replace(v, 'field[\''+v+'\']')

    # Equal equations list 
    equal_eq = dict(map(lambda y: y.split('='), list(filter(lambda x: '=' in x, equations))))
    equal_eq_list = set(equal_eq.keys())

    variable_list = whole_variable_list - equal_eq_list 
    num_variables = len(variable_list) 
    possible_answer = list(itertools.permutations(list(range(num_variables)))) # 모든 경우의 수

    for answer in possible_answer:
        # 변수 할당
        for name, value in zip(variable_list, answer):
            field[name] = value

        # Equal 변수 할당
        for name in equal_eq_list:
            field[name] = field[equal_eq[name]]

        # Evaluation
        num_solve = 0
        for e in expressions:
            if eval(e):
                num_solve +=1
            else:
                break # 프루닝

        if num_solve == len(expressions):
            print(field)
            print("최소: " + min(field, key=field.get))
            print("최대: " + max(field, key=field.get))
    
            # stop = time.time()
            # print("Best Time:", stop - start)            
            return field

    # stop = time.time()
    # print("Worst Time:", stop - start)
    return field

lambdas = dict({
    'divisors': 'divisors = lambda n: [x for x in range(1, n+1) if n % x == 0]',
    'digits': 'digits = lambda ns, n: [int(\'\'.join(str(i) for i in x)) for x in itertools.permutations(ns, n) if x[0] != 0]',
    'digitsz': 'digitsz = lambda ns, n: [int(\'\'.join(str(i) for i in x)) for x in itertools.permutations(ns, n)]',
    'alldigits': 'alldigits = lambda n: range(10**(n-1), 10**n)',
    'shiftr': 'shiftr = lambda x, n: x * 10**n',
    'shiftl': 'shiftl = lambda x, n: x / 10**n',
    'lcm': 'lcm = lambda x,y: int(x*y/math.gcd(x,y))',
    'sumdigits': 'sumdigits = lambda n: sum([int(x) for x in list(str(n))])',
    'mathcomb': 'mathcomb = lambda x, y: int(math.factorial(x)/(math.factorial(y)*math.factorial(x-y)))'
})

def solution_code_generate(equations, eq_dict, objective, code):
    global lambdas
    answer_str = "vars = dict()\n"
    for key, value in eq_dict.items():
        answer_str += "vars['" + str(key) + "']" + "=" + str(value) + "\n"

    # math와 itertools 라이브러리는 기본으로 추가
    answer_str += "import math\n"
    answer_str += "import itertools\n"

    temp = ''
    for c in code:
        temp += ' ' + c + ' '
    temp += objective
    for key in lambdas:
        if key in temp:
            answer_str += lambdas[key] + '\n'

    answer_str += "if True"
    for index, equation in enumerate(equations):
        replaced_str = equation.replace("=","==")
        answer_str += " and "
        for key in eq_dict:
            # replaced_str = re.sub(r'([^\[])(' + re.escape(str(key)) + r')([^\[])', f"\\g<1>vars['{key}']\\g<3>", replaced_str)
            replaced_str = re.sub(r'\b' + re.escape(str(key)) + r'\b', f"vars['{key}']", replaced_str)
        # vars = re.compile('(([가-힣]+)|(\([가|나|다|라|마|바|사|아|자|차|카|타|파|하]\))|([A-Za-z]))').findall(replaced_str)
        # for var in vars:
        #     replaced_str = re.sub(r'\b' + re.escape(var[0]) + r'\b', "vars['" + var[0] + "']", replaced_str)
        #     # replaced_str = replaced_str.replace(var[0], "vars['" + var[0] + "']")
        answer_str += replaced_str
    answer_str += ":\n"
    for c in code:
        answer_str += '    ' + c + '\n'
    objective_str = "    print(" + objective + ")"

    return answer_str, objective_str

def expand_term(matchobj):
    global additional_conditions

    retval = []
    term = matchobj.group(0)
    l = len(term)
    if l == 1:
        return term
    else:
        for i in range(l):
            e = l-i-1
        retval.append("{}*{}".format(10**e, term[i]))
        if term[0] in string.ascii_uppercase:
            additional_conditions.append(term[0])
        return "({})".format('+'.join(retval))

def solver_digit_var(in_formula):
    global additional_conditions

    if isinstance(in_formula, list):
        eq = ' and '.join(in_formula)
    elif isinstance(in_formula, str):
        eq = in_formula
    else:
        return None

    formula = re.sub('[0-9A-Z]+', expand_term, eq)
    formula = formula.replace('!=', '<>')
    formula = formula.replace('=', '==')
    formula = formula.replace('<>', '!=')
    for nonzero in additional_conditions:
        formula = formula + " and {}!=0".format(nonzero)

    code = parser.expr(formula).compile()

    variables = []
    for i in string.ascii_uppercase:
        if eq.find(i) > -1:
            variables.append(i)

    retval = []
    envs = dict()
    for i in range(0, 10**len(variables)):
        for v in range(0, len(variables)):
            envs[variables[v]] = (i % 10**(v+1)) // 10**v
        if eval(code, envs):
            r = dict()
        for v in variables:
            r[v] = envs[v]
        retval.append(r)

    return retval

# 주어진 statements(equation, code 등)에서 실행가능한 python 코드를 생성하고, 실행해서 얻어진 답을 반환한다.
# statements: equation, code, objective
def do_math(statements):
    # if len(statements['equation']) > 0 and len(statements['objective']) > 0:
    #equations = re.split(r'[\r\n]' , statements['equation'][0])
    # equations = statements['equation'][0].split('\r\n')
    equations = []
    for item in statements['equation']:
        equations.extend(re.split(r'[\r\n]', item))
        # splitted_item = re.split(r'[\r\n]' , item)
        # for eq_token in splitted_item:
        #     if eq_token != '':
        #         equations.append(eq_token)

    # 중복값 제거
    equations = [x for x in list(set(equations)) if x.strip() != '']
    code = []
    for item in statements['code']:
        code.extend(re.split(r'[\r\n]', item))
    # statements['code'][0] if statements['code'] != [] else ''

    objective = statements['objective'][0] if statements['objective'] != [] else ''

    # equation과 code가 없는 경우 바로 정답을 print
    if len(equations) == 0 and len(code) == '':
        answer_str = ""
        # math와 itertools 라이브러리는 기본으로 추가
        answer_str += "import math\n"
        answer_str += "import itertools\n"
        answer_str += "print(" + objective + ")"
    else:
        # 1. sympy solver로 풀이 시도
        answer_str=''
        try:
            # 수식을 좌변으로 모음
            substitued_equations = equation_substitution(equations)
            # sympy를 이용해서 정답을 찾음
            eq_dict = find_answer_using_sympy(substitued_equations)
            # 정답을 기반으로 solution 코드를 생성
            answer_str, objective_str = solution_code_generate(equations, eq_dict, objective, code)
        except Exception as e1:
            print('sympy solver exception')
        # 2. digit var solver로 풀이 시도
        if answer_str == '':
            global additional_conditions
            additional_conditions = []
            try:
                field = solver_digit_var(equations)
                eq_dict = field[0]
                answer_str, objective_str = solution_code_generate(equations, eq_dict, objective, code)
            except Exception as e2:
                print('digit var solver exception')
        # 3. 부등식 solver로 풀이 시도
        if answer_str == '':
            try:
                field = find_answer_in_inequality2(equations)
                eq_dict = field
                answer_str, objective_str = solution_code_generate(equations, eq_dict, objective, code)
            except Exception as e3:
                print('inequality solver exception')

    # if 'objective' in statements:
    # if len(statements['objective']) > 0:
        # objective = statements['objective'][0]

    env = dict()
    try:
        exec(answer_str + objective_str, env, env)
        answer = eval(objective, env, env) if objective != '' else ''

        if answer != None:
            if type(answer) == str:
                objective_in_string = objective
            elif type(answer) == int or (type(answer) == float and int(answer) == round(answer, 5)):
                objective_in_string = '"{0:.0f}".format(' + objective + ')'
            elif type(answer) == float:
                objective_in_string = '"{0:.2f}".format(' + objective + '+0.0000000001)'
            answer_str += '    print(' + objective_in_string + ')'
            answer = eval(objective_in_string, env, env)

        #print(answer_str)
        return answer, answer_str

        # exec('\n'.join(derivation), env, env)
        # answer = eval(objective, env, env)
                
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
        print(f'\033[91mTimed out statements {statements}\033[0;0m')
    except Exception as e:
        print("do_math() exception!")
        print(f'\033[91mSolver exception statements {statements}\033[0;0m')

    return answer, derivation

# %%
if __name__=="__main__": # 모듈 단독 테스트
    # do_math({'equation': [], 'code': ["strings=['흰색', '검은색', '보라색', '초록색', '빨간색']"], 'objective': ['math.comb(len(strings), (2))']})
    # do_math({'equation': ['정현이 = 15','영진 = 180 / 15', '경주 = 7 / 2\n'], 'code': [], 'objective': ["vars['정현이']"]})
    # do_math({'equation': ['r=x/(5)\nx*(5)=(100)'], 'code': [], 'objective': ["vars['x']/(5)"]})
    do_math({'equation': ['지민 = (5)\n자신 = (5)\n지민 = (지민+자신)/(27) - (@n3)'], 'code': [], 'objective': ["vars['지민']"]})
