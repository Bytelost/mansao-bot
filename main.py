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

def load_effect(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)

@bot.event
async def on_ready():
    print(f'{bot.user} has been activated !')
    
# Test bot
@bot.command(name='ping')
async def pong(ctx):
    await ctx.reply('pong!')

# Negative effects
@bot.command()
async def debuff(ctx, *, type_name):
    effect_info = load_effect("negative_effect.json")
    normalized_name = unidecode(type_name.lower())
    if normalized_name in effect_info:
        await ctx.reply(effect_info[normalized_name.lower()])
    else:
        await ctx.reply(f'Efeito desconhecido: {type_name}')

# Positive Effects
@bot.command()
async def buff(ctx, *, type_name):
    effect_info = load_effect("positive_effect.json")
    normalized_name = unidecode(type_name.lower())
    if normalized_name in effect_info:
        await ctx.reply(effect_info[normalized_name.lower()])
    else:
        await ctx.reply(f'Efeito desconhecido: {type_name}')

# Resp
@bot.command()
async def resp(ctx, type_name, technique_number):
    resp_info = load_effect("resp.json")
    normalized_name = unidecode(type_name.lower())
    if normalized_name in resp_info:
        if technique_number:
            technique_key = str(technique_number)
            if technique_key in resp_info[normalized_name]:
                await ctx.reply(resp_info[normalized_name][technique_key])
            else:
                await ctx.reply(f'Técnica {technique_number} desconhecida para {type_name}.')
        else:
            # Responde com a informação completa da respiração
            await ctx.reply(json.dumps(resp_info[normalized_name], ensure_ascii=False, indent=2))
    else:
        await ctx.reply(f'Resp desconhecido: {type_name}')
    
# Run the bot
bot.run(TOKEN)
