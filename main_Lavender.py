from settings import TOKEN
import random
import discord
from discord.ext import tasks, commands
from bs4 import BeautifulSoup
import gspread
import pprint
import time
import random
import datetime
from datetime import datetime, timedelta, timezone
import schedule
from gspread_formatting import DataValidationRule, BooleanCondition, set_data_validation_for_cell_range
from collections import Counter
from oauth2client.service_account import ServiceAccountCredentials
from discord import app_commands
import asyncio



def main() : 
    print('##### main 시작')

    intents = discord.Intents.all()
    intents.message_content = True
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)



intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents) # client 생성. 디스코드와 연결



# 콜백 스타일: 콜백은 기본적으로는 무엇인가 일어났을때 호출되는 기능
@client.event # 데코레이터 - 이벤트 등록
async def on_ready(): # 봇이 로깅을 끝내고 여러가지를 준비한 뒤 호출
    print(f'We have logged in as {client.user}')
    await schedule_daily_message()
    
async def schedule_daily_message():
    now = datetime.datetime.now()
    # then = now+datetime.timedelta(days=1)
    then = now.replace(hour=2, minute=10)
    wait_time = (then-now).total_seconds()
    await asyncio.sleep(wait_time)
    channel = client.get_channel(1205354966567624725)
    await channel.send("test")


@client.event
async def on_message(message): # 봇이 메시지를 받았을 때 호출됩니다
    
    if message.author == client.user: # 봇이 보낸 메세지면 무시
        return

    if message.content.startswith('#test'): # 메세지가 #hello로 시작하는 경우 
        await message.channel.send(f'{message.author.mention}, hello, World!') # 답장 x
    elif message.content.startswith('#안녕하세요'): # 메세지가 #안녕하세요 로 시작하는 경우
        await message.channel.send(f'{message.author.display_name}, 안녕하세요!', reference=message) # 답장
    elif message.content.startswith('#다이스'): # 메세지가 dice로 시작하는 경우
        dice_result = str(random.randint(1,100)) # 1~100 랜덤 선택 (1d100)
        await message.channel.send(f'다이스를 굴리자... <{dice_result}>이 나왔다.', reference=message) # 답장 o
    else:
        start = message.content.find('[')
        end = message.content.find(']')
        if (start != -1 and end != -1) and start<end: # [] 조건 찾기. [, ]가 존재해야 하고, 닫는 괄호가 여는 괄호보다 앞에 있으면 안된다.
            mention_keyword = message.content[start+1:end].strip().split('/') # /를 기준으로 나눠 리스트로 저장. 현재 받은 메세지에는 /가 없으므로 그냥 ['다이스'] 로 저장된다. 
            first_keyword = mention_keyword[0].strip()
            if first_keyword == '1d6':
                dice_result = str(random.randint(1,6))
                await message.channel.send(f'다이스를 굴리자... <{dice_result}>이 나왔다.', reference=message) # 답장 o
            elif first_keyword == '1D6':
                dice_result = str(random.randint(1,6))
                await message.channel.send(f'다이스를 굴리자... <{dice_result}>이 나왔다.', reference=message) # 답장 o
            elif first_keyword == '1d20':
                dice_result = str(random.randint(1,20))
                await message.channel.send(f'다이스를 굴리자... <{dice_result}>이 나왔다.', reference=message) # 답장 o
            elif first_keyword == '1D20':
                dice_result = str(random.randint(1,20))
                await message.channel.send(f'다이스를 굴리자... <{dice_result}>이 나왔다.', reference=message) # 답장 o
            elif first_keyword == '1d100':
                dice_result = str(random.randint(1,100))
                await message.channel.send(f'다이스를 굴리자... <{dice_result}>이 나왔다.', reference=message) # 답장 o   
                 
client.run(TOKEN)
