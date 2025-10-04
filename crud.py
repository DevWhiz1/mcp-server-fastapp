from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import Todo, TodoCreate, TodoUpdate, TodoResponse
from database import get_database

class TodoCRUD:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.todos

    async def create_todo(self, todo: TodoCreate) -> TodoResponse:
        """Create a new todo"""
        todo_dict = todo.dict()
        todo_dict["created_at"] = datetime.utcnow()
        todo_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(todo_dict)
        created_todo = await self.collection.find_one({"_id": result.inserted_id})
        return TodoResponse(**created_todo)

    async def get_todo(self, todo_id: str) -> Optional[TodoResponse]:
        """Get a todo by ID"""
        if not ObjectId.is_valid(todo_id):
            return None
        
        todo = await self.collection.find_one({"_id": ObjectId(todo_id)})
        if todo:
            return TodoResponse(**todo)
        return None

    async def get_todos(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[TodoResponse]:
        """Get todos with filtering and pagination"""
        filter_dict = {}
        
        if completed is not None:
            filter_dict["completed"] = completed
        
        if priority:
            filter_dict["priority"] = priority
        
        if search:
            filter_dict["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        cursor = self.collection.find(filter_dict).skip(skip).limit(limit).sort("created_at", -1)
        todos = await cursor.to_list(length=limit)
        return [TodoResponse(**todo) for todo in todos]

    async def get_todos_count(
        self, 
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None
    ) -> int:
        """Get total count of todos with filtering"""
        filter_dict = {}
        
        if completed is not None:
            filter_dict["completed"] = completed
        
        if priority:
            filter_dict["priority"] = priority
        
        if search:
            filter_dict["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        return await self.collection.count_documents(filter_dict)

    async def update_todo(self, todo_id: str, todo_update: TodoUpdate) -> Optional[TodoResponse]:
        """Update a todo"""
        if not ObjectId.is_valid(todo_id):
            return None
        
        update_dict = {k: v for k, v in todo_update.dict().items() if v is not None}
        if not update_dict:
            return await self.get_todo(todo_id)
        
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(todo_id)},
            {"$set": update_dict}
        )
        
        if result.modified_count:
            return await self.get_todo(todo_id)
        return None

    async def delete_todo(self, todo_id: str) -> bool:
        """Delete a todo"""
        if not ObjectId.is_valid(todo_id):
            return False
        
        result = await self.collection.delete_one({"_id": ObjectId(todo_id)})
        return result.deleted_count > 0

    async def toggle_todo(self, todo_id: str) -> Optional[TodoResponse]:
        """Toggle todo completion status"""
        if not ObjectId.is_valid(todo_id):
            return None
        
        todo = await self.get_todo(todo_id)
        if not todo:
            return None
        
        new_status = not todo.completed
        result = await self.collection.update_one(
            {"_id": ObjectId(todo_id)},
            {"$set": {"completed": new_status, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count:
            return await self.get_todo(todo_id)
        return None

    async def get_todos_by_tag(self, tag: str) -> List[TodoResponse]:
        """Get todos by tag"""
        cursor = self.collection.find({"tags": tag}).sort("created_at", -1)
        todos = await cursor.to_list(length=None)
        return [TodoResponse(**todo) for todo in todos]

    async def get_completed_todos(self) -> List[TodoResponse]:
        """Get all completed todos"""
        cursor = self.collection.find({"completed": True}).sort("updated_at", -1)
        todos = await cursor.to_list(length=None)
        return [TodoResponse(**todo) for todo in todos]

    async def get_pending_todos(self) -> List[TodoResponse]:
        """Get all pending todos"""
        cursor = self.collection.find({"completed": False}).sort("created_at", -1)
        todos = await cursor.to_list(length=None)
        return [TodoResponse(**todo) for todo in todos]

# Dependency to get CRUD instance
async def get_todo_crud():
    db = await get_database()
    return TodoCRUD(db)
