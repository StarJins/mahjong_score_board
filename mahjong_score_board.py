from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from decimal import Decimal
import gspread
import gspread.utils
import json
import exception_class
import traceback

class MahjongScoreBoardController:
    def insertMahjongScore(self, input_data):
        # 마작 점수표 업데이트

        # 변수 설정
        _, score_list, _, convert_input_data = self.__paringInputData(input_data)

        # 점수 합이 100000점인지 확인
        total_score = 0
        for score in score_list:
            total_score += int(score)

        if total_score != 100000:
            raise exception_class.invalidTotalScore('마작 점수 총 합은 100,000이여야 합니다. 점수를 확인해 주세요.(현재: {})'.format(total_score))

        # 구글 시트 접속
        spreadsheet = self.__openSpreadsheet()
        sheet = spreadsheet.worksheet('마작 점수표')
        total_row_index = len(sheet.get_all_values())
        total_row_index += 1

        # 마작 점수표 sheet 셀 순서
        # A: 날짜, B: 마작 점수
        insert_data = []

        # A: 날짜
        date = datetime.today()
        ymd = '{}-{}-{}'.format(date.year, date.month, date.day)
        insert_data.append(ymd)

        # B: 마작 점수
        insert_data.append(convert_input_data)

        # data 입력
        sheet.append_row(values=insert_data, value_input_option=gspread.utils.ValueInputOption.user_entered)

    def insertUmaScore(self, input_data):
        # 우마 점수표 업데이트

        # 변수 설정
        wind, score_list, name_list, _ = self.__paringInputData(input_data)

        # 구글 시트 접속
        spreadsheet = self.__openSpreadsheet()
        sheet = spreadsheet.worksheet('우마 점수표')
        total_row_index = len(sheet.get_all_values())
        total_row_index += 1

        # 우마 점수표 sheet 셀 순서
        # A: 날짜, B: 우마 점수
        insert_data = []

        # A: 날짜
        date = datetime.today()
        ymd = '{}-{}-{}'.format(date.year, date.month, date.day)
        insert_data.append(ymd)

        # B: 우마 점수
        # 원투 우마 점수 상수화
        ONE_TWO_UMA_SCORE = { '반장' : { 1 : '20', 2 : '10', 3 : '-10', 4 : '-20' }, '동장' : { 1 : '10', 2 : '5', 3 : '-5', 4 : '-10' } }

        # 마작 점수 + 원투우마 순으로 정렬
        # 이때 마작 점수가 동점인 경우, 동남서북 순서로 원투우마 기록
        result_score = {}
        priority_idx = 1
        for idx in range(4):
            result_score[name_list[idx]] = [str(Decimal(str(int(score_list[idx]) - 25000)) / Decimal('1000')), priority_idx]
            priority_idx += 1
        # -item[1][0] -> score(내림차순), item[1][1] -> priority_idx(오름차순), tuple로 만들어서 이중 정렬 구현
        result_score = dict(sorted(result_score.items(), key = lambda item : (-float(item[1][0]), float(item[1][1]))))

        rank = 1
        for key in result_score.keys():
            result_score[key].append(rank)
            rank += 1

        # result_score의 element 한 개 구조 -> [우마점수, priority, 랭킹]
        for key in result_score.keys():
            result_score[key][0] = str(Decimal(result_score[key][0]) + Decimal(ONE_TWO_UMA_SCORE[wind][result_score[key][2]]))

        total_uma = '0'
        for key in result_score.keys():
            total_uma = str(Decimal(total_uma) + Decimal(result_score[key][0]))

        if Decimal(total_uma) != Decimal('0'):
            raise exception_class.invalidUmaTotalScore('우마 총 합은 0이여야 합니다. 점수를 확인해 주세요.(현재: {})'.format(total_uma))

        convert_input_data = wind
        for i in range(4):
            convert_input_data += " " + name_list[i] + " " + result_score[name_list[i]][0]
        insert_data.append(convert_input_data)

        # data 입력
        sheet.append_row(values=insert_data, value_input_option=gspread.utils.ValueInputOption.user_entered)

    def updateRawData(self):
        # 랭킹용 raw data 업데이트

        # 구글 시트 접속
        spreadsheet = self.__openSpreadsheet()
        sheet = spreadsheet.worksheet('우마 점수표')
        uma_datas = sheet.get_all_values()

        each_total_uma_scores = {}
        for uma_data in uma_datas[1:]:
            _, uma_list, name_list, _ = self.__paringInputData(uma_data[1])
            for idx in range(4):
                if not name_list[idx] in each_total_uma_scores:
                    each_total_uma_scores[name_list[idx]] = '0'

                each_total_uma_scores[name_list[idx]] = str(Decimal(each_total_uma_scores[name_list[idx]]) + Decimal(uma_list[idx]))

        each_total_uma_scores = dict(sorted(each_total_uma_scores.items(), key=lambda x: float(x[1]), reverse=True))

        sheet = spreadsheet.worksheet('순위')

        row_index = 2
        for name, uma in each_total_uma_scores.items():
            cell_index = 'A{}'.format(row_index)
            value = row_index - 1
            sheet.update(cell_index, value, value_input_option=gspread.utils.ValueInputOption.user_entered)

            cell_index = 'B{}'.format(row_index)
            value = name
            sheet.update(cell_index, value, value_input_option=gspread.utils.ValueInputOption.user_entered)

            cell_index = 'C{}'.format(row_index)
            value = uma
            sheet.update(cell_index, value, value_input_option=gspread.utils.ValueInputOption.user_entered)

            row_index += 1
        return

    def getRanks(self):
        spreadsheet = self.__openSpreadsheet()
        sheet = spreadsheet.worksheet('순위')
        ranks = sheet.get_all_records()

        return ranks

    def getMahjongScoreData(self):
        spreadsheet = self.__openSpreadsheet()
        sheet = spreadsheet.worksheet('마작 점수표')
        scores = sheet.get_all_records()

        return scores

    def getUmaScoreData(self):
        spreadsheet = self.__openSpreadsheet()
        sheet = spreadsheet.worksheet('우마 점수표')
        scores = sheet.get_all_records()

        return scores

    def __openSpreadsheet(self):
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

    def __paringInputData(self, input_data):
        split_input_data = input_data.split()
        if len(split_input_data) != 9:
            raise exception_class.invalidInput

        wind = self.__setWind(split_input_data[0])
        name_list = [self.__getFullName(split_input_data[1]), self.__getFullName(split_input_data[3]), self.__getFullName(split_input_data[5]), self.__getFullName(split_input_data[7])]
        score_list = [split_input_data[2], split_input_data[4], split_input_data[6], split_input_data[8]]

        convert_input_data = wind
        for i in range(4):
            convert_input_data += " " + name_list[i] + " " + score_list[i]

        return wind, score_list, name_list, convert_input_data

    def __getFullName(self, name):
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
        elif name in '서준석':
            return '서준석'
        elif name in '김인태':
            return '김인태'
        else:
            return name

    def __setWind(self, wind):
        if wind == '동장' or wind == '동풍' or wind == '동':
            return '동장'
        elif wind == '반장' or wind == '반' or wind == '남' or wind == '남풍' or wind == '남장':
            return '반장'
        else:
            raise exception_class.invalidWind

if __name__ == '__main__':
    try:
        controller = MahjongScoreBoardController()
        # print('점수 입력(ex: 반장 인 20000 홍 20000 진 20000 준 40000)')
        # print('사람/점수는 동남서북 순으로 입력')
        # test_input_score = input()
        # controller.insertMahjongScore(test_input_score)
        # controller.insertUmaScore(test_input_score)
        # controller.updateRawData()
        # ranks = controller.getRanks()
        # print(ranks)

        print(controller.getMahjongScoreData())
        print(controller.getUmaScoreData())

    except ValueError as e:
        print(e)
        print('형식에 맞춰 점수를 숫자로 입력해 주세요.')
    except Exception as e:
        print(e)
    except:
        traceback.print_exc()