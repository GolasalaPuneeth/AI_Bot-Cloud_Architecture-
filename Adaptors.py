import aiofiles
import os
async def delItemsDIR(path:str)->True or False:
    try:
        print(path)
        async with aiofiles.open(path, 'wb'):
            os.remove(path)
            return True
    except Exception as error:
        print(error)
        return False

async def allowed_file(filename:str, allowed_extensions:set) ->True or None: # type: ignore
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

async def saveFile(filePath:str,file:bytes) -> True or False:
    async with aiofiles.open(filePath, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
    return True

"""cursor.execute(CREATE TABLE VideoPannel 
                   (id INTEGER PRIMARY KEY, 
                   VideoName TEXT, 
                   Description TEXT, 
                   VideoSize INTEGER, 
                   VideoLengthMin INTEGER,
                   VideoLengthSec INTEGER,
                   VideoPath TEXT,
                   ThumbPath TEXT))"""
# Above query is used to create table using python sqlite3 module
#"DROP TABLE VideoPannel" used to drop table