from fastapi import FastAPI,Body,Form,Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import AIGenerator
from pydantic import BaseModel
from VoiceGenerator import mapy
import numpy as np
from fuzzywuzzy import fuzz, process
import asyncio
from Model import DatabaseManager

app = FastAPI()
db=DatabaseManager("database.db")
templates = Jinja2Templates(directory="templates")
StackData=None


class User(BaseModel):
    TreeID: str
    TreeRequest: str    

# Mount the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")


async def background_task() -> None:
    global StackData,connection
    while True:
        try:
            list_data = await db.GetQuestionListAdmin()
            del StackData
            StackData = np.array(list_data.split(','))
            print("Updated...👍")
        except Exception as Error:
            print(Error)
        await asyncio.sleep(50)  # Sleep for 50 seconds between iterations

async def AdminTable(input_str:str) -> str or False:
    global StackData, connection
    try:
        best_match, highest_ratio = process.extractOne(input_str, StackData, scorer=fuzz.token_sort_ratio) # type: ignore
        if highest_ratio>85:
            return await db.GetAnswerFromCore(question=best_match)
    except Exception as Error:
        print(Error)
    return False

async def UserDB(tree_id: str, input_str: str)  :
    try:
        questions = await db.GetQuestionListUser(tree_id=tree_id)
        questions= np.array(questions.split(', '))
        best_match, highest_ratio = process.extractOne(input_str, questions, scorer=process.fuzz.token_sort_ratio)
        if highest_ratio > 80:
            return await db.GetAnswerWithID(tree_id=tree_id, question=best_match)
    except Exception as e:
        print(f"Error: {e}")
    return False

@app.get('/')
async def Igniter():
    asyncio.create_task(background_task())
    return {"Service Started running...🔥"}

@app.post('/')
async def MainRunner(user: User = Body(...)):
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
    
@app.get("/content")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/content")
async def logger(request: Request,TreeID :str = Form(...),TreePass: str = Form(...)):
    if (await db.check_credentials(TreeID,TreePass)):
        result = await db.get_data_user(TreeID)
        return templates.TemplateResponse("content.html", {"request": request,"data":result,"ID":TreeID})
    return templates.TemplateResponse("index.html", {"request": request,"status":True})

@app.post("/create/{TreeID}")
async def createQuestion(TreeID,request: Request,Question :str = Form(...),Answer :str = Form(...)):
    Question=Question.strip().lower().replace(",","")
    await db.ContentCreaterUser(TreeID,Question,Answer)
    result = await db.get_data_user(TreeID)
    return templates.TemplateResponse("content.html", {"request": request,"data":result,"ID":TreeID})


@app.get("/Delete/{Item_ID}/{TreeID}")
async def DeleteRec(Item_ID,TreeID,request: Request):
    await db.del_record(Item_ID)
    result = await db.get_data_user(TreeID)
    return templates.TemplateResponse("content.html", {"request": request,"data":result,"ID":TreeID})

@app.get("/update/{item_ID}/{TreeID}")
async def updateIndex(request: Request,item_ID,TreeID):
        question_and_answer = await db.updateIndex(record_id=item_ID)
        return templates.TemplateResponse("updated.html", {"request": request,"data":question_and_answer,"details":[TreeID,item_ID]})

@app.post("/update/{item_ID}/{Tree_ID}")
async def uptodate(item_ID,Tree_ID,request: Request,Question :str = Form(...),Answer :str = Form(...)):
    await db.update(record_id=item_ID,question=Question,answer=Answer)
    result = await db.get_data_user(Tree_ID)
    return templates.TemplateResponse("content.html", {"request": request,"data":result,"ID":Tree_ID})



if __name__=="__main__":
    uvicorn.run(app)