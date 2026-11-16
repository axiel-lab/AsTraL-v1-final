import discord
from config import THEME_COLOR, SUCCESS_COLOR, ERROR_COLOR, WARNING_COLOR, EMOJI_SUCCESS, EMOJI_ERROR, EMOJI_WARNING

def success_embed(description: str):
    return discord.Embed(description=f"{EMOJI_SUCCESS} {description}", color=SUCCESS_COLOR)

def error_embed(description: str):
    return discord.Embed(description=f"{EMOJI_ERROR} {description}", color=ERROR_COLOR)

def warning_embed(description: str):
    return discord.Embed(description=f"{EMOJI_WARNING} {description}", color=WARNING_COLOR)

def main_embed(title: str, description: str):
    return discord.Embed(title=title, description=description, color=THEME_COLOR)
