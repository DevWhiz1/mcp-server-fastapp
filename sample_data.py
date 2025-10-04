#!/usr/bin/env python3
"""
Script to populate the database with sample data for testing
"""
import asyncio
from datetime import datetime, timedelta
from database import connect_to_mongo, close_mongo_connection
from crud import TodoCRUD
from models import TodoCreate

async def create_sample_data():
    """Create sample todos for testing"""
    await connect_to_mongo()
    
    # Get database instance
    from database import get_database
    db = await get_database()
    crud = TodoCRUD(db)
    
    sample_todos = [
        TodoCreate(
            title="Learn FastAPI",
            description="Complete the FastAPI tutorial and build a todo app",
            priority="high",
            tags=["learning", "backend", "python"],
            due_date=datetime.utcnow() + timedelta(days=7)
        ),
        TodoCreate(
            title="Setup MongoDB",
            description="Install and configure MongoDB for the project",
            priority="high",
            tags=["database", "setup"],
            due_date=datetime.utcnow() + timedelta(days=1)
        ),
        TodoCreate(
            title="Write API Documentation",
            description="Create comprehensive API documentation",
            priority="medium",
            tags=["documentation", "api"],
            due_date=datetime.utcnow() + timedelta(days=3)
        ),
        TodoCreate(
            title="Add Error Handling",
            description="Implement proper error handling and validation",
            priority="medium",
            tags=["error-handling", "validation"],
            completed=True
        ),
        TodoCreate(
            title="Create Unit Tests",
            description="Write unit tests for all CRUD operations",
            priority="low",
            tags=["testing", "quality"],
            due_date=datetime.utcnow() + timedelta(days=14)
        ),
        TodoCreate(
            title="Deploy to Production",
            description="Deploy the application to a production environment",
            priority="high",
            tags=["deployment", "production"],
            due_date=datetime.utcnow() + timedelta(days=30)
        ),
        TodoCreate(
            title="Optimize Database Queries",
            description="Review and optimize MongoDB queries for better performance",
            priority="low",
            tags=["optimization", "database"],
            due_date=datetime.utcnow() + timedelta(days=21)
        ),
        TodoCreate(
            title="Add Authentication",
            description="Implement user authentication and authorization",
            priority="medium",
            tags=["security", "authentication"],
            due_date=datetime.utcnow() + timedelta(days=10)
        ),
        TodoCreate(
            title="Create Frontend",
            description="Build a React frontend for the todo app",
            priority="medium",
            tags=["frontend", "react", "ui"],
            due_date=datetime.utcnow() + timedelta(days=21)
        ),
        TodoCreate(
            title="Setup CI/CD Pipeline",
            description="Configure continuous integration and deployment",
            priority="low",
            tags=["ci-cd", "devops"],
            due_date=datetime.utcnow() + timedelta(days=28)
        ),
        TodoCreate(
            title="Daily 10 min walk",
            description="A quick 10-minute walk to stay active",
            priority="high",
            tags=["health", "exercise"],
            due_date=datetime.utcnow() + timedelta(days=1)
        )
    ]
    
    print("Creating sample todos...")
    created_count = 0
    
    for todo_data in sample_todos:
        try:
            await crud.create_todo(todo_data)
            created_count += 1
            print(f"✅ Created: {todo_data.title}")
        except Exception as e:
            print(f"❌ Failed to create {todo_data.title}: {e}")
    
    print(f"\n🎉 Successfully created {created_count} sample todos!")
    print("\nYou can now test the API endpoints:")
    print("- GET /todos - List all todos")
    print("- GET /stats - View statistics")
    print("- GET /todos/completed - View completed todos")
    print("- GET /todos/pending - View pending todos")
    
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(create_sample_data())
