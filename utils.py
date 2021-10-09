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
