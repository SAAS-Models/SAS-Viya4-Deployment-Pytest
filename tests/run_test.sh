#!/bin/bash

# Exit on any error
set -e

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Starting Test Execution${NC}"
echo -e "${BLUE}================================${NC}"

# Create test reports directory if it doesn't exist
echo -e "${GREEN}Creating test reports directory...${NC}"
mkdir -p test-reports

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}pytest is not installed. Please install requirements.txt${NC}"
    exit 1
fi

echo -e "${GREEN}Running pytest with coverage...${NC}"

# Run pytest with coverage and generate multiple report formats
pytest \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=xml:coverage.xml \
  --cov-report=html:htmlcov \
  --junitxml=test-reports/junit.xml \
  --html=test-reports/report.html \
  --self-contained-html \
  -v \
  tests/

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}✓ All tests passed successfully!${NC}"
    echo -e "${GREEN}================================${NC}"
    echo -e "${BLUE}Reports generated:${NC}"
    echo -e "  - Coverage XML: coverage.xml"
    echo -e "  - Coverage HTML: htmlcov/index.html"
    echo -e "  - JUnit XML: test-reports/junit.xml"
    echo -e "  - HTML Report: test-reports/report.html"
else
    echo -e "${RED}================================${NC}"
    echo -e "${RED}✗ Tests failed!${NC}"
    echo -e "${RED}================================${NC}"
    exit 1
fi
