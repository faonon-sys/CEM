#!/bin/bash
# Development startup script

echo "Starting Structured Reasoning System in development mode..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your API keys before continuing"
    exit 1
fi

# Start services with docker-compose
echo "Starting services..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 5

# Run database migrations
echo "Running database migrations..."
cd backend
alembic upgrade head
cd ..

# Start backend
echo "Starting backend API..."
cd backend
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
echo "Starting frontend..."
cd frontend
streamlit run streamlit_app/main.py --server.port 5000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "================================================"
echo "Structured Reasoning System is running!"
echo "================================================"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Frontend: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; docker-compose down; exit" INT
wait
