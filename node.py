import re
import sympy as sym

import dataset
import wordsim
import utils

random_var_name = 0
def get_random_var_name():
    global random_var_name
    random_var_name = random_var_name + 1
    return f'var{random_var_name:03d}'

# mapping = { '$a': 'var22', '$b': 'var33' }
def variable_substitute(statement, mapping):
    # print(statement)
    # print(mapping)
    for m in mapping:
        statement = statement.replace(m, str(mapping[m]))
    return statement

# 수열에서 규칙을 찾는 로직을 별도 함수로 구현
def find_regularities(list):
    try:
        l = list.split(',')
        l = [float(item) if item.strip().isnumeric() else item.strip() for item in l]
        # print(l)
        # l = eval(list)
        # An+B
        if type(l[0]) != float or type(l[1]) != float:
            return None
            # return '[' + list + ']'
        a, b = l[1] - l[0], l[0]
        found = True
        for i in range(len(l)):
            if type(l[i]) == float and l[i] != a*i+b:
                found = False
        if found:
            return f'lambda x: int({a}*x+{b})'
        if len(l) >= 4:
            # 3차 방정식
            a = sym.Symbol('a')
            b = sym.Symbol('b')
            c = sym.Symbol('c')
            d = sym.Symbol('d')
            eqs = []
            for i in range(len(l)):
                if type(l[i]) == float:
                    eqs.append(a*i**3 + b*i**2 + c*i + d - l[i])
            sol = sym.solve(eqs, (a, b, c, d))
            # print(sol)
            # print(sol[a])
            if sol:
                # print(list)
                # print(sol)
                return f'lambda x: int({sol[a]}*x*x*x+{sol[b]}*x*x+{sol[c]}*x+{sol[d]})'
        return None #'[' + list + ']'
    except Exception as e:
        print(e)
        return None

def predefined_replaces(raw):
    if '마리' in raw:
        raw = raw.replace('한 마리', '1마리')
        raw = raw.replace('두 마리', '2마리')
        raw = raw.replace('세 마리', '3마리')
        raw = raw.replace('네 마리', '4마리')
        raw = raw.replace('다섯 마리', '5마리')
        raw = raw.replace('여섯 마리', '6마리')
        raw = raw.replace('일곱 마리', '7마리')
        raw = raw.replace('여덟 마리', '8마리')
        raw = raw.replace('아홉 마리', '9마리')
        raw = raw.replace('열 마리', '10마리')

    if '번째' in raw:
        raw = raw.replace('첫 번째', '1번째')
        raw = raw.replace('두 번째', '2번째')
        raw = raw.replace('세 번째', '3번째')
        raw = raw.replace('네 번째', '4번째')
        raw = raw.replace('다섯 번째', '5번째')
        raw = raw.replace('여섯 번째', '6번째')
        raw = raw.replace('일곱 번째', '7번째')
        raw = raw.replace('여덟 번째', '8번째')
        raw = raw.replace('아홉 번째', '9번째')
        raw = raw.replace('열 번째', '10번째')
    return raw

def replace_term(m):
    r = ''
    m = m.group()
    for i in range(len(m)):
        r = ('(' + r + ')*10+' if r else '') + (m[i] if m[i].isnumeric() else 'values["' + m[i] + '"]')
    return '(' + r + ')'

def get_predefined_candidates_nodes(raw):
    nodes = []
    matches = []

    def re_list(expr):
        return expr + '([, ]+(' + expr + '))+'

    raw = predefined_replaces(raw)

    # re_number = '(([0-9]+(\.[0-9]+)?)|([0-9]+[/][0-9]+))'
    re_number = '[0-9]+(\.[0-9]+)?(\/[0-9]+(\.[0-9]+)?)?'
    for match in re.compile(re_number).finditer(raw):
        n = Node(match.group(), match.span(), '<$a:숫자>', ['$a=' + match.group()])
        nodes.append(n)
    for match in re.compile(re_list(re_number)).finditer(raw):
        # reg = find_regularities('[' + match.group() + ']')
        # n = Node(match.group(), match.span(), '<$a:수열>', ['$a=' + reg])
        n = Node(match.group(), match.span(), '<$a:수열>', ['$a=[' + match.group() + ']'])
        reg = find_regularities(match.group())
        if reg:
            n.statements.append(f'init:reg={reg}')
        nodes.append(n)
    re_number_or_indicator = '(([0-9]+(\.[0-9]+)?(\/[0-9]+(\.[0-9]+)?)?)|([A-Z]))'
    for match in re.compile(re_list(re_number_or_indicator)).finditer(raw):
        matches = re.compile('[A-Z]').findall(match.group())
        if not matches:
            continue
        reg = find_regularities(match.group())
        if not reg:
            continue
        n = Node(match.group(), match.span(), '<$a:수열>', [f'$a={reg}'])
        n.statements.append(f'init:reg={reg}')
        elements = [x.strip() for x in match.group().split(',')]
        for idx, item in enumerate(elements):
            if len(item) == 1 and 'A' <= item and item <= 'Z':
                n.statements.append(f'values["{item}"]=reg({idx})')
        # n = Node(match.group(), match.span(), '<$a:수열>', ['$a=[' + match.group() + ']'])
        # reg = find_regularities(match.group())
        # if reg:
            # n.statements.append(f'init:reg={reg}')
        nodes.append(n)

    re_indicator = '(\()([가나다라마바사아자차카타파하])(\))'
    for match in re.compile(re_indicator).finditer(raw):
        n = Node(match.group(2), match.span(), '<$a:지시자>')
        n.statements = [f'values:{match.group(2)}', f'init:indicators.add("{match.group(2)}")', f'$a="{match.group(2)}"']
        nodes.append(n)
    for match in re.compile(re_list(re_indicator)).finditer(raw):
        n = Node(match.group(), match.span(), '<$a:지시자들>', [])
        inds = []
        for m in re.compile('(\()([가나다라마바사아자차카타파하])(\))').finditer(match.group()):
            n.statements.append(f'values:{m.group(2)}')
            n.statements.append(f'init:indicators.add("{m.group(2)}")')
            inds.append(m.group(2))
        n.statements.append('$a=[' + ','.join(['"' + x + '"' for x in inds]) + ']')
        nodes.append(n)

    re_variable = '[A-Z]'
    for match in re.compile(re_variable).finditer(raw):
        n = Node(match.group(), match.span(), '<$a:미지수>', [])
        n.statements = [f'values:{match.group()}', f'$a="{match.group()}"']
        nodes.append(n)
    # for match in re.compile(re_list(re_variable)).finditer(raw):
    #     matches.append(('<미지수들>', match.span(), match.group()))

    re_mixed_term = '[0-9A-Z]*[A-Z][0-9A-Z]*' # 미지수가 최소 하나 이상 섞여 있는 항

    re_equation = '[0-9A-Z][0-9A-Z\.\+\-\*\/=<> ]*[0-9A-Z]' # 등호(=)를 포함하는 식
    for match in re.compile(re_equation).finditer(raw):
        if match.group().count('=') + match.group().count('<') + match.group().count('>') != 1:
            continue
        n = Node(match.group(), match.span(), '<$a:등식>', [])
        for m in re.compile(re_variable).finditer(match.group()):
            n.statements.append(f'values:{m.group()}')
        eq = match.group().replace('=','==')
        vars = set()
        for mixed in re.compile(re_mixed_term).finditer(match.group()):
            if len(mixed.group()) > 1:
                for m in re.compile(re_variable).finditer(mixed.group()):
                    vars.add(m.group())
        for v in vars:
            n.statements.append(f'values["{v}"]%=10')
            # n.statements.append(f'condition:0<=values["{v}"] and values["{v}"]<=9')
        eq = re.sub(re_mixed_term, replace_term, eq) # 숫자-미지수가 섞여 있는 항 처리
        n.statements.append(f'condition:{eq}')
        nodes.append(n)
    # for match in re.compile(re_list(re_equation)).finditer(raw):
        # matches.append(('<미지수들>', match.span(), match.group()))

    for match in re.compile('[0-9A-Z\(][0-9A-Z\(\)\.\+\-\*\/ ]*[0-9A-Z\)]').finditer(raw):
        n = Node(match.group(), match.span(), '<$a:수식>', [])
        for m in re.compile(re_variable).finditer(match.group()):
            n.statements.append(f'values:{m.group()}')
        vars = set()
        for mixed in re.compile(re_mixed_term).finditer(match.group()):
            if len(mixed.group()) > 1:
                for m in re.compile(re_variable).finditer(mixed.group()):
                    vars.add(m.group())
        for v in vars:
            n.statements.append(f'values["{v}"]%=10')
            # n.statements.append(f'condition:0<=values["{v}"] and values["{v}"]<=9')
        eq = re.sub(re_mixed_term, replace_term, match.group()) # 숫자-미지수가 섞여 있는 항 처리
        n.statements.append(f'$a={eq}')
        nodes.append(n)

    re_names = '(남준|석진|윤기|호석|지민|태형|정국|민영|유정|은지|유나|어머니|아버지|할아버지|할머니|손자|손녀|조카|이모|삼촌|동생|형|누나|오빠|언니)'
    for match in re.compile(re_names).finditer(raw):
        if match.span()[0] > 0 and raw[match.span()[0]-1] != ' ':
            continue
        n = Node(match.group(), match.span(), '<$a:사람>', [])
        n.statements = [f'values:{match.group()}', f'init:people.add("{match.group()}")', f'$a="{match.group()}"']
        nodes.append(n)
        # matches.append(('<사람>', match.span(), match.group()))
    # for match in re.compile(re_list(re_names)).finditer(raw):
    #     n = Node(match.group(), match.span(), '<$a:사람들>', [])
    #     matches = re.compile(re_names).findall(match.group())
    #     for item in matches:
    #         n.statements.append(f'values:{item}')
    #         n.statements.append(f'init:people.add("{item}")')
    #     n.statements.append('$a=[' + ','.join(['"' + x + '"' for x in matches]) + ']')
    #     nodes.append(n)
    #     # matches.append(('<사람들>', match.span(), match.group()))

    # re_subjects = '(?:국어|영어|수학|사회|과학|음악|미술|체육|실과|도덕)'
    # for match in re.compile(re_subjects).finditer(raw):
    #     n = Node(match.group(), match.span(), '<$a:과목>', [])
    #     n.statements = [f'subjects.append("{match.group()}")', f'$a="{match.group()}"']
    #     nodes.append(n)
    # for match in re.compile(re_list(re_subjects)).finditer(raw):
    #     n = Node(match.group(), match.span(), '<$a:과목들>', [])
    #     matches = re.compile(re_subjects).findall(match.group())
    #     for item in matches:
    #         n.statements.append(f'subjects.append("{item}")')
    #     n.statements.append('$a=[' + ','.join(['"' + x + '"' for x in matches]) + ']')
    #     nodes.append(n)

    # re_objects = ('(?:오리|닭|토끼|물고기|고래|거위|달팽이|개구리|강아지|고양이|비둘기|병아리'
    #     '|장미|백합|튤립|카네이션|국화|화분|화단|꽃병|배구공|농구공|축구공|탁구공|야구공'
    #     '|사과|배|감|귤|포도|수박|토마토|무|당근|오이|배추|사탕|김밥|빵|라면|과자|음료수|주스|우유|달걀'
    #     '|연필|색연필\')')
    # for match in re.compile(re_objects).finditer(raw):
    #     n = Node(match.group(), match.span(), '<$a:사물>', [])
    #     n.statements = [f'objects.append("{match.group()}")', f'$a="{match.group()}"']
    #     nodes.append(n)
    # for match in re.compile(re_list(re_objects)).finditer(raw):
    #     n = Node(match.group(), match.span(), '<$a:사물들>', [])
    #     matches = re.compile(re_objects).findall(match.group())
    #     for item in matches:
    #         n.statements.append(f'objects.append("{item}")')
    #     n.statements.append('$a=[' + ','.join(['"' + x + '"' for x in matches]) + ']')
    #     nodes.append(n)

    return nodes

# parsing tree 구성을 위한 node
class Node:
    def __init__(self, raw, span=[0,0], reduce='', statements=[]):
        self.raw = raw
        self.span = span
        self.children = [] # list of [key in pattern, start_pos, end_pos, child Node]
        self.comparison = '' # text used to compare to others '<숫자>와 <숫자>를 더하시오.'
        self.matched_pattern = None # matched pattern in dataset, used for debugging only
        self.closest_distance = None
        self.reduce = reduce
        self.statements = statements
    def match_predefined(self):
        nodes = get_predefined_candidates_nodes(self.raw)
        # print(nodes)
        last_pos = len(self.raw)
        for node in sorted(nodes, key=lambda x: (x.span[1], -x.span[0]), reverse=True): # greedy selection, for now
            if node.span[0] < last_pos:
                self.children.insert(0, [ None, node.span[0], node.span[1], node ])
                last_pos = node.span[0]
        return
    def compute_comparison_string(self):
        replaced = self.raw
        for child in sorted(self.children, key=lambda x: (x[2], -x[1]), reverse=True):
            replaced = replaced[:child[1]] + '<' + utils.get_name_and_type(child[3].reduce)[1] + '>' + replaced[child[2]:]
        self.comparison = replaced
        return
    def do_pattern_match(self):
        self.compute_comparison_string()
        # print(self.comparison)
        types_comparison = ''.join([utils.get_name_and_type(x[3].reduce)[1] for x in self.children])
        # print(types_comparison)
        pattern, closest_distance = None, float('inf')
        if not(types_comparison in dataset.fast_dataset):
            return pattern, closest_distance
        for p in dataset.fast_dataset[types_comparison]:
            distance = wordsim.phrase_similarity(p['C'], self.comparison)
            if distance < closest_distance:
                pattern, closest_distance = p, distance
        # for p in dataset:
        #     if ''.join([x[1] for x in p['children']]) != types_comparison:
        #         continue
        #     distance = wordsim.phrase_similarity(p['C'], self.comparison)
        #     if distance < closest_distance:
        #         pattern, closest_distance = p, distance
        if pattern:
            # print(pattern)
            for idx, child in enumerate(pattern['children']):
                self.children[idx][0] = child[0]
            self.statements = pattern['statements']
            self.reduce = pattern['R']
            self.matched_pattern = pattern
            self.closest_distance = closest_distance
        return pattern, closest_distance
    def resolve_statements(self, reduced_variable_name):
        # requirements: self.children, self.statements, self.reduce
        sts = []
        var_mapping = {}
        for child in self.children:
            key = child[0]
            if key is None:
                # continue
                child_statements = child[3].resolve_statements(get_random_var_name())
            else:
                var_mapping[key] = get_random_var_name()
                child_statements = child[3].resolve_statements(var_mapping[key])
            for s in child_statements:
                sts.append(s)
        if self.reduce:
            var_mapping[utils.get_name_and_type(self.reduce)[0]] = reduced_variable_name
        for s in self.statements:
            sts.append(s)
        # print(sts)
        # print(var_mapping)
        sts = [variable_substitute(s, var_mapping) for s in sts]
        # print(sts)
        # print(var_mapping)
            
        # print(var_mapping)
        # for s in self.statements:
        #     # print(s)
        #     sts.append(variable_substitute(s, var_mapping))
        return sts
    def print(self, level=0):
        # if len(n.children) == 0 and level > 0:
        #     return
        raw = '(parse_tree) ' + self.raw if level == 0 else self.raw
        if self.matched_pattern != None:
            print(' '*level*4 + raw + ' =1> ' + self.comparison + ' =2> ' + self.matched_pattern['P'] + f' ({self.closest_distance:.2f})')
        else:
            print(' '*level*4 + raw)

        for child in self.children:
            child[3].print(level+1)
            # print_node(child[3], level+1)
