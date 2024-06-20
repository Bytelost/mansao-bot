import discord
from discord.ext import commands
from dotenv import load_dotenv
from unidecode import unidecode
import json
import os

# Get the token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True

# Instanciete the bot
bot = commands.Bot(command_prefix='!', intents=intents)

def load_effect():
    with open('negative_effect.json', 'r') as f:
        return json.load(f)

def load_effect2():
    with open('positive_effect.json', 'r') as f:
        return json.load(f)

@bot.event
async def on_ready():
    print(f'{bot.user} has been activated !')
    
# Test bot
@bot.command(name='ping')
async def pong(ctx):
    await ctx.reply('pong!')
    
@bot.command()
async def debuff(ctx, *, type_name):
    effect_info = load_effect()
    normalized_name = unidecode(type_name.lower())
    if normalized_name in effect_info:
        await ctx.reply(effect_info[normalized_name.lower()])
    else:
        await ctx.reply(f'Efeito desconhecido: {type_name}')

@bot.command()
async def buff(ctx, *, type_name):
    effect_info = load_effect2()
    normalized_name = unidecode(type_name.lower())
    if normalized_name in effect_info:
        await ctx.reply(effect_info[normalized_name.lower()])
    else:
        await ctx.reply(f'Efeito desconhecido: {type_name}')
        

    
# Run the bot
bot.run(TOKEN)