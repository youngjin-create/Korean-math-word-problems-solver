
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://www.googleapis.com/auth/spreadsheets']
json_file_name = '/data/shared/credentials/math-word-problem-sheets-8ddc0bf38718.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)

def load_dataset(sheetname):
    global gc
    # 스프레스시트 문서 가져오기 
    doc = gc.open_by_url('https://docs.google.com/spreadsheets/d/11WuamHuk1CkmsaMA4M3AbWiem99e6zcp4d-Au_tp_oc/edit#gid=1073092697')
    # 시트 선택하기
    worksheet = doc.worksheet(sheetname)
    dataset = []
    for row in worksheet.get_all_records(numericise_ignore=['all']):
        row = list(row.values())
        q = dict(id=row[0], type=row[1], question_original=row[2], question=row[3], answer=row[5], equation=row[8], code=row[9], objective=row[10])
        if q['id'] == 'ID' or (q['question_original'] == '' and q['question'] == ''):
            continue
        dataset.append(q)

    return dataset

def save_results(sheetname, results):
    global gc
    doc = gc.open_by_url('https://docs.google.com/spreadsheets/d/1vcFgJ2feBJCg8SGuZLdkbaYU8q2XS0dqqB-vUepp1D8')
    worksheet = doc.add_worksheet(sheetname, 1, 1)
    worksheet.append_row(['ID','문제','tags','predefined patterns','match distance','match template','assignments','statements','비슷한문제ID','풀이과정','풀이답','정답','실행시간'])
    worksheet.append_rows([[str(x) for x in row] for row in results])
