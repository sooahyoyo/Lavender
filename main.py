from settings import TOKEN, guild_num, sheet_code, json_file
import random
import discord
from discord.ext import tasks, commands
from bs4 import BeautifulSoup
import gspread
import pprint
import time
import random
import datetime, requests, json, random
from datetime import timedelta, timezone
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
    then = now.replace(hour=1, minute=53, second=0)
    wait_time = (then-now).total_seconds()
    await asyncio.sleep(wait_time)
    channel = client.get_channel(1205897511689257063)
    await channel.send("test")

    # wait for some time
    # send a message
    # wait for some time
    # send a message

    


                 
client.run(TOKEN)
