import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord import SlashOption
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
        
        # For breathing user
        if(stats['enemy'] == 0):
            embed.add_field(
                name=player,
                value=f"Vida: {stats['life']}, Folêgo: {stats['stamina']}",
                inline=False
            )
        
        # For oni eaters
        elif(stats['enemy'] == 1):
            embed.add_field(
                name=player,
                value=f"Vida: {stats['life']}, Eter: {stats['stamina']}",
                inline=False
            )

        # For enemys
        else:
            embed.add_field(
                name=player,
                value=f"",
                inline=False
            )
    
    return embed

# Initiave order command
@bot.slash_command(name="game_start", description="Inicia a iniciativa da mesa")
async def game_start(interaction: Interaction, mesa: str = SlashOption(description="Nome da mesa"), jogadores: str = SlashOption(description="Lista dos jogadores")): # Players in format: 'Name1 Life Stamina, Name2 Life Stamina
    
    global games
    
    # Initialize game data if it doesn't exist
    if mesa not in games:
        games[mesa] = {"players": {}, "message": None}

    # Parse players input string and add to the game
    players_list = jogadores.split(", ")
    for player_data in players_list:
        try:
            player_name, life, stamina, enemy = player_data.split()
            games[mesa]["players"][player_name] = {"life": int(life), "stamina": int(stamina), "enemy": int(enemy)}
        except ValueError:
            await interaction.response.send_message(f"Formato errado: {player_data}", ephemeral=True)
            return

    # Create the embed with all players' stats
    embed = game_emb(mesa, games[mesa]["players"])
    
    # Send the embed message and store its reference
    message = await interaction.response.send_message(embed=embed)
    games[mesa]["message"] = message

# End the game
@bot.slash_command(name="end_game", description="Deleta a iniciativa da mesa")
async def end_game(interaction: Interaction, mesa: str = SlashOption(description="Nome da mesa")):
    global games

    # Check if the game exists
    if mesa in games:
        # Delete the embed message
        if games[mesa]["message"]:
            await games[mesa]["message"].delete()

        # Remove the game from the dictionary
        del games[mesa]

        await interaction.response.send_message(f"A iniciativa da mesa {mesa} foi deletada", ephemeral=True)
    else:
        await interaction.response.send_message(f"Nenhma mesa encontrada com o nome{mesa}!", ephemeral=True)

# Update the game
@bot.slash_command(name="update_player", description="Updates the life and stamina of a player in a game")
async def update_player(interaction: Interaction, mesa: str = SlashOption(description="Nome da mesa"), jogador: str = SlashOption(description="Nome do jogador"), vida: int = SlashOption(description="Vida do Jogador"), stamina: int = SlashOption(description="Folêgo/Eter do jogador")):
    global games

    # Check if the game exists
    if mesa in games:
        if jogador in games[mesa]["players"]:
            # Update player's stats
            games[mesa]["players"][jogador] = {"life": vida, "stamina": stamina}

            # Update the embed
            embed = game_emb(mesa, games[mesa]["players"])
            await games[mesa]["message"].edit(embed=embed)

            await interaction.response.send_message(f"O status do jogador {jogador} foi atualizado", ephemeral=True)
        else:
            await interaction.response.send_message(f"O jogador {jogador} não foi encontrado!", ephemeral=True)
    else:
        await interaction.response.send_message(f"A mesa {mesa} não foi encontrada", ephemeral=True)

# Show game initiative
@bot.slash_command(name="show_game", description="Mostra o embed do jogo criado")
async def show_game(interaction: Interaction, mesa: str = SlashOption(description="Nome da mesa")):
    
    global games
    
    # Check if the game exists
    if mesa not in games:
        await interaction.response.send_message(f"Jogo {mesa} não existe.", ephemeral=True)
        return
    
    # Check if the game has a message already
    if games[mesa]["message"] is None:
        await interaction.response.send_message(f"Embed para o jogo {mesa} ainda não foi criado.", ephemeral=True)
    else:
        # Fetch and send the existing embed
        embed = game_emb(mesa, games[mesa]["players"])
        await interaction.response.send_message(embed=embed)
        


# Run the bot
bot.run(TOKEN)
