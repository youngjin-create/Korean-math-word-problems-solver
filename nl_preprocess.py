
import re
from node import Node

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




def preprocess(question):

    
    def replace_space(m):
        return m.group(1) + m.group(3)
    question = re.sub('([0-9])( )(\w)', replace_space, question) # 숫자 띄어쓰기 표준화

    return question
    