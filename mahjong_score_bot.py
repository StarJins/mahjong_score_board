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
    print('[{}] We have logged in as {}\n'.format(datetime.today(), client))
    print('[{}] Bot name: {}\n'.format(datetime.today(), client.user.name))  # 여기서 client.user는 discord bot을 의미
    print('[{}] Bot ID: {}\n'.format(datetime.today(), client.user.id))

@client.event
async def on_command_error(ctx, error): # 없는 명령어가 입력됐을 때 실행
    await ctx.send('없는 명령어 입니다.')
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
    await ctx.send(ranks)

@client.command(name='링크')    # 구글 스프레드시트 링크 출력
async def showRank(ctx):
    await ctx.send('https://docs.google.com/spreadsheets/d/1H736VRbaNlfG92llYu0I5qZPfkr92-C6w_Q1VBBlzgM/edit?usp=sharing')

@client.command(name='help')
async def showCommand(ctx):
    dict_commands = {
        '명령어' : '설명',
        '!랭킹' : '현재 원투우마 랭킹 출력',
        '!입력 풍 사람1 점수1 사람2 점수2 사람3 점수3 사람4 점수4' : '경기 결과 입력(ex 반장 인 20000 홍 20000 진 20000 준 40000), 사람/점수는 동남서북 순으로 입력',
        '!링크' : '원투우마 엑셀 링크 출력'
    }

    for k, v in dict_commands.items():
        await ctx.send('{} : {}'.format(k, v))

if __name__ == '__main__':
    client.run(token)