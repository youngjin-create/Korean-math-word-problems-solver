
import re

# 바르게 계산하는 유형
def case_correct(q):

    return None, []

def match(problem):
    question = problem['question_preprocessed']
    if re.search('어떤 수|어떤수|바르게', question):
        return case_correct(question)
    return None, []
