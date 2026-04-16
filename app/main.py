from fastapi import FastAPI

app=FastAPI()

@app.get('/health',tags=['Status'])
def status():
    return 'OK.'