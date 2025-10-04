from fastapi import FastAPI, HTTPException, Depends, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from contextlib import asynccontextmanager

from database import connect_to_mongo, close_mongo_connection
from models import TodoCreate, TodoUpdate, TodoResponse, TodoListResponse
from crud import get_todo_crud, TodoCRUD

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Todo App API",
    description="A comprehensive todo application with MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {"message": "Todo App API is running!", "status": "healthy"}

@app.post("/todos", response_model=TodoResponse, status_code=201, tags=["Todos"])
async def create_todo(
    todo: TodoCreate,
    crud: TodoCRUD = Depends(get_todo_crud)
):
    """Create a new todo"""
    try:
        return await crud.create_todo(todo)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/todos", response_model=TodoListResponse, tags=["Todos"])
async def get_todos(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[str] = Query(None, pattern="^(low|medium|high)$", description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    crud: TodoCRUD = Depends(get_todo_crud)
):
    """Get todos with filtering and pagination"""
    try:
        skip = (page - 1) * limit
        todos = await crud.get_todos(skip, limit, completed, priority, search)
        total = await crud.get_todos_count(completed, priority, search)
        
        return TodoListResponse(
            todos=todos,
            total=total,
            page=page,
            limit=limit,
            has_next=(skip + limit) < total,
            has_prev=page > 1
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def get_todo(
    todo_id: str = Path(..., description="Todo ID"),
    crud: TodoCRUD = Depends(get_todo_crud)
):
    """Get a specific todo by ID"""
    todo = await crud.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def update_todo(
    todo_id: str = Path(..., description="Todo ID"),
    todo_update: TodoUpdate = None,
    crud: TodoCRUD = Depends(get_todo_crud)
):
    """Update a todo"""
    if not todo_update:
        raise HTTPException(status_code=400, detail="Update data is required")
    
    todo = await crud.update_todo(todo_id, todo_update)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.delete("/todos/{todo_id}", status_code=204, tags=["Todos"])
async def delete_todo(
    todo_id: str = Path(..., description="Todo ID"),
    crud: TodoCRUD = Depends(get_todo_crud)
):
    """Delete a todo"""
    success = await crud.delete_todo(todo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")

@app.patch("/todos/{todo_id}/toggle", response_model=TodoResponse, tags=["Todos"])
async def toggle_todo(
    todo_id: str = Path(..., description="Todo ID"),
    crud: TodoCRUD = Depends(get_todo_crud)
):
    """Toggle todo completion status"""
    todo = await crud.toggle_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.get("/todos/completed", response_model=List[TodoResponse], tags=["Todos"])
async def get_completed_todos(
    crud: TodoCRUD = Depends(get_todo_crud)
):
    """Get all completed todos"""
    return await crud.get_completed_todos()

@app.get("/todos/pending", response_model=List[TodoResponse], tags=["Todos"])
async def get_pending_todos(
    crud: TodoCRUD = Depends(get_todo_crud)
):
    """Get all pending todos"""
    return await crud.get_pending_todos()

@app.get("/todos/tag/{tag}", response_model=List[TodoResponse], tags=["Todos"])
async def get_todos_by_tag(
    tag: str = Path(..., description="Tag name"),
    crud: TodoCRUD = Depends(get_todo_crud)
):
    """Get todos by tag"""
    return await crud.get_todos_by_tag(tag)

@app.get("/stats", tags=["Statistics"])
async def get_stats(crud: TodoCRUD = Depends(get_todo_crud)):
    """Get todo statistics"""
    try:
        total = await crud.get_todos_count()
        completed = await crud.get_todos_count(completed=True)
        pending = await crud.get_todos_count(completed=False)
        
        high_priority = await crud.get_todos_count(priority="high")
        medium_priority = await crud.get_todos_count(priority="medium")
        low_priority = await crud.get_todos_count(priority="low")
        
        return {
            "total_todos": total,
            "completed_todos": completed,
            "pending_todos": pending,
            "completion_rate": round((completed / total * 100) if total > 0 else 0, 2),
            "priority_breakdown": {
                "high": high_priority,
                "medium": medium_priority,
                "low": low_priority
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
