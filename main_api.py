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
            # Generate .dat file
            dat_content = mpvrp_solver.generate_dat_solution(solution, file.filename)
            dat_filename = f"Sol_{file.filename}"
            dat_path = os.path.join(UPLOAD_DIR, dat_filename)
            with open(dat_path, 'w') as f:
                f.write(dat_content)
            
            # Add dat_url to response
            solution['dat_url'] = f"/download/{dat_filename}"
            return solution
        else:
            return JSONResponse(status_code=400, content={"message": "Aucune solution trouvée"})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"message": str(e)})

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        from fastapi.responses import FileResponse
        return FileResponse(path=file_path, filename=filename)
    return JSONResponse(status_code=404, content={"message": "Fichier non trouvé"})

# Mount static files for frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
