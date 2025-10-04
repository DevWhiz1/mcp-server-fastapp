#!/usr/bin/env python3
"""
FastMCP Server for Todo Application
Exposes todo functionality to LLMs via Model Context Protocol
"""
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastmcp import FastMCP
from crud import get_todo_crud, TodoCRUD
from models import TodoCreate, TodoUpdate, TodoResponse
from database import connect_to_mongo, close_mongo_connection

# Initialize FastMCP server
mcp = FastMCP("Todo App MCP Server")

# Global variable to store CRUD instance
todo_crud: Optional[TodoCRUD] = None

async def get_crud_instance():
    """Get or create CRUD instance"""
    global todo_crud
    if todo_crud is None:
        # Ensure database connection is established
        await connect_to_mongo()
        from database import get_database
        db = await get_database()
        todo_crud = TodoCRUD(db)
    return todo_crud

@mcp.tool
async def create_todo(
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    due_date: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new todo item.
    
    Args:
        title: The title of the todo (required)
        description: Optional description of the todo
        priority: Priority level (low, medium, high) - defaults to medium
        due_date: Due date in ISO format (YYYY-MM-DD) - optional
        tags: List of tags to categorize the todo - optional
    
    Returns:
        Dictionary with the created todo information
    """
    try:
        crud = await get_crud_instance()
        
        # Parse due_date if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                return {"error": f"Invalid date format: {due_date}. Use YYYY-MM-DD format."}
        
        # Create todo data
        todo_data = TodoCreate(
            title=title,
            description=description,
            priority=priority,
            due_date=parsed_due_date,
            tags=tags or []
        )
        
        # Create the todo
        created_todo = await crud.create_todo(todo_data)
        
        return {
            "success": True,
            "message": f"Todo '{title}' created successfully",
            "todo": {
                "id": str(created_todo.id),
                "title": created_todo.title,
                "description": created_todo.description,
                "completed": created_todo.completed,
                "priority": created_todo.priority,
                "due_date": created_todo.due_date.isoformat() if created_todo.due_date else None,
                "tags": created_todo.tags,
                "created_at": created_todo.created_at.isoformat()
            }
        }
    except Exception as e:
        return {"error": f"Failed to create todo: {str(e)}"}

@mcp.tool
async def get_todos(
    page: int = 1,
    limit: int = 10,
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get todos with filtering and pagination.
    
    Args:
        page: Page number (default: 1)
        limit: Number of todos per page (default: 10, max: 100)
        completed: Filter by completion status (true/false) - optional
        priority: Filter by priority (low, medium, high) - optional
        search: Search in title and description - optional
    
    Returns:
        Dictionary with todos and pagination info
    """
    try:
        crud = await get_crud_instance()
        
        skip = (page - 1) * limit
        todos = await crud.get_todos(skip, limit, completed, priority, search)
        total = await crud.get_todos_count(completed, priority, search)
        
        return {
            "success": True,
            "todos": [
                {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "completed": todo.completed,
                    "priority": todo.priority,
                    "due_date": todo.due_date.isoformat() if todo.due_date else None,
                    "tags": todo.tags,
                    "created_at": todo.created_at.isoformat(),
                    "updated_at": todo.updated_at.isoformat()
                }
                for todo in todos
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "has_next": (skip + limit) < total,
                "has_prev": page > 1
            }
        }
    except Exception as e:
        return {"error": f"Failed to get todos: {str(e)}"}

@mcp.tool
async def get_todo(todo_id: str) -> Dict[str, Any]:
    """
    Get a specific todo by ID.
    
    Args:
        todo_id: The ID of the todo to retrieve
    
    Returns:
        Dictionary with the todo information
    """
    try:
        crud = await get_crud_instance()
        todo = await crud.get_todo(todo_id)
        
        if not todo:
            return {"error": f"Todo with ID '{todo_id}' not found"}
        
        return {
            "success": True,
            "todo": {
                "id": str(todo.id),
                "title": todo.title,
                "description": todo.description,
                "completed": todo.completed,
                "priority": todo.priority,
                "due_date": todo.due_date.isoformat() if todo.due_date else None,
                "tags": todo.tags,
                "created_at": todo.created_at.isoformat(),
                "updated_at": todo.updated_at.isoformat()
            }
        }
    except Exception as e:
        return {"error": f"Failed to get todo: {str(e)}"}

@mcp.tool
async def update_todo(
    todo_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Update an existing todo.
    
    Args:
        todo_id: The ID of the todo to update
        title: New title - optional
        description: New description - optional
        completed: New completion status - optional
        priority: New priority (low, medium, high) - optional
        due_date: New due date in ISO format (YYYY-MM-DD) - optional
        tags: New list of tags - optional
    
    Returns:
        Dictionary with the updated todo information
    """
    try:
        crud = await get_crud_instance()
        
        # Parse due_date if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                return {"error": f"Invalid date format: {due_date}. Use YYYY-MM-DD format."}
        
        # Create update data
        update_data = TodoUpdate(
            title=title,
            description=description,
            completed=completed,
            priority=priority,
            due_date=parsed_due_date,
            tags=tags
        )
        
        # Update the todo
        updated_todo = await crud.update_todo(todo_id, update_data)
        
        if not updated_todo:
            return {"error": f"Todo with ID '{todo_id}' not found"}
        
        return {
            "success": True,
            "message": f"Todo '{updated_todo.title}' updated successfully",
            "todo": {
                "id": str(updated_todo.id),
                "title": updated_todo.title,
                "description": updated_todo.description,
                "completed": updated_todo.completed,
                "priority": updated_todo.priority,
                "due_date": updated_todo.due_date.isoformat() if updated_todo.due_date else None,
                "tags": updated_todo.tags,
                "created_at": updated_todo.created_at.isoformat(),
                "updated_at": updated_todo.updated_at.isoformat()
            }
        }
    except Exception as e:
        return {"error": f"Failed to update todo: {str(e)}"}

@mcp.tool
async def delete_todo(todo_id: str) -> Dict[str, Any]:
    """
    Delete a todo by ID.
    
    Args:
        todo_id: The ID of the todo to delete
    
    Returns:
        Dictionary with deletion result
    """
    try:
        crud = await get_crud_instance()
        success = await crud.delete_todo(todo_id)
        
        if not success:
            return {"error": f"Todo with ID '{todo_id}' not found"}
        
        return {
            "success": True,
            "message": f"Todo with ID '{todo_id}' deleted successfully"
        }
    except Exception as e:
        return {"error": f"Failed to delete todo: {str(e)}"}

@mcp.tool
async def toggle_todo(todo_id: str) -> Dict[str, Any]:
    """
    Toggle the completion status of a todo.
    
    Args:
        todo_id: The ID of the todo to toggle
    
    Returns:
        Dictionary with the updated todo information
    """
    try:
        crud = await get_crud_instance()
        todo = await crud.toggle_todo(todo_id)
        
        if not todo:
            return {"error": f"Todo with ID '{todo_id}' not found"}
        
        return {
            "success": True,
            "message": f"Todo '{todo.title}' marked as {'completed' if todo.completed else 'pending'}",
            "todo": {
                "id": str(todo.id),
                "title": todo.title,
                "description": todo.description,
                "completed": todo.completed,
                "priority": todo.priority,
                "due_date": todo.due_date.isoformat() if todo.due_date else None,
                "tags": todo.tags,
                "created_at": todo.created_at.isoformat(),
                "updated_at": todo.updated_at.isoformat()
            }
        }
    except Exception as e:
        return {"error": f"Failed to toggle todo: {str(e)}"}

@mcp.tool
async def get_completed_todos() -> Dict[str, Any]:
    """
    Get all completed todos.
    
    Returns:
        Dictionary with list of completed todos
    """
    try:
        crud = await get_crud_instance()
        todos = await crud.get_completed_todos()
        
        return {
            "success": True,
            "todos": [
                {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "completed": todo.completed,
                    "priority": todo.priority,
                    "due_date": todo.due_date.isoformat() if todo.due_date else None,
                    "tags": todo.tags,
                    "created_at": todo.created_at.isoformat(),
                    "updated_at": todo.updated_at.isoformat()
                }
                for todo in todos
            ],
            "count": len(todos)
        }
    except Exception as e:
        return {"error": f"Failed to get completed todos: {str(e)}"}

@mcp.tool
async def get_pending_todos() -> Dict[str, Any]:
    """
    Get all pending (incomplete) todos.
    
    Returns:
        Dictionary with list of pending todos
    """
    try:
        crud = await get_crud_instance()
        todos = await crud.get_pending_todos()
        
        return {
            "success": True,
            "todos": [
                {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "completed": todo.completed,
                    "priority": todo.priority,
                    "due_date": todo.due_date.isoformat() if todo.due_date else None,
                    "tags": todo.tags,
                    "created_at": todo.created_at.isoformat(),
                    "updated_at": todo.updated_at.isoformat()
                }
                for todo in todos
            ],
            "count": len(todos)
        }
    except Exception as e:
        return {"error": f"Failed to get pending todos: {str(e)}"}

@mcp.tool
async def get_todos_by_tag(tag: str) -> Dict[str, Any]:
    """
    Get todos by a specific tag.
    
    Args:
        tag: The tag to search for
    
    Returns:
        Dictionary with list of todos matching the tag
    """
    try:
        crud = await get_crud_instance()
        todos = await crud.get_todos_by_tag(tag)
        
        return {
            "success": True,
            "todos": [
                {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "completed": todo.completed,
                    "priority": todo.priority,
                    "due_date": todo.due_date.isoformat() if todo.due_date else None,
                    "tags": todo.tags,
                    "created_at": todo.created_at.isoformat(),
                    "updated_at": todo.updated_at.isoformat()
                }
                for todo in todos
            ],
            "count": len(todos),
            "tag": tag
        }
    except Exception as e:
        return {"error": f"Failed to get todos by tag: {str(e)}"}

@mcp.tool
async def get_todo_stats() -> Dict[str, Any]:
    """
    Get statistics about todos.
    
    Returns:
        Dictionary with todo statistics
    """
    try:
        crud = await get_crud_instance()
        
        total = await crud.get_todos_count()
        completed = await crud.get_todos_count(completed=True)
        pending = await crud.get_todos_count(completed=False)
        
        high_priority = await crud.get_todos_count(priority="high")
        medium_priority = await crud.get_todos_count(priority="medium")
        low_priority = await crud.get_todos_count(priority="low")
        
        completion_rate = round((completed / total * 100) if total > 0 else 0, 2)
        
        return {
            "success": True,
            "stats": {
                "total_todos": total,
                "completed_todos": completed,
                "pending_todos": pending,
                "completion_rate": completion_rate,
                "priority_breakdown": {
                    "high": high_priority,
                    "medium": medium_priority,
                    "low": low_priority
                }
            }
        }
    except Exception as e:
        return {"error": f"Failed to get todo stats: {str(e)}"}

# Prompts for common todo operations
@mcp.prompt
def create_todo_prompt() -> str:
    """Prompt template for creating a new todo"""
    return """Create a new todo item. You can specify:
- title (required): The main task or item
- description (optional): More details about the task
- priority (optional): low, medium, or high (defaults to medium)
- due_date (optional): When it needs to be done (YYYY-MM-DD format)
- tags (optional): Categories or labels for organization

Example: "Create a todo to 'Review project proposal' with high priority, due tomorrow, tagged with 'work' and 'urgent'"
"""

@mcp.prompt
def manage_todos_prompt() -> str:
    """Prompt template for managing todos"""
    return """Manage your todos. You can:
- View all todos or filter by completion status, priority, or search terms
- Get specific todos by ID
- Update existing todos (change title, description, priority, due date, tags, or completion status)
- Delete todos you no longer need
- Toggle completion status
- View completed or pending todos
- Find todos by tags
- Get statistics about your todo list

Example: "Show me all high priority pending todos" or "Mark todo with ID 'xyz' as completed"
"""

async def startup():
    """Initialize database connection"""
    await connect_to_mongo()

async def shutdown():
    """Clean up database connection"""
    await close_mongo_connection()

if __name__ == "__main__":
    # Set up startup and shutdown handlers
    import atexit
    atexit.register(lambda: asyncio.run(shutdown()))
    asyncio.run(startup())
    
    # Run the MCP server
    mcp.run()
