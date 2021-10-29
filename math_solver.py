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
import itertools

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
        left_eq, right_eq = equation.split('==')
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

# import time
def find_answer_in_inequality2(equations):
    # start = time.time()
    field = {}
    equations = list(map(lambda x: x.replace(' ', ''), equations))
    whole_variable_list = set(itertools.chain.from_iterable( map(lambda x: re.split('>|<|==', x), equations))) 

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

nonzero_vars = set()
singledigit_vars = set()
def expand_term(matchobj):
    global nonzero_vars
    global singledigit_vars

    retval = []
    term = matchobj.group(0)
    l = len(term)
    if l == 1:
        return term
    else:
        for i in range(l):
            e = l-i-1
            retval.append("{}*{}".format(term[i], 10**e))
            if term[i] in string.ascii_uppercase:
                singledigit_vars.add(term[i])
        # print("({})".format('+'.join(retval)))
        if term[0] in string.ascii_uppercase:
            nonzero_vars.add(term[0])
        return "({})".format('+'.join(retval))

def solver_digit_var(equations, variables, allsolutions=False):
    global nonzero_vars
    global singledigit_vars

    eq = ' and '.join(equations)
    for nonzero in list(nonzero_vars):
        eq = eq + " and {}!=0".format(nonzero)
    for sd in list(singledigit_vars):
        eq = eq + " and {}<=9".format(sd)

    envs = dict()
    solsets = dict()
    for v in variables:
        solsets[v] = set()

    varslist = list(variables)

    try:
        if len(varslist) >= 7:
            return dict() if allsolutions==False else solsets
        for i in range(0, 10**len(varslist)):
            for v in range(0, len(varslist)):
                envs[varslist[v]] = i // (10**v) % 10
            if eval(eq, envs):
                if allsolutions==False:
                    return envs
                else:
                    for v in variables:
                        solsets[v].add(envs[v])
                    
        if len(varslist) >= 4:
            return dict() if allsolutions==False else solsets
        for i in range(0, 100**len(varslist)):
            for v in range(0, len(varslist)):
                envs[varslist[v]] = i // (100**v) % 100
            if eval(eq, envs):
                if allsolutions==False:
                    return envs
                else:
                    for v in variables:
                        solsets[v].add(envs[v])

        if len(varslist) >= 3:
            return dict() if allsolutions==False else solsets
        for i in range(0, 1000**len(varslist)):
            for v in range(0, len(varslist)):
                envs[varslist[v]] = i // (1000**v) % 1000
            if eval(eq, envs):
                if allsolutions==False:
                    return envs
                else:
                    for v in variables:
                        solsets[v].add(envs[v])
    except Exception as e:
        if 'object is not callable' in str(e):
            return dict()

    if allsolutions:
        return solsets

    return dict()

lambdas = dict({
    'divisors': 'divisors = lambda n: [x for x in range(1, n+1) if n % x == 0]',
    'digits': 'digits = lambda ns, n: [int(\'\'.join(str(i) for i in x)) for x in itertools.permutations(ns, n) if x[0] != 0]',
    'digitsz': 'digitsz = lambda ns, n: [int(\'\'.join(str(i) for i in x)) for x in itertools.permutations(ns, n)]',
    'alldigits': 'alldigits = lambda n: range(10**(n-1), 10**n)',
    'shiftr': 'shiftr = lambda x, n: x * 10**n',
    'shiftl': 'shiftl = lambda x, n: x / 10**n',
    'lcm': 'lcm = lambda x,y: int(x*y/math.gcd(x,y))',
    'sumdigits': 'sumdigits = lambda n: sum([int(x) for x in list(str(n))])',
    'mathcomb': 'mathcomb = lambda x, y: int(math.factorial(x)/(math.factorial(y)*math.factorial(x-y)))',
    'mathperm': 'mathperm = lambda x, y: int(math.factorial(x)/ math.factorial(x-y))'
})

def lambda_definitions(equations, code, objective):
    global lambdas
    defs = []
    all = [*equations, *code, objective]
    for s in all:
        for key in lambdas:
            if key in s:
                defs.insert(0, lambdas[key])
    return defs

def expand_var_term(matchobj):
    term = matchobj.group(0)

    retval = []
    l = len(term)
    for i in range(l):
        e = l-i-1
        retval.append("{}*{}".format("vars['" + term[i] + "']" if term[i] in string.ascii_uppercase else term[i], 10**e))
    # print("({})".format('+'.join(retval)))
    return "({})".format('+'.join(retval))

def solution_code_generate(equations, eq_dict, code):
    global lambdas
    answer_str = "vars,sols=dict(),dict()\n"
    for key, value in eq_dict.items():
        if type(value) == set:
            answer_str += "vars['" + str(key) + "']" + "=list(" + str(value) + ")[0]\n"
            answer_str += "sols['" + str(key) + "']" + "=list(" + str(value) + ")\n"
        else:
            answer_str += "vars['" + str(key) + "']" + "=" + str(value) + "\n"

    answer_str += "if True"
    for eq in equations:
        # replaced_str = '(' + eq.replace("=","==") + ')'
        # replaced_str = re.sub('[0-9A-Z]*[A-Z][0-9A-Z]*', expand_term, eq)
        # replaced_str = replaced_str.replace('!=', '<>')
        # replaced_str = replaced_str.replace('=', '==')
        # replaced_str = replaced_str.replace('<>', '!=')

        answer_str += " and "
        for key in eq_dict:
            # replaced_str = re.sub(r'([^\[])(' + re.escape(str(key)) + r')([^\[])', f"\\g<1>vars['{key}']\\g<3>", replaced_str)
            eq = re.sub(r'\b' + re.escape(str(key)) + r'\b', f"vars['{key}']", eq)
        # vars = re.compile('(([가-힣]+)|(\([가|나|다|라|마|바|사|아|자|차|카|타|파|하]\))|([A-Za-z]))').findall(replaced_str)
        # for var in vars:
        #     replaced_str = re.sub(r'\b' + re.escape(var[0]) + r'\b', "vars['" + var[0] + "']", replaced_str)
        #     # replaced_str = replaced_str.replace(var[0], "vars['" + var[0] + "']")
        if '==' in eq:
            left, right = eq.split('==')
            eq = 'round(' + left + ', 12)==round(' + right + ', 12)'
        answer_str += eq
    answer_str += ":\n"
    # for c in code:
    #     answer_str += '    ' + c + '\n'

    return answer_str

# 주어진 statements(equation, code 등)에서 실행가능한 python 코드를 생성하고, 실행해서 얻어진 답을 반환한다.
# statements: equation, code, objective
def do_math(statements):
    global nonzero_vars
    global singledigit_vars
    nonzero_vars = set()
    singledigit_vars = set()
    equations = []
    for item in statements['equation']:
        equations.extend(re.split(r'[\r\n]', item))
    # 중복값 제거
    equations = [x.strip() for x in list(set(equations)) if x.strip() != '']
    code = []
    for item in statements['code']:
        code.extend(re.split(r'[\r\n]', item))

    objective = statements['objective'][0] if statements['objective'] != [] else ''

    allsolutions = 'allsolutions' in equations
    equations = [eq for eq in equations if eq != 'allsolutions']

    # import, lambda function 추가
    ld = lambda_definitions(equations, code, objective)
    answer_header = ['import math', 'import itertools', *ld]#, *code]

    # equations가 있으면 풀이 시도
    answer_str = ''
    if len(equations) > 0:
        variables = set()
        for idx, eq in enumerate(equations):
            vars = re.compile('[가-힣]+|[a-z]+|[A-Z]').findall(eq)
            variables.update(vars)
            variables.discard('abs')

            eq = re.sub('[0-9A-Z]*[A-Z][0-9A-Z]*', expand_term, eq)
            eq = eq.replace('!=', '<>')
            eq = eq.replace('=', '==')
            eq = eq.replace('<==', '<=')
            eq = eq.replace('>==', '>=')
            eq = eq.replace('<>', '!=')
            equations[idx] = eq

        # for nonzero in nonzero_vars:
            # formula = formula + " and {}!=0".format(nonzero)

        # 1. sympy solver로 풀이 시도
        answer_str=''
        try:
            # 수식을 좌변으로 모음
            substitued_equations = equation_substitution(equations)
            # sympy를 이용해서 정답을 찾음
            eq_dict = find_answer_using_sympy(substitued_equations)
            for key, value in eq_dict.items():
                v = eval(str(value)) # raise exception if solved partially
            # 정답을 기반으로 solution 코드를 생성
            answer_str = solution_code_generate(equations, eq_dict, code)
        except Exception as e1:
            print('sympy solver exception')
        # 2. digit var solver로 풀이 시도
        if answer_str == '':
            try:
                field = solver_digit_var(equations, variables, allsolutions=allsolutions)
                if '__builtins__' in field:
                    del field['__builtins__']
                eq_dict = field
                # eq_dict = field[0]
                answer_str = solution_code_generate(equations, eq_dict, code)
            except Exception as e2:
                print('digit var solver exception')
        # 3. 부등식 solver로 풀이 시도
        if answer_str == '':
            try:
                field = find_answer_in_inequality2(equations)
                eq_dict = field
                answer_str = solution_code_generate(equations, eq_dict, code)
            except Exception as e3:
                print('inequality solver exception')
    else:
        answer_str = 'if True:\n'

    for c in code:
        if c != '':
            answer_str += '    ' + c + '\n'
        
    answer_str = '\n'.join(answer_header) + '\n' + answer_str

    objective = re.sub('[0-9A-Z]*[A-Z][0-9A-Z]*', expand_term, objective)

    env = dict()
    try:
        exec(answer_str + '    pass', env, env)
        answer = eval(objective, env, env) if objective != '' else ''

        # objective의 타입에 맞춰서 print문 추가
        if answer != None:
            if type(answer) == str:
                objective_in_string = objective
            elif type(answer) == int or (type(answer) == float and int(answer) == round(answer, 5)):
                objective_in_string = '"{0:.0f}".format(' + objective + ')'
            elif type(answer) == float:
                objective_in_string = '"{0:.2f}".format(' + objective + '+0.0000000001)'
            answer_str += '    print(' + objective_in_string + ')'
            answer = eval(objective_in_string, env, env)

        return answer, answer_str
    except Exception as e:
        print(e)

    return None, []

# %%
def solve(statements, time_limit_sec):
    print(f'solving... \033[33mstatements = {statements}\033[0;0m')

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
    print(do_math({'equation': ['석진>호석\n석진<지민', '호석>지민', '지민>남준'], 'code': [], 'objective': ['min(vars, key=vars.get)']}))
