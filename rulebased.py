
import re

# 바르게 계산하는 유형
def case_correct(q):
    return None, []

def match(question):
    if '바르게' in question:
        return case_correct(question)
    return None, []
