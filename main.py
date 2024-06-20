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

@bot.event
async def on_ready():
    print(f'{bot.user} has been activated !')
    
# Test bot
@bot.command(name='ping')
async def pong(ctx):
    await ctx.reply('pong!')
    
@bot.command()
async def debuff(ctx, *, type_name):
    efect_info = load_effect()
    normalized_name = unidecode(type_name.lower())
    if normalized_name in efect_info:
        await ctx.reply(efect_info[normalized_name.lower()])
    else:
        await ctx.reply(f'Efeito desconhecido: {type_name}')
        

    
# Run the bot
bot.run(TOKEN)