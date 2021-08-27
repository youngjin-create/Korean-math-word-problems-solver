
# %%
random_var_name = 0
def get_random_var_name():
    global random_var_name
    random_var_name = random_var_name + 1
    return f'var{random_var_name:03d}'

# %%
# '<x:숫자>'와 같은 입력이 들어왔을 때 (x, 숫자)를 리턴
def get_name_and_type(item):
    # str_types = ['숫자', '수열', '지시자', '지시자들', '미지수', '미지수들', '사람', '사람들', '과목', '과목들']
    pos = item.find(':')
    first, second = (item[1:pos], item[pos+1:-1]) if pos != -1 else ('', item[1:-1])
    return (first, second) if second.upper() == second.lower() else (second, first)

# %%
# mapping = { '$a': 'var22', '$b': 'var33' }
def variable_substitute(statement, mapping):
    # print(statement)
    # print(mapping)
    for m in mapping:
        statement = statement.replace(m, str(mapping[m]))
    return statement
