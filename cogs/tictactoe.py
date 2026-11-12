import discord
from discord.ext import commands

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
                return await interaction.response.send_message("It is not your turn!", ephemeral=True)
            self.style = discord.ButtonStyle.danger
            self.label = "X"
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = f"It is now {view.player2.mention}'s turn (O)"
        else:
            if interaction.user != view.player2:
                return await interaction.response.send_message("It is not your turn!", ephemeral=True)
            self.style = discord.ButtonStyle.success
            self.label = "O"
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = f"It is now {view.player1.mention}'s turn (X)"

        self.disabled = True
        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f"🎉 {view.player1.mention} won!"
            elif winner == view.O:
                content = f"🎉 {view.player2.mention} won!"
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

        await interaction.response.edit_message(content=content, view=view)

class TicTacToe(discord.ui.View):
    children: list[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self, player1, player2):
        super().__init__()
        self.player1 = player1
        self.player2 = player2
        self.current_player = self.X
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
            return self.Tie
        return None

class Games(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.command(name="tictactoe", aliases=["ttt"])
    async def tictactoe(self, ctx, opponent: discord.Member):
        if opponent.bot or opponent == ctx.author:
            return await ctx.send("You can't play against a bot or yourself.")
        
        view = TicTacToe(ctx.author, opponent)
        await ctx.send(f"Tic-Tac-Toe: {ctx.author.mention} (X) vs {opponent.mention} (O)\nIt is {ctx.author.mention}'s turn.", view=view)

async def setup(bot): await bot.add_cog(Games(bot))