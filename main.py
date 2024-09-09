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
@bot.slash_command(name="ping", description="Responde com um pong!")
async def ping(interaction: Interaction):
    await interaction.response.send_message("Pong!")

# Negative effects
@bot.slash_command(name="debuff", description="Responde com a descrição de um efeito negativo.")
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
@bot.slash_command(name="buff", description="Responde com a descrição de um efeito positivo.")   
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
    
# Dictionary to hold the on going games
games = {}

# Function to help create game embs
def game_emb(game_id, players):
    
    # Instantiate the embed
    embed = nextcord.Embed(
        title=f"{game_id} - Iniciativa",
        description="Status dos personagens",
        color=nextcord.Color.blue()
    )
    
    # Fill the embed
    for player, stats in players.items():
        embed.add_field(
            name=player,
            value=f"Vida: {stats['life']}, Folêgo: {stats['stamina']}",
            inline=False
        )
    
    return embed

# Initiave order command
@bot.slash_command(name="game_start", description="Inicia o iniciativa da mesa")
async def game_start(interaction: Interaction, game_id: str, players: str): # Players in format: 'Name1 Life Stamina, Name2 Life Stamina
    
    global games
    
    # Initialize game data if it doesn't exist
    if game_id not in games:
        games[game_id] = {"players": {}, "message": None}

    # Parse players input string and add to the game
    players_list = players.split(", ")
    for player_data in players_list:
        try:
            player_name, life, stamina = player_data.split()
            games[game_id]["players"][player_name] = {"life": int(life), "stamina": int(stamina)}
        except ValueError:
            await interaction.response.send_message(f"Invalid format for player data: {player_data}", ephemeral=True)
            return

    # Create the embed with all players' stats
    embed = game_emb(game_id, games[game_id]["players"])
    
     # Send the embed message and store its reference
    if games[game_id]["message"] is None:
        message = await interaction.response.send_message(embed=embed)
        games[game_id]["message"] = message
    else:
        # Update the existing embed if the game was already started
        await games[game_id]["message"].edit(embed=embed)
        await interaction.response.send_message(f"Game {game_id} updated with players!", ephemeral=True)

# End the game
@bot.slash_command(name="end_game", description="Ends the game and deletes the embed for the game")
async def end_game(interaction: Interaction, game_id: str):
    global games

    # Check if the game exists
    if game_id in games:
        # Delete the embed message
        if games[game_id]["message"]:
            await games[game_id]["message"].delete()

        # Remove the game from the dictionary
        del games[game_id]

        await interaction.response.send_message(f"Game {game_id} has ended and the embed deleted!", ephemeral=True)
    else:
        await interaction.response.send_message(f"No game found with ID {game_id}!", ephemeral=True)

# Update the game
@bot.slash_command(name="update_player", description="Updates the life and stamina of a player in a game")
async def update_player(interaction: Interaction, game_id: str, player_name: str, life: int, stamina: int):
    global games

    # Check if the game exists
    if game_id in games:
        if player_name in games[game_id]["players"]:
            # Update player's stats
            games[game_id]["players"][player_name] = {"life": life, "stamina": stamina}

            # Update the embed
            embed = game_emb(game_id, games[game_id]["players"])
            await games[game_id]["message"].edit(embed=embed)

            await interaction.response.send_message(f"{player_name}'s stats updated!", ephemeral=True)
        else:
            await interaction.response.send_message(f"Player {player_name} not found in Game {game_id}!", ephemeral=True)
    else:
        await interaction.response.send_message(f"Game {game_id} not found!", ephemeral=True)
        
# Run the bot
bot.run(TOKEN)
