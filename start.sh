#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"

echo "🚀 AI Dashboard Builder"
echo "========================"

# ── Backend ──────────────────────────────────────────────────────────────────
if [ ! -f "$BACKEND/.env" ]; then
  if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo ""
    echo "⚠️  ANTHROPIC_API_KEY not set."
    echo "   Copy backend/.env.example → backend/.env and add your key, or:"
    echo "   export ANTHROPIC_API_KEY=your_key_here"
    echo ""
    exit 1
  fi
  echo "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" > "$BACKEND/.env"
fi

if [ ! -d "$BACKEND/venv" ]; then
  echo "📦 Creating Python virtual environment..."
  python3 -m venv "$BACKEND/venv"
fi

echo "📦 Installing backend dependencies..."
"$BACKEND/venv/bin/pip" install -q -r "$BACKEND/requirements.txt"

echo "🔧 Starting backend on http://localhost:8000 ..."
cd "$BACKEND"
"$BACKEND/venv/bin/uvicorn" main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# ── Frontend ──────────────────────────────────────────────────────────────────
if ! command -v node &> /dev/null; then
  echo ""
  echo "⚠️  Node.js not found. Install from https://nodejs.org"
  echo "   Backend is running at http://localhost:8000"
  echo "   Install Node.js and run: cd frontend && npm install && npm run dev"
  wait $BACKEND_PID
  exit 0
fi

if [ ! -d "$FRONTEND/node_modules" ]; then
  echo "📦 Installing frontend dependencies..."
  cd "$FRONTEND" && npm install --silent
fi

echo "🎨 Starting frontend on http://localhost:3000 ..."
cd "$FRONTEND" && npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Ready!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API docs: http://localhost:8000/docs"
echo ""
echo "   Drop CSV files into:  data_dashboard/csvs/"
echo ""
echo "Press Ctrl+C to stop."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
