from fastapi import FastAPI
from sentence_transformers import SentenceTransformer #embed
from sklearn.metrics import DistanceMetric
# model info
model_name = 'all-MiniLM'
model_path = "app/data/" + model_name

#load model
model = SentenceTransformer(model_path)

#load index
# df = pl.scan_parquet('path/file.parquet')

#create distance metric
dist_name = 'manhattan'
dist = DistanceMetric.get_metric(dist_name)


#create FastAPI object
app = FastAPI()

#API end points
@app.get("/")
def read_root():
    return {"health_check": 'OK'}

@app.get("/info")
def info():
    return {"name": 'btruong_test',
            "description": 'sample'}
    
@app.get("/search")
def search(query: str):
    result = srx_func(query)
    return {"result": result}

@app.get("items/{item_id}")
def read_item(item_id: int, q: None):
    return {"item_id":item_id,
            "q": q}