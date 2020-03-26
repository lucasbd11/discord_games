import discord
from discord.ext import commands
import asyncio
import numpy as np
import time

client = commands.Bot(command_prefix = "!")

saved_data = []



async def party_timeout():
    
    await client.wait_until_ready()
    
    global saved_data
    while not(client.is_closed()):
        await asyncio.sleep(10)
      
        i = 0
        while i<len(saved_data):
            print(time.time()-saved_data[i]["start_time"])
            if time.time()-saved_data[i]["start_time"] > 600:
                await saved_data[i]["bot_msg"].edit(content="Temps maximal pour une partie écoulé !")
                saved_data.pop(saved_data.index(saved_data[i]))
            
            i+=1
                


async def remove_all_reaction(message):
    reactions_list = [i for i in message.reactions]
    users = []
    
    for i_reaction in reactions_list:
    
        users += await i_reaction.users().flatten()
        
    for i_user in users:
        for i_reaction in message.reactions:
            await i_reaction.remove(i_user)
   

async def create_msg(data_array):
    msg = ""
    for row in range(data_array.shape[0]):
        for column in range(data_array.shape[1]):
            if data_array[row,column] == 0:
                msg += "\U000026AA"

            if data_array[row,column] == 1:
                msg += "\U0001F535"
            
            if data_array[row,column] == 2:
                msg += "\U0001F7E1"
        msg += "\n"
    return msg + "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣"


async def do_turn(data_array,player,position):
    free_row = -1
    for i in enumerate(data_array[:,position]):
        if i[1] != 0 and free_row == -1:
            free_row = i[0]-1
    if i[0] == data_array.shape[0]-1 and free_row == -1:
        free_row = i[0]
    
    if free_row < 0:
        
        return data_array,False
    
    else:
        data_array[free_row,position] = player
        return data_array, True


async def check(data_array):
    max_row, max_column = data_array.shape
    win = (False,0)
    
    for array_type in range(2):
        if array_type == 0:
            data_array_temp = data_array
        else:
            data_array_temp = np.fliplr(data_array)
        for i in range(-max_row+1,max_column,1):
            
            array_diagonal = data_array_temp.diagonal(i)
            
            
            color_streak = [array_diagonal[0],0]
            for j in array_diagonal[1:]:
                if j == color_streak[0]:
                    color_streak[1] += 1
                else:
                    color_streak = [j,1]
                if color_streak[0] != 0 and color_streak[1] > 2:
                    win = (True,color_streak[0])

    for i in range(0,max_row,1):
        array_row = data_array[i,:]
        color_streak = [array_row[0],0]
        for j in array_row[1:]:
            if j == color_streak[0]:
                color_streak[1] += 1
            else:
                color_streak = [j,1]
            if color_streak[0] != 0 and color_streak[1] > 2:
                win = (True,color_streak[0])

    for i in range(0,max_row,1):
        
        array_column = data_array[:,i]
        color_streak = [array_column[0],0]
        for j in array_column[1:]:

            if j == color_streak[0]:
                color_streak[1] += 1
            else:
                color_streak = [j,1]
                
            if color_streak[0] != 0 and color_streak[1] > 2:
                win = (True,color_streak[0])
    return win
    

@client.event
async def on_ready():
    print("Bot connecté !")


@client.event
async def on_reaction_add(reaction, user):
    
    #print(saved_data)
    
    if reaction.message.id in [i["bot_msg"].id for i in saved_data] and not(user.bot):
        data_ref = [i["bot_msg"].id for i in saved_data].index(reaction.message.id)
    
        
        await reaction.remove(user)
        
        if reaction.emoji == "\U0000274C" and user == saved_data[data_ref]["player2"]:
        
            await reaction.message.edit(content=user.mention+" a refusé le duel")
        
            await asyncio.sleep(1)
            await remove_all_reaction(reaction.message)
            

            

        if reaction.emoji == "\U00002705" and user == saved_data[data_ref]["player2"]:
            
            await reaction.message.edit(content=user.mention+" a accepté")
    
            await asyncio.sleep(1)
            await remove_all_reaction(reaction.message)
            

            data_array = np.array([ [0,0,0,0,0,0,0],
                                    [0,0,0,0,0,0,0],
                                    [0,0,0,0,0,0,0],
                                    [0,0,0,0,0,0,0],
                                    [0,0,0,0,0,0,0],
                                    [0,0,0,0,0,0,0]], dtype= np.uint8)
        
            saved_data[data_ref]["data"] = data_array
            saved_data[data_ref]["turn"] = "player1"
            
            
            msg = await create_msg(data_array)
            
            msg += "\n**C'est au tour de:** " + saved_data[data_ref][saved_data[data_ref]["turn"]].nick
            await reaction.message.edit(content=msg)

            emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣"]
            for i in emojis:
                await reaction.message.add_reaction(i)
        
        
        if reaction.emoji in ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣"]:
            if user == saved_data[data_ref][saved_data[data_ref]["turn"]]:
                
                if saved_data[data_ref]["turn"] == "player1":
                    saved_data[data_ref]["turn"] = "player2"
                else:
                    saved_data[data_ref]["turn"] = "player1"
                
                
                emoji_index = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣"]
                position = emoji_index.index(reaction.emoji)
                
    
                
                if user == saved_data[data_ref]["player2"]:
                    player = 2
                elif user == saved_data[data_ref]["player1"]:
                    player = 1
                
                data_array,result = await do_turn(saved_data[data_ref]["data"],player,position)
                rep = await check(data_array)
                

                
                
                msg = await create_msg(data_array)
            
                if rep[0]:
                    winner = saved_data[data_ref]["player"+str(rep[1])]
                    msg = "**Le joueur " + winner.nick + " à gagné !**\n" + msg
                    saved_data.pop(data_ref)
                else:
                
                    msg += "\n**C'est au tour de:** " + saved_data[data_ref][saved_data[data_ref]["turn"]].nick
                
                
                
                await reaction.message.edit(content=msg)
                


@client.command(aliases = ["c4"])
async def connect4(ctx,*param):
    global saved_data
    
       
    if len(ctx.message.mentions) == 1:
            
        if ctx.message.author != ctx.message.mentions[0]:
            
            bot_message= await ctx.send(ctx.message.mentions[0].mention+", "+ ctx.message.author.mention + " vous défi au puissance 4 !\nUtilisez les réactions pour accepter ou non le défi")
    
            saved_data += [{"bot_msg":bot_message,"player1":ctx.message.author,"player2":ctx.message.mentions[0],"msg_type":"validation","start_time":time.time()}]
            
            emoji = "\U00002705" #validé
            await bot_message.add_reaction(emoji)
            
            emoji = "\U0000274C" #non validé
            await bot_message.add_reaction(emoji)
        
        else:
            await ctx.send("Vous ne pouvez pas jouer contre vous même !")
    
    else:
        await ctx.send("Vous devez mentionner une unique personne.")




client.loop.create_task(party_timeout())

client.run("token")
