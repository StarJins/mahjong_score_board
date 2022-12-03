from discord.ext import commands
from datetime import datetime
import discord, mahjong_score_board
import json

with open(".discord_bot_token.json", 'r', encoding='UTF-8') as json_file:
    json_data = json.load(json_file)
    token = json_data['botToken']

intents = discord.Intents.default()
intents.presences = True        # 상태표시 변경 권한
intents.message_content = True  # 메세지 컨트롤 권환
client = commands.Bot(command_prefix='!', intents=intents)
client.remove_command('help')   # default help 명령어 삭제

@client.event
async def on_ready():  # on_ready event는 discord bot이 discord에 정상적으로 접속했을 때 실행
    await client.change_presence(status=discord.Status.online)
    print('[{}] We have logged in as {}'.format(datetime.today(), client))
    print('[{}] Bot name: {}'.format(datetime.today(), client.user.name))  # 여기서 client.user는 discord bot을 의미
    print('[{}] Bot ID: {}'.format(datetime.today(), client.user.id))

@client.event
async def on_command_error(ctx, error): # 없는 명령어가 입력됐을 때 실행
    await ctx.send('없는 명령어 입니다.')
    await ctx.send(error)
    await showCommand(ctx)

@client.command(name='입력')    # 마작 점수 입력 함수
async def insertScore(ctx, *args):
    input_score = ' '.join(args)

    await ctx.send('입력중...')
    try:
        boardController = mahjong_score_board.MahjongScoreBoardController()
        boardController.insertMahjongScore(input_score)
        boardController.insertUmaScore(input_score)
        boardController.updateRawData()
    except Exception as e:
        await ctx.send(e)
        await ctx.send('ex 반장 인 20000 홍 20000 진 20000 준 40000')
        await ctx.send('사람/점수는 동남서북 순으로 입력')
    else:
        await ctx.send('입력 완료')

@client.command(name='랭킹')    # 랭킹 출력 함수
async def showRank(ctx):
    await ctx.send('수집중...')
    boardController = mahjong_score_board.MahjongScoreBoardController()
    ranks = boardController.getRanks()

    # ranks raw 데이터
    # [{'순위': 1, '이름': '권혁규', '점수': 0},
    #  {'순위': 2, '이름': '김동현', '점수': 0},
    #  {'순위': 3, '이름': '김재경', '점수': 0},
    #  {'순위': 4, '이름': '김진태', '점수': 0},
    #  {'순위': 5, '이름': '박인수', '점수': 0},
    #  {'순위': 6, '이름': '서준석', '점수': 0}]

    rank_data = ''
    name_data = ''
    score_data = ''
    # 각 col별 데이터 설정
    for rank in ranks:
        rank_data += str(rank['순위']) + '\n'
        name_data += str(rank['이름']) + '\n'
        score_data += str(rank['점수']) + '\n'

    # 테이블 세팅
    embed=discord.Embed(title='전체 순위', color=discord.Color.purple())
    embed.add_field(name='순위', value=rank_data)
    embed.add_field(name='이름', value=name_data)
    embed.add_field(name='점수', value=score_data)
    await ctx.send(embed=embed)

@client.command(name='마작점수')    # 마작 점수 출력
async def showMahjongScore(ctx):
    await ctx.send('수집중...')
    boardController = mahjong_score_board.MahjongScoreBoardController()
    scores = boardController.getMahjongScoreData()
    
    date_data = ''
    wind_data = ''
    person_data = ['', '', '', '', '', '']
    total_score_data = ''
    order_data = ''
    # 각 col별 데이터 설정
    for score in scores:
        date_data += str(score['날짜']) + '\n'
        wind_data += str(score['동장/반장']) + '\n'
        person_data[0] += str(score['권혁규']) + '\n'
        person_data[1] += str(score['김동현']) + '\n'
        person_data[2] += str(score['김재경']) + '\n'
        person_data[3] += str(score['김진태']) + '\n'
        person_data[4] += str(score['박인수']) + '\n'
        person_data[5] += str(score['서준석']) + '\n'
        total_score_data += str(score['총합']) + '\n'
        order_data += str(score['동남서북']) + '\n'
        
    # 테이블 세팅
    embed=discord.Embed(title='마작 점수', color=discord.Color.purple())
    embed.add_field(name='날짜', value=date_data)
    embed.add_field(name='동장/반장', value=wind_data)
    embed.add_field(name='권혁규', value=person_data[0])
    embed.add_field(name='김동현', value=person_data[1])
    embed.add_field(name='김재경', value=person_data[2])
    embed.add_field(name='김진태', value=person_data[3])
    embed.add_field(name='박인수', value=person_data[4])
    embed.add_field(name='서준석', value=person_data[5])
    embed.add_field(name='총합', value=total_score_data)
    embed.add_field(name='동남서북', value=order_data)
    await ctx.send(embed=embed)


@client.command(name='우마점수')    # 우마 점수 출력
async def showMahjongScore(ctx):
    await ctx.send('수집중...')
    boardController = mahjong_score_board.MahjongScoreBoardController()
    scores = boardController.getUmaScoreData()
    
    date_data = ''
    wind_data = ''
    person_data = ['', '', '', '', '', '']
    total_score_data = ''
    order_data = ''
    # 각 col별 데이터 설정
    for score in scores:
        date_data += str(score['날짜']) + '\n'
        wind_data += str(score['동장/반장']) + '\n'
        person_data[0] += str(score['권혁규']) + '\n'
        person_data[1] += str(score['김동현']) + '\n'
        person_data[2] += str(score['김재경']) + '\n'
        person_data[3] += str(score['김진태']) + '\n'
        person_data[4] += str(score['박인수']) + '\n'
        person_data[5] += str(score['서준석']) + '\n'
        total_score_data += str(score['총합']) + '\n'
        order_data += str(score['동남서북']) + '\n'
        
    # 테이블 세팅
    embed=discord.Embed(title='우마 점수', color=discord.Color.purple())
    embed.add_field(name='날짜', value=date_data)
    embed.add_field(name='동장/반장', value=wind_data)
    embed.add_field(name='권혁규', value=person_data[0])
    embed.add_field(name='김동현', value=person_data[1])
    embed.add_field(name='김재경', value=person_data[2])
    embed.add_field(name='김진태', value=person_data[3])
    embed.add_field(name='박인수', value=person_data[4])
    embed.add_field(name='서준석', value=person_data[5])
    embed.add_field(name='총합', value=total_score_data)
    embed.add_field(name='동남서북', value=order_data)
    await ctx.send(embed=embed)

@client.command(name='DB링크')    # 구글 스프레드시트 링크 출력
async def showRank(ctx):
    await ctx.send('https://docs.google.com/spreadsheets/d/1H736VRbaNlfG92llYu0I5qZPfkr92-C6w_Q1VBBlzgM/edit?usp=sharing')

@client.command(name='작혼링크')    # 작혼 주소 출력
async def showRank(ctx):
    await ctx.send('https://game.mahjongsoul.com/index.html')

@client.command(name='help')
async def showCommand(ctx):
    dict_commands = {
        '명령어' : '설명',
        '!랭킹' : '현재 원투우마 랭킹 출력',
        '!마작점수' : '현재 저장된 마작 점수 전체 출력',
        '!우마점수' : '현재 저장된 우마 점수 전체 출력',
        '!입력 풍 사람1 점수1 사람2 점수2 사람3 점수3 사람4 점수4' : '경기 결과 입력(ex 반장 인 20000 홍 20000 진 20000 준 40000), 사람/점수는 동남서북 순으로 입력',
        '!DB링크' : '원투우마 엑셀 링크 출력',
        '!작혼링크' : '작혼주소 출력',
    }

    for k, v in dict_commands.items():
        await ctx.send('{} : {}'.format(k, v))

if __name__ == '__main__':
    client.run(token)