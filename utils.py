# %%
import re

re_var = re.compile(r'((@[ns]?|#|\$)[0-9]+)(\D|$)')
re_number = re.compile(r'[0-9]+([.][0-9]+)?(/[0-9]+([.][0-9]+)?)?')
re_string = re.compile(r'\(\w\)')
re_equation = re.compile('[0-9A-Z][0-9A-Z\.\+\-\*\/\(\)=<> ]*=[0-9A-Z\.\+\-\*\/\(\)=<> ]*[0-9A-Z]') # 등호(=)를 포함하는 식

def predefined_replaces(raw):
    raw = raw.strip()

    raw = re.sub(r'×', '*', raw)
    raw = re.sub(r'÷', '/', raw)

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
        
    # raw = re.sub(r'\b몇개', '몇 개', raw)

    # raw = re.sub(r'\b어떤 수', '어떤수', raw)
    raw = re.sub(r'\b몇 개가 있습니까?', '몇 개입니까?', raw)
    raw = re.sub(r'\b무슨 색깔입니까?', '무슨 색입니까?', raw)

    raw = re.sub(r'세요.$', '시오.', raw)
    raw = re.sub(r'인가[요]?[\.\?]$', '입니까?', raw)
    raw = re.sub(r'일까[요]?[\.\?]$', '입니까?', raw)
    raw = re.sub(r'할까[요]?[\.\?]$', '합니까?', raw)

    return raw

def preprocess(question):
    def replace_space(m):
        return m.group(1) + m.group(3)
    question = re.sub('([0-9])( )(\w)', replace_space, question) # 숫자 띄어쓰기 표준화

    question = predefined_replaces(question)

    return question

# 템플릿 매칭에서 pruning에 사용될 값 계싼
def pruning_vector(q):
    vector = [False] * 6
    vector[0] = re.search('[A-Z]', q) != None
    vector[1] = re.search('바르게', q) != None
    vector[2] = re.search('어떤 수|어떤수', q) != None
    vector[3] = re.search('누구|누가', q) != None
    vector[4] = re.search('도형|각형|면체|모서리|꼭지점', q) != None
    vector[5] = re.search('몇 번째|몇번째', q) != None
    return vector

# purning 조건, 위에서 계산한 pruning vector가 완전히 일치하지 않으면 prune
def is_pruning(v1, v2):
    if v1 != v2:
        return True
    return False

# re_number = re.compile(r'[0-9]+([.][0-9]+)?(/[0-9]+([.][0-9]+)?)?')
re_variable = re.compile(r'[A-Z]')

def literal_type(str):
    global re_number
    global re_variable
    if '=' in str:
        return 'equation'
    elif re_number.fullmatch(str):
        return 'number'
    elif re_variable.fullmatch(str):
        return 'variable'
    else:
        return 'string'

def 받침판단기(word):    #아스키(ASCII) 코드 공식에 따라 입력된 단어의 마지막 글자 받침 유무를 판단해서 뒤에 붙는 조사를 리턴하는 함수
    last = word[-1]     #입력된 word의 마지막 글자를 선택해서
    criteria = (ord(last) - 44032) % 28     #아스키(ASCII) 코드 공식에 따라 계산 (계산법은 다음 포스팅을 참고하였습니다 : http://gpgstudy.com/forum/viewtopic.php?p=45059#p45059)
    if criteria == 0:       #나머지가 0이면 받침이 없는 것
        return '와 or 를'
    else:                   #나머지가 0이 아니면 받침 있는 것
        return '과 or 을'

def compare_ending(e1, e2):
    if e1 == '과':
        e1 = '와'
    if e2 == '과':
        e2 = '와'
    if e1 == '을':
        e1 = '를'
    if e2 == '을':
        e2 = '를'
    if e2 == '은':
        e2 = '는'
    if e2 == '은':
        e2 = '는'
    return e1 == e2

re_noun_ending = re.compile(r'^(높이|넓이|겉넓이|하와이|떡볶이|올챙이|\w+?)(은|는|이가|이는|이|가|에게|을|를|의|으로|에|에는|중에서|마다|이고|입니다|이다)?([,.]?)$')
def remove_ending(word):
    # if word in ['높이', '하와이', '떡볶이', '올챙이']:
        # return word
    return re_noun_ending.sub(r'\1', word)

regexp_num = r'((\d+([.]\d+)?)((/)(\d+([.]\d+)?))?)'
re_numbers = re.compile(r'(' + regexp_num + r'(\D*)([ ]*,[ ]*' + regexp_num + r'(\9)){2,})')
re_strings = re.compile(r'(([^\d\W]+)([ ]*,[ ]*[^\d\W]+){2,})')
re_word_word_list = re.compile(r'(([^\d\W]+\s([^\d\W]+))([ ]*,[ ]*[^\d\W]+\s\3){2,})')

def extract_lists(q):
    results = dict()

    global re_numbers
    numbers = re_numbers.findall(q)
    if numbers:
        items = re.findall(regexp_num, numbers[0][0])
        # results['numbers'] = [float(x[1])/(1 if x[5] == '' else float(x[5])) for x in items]
        results['numbers'] = [eval(x[0]) for x in items]
        q = q.replace(numbers[0][0], '@numbers').strip()

    global re_strings
    strings = re_strings.findall(q)
    if strings:
        items = re.findall(r'\w+', strings[0][0])
        results['strings'] = [x for x in items]
        results['strings'][-1] = remove_ending(results['strings'][-1])
        q = q.replace(strings[0][0], '@strings').strip()

    strings = re_word_word_list.findall(q)
    if strings:
        items = re.findall(r'(\w+)\s' + re.escape(strings[0][2]), strings[0][0])
        results['strings'] = items
        q = q.replace(strings[0][0], '@strings').strip()

    return results, q

regexp_num = r'(\d+([.]\d+)?(/\d+([.]\d+)?)?)'
regexp_wordspacenum = r'((\S+)\s' + regexp_num + r')'
regexp_wordspacenums = r'(' + regexp_wordspacenum + r'(\D*)([ ]*,[ ]*' + regexp_wordspacenum + r'(\8)){2,})'
re_wordspacenums = re.compile(regexp_wordspacenums)
regexp_word_object_num_unit = r'(([^\d\W]+)\s([^\d\W]+)\s' + regexp_num + r'(\D*))'
regexp_word_object_num_unit_following = r'(([^\d\W]+)\s(\4)\s' + regexp_num + r'(\9))'
regexp_word_object_num_unit_repeat = r'(' + regexp_word_object_num_unit + r'([ ]*,[ ]*' + regexp_word_object_num_unit_following + r'){2,})'
re_word_object_num_unit_repeat = re.compile(regexp_word_object_num_unit_repeat)
def extract_mapping(q):
    results = dict()

    global re_wordspacenums
    mapping = re_wordspacenums.findall(q)
    if mapping:
        items = re.findall(regexp_wordspacenum, mapping[0][0])
        for item in items:
            results[item[1]] = eval(item[2])
        q = q.replace(mapping[0][0], '@mapping').strip()

    global re_word_object_num_unit_repeat
    mapping = re_word_object_num_unit_repeat.findall(q)
    if mapping:
        object = mapping[0][3].strip()
        unit = mapping[0][8].strip()
        # print(object)
        # print(unit)
        items = re.findall(r'(\w+)\s' + re.escape(object) + r'\s' + regexp_num + re.escape(unit), mapping[0][0])
        for item in items:
            results[item[0]] = eval(item[1])
        q = q.replace(mapping[0][0], '@mapping').strip()

    return results, q

def extract_equations(q):
    re_equation = '[0-9A-Z][0-9A-Z\.\+\-\*\/\(\)=<> ]*=[0-9A-Z\.\+\-\*\/\(\)=<> ]*[0-9A-Z]' # 등호(=)를 포함하는 식
    equations = re.findall(re_equation, q)
    for eq in equations:
        q = q.replace(eq, '').strip(' ,')
    return equations, q

q = '4장의 수 카드 4.22개, 5/2명,6.1/2.2,8 한 번씩만 사용하여 (두 자리 수)×(두 자리 수)를 만들 때 곱이 가장 작은 경우를 계산하세요.'
q = '정국이는 3개, 영진이는 2개 사탕을 가지고 있습니다.'
q = '수연이는 가로에 3칸, 세로에 2칸인 붕어빵 틀로 붕어빵을 만들려고 합니다. 수연이가 한 번에 만들 수 있는 붕어빵은 모두 몇 개일까요?'
q = '가현이는 친구들에게 빨간 구슬 5개, 노란 구슬 3개, 초록 구슬 14개, 검정 구슬 2개를 빌렸습니다. 총 몇 개의 구슬을 빌렸나요?'
q = '방과후 교실 수업 신청자는 통기타 71명, 요리 19명, 풋살 13명, 농구 6명, 컴퓨터교실 13명입니다. 어느 수업이 가장 인기가 많습니까?'
q = '각 학생들이 게임에서 얻은 점수는 다음과 같습니다. 승연 98.11/22.22점, 호성 78점, 권영 89점입니다. 가장 높은 점수를 얻은 학생은 누구입니까?'
q = '정국, 시형, 태형, 유정, 윤기는 한 팀이 되어 이어달리기 경기를 하고 있습니다. 각 팀의 선수는 순서대로 2번씩 달릴 때, 8번째로 달리는 사람은 누구인가요?'
q = '흰색 차, 검은색 차, 보라색 차, 초록색 차, 빨간색 차가 1개씩 있습니다. 이 차 중 서로 다른 2대의 차를 골라 여행을 가려고 합니다. 고르는 방법은 모두 몇 가지입니까?'
q = '우리학교 운동회에서 6학년, 5학년, 4학년, 1학년, 2학년, 3학년 순서로 경기를 진행합니다. 네번째로 경기를 하는 학년은 몇 학년입니까?'
q = '방과후 교실 수업 신청자는 통기타 7명, 요리 19명, 풋살 13명, 농구 6명, 컴퓨터교실 13명입니다. 어느 수업이 가장 인기가 많습니까?'
q = '546/11, 167.22, 393.22/33.44, 283, 181의 5개의 수 중에서 두 수를 골라 차를 구했을 때 차가 두 번째로 크게 되는 식을 세우고 답을 구하세요.'
q = '각 학생들이 게임에서 얻은 점수는 다음과 같습니다. 승연 98점, 호성 78점, 권영 89점, 두혁 91점입니다. 가장 높은 점수를 얻은 학생은 누구입니까?'
q = 'A75+2BC=993일 때, A-B의 값은 얼마입니까?'
q = '무지개는 일반적으로 빨강색, 주황색, 노랑색, 초록색, 파랑색, 남색, 보라색으로 표현 됩니다. 다섯번째 색깔은 무엇인가요?'

def extract_predefined_patterns(q):
    q = preprocess(q)
    lists, q = extract_lists(q)
    mapping, q = extract_mapping(q)
    equations, q = extract_equations(q)

    return dict(lists=lists, mapping=mapping, equations=equations), q

if __name__=="__main__": # 모듈 단독 테스트
    predefined_patters, q = extract_predefined_patterns(q)
    print(predefined_patters)
    print(q)

    
