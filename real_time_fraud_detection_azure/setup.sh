#!/usr/bin/env bash
set -euo pipefail

# Python Project Setup Script
# This script sets up the Python development environment

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Python Project Setup ===${NC}\n"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python is not installed or not in PATH${NC}"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python version: ${PYTHON_VERSION}${NC}"

# Check Python version (should be 3.8+)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [[ "$PYTHON_MAJOR" -lt 3 ]] || [[ "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 8 ]]; then
    echo -e "${RED}Error: Python 3.8 or higher is required${NC}"
    exit 1
fi

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate || source venv/Scripts/activate 2>/dev/null || {
    echo -e "${RED}Error: Could not activate virtual environment${NC}"
    exit 1
}
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
python -m pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install dependencies based on user choice
echo -e "\n${YELLOW}Choose installation option:${NC}"
echo "1) Core dependencies only"
echo "2) Core + Development tools"
echo "3) Core + ML dependencies"
echo "4) Core + Azure ML"
echo "5) All dependencies (recommended for full dev setup)"
echo -n "Enter choice [1-5]: "
read -r choice

case $choice in
    1)
        echo -e "${YELLOW}Installing core dependencies...${NC}"
        pip install -e .
        ;;
    2)
        echo -e "${YELLOW}Installing core + development dependencies...${NC}"
        pip install -e ".[dev]"
        ;;
    3)
        echo -e "${YELLOW}Installing core + ML dependencies...${NC}"
        pip install -e ".[ml]"
        ;;
    4)
        echo -e "${YELLOW}Installing core + Azure ML dependencies...${NC}"
        pip install -e ".[azureml]"
        ;;
    5)
        echo -e "${YELLOW}Installing all dependencies...${NC}"
        pip install -e ".[all]"
        ;;
    *)
        echo -e "${RED}Invalid choice. Installing core dependencies only.${NC}"
        pip install -e .
        ;;
esac

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Set up pre-commit hooks if dev dependencies installed
if [[ "$choice" == "2" ]] || [[ "$choice" == "5" ]]; then
    echo -e "${YELLOW}Setting up pre-commit hooks...${NC}"
    if command -v pre-commit &> /dev/null; then
        pre-commit install
        echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
    else
        echo -e "${YELLOW}⚠ pre-commit not found, skipping hook installation${NC}"
    fi
fi

# Create .env file if it doesn't exist
if [[ ! -f ".env" ]]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Remember to update .env with your actual Azure credentials!${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}Creating project directories...${NC}"
mkdir -p src/models src/services src/utils src/config src/exceptions
mkdir -p tests/unit tests/integration tests/fixtures
mkdir -p data models logs

# Create __init__.py files
touch src/__init__.py
touch src/models/__init__.py
touch src/services/__init__.py
touch src/utils/__init__.py
touch src/config/__init__.py
touch src/exceptions/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py

echo -e "${GREEN}✓ Project directories created${NC}"

# Display summary
echo -e "\n${GREEN}=== Setup Complete! ===${NC}\n"
echo -e "Project: Real-Time Fraud Detection System"
echo -e "Python version: ${PYTHON_VERSION}"
echo -e "Virtual environment: venv/"
echo -e "Configuration: pyproject.toml"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Activate virtual environment: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
echo "2. Update .env file with your Azure credentials"
echo "3. Run tests: python -m pytest"
echo "4. Format code: python -m black src/"
echo "5. Lint code: python -m flake8 src/"
echo ""
echo -e "${GREEN}Happy coding!${NC}"

