from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import gspread
import gspread.utils
import json
import exception_class
import traceback

def openSpreadsheet():
    with open('info.json', 'r', encoding='UTF-8') as json_file:
        info = json.load(json_file)

        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/drive']

        creds = ServiceAccountCredentials.from_json_keyfile_name(info['keyFile'], scope)

        spreadsheet_name = info['spreadsheetName']
        client = gspread.authorize(creds)
        spreadsheet = client.open(spreadsheet_name)
        
        return spreadsheet

def printRank():
    spreadsheet = openSpreadsheet()
    sheet = spreadsheet.worksheet('순위')
    ranks = sheet.get_all_records()
    
    # 순위, 이름, 점수
    for key in ranks[0].keys():
        print(key, end = '\t')
    print()

    # 각 해당하는 값
    for rank in ranks:
        for value in rank.values():
            print(value, end = '\t')
        print()

def getFullName(name):
    if name in '권혁규':
        return '권혁규'
    elif name in '김동현' or name in '마산':
        return '김동현'
    elif name in '김재경' or name in '홍':
        return '김재경'
    elif name in '김진태':
        return '김진태'
    elif name in '박인수':
        return '박인수'
    else: # name in '서준석'
        return '서준석'

def getNameIdx(name):
    if name in '권혁규':
        return 2
    elif name in '김동현' or name in '마산':
        return 3
    elif name in '김재경' or name in '홍':
        return 4
    elif name in '김진태':
        return 5
    elif name in '박인수':
        return 6
    elif name in '서준석':
        return 7
    else:
        return -1
    
def getCellAlphaByIdx(idx):
    if idx == 2:
        return 'C'
    elif idx == 3:
        return 'D'
    elif idx == 4:
        return 'E'
    elif idx == 5:
        return 'F'
    elif idx == 6:
        return 'G'
    else: #idx == 7
        return 'H'

def insertMahjongScore(input_data):
    # 마작 점수표 업데이트
    
    # 변수 설정
    split_input_data = input_data.split()
    if len(split_input_data) != 9:
        raise exception_class.invalidInput

    wind = split_input_data[0]
    name_list = [split_input_data[1], split_input_data[3], split_input_data[5], split_input_data[7]]
    score_list = [split_input_data[2], split_input_data[4], split_input_data[6], split_input_data[8]]

    # 구글 시트 접속
    spreadsheet = openSpreadsheet()
    sheet = spreadsheet.worksheet('마작 점수표')
    total_row_index = len(sheet.get_all_values())
    total_row_index += 1
    
    # 마작 점수표 sheet 셀 순서
    # A: 날짜, B: 동장/반장, C: 권, D: 마, E: 재, F: 진, G: 인, H: 준, I: 총합, J: 동남서북
    insert_data = [0 for i in range(10)]
    check_array = [0 for i in range(10)]

    # A: 날짜
    date = datetime.today()
    ymd = '{}-{}-{}'.format(date.year, date.month, date.day)
    insert_data[0] = ymd
    
    # B: 동장/반장
    if wind == '동장' or wind == '동풍' or wind == '동':
        wind = '동장'
    elif wind == '반장' or wind == '반' or wind == '남' or wind == '남풍':
        wind == '반장'
    else:
        raise exception_class.invalidWind
    insert_data[1] = wind

    # C ~ H: 점수 입력
    total_score = 0
    for i in range(4):
        idx = getNameIdx(name_list[i])
        if idx == -1 or check_array[idx] == 1:
            raise exception_class.invalidName
        else:
            insert_data[idx] = score_list[i]
            total_score += int(score_list[i])
            check_array[idx] = 1
            
    # I: 총합
    if total_score != 100000:
        raise exception_class.invalidTotalScore
    insert_data[8] = total_score
    
    # J: 동남서북
    insert_data[9] = '동:{}, 남:{}, 서:{}, 북:{}'.format(getFullName(name_list[0]), getFullName(name_list[1]), getFullName(name_list[2]), getFullName(name_list[3]))
    
    # data 입력
    sheet.append_row(values=insert_data, value_input_option=gspread.utils.ValueInputOption.user_entered)

def insertUmaScore():
    # 우마 점수표 업데이트

    # 구글 시트 접속
    spreadsheet = openSpreadsheet()
    sheet = spreadsheet.worksheet('우마 점수표')
    total_row_index = len(sheet.get_all_values())
    total_row_index += 1
    
    # 우마 점수표 sheet 셀 순서
    # A: 날짜, B: 동장/반장, C: 권, D: 마, E: 재, F: 진, G: 인, H: 준, I: 총합, J: 동남서북
    insert_data = [0 for i in range(10)]
    
    # A: 날짜
    insert_data[0] = "='마작 점수표'!A{}".format(total_row_index)
    
    # B: 동장/반장
    insert_data[1] = "='마작 점수표'!B{}".format(total_row_index)
    
    # C ~ H: 점수 입력
    for idx in range(2, 8):
        insert_data[idx] = """=IF(RANK('마작 점수표'!{col_index}{row_index}, '마작 점수표'!$C{row_index}:$H{row_index}) + COUNTIF('마작 점수표'!$C${row_index}:'마작 점수표'!{col_index}{row_index},'마작 점수표'!{col_index}{row_index}) - 1 = 1, ('마작 점수표'!{col_index}{row_index} / 1000) + IF('마작 점수표'!B{row_index} = "반장", '원투우마'!$A$1, 10), IF(RANK('마작 점수표'!{col_index}{row_index}, '마작 점수표'!$C{row_index}:$H{row_index}) + COUNTIF('마작 점수표'!$C${row_index}:'마작 점수표'!{col_index}{row_index},'마작 점수표'!{col_index}{row_index}) - 1 = 2, ('마작 점수표'!{col_index}{row_index} / 1000) + IF('마작 점수표'!B{row_index} = "반장", '원투우마'!$B$1, 5), IF(RANK('마작 점수표'!{col_index}{row_index}, '마작 점수표'!$C{row_index}:$H{row_index}) + COUNTIF('마작 점수표'!$C${row_index}:'마작 점수표'!{col_index}{row_index},'마작 점수표'!{col_index}{row_index}) - 1 = 3, ('마작 점수표'!{col_index}{row_index} / 1000) + IF('마작 점수표'!B{row_index} = "반장", '원투우마'!$C$1, -5), IF(RANK('마작 점수표'!{col_index}{row_index}, '마작 점수표'!$C{row_index}:$H{row_index}) + COUNTIF('마작 점수표'!$C${row_index}:'마작 점수표'!{col_index}{row_index},'마작 점수표'!{col_index}{row_index}) - 1 = 4, ('마작 점수표'!{col_index}{row_index} / 1000) + IF('마작 점수표'!B{row_index} = "반장", '원투우마'!$D$1, -10), 0))))""".format(col_index=getCellAlphaByIdx(idx),row_index=total_row_index)

    # I: 총합
    insert_data[8] = '=sum(C{row_index}:H{row_index})'.format(row_index=total_row_index)
    
    # J: 동남서북
    insert_data[9] = "='마작 점수표'!J{}".format(total_row_index)

    # data 입력
    sheet.append_row(values=insert_data, value_input_option=gspread.utils.ValueInputOption.user_entered)

def updateRawData():
    # 랭킹용 raw data 업데이트

    # 구글 시트 접속
    spreadsheet = openSpreadsheet()
    sheet = spreadsheet.worksheet('우마 점수표')
    total_row_index = len(sheet.get_all_values())   # 추가된 row index 구하기

    sheet = spreadsheet.worksheet('RAW 데이터')
    
    # 추가된 row index를 총점 계산에 반영
    for idx in range(2, 8):
        cellidx = '{col_index}2'.format(col_index=getCellAlphaByIdx(idx))
        value = "=SUM('우마 점수표'!{col_index}2:{col_index}{row_index})".format(col_index=getCellAlphaByIdx(idx), row_index=total_row_index)
        sheet.update(cellidx, value, value_input_option=gspread.utils.ValueInputOption.user_entered)
    

if __name__ == '__main__':
    try:
        try:
            print('점수 입력(ex: 반장 인 15000 홍 30000 진 20000 준 35000)')
            print('사람/점수는 동남서북 순으로 입력')
            test_input_score = input()
            insertMahjongScore(test_input_score)
        except exception_class.invalidInput as e:
            print(e)
        except exception_class.invalidWind as e:
            print(e)
        except exception_class.invalidName as e:
            print(e)
        except exception_class.invalidTotalScore as e:
            print(e)
        except ValueError as e:
            print(e)
            print('형식에 맞춰 점수를 숫자로 입력해 주세요.')
        else:
            insertUmaScore()
            updateRawData()
            printRank()
    except gspread.exceptions.APIError as e:
        print(e)
    except gspread.exceptions.CellNotFound as e:
        print(e)
    except gspread.exceptions.GSpreadException as e:
        print(e)
    except gspread.exceptions.IncorrectCellLabel as e:
        print(e)
    except gspread.exceptions.InvalidInputValue as e:
        print(e)
    except gspread.exceptions.NoValidUrlKeyFound as e:
        print(e)
    except gspread.exceptions.SpreadsheetNotFound as e:
        print(e)
    except gspread.exceptions.UnSupportedExportFormat as e:
        print(e)
    except gspread.exceptions.WorksheetNotFound as e:
        print(e)
    except:
        traceback.print_exc()