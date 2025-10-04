# Todo App - FastAPI with MCP Server & Gemini CLI Integration

A comprehensive todo application built with FastAPI and MongoDB, exposed as an MCP (Model Context Protocol) server for integration with Gemini CLI.

## 🎯 Project Overview

This project demonstrates:
- ✅ **FastAPI Application** with full CRUD operations
- ✅ **MongoDB Integration** with async Motor driver
- ✅ **MCP Server** using FastMCP framework
- ✅ **Gemini CLI Integration** for natural language todo management
- ✅ **Complete Tool Suite** with 10 MCP tools and 2 prompts

## Features

### FastAPI Application
- ✅ **Create Todos**: Add new todos with title, description, priority, due date, and tags
- ✅ **Read Todos**: Get todos with pagination, filtering, and search
- ✅ **Update Todos**: Modify existing todos
- ✅ **Delete Todos**: Remove todos
- ✅ **Toggle Completion**: Quickly mark todos as complete/incomplete
- 🔍 **Search**: Search todos by title and description
- 🏷️ **Tags**: Organize todos with custom tags
- ⚡ **Priority Levels**: Set priority (low, medium, high)
- 📅 **Due Dates**: Set and track due dates
- 📊 **Statistics**: Get completion rates and priority breakdowns
- 🔄 **Pagination**: Efficient data loading with pagination
- 🎯 **Filtering**: Filter by completion status, priority, and tags

### MCP Server Features
- **10 MCP Tools**: Complete todo management functionality
- **2 MCP Prompts**: Helpful templates for common operations
- **Natural Language Interface**: Use with Gemini CLI
- **Real-time Database Sync**: All operations persist to MongoDB

## Tech Stack

- **Backend**: FastAPI
- **Database**: MongoDB with Motor (async driver)
- **Validation**: Pydantic
- **Documentation**: Automatic OpenAPI/Swagger docs

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd todo-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MongoDB**
   - Install MongoDB locally or use MongoDB Atlas
   - Update the connection string in `config.py` if needed
   - Default: `mongodb://localhost:27017`

4. **Run the FastAPI application**
   ```bash
   python run.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Install MCP server in Gemini CLI**
   ```bash
   gemini mcp add "Todo App MCP Server" "python mcp_server.py" \
     --env MONGODB_URL="" \
     --env DATABASE_NAME="todo"
   ```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /` - Health check endpoint

### Todo Management
- `POST /todos` - Create a new todo
- `GET /todos` - Get todos with filtering and pagination
- `GET /todos/{todo_id}` - Get a specific todo
- `PUT /todos/{todo_id}` - Update a todo
- `DELETE /todos/{todo_id}` - Delete a todo
- `PATCH /todos/{todo_id}/toggle` - Toggle todo completion

### Special Queries
- `GET /todos/completed` - Get all completed todos
- `GET /todos/pending` - Get all pending todos
- `GET /todos/tag/{tag}` - Get todos by tag
- `GET /stats` - Get todo statistics

## Usage Examples

### Create a Todo
```bash
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI",
    "description": "Complete the FastAPI tutorial",
    "priority": "high",
    "tags": ["learning", "backend"]
  }'
```

### Get Todos with Filtering
```bash
curl "http://localhost:8000/todos?page=1&limit=10&completed=false&priority=high&search=learn"
```

### Toggle Todo Completion
```bash
curl -X PATCH "http://localhost:8000/todos/{todo_id}/toggle"
```

### Get Statistics
```bash
curl "http://localhost:8000/stats"
```

## 📹 Video Demonstration

A complete video demonstration is available in the `video/` folder showing:
- FastAPI application running and API documentation
- MCP server startup and functionality
- Gemini CLI integration and MCP tools usage
- Database operations and data persistence
- Natural language todo management

**Video Location**: `video/demo.webm` 

## 🚀 MCP Server Usage

### With Gemini CLI
Once installed, you can use natural language with Gemini CLI:

```bash
gemini chat
```

Then ask things like:
- *"Create a todo to review the project proposal with high priority"*
- *"Show me all my pending todos"*
- *"Mark the proposal review as completed"*
- *"Give me statistics about my todo progress"*
- *"Find all todos tagged with 'work'"*

### Available MCP Tools
- `create_todo` - Create new todos with all options
- `get_todos` - List todos with filtering and pagination
- `get_todo` - Get specific todo by ID
- `update_todo` - Update existing todos
- `delete_todo` - Delete todos
- `toggle_todo` - Toggle completion status
- `get_completed_todos` - Get all completed todos
- `get_pending_todos` - Get all pending todos
- `get_todos_by_tag` - Filter todos by tags
- `get_todo_stats` - Get comprehensive statistics

## Data Models

### Todo Schema
```json
{
  "id": "string",
  "title": "string (1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "completed": "boolean",
  "priority": "low|medium|high",
  "due_date": "datetime (optional)",
  "tags": ["string array"],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Configuration

The application uses environment variables for configuration:

- `MONGODB_URL`: MongoDB connection string (default: mongodb://localhost:27017)
- `DATABASE_NAME`: Database name (default: todo_app)

## Error Handling

The API includes comprehensive error handling:
- 400: Bad Request (validation errors)
- 404: Not Found (todo not found)
- 500: Internal Server Error (server issues)

## Development

### Project Structure
```
todo-app/
├── main.py          # FastAPI application
├── models.py        # Pydantic models
├── crud.py          # Database operations
├── database.py      # Database connection
├── config.py        # Configuration
├── requirements.txt # Dependencies
└── README.md        # Documentation
```

### Adding New Features

1. **New Fields**: Add to `TodoBase` model in `models.py`
2. **New Endpoints**: Add routes in `main.py`
3. **New Operations**: Add methods to `TodoCRUD` class in `crud.py`

## License

This project is open source and available under the MIT License.
