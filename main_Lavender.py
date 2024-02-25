import os

print(os.getcwd())
os.chdir('c:/Users/dudtj/Desktop/라리에/배포용')

#!/usr/bin/python3
# -*- coding: utf-8 -*-
from settings import TOKEN, guild_num, sheet_code, json_file, counter_dice, dodge_dice, no_of_dice, dice_side
import discord
from discord import app_commands
import asyncio
import random
import json
import datetime
from collections import Counter
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gspread_formatting import DataValidationRule, BooleanCondition, set_data_validation_for_cell_range


# 디스코드 세팅 시작
intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
# 디스코드 세팅 끝

guilds = discord.Object(id=guild_num)

# 구글시트 세팅

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)
gc = gspread.authorize(creds)
sh = gc.open_by_key(sheet_code)
char = sh.worksheet("캐릭터")
item = sh.worksheet("아이템")
default = sh.worksheet("기본 설정")
validation_rule = DataValidationRule(BooleanCondition('BOOLEAN', ['TRUE', 'FALSE']), showCustomUi=True, strict=False)

# 구글시트 세팅 끝


def search(ch_id):
    return char.find(str(ch_id), in_column=2).row


def change_money(row, num):
    result = char.cell(row, 10, value_render_option='UNFORMATTED_VALUE').value + num
    char.update_cell(row, 10, result)


def change_plant(row, num):
    result = char.cell(row, 16, value_render_option='UNFORMATTED_VALUE').value + num
    char.update_cell(row, 16, result)


def edit_inven(row_no, it_name, much):
    fetched = char.cell(row_no, 13, value_render_option='UNFORMATTED_VALUE').value
    if fetched == '' or fetched is None:
        inven = []
    else:
        inven = fetched.split(', ')
    if much > 0:
        while much != 0:
            inven.append(it_name)
            much -= 1
    elif much < 0:
        much = abs(much)
        try:
            while much != 0:
                inven.remove(it_name)
                much -= 1
        except ValueError:
            pass
    inven_count = str(Counter(inven)).replace(':', '×')
    for i in ["{", "}", "'", "Counter(", ")"]:
        inven_count = inven_count.replace(i, '')
    inven = str(inven)
    for i in "[]'":
        inven = inven.replace(i, '')
    char.update_cell(row_no, 13, inven)
    char.update_cell(row_no, 11, inven_count)


def get_hp(ch_id):
    return char.cell(search(ch_id), 7, value_render_option='UNFORMATTED_VALUE').value


def get_atk(ch_id):
    return char.cell(search(ch_id), 8, value_render_option='UNFORMATTED_VALUE').value


def get_dfs(ch_id):
    return char.cell(search(ch_id), 9, value_render_option='UNFORMATTED_VALUE').value


def heal(ch_id, num):
    row_no = search(ch_id)
    fetched = (char.get(f'F{row_no}:G{row_no}', value_render_option='UNFORMATTED_VALUE'))[0]
    result = fetched[1] + num
    if result < 0:
        result = 0
    elif result > fetched[0]:
        result = fetched[0]
    else:
        pass
    char.update_cell(row_no, 7, result)


def get_data():
    with open('combat.json', 'r', encoding="UTF-8") as f:
        fetched = json.load(f)
    f.close()

    return fetched


def delete_combat(chan_id):
    combat = get_data()
    del combat[str(chan_id)]
    with open('combat.json', 'w', encoding="UTF-8") as f:
        json.dump(combat, f, indent=4, ensure_ascii=False)
        f.close()


@client.event
async def on_ready():
    await tree.sync(guild=guilds)
    print(f'{client.user} online!')


@tree.command(guild=guilds, description='캐릭터 정보를 시스템에 등록합니다.')
async def 등록(interaction: discord.Interaction):
    await interaction.response.defer()
    to = default.cell(11, 3, value_render_option='UNFORMATTED_VALUE').value
    got = [num[0] for num in char.get(f'B2:B{str(to + 1)}', value_render_option='UNFORMATTED_VALUE')]
    if str(interaction.user.id) in got:
        await interaction.followup.send("이미 등록된 캐릭터입니다.")
    else:
        to = str(to + 2)
        char.append_row(values=[interaction.user.display_name, str(interaction.user.id), 0, 0, 0,
                                f"='기본 설정'!B4+('기본 설정'!B9*C{to})", f"='기본 설정'!B4+('기본 설정'!B9*C{to})",
                                f"='기본 설정'!C4+('기본 설정'!C9*D{to})", f"='기본 설정'!D4+('기본 설정'!D9*E{to})",
                                default.cell(4, 6).value],
                        value_input_option='USER_ENTERED')
        await interaction.followup.send("캐릭터 정보가 등록되었습니다.")


@tree.command(guild=guilds, description=' 주문으로 출석 체크를 합니다. 하루에 1회 사용 가능.')
async def 주문(interaction: discord.Interaction):
    await interaction.response.defer()
    checked = (interaction.created_at + datetime.timedelta(hours=9)).strftime('%Y/%m/%d')
    row_no = search(interaction.user.id)
    if checked == char.cell(row_no, 12).value:
        await interaction.followup.send("이미 오늘 출석했습니다.")
    else:
        reward = default.cell(6, 6, value_render_option='UNFORMATTED_VALUE').value
        char.update_cell(row_no, 12, checked)
        change_money(row_no, reward)
        await interaction.followup.send(f"출석이 완료되었습니다. \n"
                                        f"***소지금 + {reward}***")



@tree.command(guild=guilds, description='아이템을 구매합니다.')
@app_commands.describe(name='구매할 아이템의 이름을 적어주세요.', much='구매할 개수를 적어주세요.')
async def 구매(interaction: discord.Interaction, name: str, much: int):
    await interaction.response.defer()
    try:
        row_no = item.find(name, in_column=1).row
    except:
        await interaction.followup.send("존재하지 않는 아이템입니다.")
        return
    fetched = [n[0] for n in
               item.batch_get([f'B{row_no}:C{row_no}', f'G{row_no}'], value_render_option='UNFORMATTED_VALUE')]
    if fetched[0][0] is False:
        await interaction.followup.send("해당 아이템은 비매품입니다.")
    else:
        row_no = search(interaction.user.id)
        if char.cell(row_no, 10, value_render_option='UNFORMATTED_VALUE').value < fetched[0][1] * much:
            await interaction.followup.send("소지금이 부족합니다.")
        else:
            change_money(row_no, -(much * fetched[0][1]))
            edit_inven(row_no, name, much)
            await interaction.followup.send(f"{name} {much}개를 구매했습니다.\n"
                                            f">>> {fetched[1][0]}")


@tree.command(guild=guilds, description='뽑기를 1회 돌립니다.')
async def 뽑기(interaction: discord.Interaction):
    await interaction.response.defer()
    row_no = search(interaction.user.id)
    cost = default.cell(13, 3, value_render_option='UNFORMATTED_VALUE').value
    if char.cell(row_no, 10, value_render_option='UNFORMATTED_VALUE').value < cost:
        await interaction.followup.send("소지금이 부족합니다.")
    else:
        fetched = item.findall('TRUE', in_column=6)
        if len(fetched) == 0:
            await interaction.followup.send("뽑을 수 있는 아이템이 없습니다.")
        else:
            change_money(row_no, cost)
            fetched = [i.row for i in fetched]
            result = random.choice(fetched)
            fetched = [i[0] for i in item.batch_get([f'A{result}', f'G{result}'],
                                                    value_render_option='UNFORMATTED_VALUE')]
            await interaction.followup.send(f">>> **{fetched[0][0]}** 획득\n"
                                            f"{fetched[1][0]}")
            edit_inven(row_no, fetched[0][0], 1)


@tree.command(guild=guilds, description='아이템을 사용합니다.')
@app_commands.describe(name='사용할 아이템의 이름을 적어주세요.')
async def 사용(interaction: discord.Interaction, name: str):
    await interaction.response.defer()
    row_no = search(interaction.user.id)
    fetched = char.cell(row_no, 13, value_render_option='UNFORMATTED_VALUE').value
    if fetched == '':
        inven = []
    else:
        inven = fetched.split(', ')
    if name in inven:
        it_row = item.find(name, in_column=1).row
        fetched = [i[0] for i in item.batch_get([f'D{it_row}:E{it_row}', f'H{it_row}'],
                                                value_render_option='UNFORMATTED_VALUE')]
        if fetched[0][0] is True:
            edit_inven(row_no, name, 0)
            await interaction.followup.send(f'>>> {fetched[1][0]}')
            if fetched[0][1] != 0:
                heal(interaction.user.id, fetched[0][1])
            else:
                pass
        else:
            await interaction.followup.send("해당 아이템은 /사용 커맨드로 사용할 수 없습니다.")
    else:
        await interaction.followup.send("해당 아이템을 소지하고 있지 않습니다.")


@tree.command(guild=guilds, description='필요없는 소지품 1개를 1메모리로 교환합니다.')
@app_commands.describe(name='교환할 아이템의 이름을 적어주세요.')
async def 교환(interaction: discord.Interaction, name: str):
    await interaction.response.defer()
    row_no = search(interaction.user.id)
    fetched = char.cell(row_no, 13, value_render_option='UNFORMATTED_VALUE').value
    if fetched == '':
        inven = []
    else:
        inven = fetched.split(', ')
    if name in inven:
            reward = default.cell(6, 6, value_render_option='UNFORMATTED_VALUE').value
            change_money(row_no, reward)
            edit_inven(row_no, name, -1)
            await interaction.followup.send(f"{name} 1개를 1메모리로 교환했습니다.\n")
    else:
        await interaction.followup.send("해당 아이템을 소지하고 있지 않습니다.")




class Dice(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.value = None

    @discord.ui.button(label='수용', style=discord.ButtonStyle.primary)
    async def dice1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        result1 = random.randint(1,100)
        result2 = get_atk(interaction.user.id)
        if result1 < result2:
            await interaction.followup.send(f'>>> {interaction.user.display_name}의 수용 판정\n'
                                            f'수용 **__{result2}__** > 주사위 **__{result1}__** 결과 **__성공__**')
        else: 
            if result1 > result2 :
                await interaction.followup.send(f'>>> {interaction.user.display_name}의 수용 판정\n'
                                                f'수용 **__{result2}__** < 주사위 **__{result1}__** 결과 **__실패__**')
            else:
                await interaction.followup.send(f'>>> {interaction.user.display_name}의 수용 판정\n'
                                                f'수용 **__{result2}__** = 주사위 **__{result1}__** 결과 **__성공__**')
        self.value = True
        self.stop()

    @discord.ui.button(label='관찰', style=discord.ButtonStyle.primary)
    async def dice2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        result1 = random.randint(1,100)
        result2 = get_dfs(interaction.user.id)
        if result1 < result2:
            await interaction.followup.send(f'>>> {interaction.user.display_name}의 관찰 판정\n'
                                            f'관찰 **__{result2}__** > 주사위 **__{result1}__** 결과 **__성공__**')
        else: 
            if result1 > result2 :
                await interaction.followup.send(f'>>> {interaction.user.display_name}의 관찰 판정\n'
                                                f'관찰 **__{result2}__** < 주사위 **__{result1}__** 결과 **__실패__**')
            else:
                await interaction.followup.send(f'>>> {interaction.user.display_name}의 관찰 판정\n'
                                                f'관찰 **__{result2}__** = 주사위 **__{result1}__** 결과 **__성공__**')
        self.value = True
        self.stop()


@tree.command(guild=guilds, description='작품을 감상합니다.')
async def 감상(interaction: discord.Interaction):
    await interaction.response.defer()
    view = Dice()
    await interaction.followup.send('특기를 선택하세요.', view=view)
    await view.wait()
    if view.value is None:
         pass



@tree.command(guild=guilds, description='작품을 판매합니다')
async def 판매(interaction: discord.Interaction):
    await interaction.response.defer()
    result1 = random.randint(1,100)
    result2 = random.randint(1,100)
    if result1 < result2:
        await interaction.followup.send(f'>>> 누군가 {interaction.user.display_name}의 작품에 흥미를 보입니다.\n'
                                        f'{interaction.user.display_name} **__{result2}__** > 주사위 **__{result1}__** 결과 **__판매 성공__**')
    else: 
        if result1 > result2 :
            await interaction.followup.send(f'>>> 누군가 {interaction.user.display_name}의 작품에 흥미를 보입니다.\n'
                                            f'{interaction.user.display_name} **__{result2}__** < 주사위 **__{result1}__** 결과 **__판매 실패__**')
        else:
            await interaction.followup.send(f'>>> 누군가 {interaction.user.display_name}의 작품에 흥미를 보입니다.\n'
                                            f'{interaction.user.display_name} **__{result2}__** = 주사위 **__{result1}__** 결과 **__판매 성공__**')


@tree.command(guild=guilds, description='보너스주사위를 굴립니다.')
async def 보너스주사위(interaction: discord.Interaction):
    await interaction.response.defer()
    result = random.randint(1,10)
    await interaction.followup.send(f'>>> 10면체 보너스주사위를 굴립니다.\n'
                                        f'주사위 값 **__{result}__** 판정 결과에 더해주세요.')


#채널명 다마고치
@tree.command(guild=guilds, description='화분에 물을 줍니다. 하루에 1회 사용 가능.')
async def 물주기(interaction: discord.Interaction):
    await interaction.response.defer()
    checked = (interaction.created_at + datetime.timedelta(hours=9)).strftime('%Y/%m/%d')
    row_no = search(interaction.user.id)
    cost = default.cell(14, 3, value_render_option='UNFORMATTED_VALUE').value
    if checked == char.cell(row_no, 15).value:
        await interaction.followup.send("이미 오늘 물을 줬습니다.")
    else:
        if char.cell(row_no, 16, value_render_option='UNFORMATTED_VALUE').value > 6:
            fetched = item.findall('TRUE', in_column=9)
            change_plant(row_no, cost)
            fetched = [i.row for i in fetched]
            result = random.choice(fetched)
            fetched = [i[0] for i in item.batch_get([f'A{result}', f'G{result}'],
                                                    value_render_option='UNFORMATTED_VALUE')]
            await interaction.followup.send(f">>> **{fetched[0][0]}** 획득\n"
                                            f"{fetched[1][0]}")
            edit_inven(row_no, fetched[0][0], 1) 

        else:    
            reward = default.cell(10, 6, value_render_option='UNFORMATTED_VALUE').value
            char.update_cell(row_no, 15, checked)
            change_plant(row_no, reward)
            await interaction.followup.send(f"화분에 물을 줬습니다. \n")
        




# 서버 관리자들만 사용할 수 있도록 권한 설정을 해두시기를 권장하는 커맨드들입니다.

@tree.command(guild=guilds, description='캐릭터들에게 소지금이나 아이템을 지급합니다.')
@app_commands.describe(name='정산 받을 캐릭터의 이름을 적어주세요.', money='양수는 소지금을 증가, 음수는 소지금을 차감합니다.',
                           it_name='지급할 아이템의 이름을 적어주세요.', much='지급할 아이템의 개수를 적어주세요.')
async def 정산(interaction: discord.Interaction, name: str, money: int = 0, it_name: str = None, much: int = 0):
    await interaction.response.defer()
    try:
        row_no = char.find(name, in_column=1).row
        if it_name is None or much == 0:
            pass
        else:
            item.find(it_name, in_column=1)
            edit_inven(row_no, it_name, much)
        if money == 0:
            pass
        else:
            change_money(row_no, money)
        await interaction.followup.send(f"소지금: {money} | 아이템: {it_name} × {much}"
                                        f"\n{name}에게 정산되었습니다.")
    except gspread.exceptions.CellNotFound:
        await interaction.followup.send("존재하지 않는 캐릭터 혹은 아이템을 지정했습니다. 오탈자는 없는지 다시 확인해주세요.")


@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.errors.CommandInvokeError):
    if isinstance(error, app_commands.CommandNotFound):
        await interaction.channel.send("존재하지 않는 커맨드입니다. 사용 가능한 커맨드 목록을 다시 확인해주세요.")
    elif isinstance(error, app_commands.MissingRole):
        await interaction.channel.send("해당 동작을 실행할 권한이 없습니다.")
    elif isinstance(error, discord.NotFound):
        await interaction.channel.send("해당 동작을 이 채널에서 실행할 수 없습니다. 만일 올바른 채널에서 실행했다면 서버의 문제이므로 기다리신 후에 다시 시도해주세요.")
    elif isinstance(error, discord.ConnectionClosed):
        await interaction.channel.send("현재 서버에 장애가 발생했습니다. 해당 오류가 발생할 경우 총괄계를 통해 문의를 넣어주세요.")
    else:
        embed = discord.Embed(title="오류", description="예기치 않은 오류가 발생했습니다.", color=0xFF0000)
        embed.add_field(name="상세", value=f"{error}")
        embed.set_footer(text='Powered by @닭다리')
        await interaction.channel.send(embed=embed)
    print(error)


client.run(TOKEN)
