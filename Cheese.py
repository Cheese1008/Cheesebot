import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from discord.utils import get
from discord import FFmpegPCMAudio
import asyncio
import time
import random
import os

bot = commands.Bot(command_prefix='!')

user = []
musictitle = []
song_queue = []
musicnow = []

def title(msg):
    global music

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    chromedriver_dir = r"E:\chromedriver\chromedriver.exe"
    driver = webdriver.Chrome(chromedriver_dir, options = options)
    driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, 'lxml')
    entire = bs.find_all('a', {'id': 'video-title'})
    entireNum = entire[0]
    music = entireNum.text.strip()

    musictitle.append(music)
    musicnow.append(music)
    test1 = entireNum.get('href')
    url = 'https://www.youtube.com'+test1
    with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
    URL = info['formats'][0]['url']

    driver.quit()

    return music, URL

def play(ctx):
    global vc
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    URL = song_queue[0]
    del user[0]
    del musictitle[0]
    del song_queue[0]
    vc = get(bot.voice_clients, guild=ctx.guild)
    if not vc.is_playing():
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))

def play_next(ctx):
    if len(musicnow) - len(user) >= 2:
        for i in range(len(musicnow) - len(user) - 1):
            del musicnow[0]
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    if len(user) >= 1:
        if not vc.is_playing():
            del musicnow[0]
            URL = song_queue[0]
            del user[0]
            del musictitle[0]
            del song_queue[0]
            vc.play(discord.FFmpegPCMAudio(URL,**FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
    

@bot.event
async def on_ready():
    print('다음으로 로그인합니다: ')
    print(bot.user.name)
    print('connection was succedful')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("!h"))
        

@bot.command()
async def off(ctx):
    try:
        await vc.disconnect()
    except:
        await ctx.send("채널에 속해있지 않습니다.")


@bot.command()
async def p(ctx, *, msg):

    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("우선 채널에 접속해주세요.")

    if not vc.is_playing():

        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        
        global entireText
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        chromedriver_dir = r"E:\chromedriver\chromedriver.exe"
        driver = webdriver.Chrome(chromedriver_dir, options = options)
        driver.get("https://www.youtube.com/results?search_query="+msg+"")
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a', {'id': 'video-title'})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get('href')
        url = 'https://www.youtube.com'+musicurl

        driver.quit()

        musicnow.insert(0, entireText)
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        await ctx.send(embed = discord.Embed(title= "PLAY", description = "" + musicnow[0] + "", color = 0x9ffd80))
        vc.play(discord.FFmpegPCMAudio(URL,**FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
    else:
      user.append(msg)
      result,URLTEST = title(msg)
      song_queue.append(URLTEST)
      await ctx.send("" + result + "｜음악을 대기열에 추가했습니다.")



@bot.command()
async def pa(ctx):
    if vc.is_playing():
        vc.pause()
        await ctx.send(embed = discord.Embed(title= "PAUSE", description = musicnow[0] + "", color = 0xffd264))
    else:
        await ctx.send("이미 음악이 중지되었습니다.")

@bot.command()
async def re(ctx):
    try:
        vc.resume()
    except:
        await ctx.send("음악을 다시 재생합니다.")
    else:
        await ctx.send(embed = discord.Embed(title= "PLAY", description = musicnow[0]  + "", color = 0x9ffd80))

@bot.command()
async def s(ctx):
    if vc.is_playing():
        vc.stop()
        await ctx.send(embed = discord.Embed(title= "SONG SKIP", description = musicnow[0]  + "", color = 0xfc6e6e))
    else:
        await ctx.send("이미 음악이 중단되었습니다.")

@bot.command()
async def np(ctx):
    if not vc.is_playing():
        await ctx.send("재생중인 음악이 없습니다.")
    else:
        await ctx.send(embed = discord.Embed(title = "NOW PLAYING", description = "" + musicnow[0] + "", color = 0xecd4ff))

@bot.command()
async def melon(ctx):

    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("우선 채널에 접속해주세요.")

    if not vc.is_playing():

        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        global entireText
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            
        chromedriver_dir = r"E:\chromedriver\chromedriver.exe"
        driver = webdriver.Chrome(chromedriver_dir, options = options)
        driver.get("https://www.youtube.com/results?search_query=멜론차트")
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a', {'id': 'video-title'})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get('href')
        url = 'https://www.youtube.com'+musicurl 

        driver.quit()

        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        await ctx.send(embed = discord.Embed(title= "MELON TOP 100", description = "" + entireText + "", color = 0x00cd3c))
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
    else:
        await ctx.send("아직 음악이 재생중입니다.")

@bot.command()
async def nod(ctx, *, number):
    try:
        ex = len(musicnow) - len(user)
        del user[int(number) - 1]
        del musictitle[int(number) - 1]
        del song_queue[int(number)-1]
        del musicnow[int(number)-1+ex]
            
        await ctx.send("해당 음악이 삭제되었습니다.")
    except:
        if len(list) == 0:
            await ctx.send("대기열에 음악이 없어 삭제할 수 없습니다.")
        else:
            if len(list) < int(number):
                await ctx.send("대기번호가 목록의 범위를 벗어났습니다.")
            else:
                await ctx.send("대기번호를 입력하세요.")

@bot.command()
async def q(ctx):
    if len(musictitle) == 0:
        await ctx.send("대기열에 음악이 없습니다.")
    else:
        global Text
        Text = ""
        for i in range(len(musictitle)):
            Text = Text + "\n" + str(i + 1) + ". " + str(musictitle[i])
            
        await ctx.send(embed = discord.Embed(title= "QUEUE", description = Text.strip(), color = 0xecd4ff))

@bot.command()
async def qc(ctx):
    try:
        ex = len(musicnow) - len(user)
        del user[:]
        del musictitle[:]
        del song_queue[:]
        while True:
            try:
                del musicnow[ex]
            except:
                break
        await ctx.send(embed = discord.Embed(title= "QUEUE CLEAR", description = "대기열이 청소되었습니다.", color = 0xcc3150))
    except:
        await ctx.send("대기열에 음악이 없습니다.")

@bot.command()
async def qp(ctx):

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    
    if len(user) == 0:
        await ctx.send("대기열에 음악이 없습니다.")
    else:
        if len(musicnow) - len(user) >= 1:
            for i in range(len(musicnow) - len(user)):
                del musicnow[0]
        if not vc.is_playing():
            play(ctx)
        else:
            await ctx.send("음악이 이미 재생되고 있습니다.")

@bot.command()
async def mix(ctx):
    try:
        global musicnow, user, musictitle,song_queue
        numbershuffle = len(musicnow) - len(user)
        for i in range(numbershuffle):
            shuffles.append(musicnow[0])
            del musicnow[0]
        combine = list(zip(user, musicnow, musictitle, song_queue))
        random.shuffle(combine)
        a, b, c, d = list(zip(*combine))

        user = list(a)
        musicnow = list(b)
        musictitle = list(c)
        song_queue = list(d)

        for i in range(numbershuffle):
            musicnow.insert(0, shuffles[i])

        del shuffles[:]
        await ctx.send("대기열의 순서가 재배치되었습니다.")
    except:
        await ctx.send("순서를 섞을 대기열이 없습니다.")

@bot.command()
async def h(ctx):
    await ctx.send(embed = discord.Embed(title='COMMAND',description="""
\n!off ｜ 봇을 음성 채널에서 내보냅니다.
\n!p [음악 이름] ｜ 음악을 재생합니다. 음악이 재생 중일 경우 대기열에 등록됩니다.
\n!pa ｜ 음악을 정지시킵니다.
\n!re ｜ 음악을 다시 재생합니다.
\n!np ｜ 재생되고 있는 음악을 알려줍니다.
\n!melon ｜ 멜론 TOP100 차트를 재생합니다.
\n!q ｜ 이어서 재생할 대기열을 보여줍니다.
\n!mix ｜ 대기열을 섞습니다.
\n!qp [번호] ｜ 해당 번호의 노래를 다음 순서에 재생합니다. (오류)
\n!nod [번호] ｜ 대기열의 번호에 해당하는 음악을 제거합니다.
\n!qc ｜ 대기열의 모든 음악을 제거합니다.
\n!청소 [번호] ｜ 채팅을 번호만큼 삭제합니다.   """, color = 0xfaf0cf))

@bot.command(name="청소", pass_context=True)
async def clear(ctx, *, amount=5):
    await ctx.channel.purge(limit=amount)
    await ctx.send(embed = discord.Embed(title= 'CHAT CLEAR',description = '청소를 마쳤습니다', color = 0xcc3150))

@bot.event
async def on_message(msg):
    if msg.author.bot: return None
    topic = msg.channel.topic
    if topic is not None and 'Cheese' in topic:
        await bot.process_commands(msg)            
    
access_token = os.environ["BOT_TOKEN"]
bot.run(access_token)

