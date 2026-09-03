from fastapi import FastAPI

app = FastAPI(
    title="BranchIT API",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"message": "BranchIT API funcionando"}