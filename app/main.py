from fastapi import FastAPI , Response , File , UploadFile 
import sqlalchemy as db
from pydantic import BaseModel,Field
from fastapi.responses import FileResponse
from typing import Optional , Union
connection_str = f'mysql+pymysql://user:password@mysql-db:3306/test_DB'
app = FastAPI()
table = None

stored_file = []
class Item(BaseModel):
    name: str = Field(default = None,max_length = 40)
    ID: int = Field(default=None)


class connection:
    def __init__(self):
        self.engine = db.create_engine(connection_str)
        self.connection = self.engine.connect()
        self.metadata = db.MetaData()
    
    def use_table(self,input: str):
        return db.Table(input, self.metadata, autoload_with=self.engine)  

    def close(self):
        self.connection.close()
    
    def execute(self,query):
        return self.connection.execute(query)

    def commit(self):
        self.connection.commit()

#idempotent route
@app.get("/")
def index(res: Response):
    return "This is an index page."
    
@app.get("/get")
def getall(res: Response,sortBy: Optional[str] = None,count: Optional[int] = None,offset: Optional[int] = None): 
    con = connection()
    table = con.use_table("testing")
    if table is not None:
        query = db.select(table)
        if sortBy is not None:
            if sortBy not in table.columns.keys():
                res.status_code = 400
                return "["+sortBy+"] colmun does not exist."
            query = query.order_by(db.desc(sortBy))
        if count is not None:
            query = query.limit(count) if offset is None else query.limit(count+offset)
        ResultProxy = con.execute(query)
        ResultSet = ResultProxy.fetchall()
        con.close()
        if offset is not None:
            ResultSet = ResultSet[:offset] if len(ResultSet) > offset else []
        arr = []
        for i in ResultSet:
            arr.append(Item(name=i[1],ID=i[0]))
        return arr
    res.status_code = 500
    return "something wrong with our serivce.. \nPlease standby.."

@app.post("/add")
def create_item(item: Item, res: Response):
    if(item.name is None or item.ID is None):
        res.status_code = 400
        return "invalid Item attached in request !!"
    con = connection()
    table = con.use_table("testing")
    if table is not None:
        query = db.insert(table).values(name=item.name)
        try:
            ResultProxy = con.execute(query)
            con.commit()
        except:
            con.close()
            res.status_code = 500
            return "something wrong with our serivce,Please standby.."
        con.close()
        res.status_code = 200
        return "item added successfully."

@app.put("/update")
def update_item(item: Item, res: Response):
    if(item.name is None or item.ID is None):
        res.status_code = 400
        return "invalid Item attached in request !!"
    con = connection()
    table = con.use_table("testing")
    if table is not None:
        query = db.update(table).where(table.c.id == item.ID).values(name=item.name)
        try:
            ResultProxy = con.execute(query)
            con.commit()
        except:
            con.close()
            res.status_code = 500
            return "something wrong with our serivce,Please standby.."
        con.close()
        res.status_code = 200
        return "item updated successfully."

@app.post("/upload")
def upload_file(res: Response,file: Union[UploadFile,None] = None):
    if not file:
        res.status_code = 400
        return "no file sent."
    stored_file.append(file.filename)
    f = open(file.filename,"wb")
    f.write(file.file.read())
    f.close()
    file.file.close()
    res.status_code = 200
    return "file uploaded successfully."

@app.get("/getfile")    
def get_file(res: Response,filename: Optional[str]=None):
    if filename is None:
        res.status_code = 400
        return "missing filename required."
    for f in stored_file:
        if f == filename.strip():
            res.status_code = 200
            return FileResponse(f)
    res.status_code = 400
    return "file requested not found."

@app.get("/getallfile")
def get_all_file():
    filename = []
    for i in stored_file:
        filename.append(i.filename)
    return filename

