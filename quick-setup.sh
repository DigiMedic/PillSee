#!/bin/bash
# PillSee - Rychlé nastavení pro development
# Tento script nastaví celý PillSee stack

echo "🏥 PillSee - Rychlé nastavení"
echo "================================"

# Kontrola prerekvizit
echo "🔍 Kontroluji prerekvizity..."

# Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.9+ není nainstalován"
    exit 1
fi
echo "✅ Python nalezen: $(python3 --version)"

# Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 18+ není nainstalován"
    exit 1
fi
echo "✅ Node.js nalezen: $(node --version)"

# Backend setup
echo ""
echo "🐍 Nastavuji backend..."
cd pillsee-backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Vytvořen virtual environment"
fi

source venv/bin/activate
pip install -r requirements.txt
pip install chardet requests
echo "✅ Backend závislosti nainstalovány"

# Environment check
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Vytvořen .env soubor - NASTAVTE své API klíče!"
    echo "   - OPENAI_API_KEY"
    echo "   - SUPABASE_URL"
    echo "   - SUPABASE_ANON_KEY"
    echo "   - SUPABASE_SERVICE_KEY"
fi

cd ..

# Frontend setup
echo ""
echo "⚛️  Nastavuji frontend..."
cd pillsee-frontend

npm install
echo "✅ Frontend závislosti nainstalovány"

if [ ! -f ".env.local" ]; then
    echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local
    echo "✅ Frontend environment nastaven"
fi

cd ..

echo ""
echo "🎉 Setup dokončen!"
echo ""
echo "📋 Další kroky:"
echo "1. Nastavte API klíče v pillsee-backend/.env"
echo "2. Vytvořte Supabase projekt a spusťte supabase-setup.sql"
echo "3. Importujte SÚKL data: cd pillsee-backend && python import_sukl_data.py"
echo "4. Spusťte backend: uvicorn app.main:app --reload"
echo "5. Spusťte frontend: cd pillsee-frontend && npm run dev"
echo ""
echo "🌐 Backend: http://localhost:8000"
echo "📱 Frontend: http://localhost:3000"