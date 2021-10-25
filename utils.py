# %%
import re

import extract

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

    raw = re.sub(r'\b한자리', '1', raw)
    raw = re.sub(r'\b두자리', '2', raw)
    raw = re.sub(r'\b세자리', '3', raw)
    raw = re.sub(r'\b네자리', '4', raw)
    raw = re.sub(r'\b다섯자리', '5', raw)
    raw = re.sub(r'\b여섯자리', '6', raw)
    raw = re.sub(r'\b일곱자리', '7', raw)
    raw = re.sub(r'\b여덟자리', '8', raw)
    raw = re.sub(r'\b아홉자리', '9', raw)
    raw = re.sub(r'\b열자리', '10', raw)

    raw = re.sub(r'\b첫째', '1째', raw)
    raw = re.sub(r'\b둘째', '2째', raw)
    raw = re.sub(r'\b셋째', '3째', raw)
    raw = re.sub(r'\b넷째', '4째', raw)
    raw = re.sub(r'\b다섯째', '5째', raw)
    raw = re.sub(r'\b여섯째', '6째', raw)
    raw = re.sub(r'\b일곱째', '7째', raw)
    raw = re.sub(r'\b여덟째', '8째', raw)
    raw = re.sub(r'\b아홉째', '9째', raw)
        
    raw = re.sub(r'\b첫번째', '1번째', raw)
    raw = re.sub(r'\b두번째', '2번째', raw)
    raw = re.sub(r'\b세번째', '3번째', raw)
    raw = re.sub(r'\b네번째', '4번째', raw)
    raw = re.sub(r'\b다섯번째', '5번째', raw)
    raw = re.sub(r'\b여섯번째', '6번째', raw)
    raw = re.sub(r'\b일곱번째', '7번째', raw)
    raw = re.sub(r'\b여덟번째', '8번째', raw)
    raw = re.sub(r'\b아홉번째', '9번째', raw)

    raw = re.sub(r'\b몇 개가 있습니까?', '몇 개입니까?', raw)
    raw = re.sub(r'\b무슨 색깔입니까?', '무슨 색입니까?', raw)

    raw = re.sub(r'세요.$', '시오.', raw)
    raw = re.sub(r'인가[요]?[\.\?]$', '입니까?', raw)
    raw = re.sub(r'일까[요]?[\.\?]$', '입니까?', raw)
    raw = re.sub(r'할까[요]?[\.\?]$', '합니까?', raw)

    raw = re.sub(r'\b더해야\b', '더하여야', raw)
    raw = re.sub(r'\b더할 것을\b', '더하여야 할 것을', raw)
    raw = re.sub(r'\b더했더니\b', '더하였더니', raw)
    raw = re.sub(r'\b더한 결과가\b', '더하였더니', raw)
    raw = re.sub(r'\b뺐더니\b', '빼었더니', raw)
    raw = re.sub(r'\b뺀 결과가\b', '빼었더니', raw)
    raw = re.sub(r'\b곱해야\b', '곱하여야', raw)
    raw = re.sub(r'\b곱할 것을\b', '곱하여야 할 것을', raw)
    raw = re.sub(r'\b곱했더니\b', '곱하였더니', raw)
    raw = re.sub(r'\b곱한 결과가\b', '곱하였더니', raw)
    raw = re.sub(r'\b나눠야\b', '나누어야', raw)
    raw = re.sub(r'\b나눌 것을\b', '나누어야 할 것을', raw)
    raw = re.sub(r'\b나눴더니\b', '나누었더니', raw)
    raw = re.sub(r'\b나눈 결과가\b', '나누었더니', raw)
    raw = re.sub(r'\b할 것을\b', '하는데', raw)
    raw = re.sub(r'\b하는 것을\b', '하는데', raw)

    raw = re.sub(r'\b실수로\b', '잘못하여', raw)
    raw = re.sub(r'\b실수하여\b', '잘못하여', raw)

    raw = re.sub(r'\b나왔습니다', '되었습니다', raw)

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

otn = dict(zip(['삼', '사', '오', '육', '칠', '팔', '구', '십', '십일', '십이', '십삼', '십사', '십오', '십육', '십칠', '십팔', '십구', '이십'], [str(x) for x in list(range(3,21))]))
def object_to_number(w):
    for key in otn:
        if key in w:
            return otn[key]
    return w

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

q = '546/11, 167.22, 393.22/33.44, 283, 181의 5개의 수 중에서 두 수를 골라 차를 구했을 때 차가 두 번째로 크게 되는 식을 세우고 답을 구하세요.'

def extract_predefined_patterns(q):
    return extract.extract_predefined_patterns(q)

if __name__=="__main__": # 모듈 단독 테스트
    predefined_patters, q = extract_predefined_patterns(q)
    print(predefined_patters)
    print(q)

    
