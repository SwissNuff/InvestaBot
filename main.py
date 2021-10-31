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

def add_crypto(stock, buy_price):
  if "crypto_symbols" in db.keys():
    crypto_symbols = db["crypto_symbols"]
    crypto_symbols.append(stock)
    db["crypto_symbols"] = crypto_symbols
  else:
    db["crypto_symbols"] = [stock]
  if "crypto_buyPrice" in db.keys():
    crypto_buyPrice = db["crypto_buyPrice"]
    crypto_buyPrice.append(buy_price)
    db["crypto_buyPrice"] = crypto_buyPrice
  else:
    db["crypto_buyPrice"] = [buy_price]

def delete_stonks(index):
  symbols = db["symbols"]
  buyPrice = db["buyPrice"]
  if len(symbols) > index:
    del symbols[index]
    del buyPrice[index]
  db["symbols"] = symbols
  buyPrice = db["buyPrice"]

def delete_crypto(index):
  crypto_symbols = db["crypto_symbols"]
  crypto_buyPrice = db["crypto_buyPrice"]
  if len(crypto_symbols) > index:
    del crypto_symbols[index]
    del crypto_buyPrice[index]
  db["crypto_symbols"] = crypto_symbols
  crypto_buyPrice = db["crypto_buyPrice"]


def get_stocks(smbl):
  response = requests.get(f"http://phisix-api4.appspot.com/stocks/{smbl}.json")
  json_data = json.loads(response.text)
  name = json_data['stock'][0]['name']
  symbol = json_data['stock'][0]['symbol']
  amount = json_data['stock'][0]['price']['amount']
  return name, symbol, amount

def get_crypto(smbl):
  response = requests.get(f"https://api.binance.com/api/v3/avgPrice?symbol={smbl}USDT")
  json_data = json.loads(response.text)
  amount = json_data['price']
  return amount

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  
  msg = message.content

  if msg.startswith("$stonks"):
    symbols = db["symbols"]
    buyPrice = db["buyPrice"]
    crypto_symbols = db["crypto_symbols"]
    crypto_buyPrice = db["crypto_buyPrice"]
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
    for i in range(len(crypto_symbols)):
      current_price = get_crypto(crypto_symbols[i])
      gains = ((float(current_price) - float(crypto_buyPrice[i])) / float(crypto_buyPrice[i]))*100
      await message.channel.send(
        f"""
        Stock: {crypto_symbols[i]}
```py
Current price: USD {current_price}
Buy price: USD {crypto_buyPrice[i]}
gains/loss: {round(gains, 2)}%
```
        """
        )
  
  if msg.startswith("$add"):
    stock = msg.split("$add ",1)[1]
    smbl, buy_price = stock.split()
    add_stonks(smbl, buy_price)
    await message.channel.send(f"{smbl} has been added to lists with a buy price of {buy_price}.")

  if msg.startswith("$cadd"):
    stock = msg.split("$cadd ",1)[1]
    smbl, buy_price = stock.split()
    add_crypto(smbl, buy_price)
    await message.channel.send(f"{smbl} has been added to lists with a buy price of {buy_price}.")

  if msg.startswith("$del"):
    symbols = []
    if "symbols" in db.keys():
      index = int(msg.split("$del",1)[1])
      delete_stonks(index)
      symbols = db["symbols"]
    await message.channel.send(symbols)

  if msg.startswith("$cdel"):
    crypto_symbols = []
    if "crypto_symbols" in db.keys():
      index = int(msg.split("$cdel",1)[1])
      delete_crypto(index)
      crypto_symbols = db["crypto_symbols"]
    await message.channel.send(crypto_symbols)

  if msg.startswith("$show"):
    symbols = []
    if "symbols" in db.keys():
      symbols = db["symbols"]
    if "crypto_symbols" in db.keys():
      crypto_symbols = db["crypto_symbols"]
    await message.channel.send(f"Current stocks bought\n{symbols}\n{crypto_symbols}")

  if msg.startswith("$help"):
    await message.channel.send("`$help` : shows list of commands\n`$add <stock symbol> <buyprice>` : add stock symbol to the list\n`$del <list index>`: deletes stock symbol from the list\n`$cadd <stock symbol> <buyprice>` : add crypto to the list\n`$cdel <list index>`: deletes crypto from the list\n`$show:`:Show all stocks bought")
    
    
client.run(os.environ['BOT'])