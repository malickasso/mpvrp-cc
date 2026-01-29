from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import shutil
import sys

# Add solver directory to path
sys.path.append(os.path.abspath("solver"))
import mpvrp_solver

app = FastAPI()

# Create dynamic directory for uploads
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/solve")
async def solve_instance(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        solution = mpvrp_solver.solve(file_path)
        if solution:
            return solution
        else:
            return JSONResponse(status_code=400, content={"message": "No solution found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

# Mount static files for frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
