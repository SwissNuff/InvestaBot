import os
import discord
import requests
import json
from replit import db


client = discord.Client()

@client.event
async def on_ready():
  print("We have logged in as (0.user)".format(client))



# ===== BOT COMMANDS  =====  #
def add_stonks(stock, buy_price):
  if "symbols" in db.keys():
    symbols = db["symbols"]
    symbols.append(stock)
    db["symbols"] = symbols
  else:
    db["symbols"] = [stock]
  if "buyPrice" in db.keys():
    buyPrice = db["buyPrice"]
    buyPrice.append(buy_price)
    db["buyPrice"] = buyPrice
  else:
    db["buyPrice"] = [buy_price]


def delete_stonks(index):
  symbols = db["symbols"]
  buyPrice = db["buyPrice"]
  if len(symbols) > index:
    del symbols[index]
    del buyPrice[index]
  db["symbols"] = symbols
  buyPrice = db["buyPrice"]


def get_stocks(smbl):
  response = requests.get(f"http://phisix-api4.appspot.com/stocks/{smbl}.json")
  json_data = json.loads(response.text)
  name = json_data['stock'][0]['name']
  symbol = json_data['stock'][0]['symbol']
  amount = json_data['stock'][0]['price']['amount']
  return name, symbol, amount



@client.event
async def on_message(message):
  if message.author == client.user:
    return
  
  msg = message.content

  if msg.startswith("$stonks"):
    symbols = db["symbols"]
    buyPrice = db["buyPrice"]
    for i in range(len(symbols)):
      output = get_stocks(symbols[i])
      gains = ((float(output[2]) - float(buyPrice[i])) / float(buyPrice[i]))*100
      await message.channel.send(
        f"""
        Stock: {output[0]} ({output[1]})
```py
Current price: PHP {output[2]}
Buy price: PHP {buyPrice[i]}
gains/loss: {round(gains, 2)}%
```
        """
        )
  
  if msg.startswith("$add"):
    stock = msg.split("$add ",1)[1]
    smbl, buy_price = stock.split()
    add_stonks(smbl, buy_price)
    await message.channel.send(f"{smbl} has been added to lists with a buy price of {buy_price}.")

  if msg.startswith("$del"):
    symbols = []
    if "symbols" in db.keys():
      index = int(msg.split("$del",1)[1])
      delete_stonks(index)
      symbols = db["symbols"]
    await message.channel.send(symbols)

  if msg.startswith("$show"):
    await message.channel.send("Current stocks bought")
    symbols = []
    if "symbols" in db.keys():
      symbols = db["symbols"]
    await message.channel.send(symbols)

  if msg.startswith("$help"):
    await message.channel.send("`$help` : shows list of commands\n`$add <stock symbol> <buyprice>` : add stock symbol to the list\n `$del <list index>`: deletes stock symbol to the list\n`$show:`:Show all stocks bought")
    
    
client.run(os.environ['BOT'])