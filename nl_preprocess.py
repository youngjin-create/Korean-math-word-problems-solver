
import re
from node import Node

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

def preprocess(question):
    def replace_space(m):
        return m.group(1) + m.group(3)
    question = re.sub('([0-9])( )(\w)', replace_space, question) # 숫자 띄어쓰기 표준화

    question = predefined_replaces(question)

    return question
    