
import re
import wordsim
from node import Node

# %%
def get_sentences(question):
    end_of_phrases = '[^0-9a-zA-Z\(\)][\.\?][ ]'
    phrases = []
    pos = 0
    for x in re.compile(end_of_phrases).finditer(question):
        phrases.append(question[pos:x.span()[1]])
        pos = x.span()[1]
    if pos != len(question):
        phrases.append(question[pos:])
    return [x.strip() for x in phrases]

def get_phrases(question):
    # end_of_phrases = '.+면,|.+며,|.+고,|.+때,|.+다\. |.+오\.|.+\. |.+$'
    # end_of_phrases = '.+?면,|.+?며,|.+?고,|.+?때,|.+?다\.|.+?오\.|.+?\. |.+?$'
    end_of_phrases = '[^0-9a-zA-Z\(\)][\,\.\?][ ]'
    phrases = []
    pos = 0
    for x in re.compile(end_of_phrases).finditer(question):
        phrases.append(question[pos:x.span()[1]])
        pos = x.span()[1]
    if pos != len(question):
        phrases.append(question[pos:])
    return [x.strip() for x in phrases]

# %%
# 문장에서 가능한 파싱을 계속 yield해주는 함수
# 일단 단순하게 몇 가지 경우로 구현
def generate(question):
    # 1. 문장 전체로 매칭
    root = Node(question)
    root.match_predefined()
    _, matching_score = root.do_pattern_match()
    yield root, matching_score

    # 2. 일단 문장별로 나누고 문장을 쪼개서 매칭
    matching_score = 0
    root = Node(question)
    for sentence in get_sentences(question):
        best_nodes, best_score = [], float('inf')

        # sentence 전체로 매칭
        whole = Node(sentence)
        whole.match_predefined()
        pattern, score = whole.do_pattern_match()
        # print(f'whole {sentence} {score}')
        if pattern:
            best_nodes, best_score = [whole], score

        # sentence를 나누어서 매칭
        words = sentence.split(' ')
        for i in range(1, len(words)):
            left = Node(' '.join(words[:i]))
            left.match_predefined()
            _, score_left = left.do_pattern_match()
            right = Node(' '.join(words[i:]))
            right.match_predefined()
            _, score_right = right.do_pattern_match()
            if score_left + score_right < best_score:
                best_nodes, best_score = [left, right], score_left + score_right

        # 최적의 매칭을 파싱 트리에 추가
        for node in best_nodes:
            root.children.append([None, 0, 0, node])
        matching_score = matching_score + best_score

    yield root, matching_score

    # 3. 일단 phrase별로 나누고 그 안에서 다시 쪼개서 매칭
    matching_score = 0
    root = Node(question)
    for phrase in get_phrases(question):
        best_nodes, best_score = [], float('inf')

        # phrase 전체로 매칭
        whole = Node(phrase)
        whole.match_predefined()
        pattern, score = whole.do_pattern_match()
        if pattern:
            best_nodes, best_score = [whole], score

        # phrase를 나누어서 매칭
        words = phrase.split(' ')
        for i in range(1, len(words)):
            left = Node(' '.join(words[:i]))
            left.match_predefined()
            _, score_left = left.do_pattern_match()
            right = Node(' '.join(words[i:]))
            right.match_predefined()
            _, score_right = right.do_pattern_match()
            if score_left + score_right < best_score:
                best_nodes, best_score = [left, right], score_left + score_right

        # 최적의 매칭을 파싱 트리에 추가
        for node in best_nodes:
            root.children.append([None, 0, 0, node])
        matching_score = matching_score + best_score

    yield root, matching_score
