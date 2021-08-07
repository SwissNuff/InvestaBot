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
def add_stonks(smbl, buy_price):
  if "symbols" in db.keys():
    symbols = db["symbols"]
    symbols.append(smbl)
    db["symbols"] = symbols
  if "price_list" in db.keys():
    price_list = db["price_list"]
    symbols.append(buy_price)
    db["price_list"] = price_list
  else:
    db["symbols"] = [smbl]
    db["price_list"] = [price_list]

def delete_stonks(index):
  symbols = db["symbols"]
  price_list = db["price_list"]
  if len(symbols) > index:
    del symbols[index]
    del price_list[index]
  db["symbols"] = symbols
  db["price_list"] = price_list


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
    price_list = db["price_list"]
    for i in range(len(symbols)):
      output = get_stocks(symbols[i])
      await message.channel.send(
        f"""Stock: {output[0]} ({output[1]})
        Current price: PHP {output[2]}
        Price bought: PHP {price_list[i]}
        """
        )
  
  if msg.startswith("$add"):
    stock = msg.split("$add ",1)[1]
    smbl, buy_price = stock.split()
    add_stonks(smbl, buy_price)
    await message.channel.send(f"{smbl} has been added to lists with a buy price of {buy_price}.")

  if msg.startswith("$del"):
    symbols = []
    price_list = []
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

    
client.run(os.environ['BOT'])