from fastapi import FastAPI,Body
from fastapi.staticfiles import StaticFiles
import uvicorn
import AIGenerator
from pydantic import BaseModel
from VoiceGenerator import mapy
import sqlite3
import numpy as np
from fuzzywuzzy import fuzz, process
import asyncio

app = FastAPI()
connection = sqlite3.connect("database.db")
StackData=None


class User(BaseModel):
    TreeID: str
    TreeRequest: str    

# Mount the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")
async def GetQuestionList(tree_id: str) :
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT GROUP_CONCAT(Question, ', ') AS list_data FROM User_ID WHERE TreeID = ?", (tree_id,))
        questions = cursor.fetchone()
        try:
            return np.array(questions[0].split(', '))
        except Exception as Error:
            print(Error,"it an error")
            pass
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return None

async def GetAnswerWithID(tree_id: str, question: str) :
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT Answer FROM User_ID WHERE TreeID = ? AND Question = ?", (tree_id, question))
        result = cursor.fetchone()
        return result[0]
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return None

async def background_task():
    global StackData,connection
    while True:
        try:
            cursor = connection.cursor()
            cursor.execute("""SELECT GROUP_CONCAT(Question, ',') AS list_data
            FROM user;
            """)
            list_data = cursor.fetchone()[0]  # Get the first element from the result
            del StackData
            StackData = np.array(list_data.split(',')) 
            print("Updated...👍")
        except Exception as Error:
            print(Error)
        finally:
            cursor.close()
        await asyncio.sleep(50)  # Sleep for 10 seconds between iterations

async def AdminTable(input_str:str) -> str or False:
    global StackData, connection
    try:
        cursor = connection.cursor()
        best_match, highest_ratio = process.extractOne(input_str, StackData, scorer=fuzz.token_sort_ratio) # type: ignore
        if highest_ratio>85:
            cursor.execute("SELECT Answer FROM user WHERE Question = ?", (best_match,))
            return cursor.fetchone()[0]
    except Exception as Error:
        print(Error)
    finally:
        cursor.close()
    return False

async def UserDB(tree_id: str, input_str: str)  :
    try:
        questions = await GetQuestionList(tree_id)
        best_match, highest_ratio = process.extractOne(input_str, questions, scorer=process.fuzz.token_sort_ratio)
        if highest_ratio > 80:
            return await GetAnswerWithID(tree_id, best_match)
    except Exception as e:
        print(f"Error: {e}")
    return False

@app.get('/')
async def Igniter():
    asyncio.create_task(background_task())
    return {"Service Started running...🔥"}

@app.post('/')
async def Igniter(user: User = Body(...)):
    asyncio.create_task(background_task())
    print(user.TreeID)
    print(user.TreeRequest)
    RawText = user.TreeRequest
    if "play" in RawText:
        AudioData = await mapy("As you wish")
        return {
            "ResponseAudio":RawText,
            "Audio_data": AudioData
            }
    if "time" in RawText:
        AudioData = await mapy("Time in Progress")
        return {
            "ResponseAudio":RawText,
            "Audio_data": AudioData
            }
    RawData = await UserDB(user.TreeID,user.TreeRequest)
    if RawData :
        AudioData = await mapy(RawData)
        return {
            "ResponseAudio":RawData,
            "Audio_data": AudioData
            }
    RawData = await AdminTable(user.TreeRequest)
    if RawData :
        AudioData = await mapy(RawData)
        return {
            "ResponseAudio":RawData,
            "Audio_data": AudioData
            }
    else:
        RawData = await AIGenerator.intell(RawText)
        AudioData = await mapy(RawData)
        return {
            "ResponseAudio":RawData,
            "Audio_data": AudioData
            }



if __name__=="__main__":
    uvicorn.run(app)