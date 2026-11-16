import discord
from discord import app_commands
from discord.ext import commands
from ui import error_embed, main_embed, success_embed
from config import THEME_COLOR, EMOJI_STAR

class TicTacToeButton(discord.ui.Button):
    def __init__(self, x, y):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            if interaction.user != view.player1:
                return await interaction.response.send_message(embed=error_embed("It is not your turn!"), ephemeral=True)
            self.style = discord.ButtonStyle.danger
            self.label = "X"
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = f"It is now {view.player2.mention}'s turn (O)"
        else:
            if interaction.user != view.player2:
                return await interaction.response.send_message(embed=error_embed("It is not your turn!"), ephemeral=True)
            self.style = discord.ButtonStyle.success
            self.label = "O"
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = f"It is now {view.player1.mention}'s turn (X)"

        self.disabled = True
        winner = view.check_board_winner()
        
        embed = main_embed(f"{EMOJI_STAR} Tic-Tac-Toe", content)
        
        if winner is not None:
            if winner == view.X:
                embed.description = f"🎉 {view.player1.mention} won!"
            elif winner == view.O:
                embed.description = f"🎉 {view.player2.mention} won!"
            else:
                embed.description = "It's a tie!"

            for child in view.children:
                child.disabled = True
            view.stop()

        await interaction.response.edit_message(embed=embed, view=view)

class TicTacToe(discord.ui.View):
    def __init__(self, player1, player2):
        super().__init__(timeout=120)
        self.player1 = player1
        self.player2 = player2
        self.current_player = 1
        self.X = -1
        self.O = 1
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3: return self.O
            elif value == -3: return self.X

        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3: return self.O
            elif value == -3: return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3: return self.O
        elif diag == -3: return self.X

        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3: return self.O
        elif diag == -3: return self.X

        if all(i != 0 for row in self.board for i in row):
            return 2
        return None

class Games(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @app_commands.command(name="tictactoe", description="Play Tic-Tac-Toe against another member")
    @app_commands.describe(opponent="The member you want to challenge")
    async def tictactoe(self, interaction: discord.Interaction, opponent: discord.Member):
        if opponent.bot or opponent == interaction.user:
            return await interaction.response.send_message(embed=error_embed("You can't play against a bot or yourself."), ephemeral=True)
        
        view = TicTacToe(interaction.user, opponent)
        embed = main_embed(f"{EMOJI_STAR} Tic-Tac-Toe", f"{interaction.user.mention} (X) vs {opponent.mention} (O)\n\nIt is {interaction.user.mention}'s turn.")
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot): 
    await bot.add_cog(Games(bot))
