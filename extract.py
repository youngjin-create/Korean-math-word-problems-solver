# %%
import re
import string

import tagging

re_var = re.compile(r'((@[ns]?|#|\$)[0-9]+)(\D|$)')
re_number = re.compile(r'[-]?[0-9]+([.][0-9]+)?(/[0-9]+([.][0-9]+)?)?')
re_string = re.compile(r'\(\w\)')
re_equation = re.compile('[0-9A-Z][0-9A-Z\.\+\-\*\/\(\)=<> ]*[=<>][0-9A-Z\.\+\-\*\/\(\)=<> ]*[0-9A-Z]') # 등호(=)를 포함하는 식

re_noun_ending = re.compile(r'^(높이|넓이|겉넓이|하와이|떡볶이|올챙이|\w+?)(은|는|이가|이는|이의|이|가|에게|을|를|의|으로|에|에는|중에서|마다|이고|입니다|이다)?([,.]?)$')
def remove_ending(word):
    # if word in ['높이', '하와이', '떡볶이', '올챙이']:
        # return word
    return re_noun_ending.sub(r'\1', word)

regexp_num = r'(([-]?\d+([.]\d+)?)((/)(\d+([.]\d+)?))?)'
re_numbers = re.compile(r'(' + regexp_num + r'(\D*)([ ]*,[ ]*' + regexp_num + r'(\9)){2,})')
re_strings = re.compile(r'(([^\d\W]+)([ ]*,[ ]*[^\d\W]+){2,})')
re_word_word_list = re.compile(r'(([^\d\W]+\s([^\d\W]+))([ ]*,[ ]*[^\d\W]+\s\3){2,})')

def extract_lists(q):
    results = dict()

    global re_numbers
    numbers = re_numbers.findall(q)
    if numbers:
        for idx, nums in enumerate(numbers):
            id = 'numbers' + ('' if len(numbers)==1 else str(idx+1))
            items = re.findall(regexp_num, nums[0])
            results[id] = [eval(x[0].lstrip('0') if len(x[0].lstrip('0'))!=0 else x[0]) for x in items]
            q = q.replace(nums[0], '@' + id).strip()
        q = re.sub(r'^(\w+\s+){1,3}@numbers', '@numbers', q)

    global re_strings
    strings = re_strings.findall(q)
    if strings:
        for idx, strs in enumerate(strings):
            id = 'strings' + ('' if len(strings)==1 else str(idx+1))
            items = re.findall(r'\w+', strs[0])
            alphabets = [remove_ending(x) for x in items if remove_ending(x) in string.ascii_uppercase] # A,B,C 와 같이 영문자로 된 문자열을 strings에 넣지 않는다.
            if len(alphabets) == len(items):
                break
            results[id] = [remove_ending(x) for x in items]
            q = q.replace(strs[0], '@' + id).strip()

    strings = re_word_word_list.findall(q)
    if strings:
        items = re.findall(r'(\w+)\s' + re.escape(strings[0][2]), strings[0][0])
        results['strings'] = items
        q = q.replace(strings[0][0], '@strings').strip()

    return results, q

regexp_num = r'([-]?\d+([.]\d+)?(/\d+([.]\d+)?)?)'
regexp_wordspacenum = r'(([^\d\W]+)\s' + regexp_num + r')'
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
            results[remove_ending(item[1])] = eval(item[2])
        q = q.replace(mapping[0][0], '@mapping').strip()

    global re_word_object_num_unit_repeat
    mapping = re_word_object_num_unit_repeat.findall(q)
    if mapping:
        object = mapping[0][3].strip()
        unit = mapping[0][8].strip()
        # print(object)
        # print(unit)
        items = re.findall(r'([^\d\W]+)\s' + re.escape(object) + r'\s' + regexp_num + re.escape(unit), mapping[0][0])
        for item in items:
            results[remove_ending(item[0])] = eval(item[1])
        q = q.replace(mapping[0][0], '@mapping').strip()

    return results, q

def extract_equations(q):
    re_equation = '[0-9A-Z][0-9A-Z\.\+\-\*\/\(\)=<> ]*[=<>][0-9A-Z\.\+\-\*\/\(\)=<> ]*[0-9A-Z]' # 등호(=)를 포함하는 식
    equations = re.findall(re_equation, q)
    for eq in equations:
        q = q.replace(eq, '@equation') #.strip(' ,')
    return equations, q

def extract_predefined_patterns(q):
    # q = preprocess(q)
    lists, q = extract_lists(q)
    mapping, q = extract_mapping(q)
    if 'numbers' in lists and 'strings' in lists and mapping == {}:
        if len(lists['numbers']) == len(lists['strings']):
            for i in range(0, len(lists['numbers'])):
                mapping[lists['strings'][i]] = lists['numbers'][i]
    equations, q = extract_equations(q)

    return dict(lists=lists, mapping=mapping, equations=equations), q

q = '사과 7개를 서로 다른 2마리의 원숭이에게 나누어 주려고 합니다. 원숭이는 적어도 사과 1개는 받습니다. 사과를 나누어 주는 방법은 모두 몇 가지입니까?'

if __name__=="__main__": # 모듈 단독 테스트
    predefined_patters, q = extract_predefined_patterns(q)
    print(predefined_patters)
    print(q)
