
import utils
import tagging
import re

# 바르게 계산하는 유형
def case_correct(q):

    return None, []

def classify_question_type(problem):
    q = problem['question_preprocessed']

    for word in ['누가', '누구']:
        if word in q:
            return 'string', 'who'

    for word in ['어디', '무엇', '어느']:
        if word in q:
            return None, 'which'

    for word in ['몇 번째', '몇번째', '몇째로']:
        if word in q:
            return 'number', 'rank'
        
    # for word in ['중 가장', '중에서 가장', '가운데 가장']:
    #     if word in q:
    #         return 'string', 'most'

    return None, None

def get_choices(problem):
    q = problem['question_preprocessed']

    koralphabet = set()
    for match in re.findall(r'(^|[( ])(가|나|다|라|마|바|사|아|자|차|카|타|파|하)([) ])', q):
        koralphabet.add(match[1])
    if len(koralphabet) >= 2:
        return koralphabet

    atoz = set()
    for match in re.findall(r'[A-Z]', q):
        atoz.add(match)
    if len(atoz) >= 2:
        return atoz

    q_tags = tagging.pos_tagging(q)
    persons = set()
    for idx in range(0, len(q_tags)):
        if q_tags[idx][1] == 'NNP':
            persons.add(q_tags[idx][0])
    if problem['question_rule_type'][1] == 'who':
        for name in re.findall('(\w\w)이는', q):
            persons.add(name)
    if len(persons) >= 2:
        return persons

    objects = set()
    if 'question_predefined_patterns' in problem and 'lists' in problem['question_predefined_patterns']:
        if 'strings' in problem['question_predefined_patterns']['lists']:
            for s in problem['question_predefined_patterns']['lists']['strings']:
                objects.add(s)
        if 'strings1' in problem['question_predefined_patterns']['lists']:
            for s in problem['question_predefined_patterns']['lists']['strings1']:
                objects.add(s)
        if 'strings2' in problem['question_predefined_patterns']['lists']:
            for s in problem['question_predefined_patterns']['lists']['strings2']:
                objects.add(s)
    if len(objects) >= 2:
        return objects

    objects = set()
    if 'question_predefined_patterns' in problem and 'mapping' in problem['question_predefined_patterns']:
        for s in problem['question_predefined_patterns']['mapping']:
            objects.add(s)
    if len(objects) >= 2:
        return objects

    objects = set()
    for idx in range(0, len(q_tags)):
        if q_tags[idx][1] == 'NNP' or q_tags[idx][1] == 'NNG':
            objects.add(q_tags[idx][0])
    if len(objects) >= 2:
        return objects

    return set()

def choice_type(problem):
    q = problem['question_preprocessed']

    choices = get_choices(problem)
    vars = dict()
    for idx, c in enumerate(choices):
        vars[c] = ''#idx
    varname = ''

    q_tags = tagging.pos_tagging(q)
    for idx in range(0, len(q_tags)):
        if q_tags[idx][0] in choices:
            varname = q_tags[idx][0]
        elif varname != '' and q_tags[idx][1] == 'NUMBER':
            vars[varname] = vars[varname] + '*' + q_tags[idx][0] if vars[varname] != '' else q_tags[idx][0]
    for idx, c in enumerate(choices):
        if vars[c] == '':
            vars[c] = idx*2+3

    code = ''
    objective = 'max(vars, key=vars.get)'
    if '가장' in q:
        if '작은' in q:
            objective = 'min(vars, key=vars.get)'
        else:
            objective = 'max(vars, key=vars.get)'
    else:
        code = 'x = sorted(vars.keys(), key=(lambda k: vars[k]))'
        objective = 'x[len(x)//2]'

    statements = {'equation': [], 'code': [code], 'objective': [objective]}
    for key in vars:
        statements['equation'].append('{}={}'.format(key, vars[key]))

    return 0.0, statements

def match(problem):
    problem['question_preprocessed'] = utils.preprocess(problem['question'])
    problem['is_rule_based'] = True
    q = problem['question_preprocessed']

    # if re.search('어떤 수|어떤수|바르게', q):
    #     return case_correct(q)

    answer_type, question_type = classify_question_type(problem)
    # if answer_type != None and question_type != None:
    problem['question_rule_type'] = (answer_type, question_type)

    if question_type == 'who' or question_type == 'which':
        return choice_type(problem)

    q_tags = tagging.pos_tagging(q)

    names = set()
    if 'question_predefined_patterns' in problem and 'lists' in problem['question_predefined_patterns'] and 'strings' in problem['question_predefined_patterns']['lists']:
        for s in problem['question_predefined_patterns']['lists']['strings']:
            names.add(s)

    for idx in range(0, len(q_tags)):
        if q_tags[idx][1] == 'NNP':
            names.add(q_tags[idx][0])
        # if idx > 0 and q_tags[idx-1][1] == 'NNG' and q_tags[idx][1] == 'SC':
        #     names.add(q_tags[idx-1][0])
        if idx > 0 and q_tags[idx-1][1].startswith('NN') and q_tags[idx][1].startswith('J'):
            names.add(q_tags[idx-1][0])

    if question_type == 'rank':
        statements = {'equation': [], 'code': [], 'objective': ["'순서'"]}
        # statements = {'equation': [], 'code': [], 'objective': ['max(1, len(vars)//2)']}
        for idx, name in enumerate(names):
            statements['equation'].append('{}={}'.format(name, idx))
        return 0.0, statements

    # if question_type == 'most':
    #     statements = {'equation': [], 'code': [], 'objective': ["'객관식'"]}
    #     # statements = {'equation': [], 'code': [], 'objective': ['max(vars, key=vars.get)']}
    #     for idx, name in enumerate(names):
    #         statements['equation'].append('{}={}'.format(name, idx))
    #     return 0.0, statements

    return None, []
