# %%
import re

def predefined_replaces(raw):
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
        
    raw = re.sub(r'\b몇개', '몇 개', raw)

    raw = re.sub(r'\b어떤 수', '어떤수', raw)
    raw = re.sub(r'\b몇 개가 있습니까?', '몇 개입니까?', raw)
    raw = re.sub(r'\b무슨 색깔입니까?', '무슨 색일까요?', raw)

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

re_number = re.compile(r'[0-9]+([.][0-9]+)?(/[0-9]+([.][0-9]+)?)?')
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

regexp_num = r'((\d+([.]\d+)?)((/)(\d+([.]\d+)?))?)'
re_numlist = re.compile(r'(' + regexp_num + r'(,[ ]*' + regexp_num + r')+)')
re_numunitlist = re.compile(r'(' + regexp_num + r'(\D*)([ ]*,[ ]*' + regexp_num + r'(\9))+)')
regexp_wordspacenum = r'(\S+\s\d+([.]\d+)?(/\d+([.]\d+)?)?)'
regexp_wordspacenum_list = r'(' + regexp_wordspacenum + r'(\D*)([ ]*,[ ]*' + regexp_wordspacenum + r'(\6))+)'
re_strings = re.compile(r'((\w+)(,[ ]?\w+)+)')

def extract_lists(q):
    global re_numlist
    global re_numunitlist
    # print(re_numlist.findall(q)[0])
    # print(re_numunitlist.findall(q))
    # print(re.findall(regexp_wordspacenum_list, q))
    # lists = re_strings.findall(q)
    lists = re_numunitlist.findall(q)
    if lists:
        numbers = re.findall(regexp_num, lists[0][0])
        # for num in numbers:
            # if num[5] == '':
                # num[5] = '1'
        return dict(numbers=[float(x[1])/(1 if x[5] == '' else float(x[5])) for x in numbers]), q.replace(lists[0][0], '').strip()
    return dict(), q

def extract_equations(q):
    re_equation = '[0-9A-Z][0-9A-Z\.\+\-\*\/\(\)=<> ]*=[0-9A-Z\.\+\-\*\/\(\)=<> ]*[0-9A-Z]' # 등호(=)를 포함하는 식
    equations = re.findall(re_equation, q)
    for eq in equations:
        q = q.replace(eq, '').strip(' ,')
    return equations, q

q = '4장의 수 카드 4.22개, 5/2명,6.1/2.2,8 한 번씩만 사용하여 (두 자리 수)×(두 자리 수)를 만들 때 곱이 가장 작은 경우를 계산하세요.'
q = '정국이는 3개, 영진이는 2개 사탕을 가지고 있습니다.'
q = '각 학생들이 게임에서 얻은 점수는 다음과 같습니다. 승연 98점, 호성 78점, 권영 89점, 두혁 91점입니다. 가장 높은 점수를 얻은 학생은 누구입니까?'
q = '우리학교 운동회에서 6학년, 5학년, 4학년, 1학년, 2학년, 3학년 순서로 경기를 진행합니다. 네번째로 경기를 하는 학년은 몇 학년입니까?'
q = '방과후 교실 수업 신청자는 통기타 7명, 요리 19명, 풋살 13명, 농구 6명, 컴퓨터교실 13명입니다. 어느 수업이 가장 인기가 많습니까?'
q = '정국, 시형, 태형, 유정, 윤기는 한 팀이 되어 이어달리기 경기를 하고 있습니다. 각 팀의 선수는 순서대로 2번씩 달릴 때, 8번째로 달리는 사람은 누구인가요?'
q = '546/11, 167.22, 393.22/33.44, 283, 181의 5개의 수 중에서 두 수를 골라 차를 구했을 때 차가 두 번째로 크게 되는 식을 세우고 답을 구하세요.'
q = 'A75+2BC=993일 때, A-B의 값은 얼마입니까?'
# q = 'A=16+8×(9-3)÷4, B=30-96÷(2×8)+5, 두 식 중 계산 결과가 더 작은 계산식의 기호를 쓰세요. '
# q2, d = extract_lists(q)
q2, d = extract_equations(preprocess(q))
print(q2)
print(d)

# 문장에서 반복되는 숫자나 표현 분류
#numbers
#strings
#mapping