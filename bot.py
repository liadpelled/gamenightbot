#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import random
import json
import requests
import xml.etree.ElementTree as ET
import time

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

games = ['Raiders of the North Sea', 'Architects of the West Kingdom', \
    'Viscounts of the West Kingdom', 'Sagrada', 'Five Tribes', 'Istanbul', \
        'Cyclades', 'Great Western Trail', 'Lorenzo il Magnifico', 'Bonfire']

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def choose_game(update, context):
    """Choose a random game."""
    chosenGame = random.choice(games)
    update.message.reply_text("Tonight you'll play " + chosenGame + "!")


def poll_games(update, context):
    """Create a poll with 3 random games."""
    chosenGames = random.sample(games, 3)
    context.bot.send_poll(update.message.chat.id, 'What would you like to play?', chosenGames)


def lastwinner(update, context):
    requestedGame = update.message.text[4:].title()
    gameId = findGameId(requestedGame)
    if not gameId:
        update.message.reply_text("The game " + requestedGame + " doesn't exist.")
    else:
        url = 'https://boardgamegeek.com/xmlapi2/plays?username=FinalArrow&id=' + gameId
        resp = requests.get(url)
        tree = ET.fromstring(resp.content.decode('utf-8'))
        latest_playtag = tree.find(".//play[1]//player[@win='1']")
        if (latest_playtag is not None):
            latest_victor = latest_playtag.attrib['name']
            update.message.reply_text("Last winner of " + requestedGame + " was " + latest_victor + "!")
        else:
            update.message.reply_text("You haven't played " + requestedGame + " yet.")


def info(update, context):
    requestedGame = update.message.text[6:].title()
    gameId = findGameId(requestedGame)
    if not gameId:
        update.message.reply_text("The game " + requestedGame + " doesn't exist.")
    else:
        url = 'https://www.boardgamegeek.com/xmlapi2/thing?id=' + gameId
        resp = requests.get(url)
        tree = ET.fromstring(resp.content.decode('utf-8'))
        gameDetails = {
            'cover_img': tree.find(".//image").text,
            'year': tree.find(".//yearpublished").attrib['value'],
            'min_players': tree.find(".//minplayers").attrib['value'],
            'max_players': tree.find(".//maxplayers").attrib['value'],
            'description': tree.find(".//description").text
        }
        msg = requestedGame + ' (' + gameDetails['year'] + ')' + '\n' + \
            '{} to {} players'.format(gameDetails['min_players'], gameDetails['max_players']) + '\n' + \
                gameDetails['description']

        print(msg)
        update.message.reply_text(msg)
        context.bot.send_photo(update.message.chat.id, gameDetails['cover_img'])
    

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def findGameId(gameName):
    url = 'https://boardgamegeek.com/xmlapi2/search?query=' + gameName + '&exact=1'
    resp = requests.get(url)
    tree = ET.fromstring(resp.content.decode('utf-8'))
    gameIds = [x.attrib['id'] for x in tree.findall(".//item")]
    if (not gameIds):
        return False
    for gId in gameIds:
        url = 'https://boardgamegeek.com/xmlapi2/collection?username=FinalArrow&id=' + gId
        resp = requests.get(url)
        time.sleep(0.5)
        resp = requests.get(url)
        tree = ET.fromstring(resp.content.decode('utf-8'))
        if tree.find(".//item"):
            return gId


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1645981835:AAGArnNo90J6P2QbKGaW-PMr12SemjFx9sg", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("lw", lastwinner))
    dp.add_handler(CommandHandler("info", info))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()