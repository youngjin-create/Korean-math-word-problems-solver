# %%
import re

def predefined_replaces(raw):
    raw = re.sub(r'\b한 ', '1', raw)
    raw = re.sub(r'\b두 ', '2', raw)
    raw = re.sub(r'\b세 ', '3', raw)
    raw = re.sub(r'\b네 ', '4', raw)
    raw = re.sub(r'\b다섯 ', '5', raw)
    raw = re.sub(r'\b여섯 ', '6', raw)
    raw = re.sub(r'\b일곱 ', '7', raw)
    raw = re.sub(r'\b여덟 ', '8', raw)
    raw = re.sub(r'\b아홉 ', '9', raw)
    raw = re.sub(r'\b열 ', '10', raw)

    raw = re.sub(r'\b첫 ', '1', raw)
        
    raw = re.sub(r'\b몇개', '몇 개', raw)

    raw = re.sub(r'\b어떤 수', '어떤수', raw)

    return raw

def preprocess(question):
    def replace_space(m):
        return m.group(1) + m.group(3)
    question = re.sub('([0-9])( )(\w)', replace_space, question) # 숫자 띄어쓰기 표준화

    question = predefined_replaces(question)

    return question

# %%
def find_candidates(raw):
    literals = []
    matches = []

    def re_list(expr):
        return expr + '([, ]+(' + expr + '))+'

    # raw = predefined_replaces(raw)

    # re_number = '(([0-9]+(\.[0-9]+)?)|([0-9]+[/][0-9]+))'
    re_number = '[0-9]+(\.[0-9]+)?(\/[0-9]+(\.[0-9]+)?)?'
    for match in re.compile(re_number).finditer(raw):
        literal = dict(text=match.group(), span=match.span(), type='수', code='$a=' + match.group())
        # n = Node(match.group(), match.span(), '<$a:숫자>', ['$a=' + match.group()])
        literals.append(literal)
    for match in re.compile(re_list(re_number)).finditer(raw):
        # reg = find_regularities('[' + match.group() + ']')
        # n = Node(match.group(), match.span(), '<$a:수열>', ['$a=' + reg])
        literal = dict(text=match.group(), span=match.span(), type='수열', code='$a=[' + match.group() + ']')

        # n = Node(match.group(), match.span(), '<$a:수열>', ['$a=[' + match.group() + ']'])
        # reg = find_regularities(match.group())
        # if reg:
            # n.statements.append(f'init:reg={reg}')
        literals.append(literal)

    # re_number_or_indicator = '(([0-9]+(\.[0-9]+)?(\/[0-9]+(\.[0-9]+)?)?)|([A-Z]))'
    # for match in re.compile(re_list(re_number_or_indicator)).finditer(raw):
    #     matches = re.compile('[A-Z]').findall(match.group())
    #     if not matches:
    #         continue
    #     reg = find_regularities(match.group())
    #     if not reg:
    #         continue
    #     n = Node(match.group(), match.span(), '<$a:수열>', [f'$a={reg}'])
    #     n.statements.append(f'init:reg={reg}')
    #     elements = [x.strip() for x in match.group().split(',')]
    #     for idx, item in enumerate(elements):
    #         if len(item) == 1 and 'A' <= item and item <= 'Z':
    #             n.statements.append(f'values["{item}"]=reg({idx})')
    #     # n = Node(match.group(), match.span(), '<$a:수열>', ['$a=[' + match.group() + ']'])
    #     # reg = find_regularities(match.group())
    #     # if reg:
    #         # n.statements.append(f'init:reg={reg}')
    #     literals.append(n)

    # re_indicator = '(\()([가나다라마바사아자차카타파하])(\))'
    # for match in re.compile(re_indicator).finditer(raw):
    #     n = Node(match.group(2), match.span(), '<$a:지시자>')
    #     n.statements = [f'values:{match.group(2)}', f'init:indicators.add("{match.group(2)}")', f'$a="{match.group(2)}"']
    #     literals.append(n)
    # for match in re.compile(re_list(re_indicator)).finditer(raw):
    #     n = Node(match.group(), match.span(), '<$a:지시자들>', [])
    #     inds = []
    #     for m in re.compile('(\()([가나다라마바사아자차카타파하])(\))').finditer(match.group()):
    #         n.statements.append(f'values:{m.group(2)}')
    #         n.statements.append(f'init:indicators.add("{m.group(2)}")')
    #         inds.append(m.group(2))
    #     n.statements.append('$a=[' + ','.join(['"' + x + '"' for x in inds]) + ']')
    #     literals.append(n)

    # re_variable = '[A-Z]'
    # for match in re.compile(re_variable).finditer(raw):
    #     n = Node(match.group(), match.span(), '<$a:미지수>', [])
    #     n.statements = [f'values:{match.group()}', f'$a="{match.group()}"']
    #     literals.append(n)
    # # for match in re.compile(re_list(re_variable)).finditer(raw):
    # #     matches.append(('<미지수들>', match.span(), match.group()))

    # re_mixed_term = '[0-9A-Z]*[A-Z][0-9A-Z]*' # 미지수가 최소 하나 이상 섞여 있는 항

    # re_equation = '[0-9A-Z][0-9A-Z\.\+\-\*\/=<> ]*[0-9A-Z]' # 등호(=)를 포함하는 식
    # for match in re.compile(re_equation).finditer(raw):
    #     if match.group().count('=') + match.group().count('<') + match.group().count('>') != 1:
    #         continue
    #     n = Node(match.group(), match.span(), '<$a:등식>', [])
    #     for m in re.compile(re_variable).finditer(match.group()):
    #         n.statements.append(f'values:{m.group()}')
    #     eq = match.group().replace('=','==')
    #     vars = set()
    #     for mixed in re.compile(re_mixed_term).finditer(match.group()):
    #         if len(mixed.group()) > 1:
    #             for m in re.compile(re_variable).finditer(mixed.group()):
    #                 vars.add(m.group())
    #     for v in vars:
    #         n.statements.append(f'values["{v}"]%=10')
    #         # n.statements.append(f'condition:0<=values["{v}"] and values["{v}"]<=9')
    #     eq = re.sub(re_mixed_term, replace_term, eq) # 숫자-미지수가 섞여 있는 항 처리
    #     n.statements.append(f'condition:{eq}')
    #     literals.append(n)
    # # for match in re.compile(re_list(re_equation)).finditer(raw):
    #     # matches.append(('<미지수들>', match.span(), match.group()))

    # for match in re.compile('[0-9A-Z\(][0-9A-Z\(\)\.\+\-\*\/ ]*[0-9A-Z\)]').finditer(raw):
    #     n = Node(match.group(), match.span(), '<$a:수식>', [])
    #     for m in re.compile(re_variable).finditer(match.group()):
    #         n.statements.append(f'values:{m.group()}')
    #     vars = set()
    #     for mixed in re.compile(re_mixed_term).finditer(match.group()):
    #         if len(mixed.group()) > 1:
    #             for m in re.compile(re_variable).finditer(mixed.group()):
    #                 vars.add(m.group())
    #     for v in vars:
    #         n.statements.append(f'values["{v}"]%=10')
    #         # n.statements.append(f'condition:0<=values["{v}"] and values["{v}"]<=9')
    #     eq = re.sub(re_mixed_term, replace_term, match.group()) # 숫자-미지수가 섞여 있는 항 처리
    #     n.statements.append(f'$a={eq}')
    #     literals.append(n)

    re_names = '(남준|석진|윤기|호석|지민|태형|정국|민영|유정|은지|유나|어머니|아버지|할아버지|할머니|손자|손녀|조카|이모|삼촌|동생|형|누나|오빠|언니)'
    for match in re.compile(re_names).finditer(raw):
        if match.span()[0] > 0 and raw[match.span()[0]-1] != ' ':
            continue
        literal = dict(text=match.group(), span=match.span(), type='사람', code=f'$a="{match.group()}"')
        # n = Node(match.group(), match.span(), '<$a:사람>', [])
        # n.statements = [f'values:{match.group()}', f'init:people.add("{match.group()}")', f'$a="{match.group()}"']
        literals.append(literal)
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

    return literals

# %%
def find_literals(rawtext):
    literals = []
    candidates = find_candidates(rawtext)
    last_pos = len(rawtext)
    for c in sorted(candidates, key=lambda x: (x['span'][1], -x['span'][0]), reverse=True): # greedy selection, for now
        if c['span'][0] < last_pos:
            literals.insert(0, c)
            last_pos = c['span'][0]
    return
