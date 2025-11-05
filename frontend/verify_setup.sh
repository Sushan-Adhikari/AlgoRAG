#!/bin/bash

# AlgoRAG Frontend Setup Verification Script
# This script checks that all required files are in place

echo "========================================"
echo "AlgoRAG Frontend Setup Verification"
echo "========================================"
echo ""

FRONTEND_DIR="/Users/sushan/Desktop/Papers/RAG_Algorithms_and_Complexity/algorag/frontend"
cd "$FRONTEND_DIR" || exit 1

echo "Checking directory: $FRONTEND_DIR"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check file existence
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 (missing)"
        return 1
    fi
}

# Function to check directory existence
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        return 0
    else
        echo -e "${RED}✗${NC} $1/ (missing)"
        return 1
    fi
}

echo "1. Checking directories..."
echo "----------------------------"
check_dir "public"
check_dir "src"
check_dir "node_modules"
echo ""

echo "2. Checking public/ files..."
echo "----------------------------"
check_file "public/index.html"
check_file "public/manifest.json"
check_file "public/robots.txt"
check_file "public/favicon.ico"
echo ""

echo "3. Checking src/ files..."
echo "----------------------------"
check_file "src/index.js"
check_file "src/App.jsx"
check_file "src/App.css"
echo ""

echo "4. Checking configuration files..."
echo "----------------------------"
check_file "package.json"
check_file "package-lock.json"
check_file ".env"
check_file ".gitignore"
echo ""

echo "5. Checking package.json dependencies..."
echo "----------------------------"
if command -v jq &> /dev/null; then
    REACT_VERSION=$(jq -r '.dependencies.react' package.json 2>/dev/null)
    REACT_DOM_VERSION=$(jq -r '.dependencies["react-dom"]' package.json 2>/dev/null)
    REACT_SCRIPTS_VERSION=$(jq -r '.dependencies["react-scripts"]' package.json 2>/dev/null)

    echo "  react: $REACT_VERSION"
    echo "  react-dom: $REACT_DOM_VERSION"
    echo "  react-scripts: $REACT_SCRIPTS_VERSION"
else
    echo -e "${YELLOW}⚠${NC} jq not installed, skipping JSON parsing"
    grep -E '"react"|"react-dom"|"react-scripts"' package.json | head -3
fi
echo ""

echo "6. Checking .env configuration..."
echo "----------------------------"
if [ -f ".env" ]; then
    API_URL=$(grep REACT_APP_API_URL .env | cut -d '=' -f2)
    echo "  API URL: $API_URL"
else
    echo -e "${RED}✗${NC} .env file missing"
fi
echo ""

echo "7. Verifying React app structure..."
echo "----------------------------"

# Check if index.html has root div
if grep -q '<div id="root">' public/index.html 2>/dev/null; then
    echo -e "${GREEN}✓${NC} index.html has root div"
else
    echo -e "${RED}✗${NC} index.html missing root div"
fi

# Check if index.html includes MathJax
if grep -q 'mathjax' public/index.html 2>/dev/null; then
    echo -e "${GREEN}✓${NC} MathJax included in index.html"
else
    echo -e "${YELLOW}⚠${NC} MathJax not found in index.html"
fi

# Check if index.js imports React
if grep -q 'import React' src/index.js 2>/dev/null; then
    echo -e "${GREEN}✓${NC} index.js imports React"
else
    echo -e "${RED}✗${NC} index.js doesn't import React"
fi

# Check if index.js imports App
if grep -q 'import App' src/index.js 2>/dev/null; then
    echo -e "${GREEN}✓${NC} index.js imports App component"
else
    echo -e "${RED}✗${NC} index.js doesn't import App"
fi

echo ""

echo "8. Testing npm commands..."
echo "----------------------------"
if command -v npm &> /dev/null; then
    echo -e "${GREEN}✓${NC} npm is installed ($(npm --version))"

    # Check if node_modules is properly installed
    if [ -d "node_modules/react" ]; then
        echo -e "${GREEN}✓${NC} React modules installed"
    else
        echo -e "${RED}✗${NC} React modules not found, run: npm install"
    fi
else
    echo -e "${RED}✗${NC} npm not found"
fi
echo ""

echo "========================================"
echo "Setup Verification Complete"
echo "========================================"
echo ""
echo "To start the frontend:"
echo "  cd $FRONTEND_DIR"
echo "  npm start"
echo ""
echo "Frontend will run on: http://localhost:3000"
echo "Backend should be on: http://localhost:8000"
echo ""
