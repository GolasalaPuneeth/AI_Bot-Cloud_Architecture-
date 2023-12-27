import aiosqlite
class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path

    #used to create Questions and answer from user end based on Tree_ID
    async def ContentCreaterUser(self, tree_id:str, question:str, answer:str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            query = "INSERT INTO User_ID (TreeID, Question, Answer) VALUES (?, ?, ?)"
            await cursor.execute(query, (tree_id, question, answer))
            await db.commit()

    # used to delete record based on record ID
    async def del_record(self, record_id:int) -> None :
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            delete_query = "DELETE FROM User_ID WHERE ID = ?"
            await cursor.execute(delete_query, (record_id,))
            await db.commit()

    #used for checking login credentials if write returns "True" else 'False'
    async def check_credentials(self, username:str, password:str) -> False: 
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            query = "SELECT * FROM Logindetais WHERE UserName = ? AND UserPass = ?"
            await cursor.execute(query, (username, password))
            result = await cursor.fetchone()
        return result is not None

    #used to display entire data of perticular user based on Tree_ID
    async def get_data_user(self, tree_id:str) -> [] : #checked
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            query = "SELECT ID, Question, Answer FROM User_ID WHERE TreeID = ?"
            await cursor.execute(query, (tree_id,))
            result = await cursor.fetchall()
        return result if result else []
    
    #Used to fetch perticular question and answer form a record based on record ID
    async def updateIndex(self,record_id:int) -> (): #checked
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            query = "SELECT Question, Answer FROM User_ID WHERE ID = ?"
            await cursor.execute(query, (record_id,))
            result = await cursor.fetchone()
            return result
        
    #used to update record based on record_ID
    async def update(self,record_id:str,question:str,answer:str)->None : #checked
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            query = "UPDATE User_ID SET Question = ?, Answer = ? WHERE ID = ?"
            await cursor.execute(query,(question, answer, record_id))
            await db.commit()

    #used to fetch entire questions related to perticular user
    async def GetQuestionListUser(self,tree_id:str)->str: #checked
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            query = "SELECT GROUP_CONCAT(Question, ', ') AS list_data FROM User_ID WHERE TreeID = ?"
            await cursor.execute(query,(tree_id,))
            result = await cursor.fetchone()
            return result[0]
    #used to fetch perticular answer based on tree_ID and Question
    async def GetAnswerWithID(self,tree_id:str,question:str) -> str: #checked
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            query = "SELECT Answer FROM User_ID WHERE TreeID = ? AND Question = ?"
            await cursor.execute(query,(tree_id,question,))
            result = await cursor.fetchone()
            return result[0]
    
    #used to fectch entire questions and from Admin table
    async def GetQuestionListAdmin(self) ->[]: #checked
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            query = "SELECT GROUP_CONCAT(Question, ',') AS list_data FROM user;"
            await cursor.execute(query,)
            result = await cursor.fetchone()
            return result[0]
    
    #fetch answer from core(Admin) table
    async def GetAnswerFromCore(self,question) ->[]: #checked
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            query = "SELECT Answer FROM user WHERE Question = ?"
            await cursor.execute(query,(question,))
            result = await cursor.fetchone()
            return result[0]