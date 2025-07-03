#!/bin/bash
# Automated security testing for agent framework

set -e  # Exit on error

echo "========================================="
echo "Agent Framework Security Test Suite"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Warning: Virtual environment not activated${NC}"
    echo "Attempting to activate .venv..."
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    else
        echo -e "${RED}Error: Virtual environment not found${NC}"
        exit 1
    fi
fi

# Install security testing dependencies if needed
echo "Checking dependencies..."
pip install -q pytest pytest-cov pytest-timeout matplotlib seaborn pandas

# Run security-specific tests
echo ""
echo "1. Running Security Unit Tests"
echo "------------------------------"
pytest tests/test_security.py -v --tb=short

# Run tests for secure agent implementations
echo ""
echo "2. Running Secure Agent Tests"
echo "-----------------------------"
pytest tests/test_agent_simpledspy_secure.py -v --tb=short

# Run integration tests if available
echo ""
echo "3. Running Integration Tests"
echo "----------------------------"
pytest tests/ -v -m integration --tb=short || echo "No integration tests found"

# Test for command injection vulnerabilities
echo ""
echo "4. Command Injection Tests"
echo "--------------------------"
python -c "
from utils.command_executor import CommandValidator

validator = CommandValidator()
dangerous_commands = [
    'rm -rf /',
    'echo safe && rm -rf /',
    ':(){ :|:& };:',
    'cat /etc/passwd',
    'sudo anything',
]

print('Testing dangerous command patterns...')
all_blocked = True
for cmd in dangerous_commands:
    is_safe, msg = validator.validate(cmd)
    if is_safe:
        print(f'❌ FAILED: {cmd} was not blocked!')
        all_blocked = False
    else:
        print(f'✅ PASSED: {cmd} was blocked')

if all_blocked:
    print('\n✅ All dangerous commands were blocked')
else:
    print('\n❌ Some dangerous commands were not blocked!')
    exit(1)
"

# Test resource limits
echo ""
echo "5. Resource Limit Tests"
echo "-----------------------"
python -c "
import time
from utils.command_executor import SecureCommandExecutor

executor = SecureCommandExecutor(
    max_memory_mb=50,
    max_cpu_seconds=2,
)

print('Testing resource limits...')

# Test memory limit
print('Testing memory limit...')
result = executor.execute('python -c \"x = [0] * (100 * 1024 * 1024)\"', timeout=3)
if result.return_code != 0:
    print('✅ PASSED: Memory limit enforced')
else:
    print('❌ FAILED: Memory limit not enforced')

# Test CPU limit
print('Testing CPU time limit...')
result = executor.execute('python -c \"while True: pass\"', timeout=3)
if result.timed_out or result.return_code != 0:
    print('✅ PASSED: CPU limit enforced')
else:
    print('❌ FAILED: CPU limit not enforced')
"

# Check for common security issues in code
echo ""
echo "6. Static Security Analysis"
echo "---------------------------"
echo "Checking for common security issues..."

# Check for shell=True usage
echo -n "Checking for unsafe shell=True usage... "
SHELL_TRUE_COUNT=$(grep -r "shell=True" --include="*.py" . 2>/dev/null | grep -v "test_" | grep -v "secure" | wc -l)
if [ $SHELL_TRUE_COUNT -gt 0 ]; then
    echo -e "${RED}Found $SHELL_TRUE_COUNT instances of shell=True${NC}"
    grep -r "shell=True" --include="*.py" . 2>/dev/null | grep -v "test_" | grep -v "secure" | head -5
else
    echo -e "${GREEN}No unsafe shell=True usage found${NC}"
fi

# Check for subprocess without validation
echo -n "Checking for subprocess calls without validation... "
SUBPROCESS_COUNT=$(grep -r "subprocess\." --include="*.py" . 2>/dev/null | grep -v "test_" | grep -v "secure" | grep -v "command_executor" | wc -l)
if [ $SUBPROCESS_COUNT -gt 0 ]; then
    echo -e "${YELLOW}Found $SUBPROCESS_COUNT subprocess calls to review${NC}"
else
    echo -e "${GREEN}No direct subprocess calls found${NC}"
fi

# Generate security report
echo ""
echo "7. Generating Security Report"
echo "-----------------------------"
if [ -f "command_audit.ndjson" ]; then
    python security_dashboard.py --report --output security_report.txt
else
    echo "No audit data found yet. Run some agents to generate audit logs."
fi

# Summary
echo ""
echo "========================================="
echo "Security Test Summary"
echo "========================================="

# Count test results
TOTAL_TESTS=$(pytest tests/test_security.py tests/test_agent_simpledspy_secure.py --collect-only -q 2>/dev/null | grep -c "<" || echo "0")
echo "Total security tests: $TOTAL_TESTS"

# Check coverage if available
if command -v coverage &> /dev/null; then
    echo ""
    echo "Running coverage analysis..."
    coverage run -m pytest tests/test_security.py tests/test_agent_simpledspy_secure.py -q
    echo ""
    echo "Security-related code coverage:"
    coverage report -m --include="utils/command_executor.py,utils/context_manager.py,safe_command_agent.py,agent_simpledspy_secure.py" || true
fi

echo ""
echo "✅ Security testing complete!"
echo ""
echo "Next steps:"
echo "1. Review any failed tests above"
echo "2. Check security_report.txt for detailed analysis"
echo "3. Run 'python security_dashboard.py' to generate visualizations"
echo "4. Migrate remaining agents using SECURITY_MIGRATION.md"