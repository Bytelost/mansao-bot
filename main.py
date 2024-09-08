import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from dotenv import load_dotenv
from unidecode import unidecode
import json
import os

# Get the token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create the bot
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Load data function
def load_effect(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)

@bot.event
async def on_ready():
    print(f'{bot.user} has been activated !')
    
# Test bot
@bot.slash_command(name="ping", description="Replies with pong!")
async def ping(interaction: Interaction):
    await interaction.response.send_message("Pong!")

# Negative effects
@bot.slash_command(name="debuff", description="Replies with the description of a negative effect.")
async def debuff(interaction: Interaction, efeito: str):
    
    # Load the negative effects
    effect_info = load_effect("negative_effect.json")
    normalized_name = unidecode(efeito.lower())
    
    # Reply with the effect description
    if normalized_name in effect_info:
        await interaction.response.send_message(effect_info[normalized_name.lower()])
    else:
        await interaction.response.send_message(f'Efeito desconhecido: {efeito}')

# Positive Effects
@bot.slash_command(name="buff", description="Replies with the description of a positive effect.")   
async def buff(interaction: Interaction, efeito: str):
    
    # Load the positive effects
    effect_info = load_effect("positive_effect.json")
    normalized_name = unidecode(efeito.lower())
    
    # Reply with the effect description
    if normalized_name in effect_info:
        await interaction.response.send_message(effect_info[normalized_name.lower()])
    else:
        await interaction.response.send_message(f'Efeito desconhecido: {efeito}')

# Resp
@bot.slash_command(name="resp", description="Replies with the description of a breathing technique.")
async def resp(interaction: Interaction, respiracao: str, tecnica: int):
    
    # Load the breathing techniques
    resp_info = load_effect("resp.json")
    normalized_name = unidecode(respiracao.lower())
    
    # Search for the technique
    if normalized_name in resp_info:
        if tecnica:
            technique_key = str(tecnica)
            
            # Reply with the technique description
            if technique_key in resp_info[normalized_name]:
                await interaction.response.send_message(resp_info[normalized_name][technique_key])
            else:
                await interaction.response.send_message(f'Técnica {tecnica} desconhecida para {respiracao}.')
                
        # Reply with the list of techniques
        else:
            await interaction.response.send_message(json.dumps(resp_info[normalized_name], ensure_ascii=False, indent=2))
    else:
        await interaction.response.send_message(f'Respiração desconhecida: {respiracao}')
    

    
# Run the bot
bot.run(TOKEN)
