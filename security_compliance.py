#!/usr/bin/env python3
"""
Security compliance checker for agent codebase.
Identifies potential security issues and suggests fixes.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
import argparse
import json


@dataclass
class SecurityIssue:
    """Represents a security issue found in code."""
    severity: str  # 'critical', 'high', 'medium', 'low'
    category: str
    file_path: str
    line_number: int
    code_snippet: str
    description: str
    recommendation: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'severity': self.severity,
            'category': self.category,
            'file': str(self.file_path),
            'line': self.line_number,
            'code': self.code_snippet,
            'description': self.description,
            'recommendation': self.recommendation,
        }


class SecurityComplianceChecker:
    """Check codebase for security compliance."""
    
    def __init__(self, project_root: Path = Path(".")):
        self.project_root = project_root
        self.issues: List[SecurityIssue] = []
        self.stats = defaultdict(int)
    
    def check_file(self, file_path: Path) -> List[SecurityIssue]:
        """Check a single Python file for security issues."""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Parse AST for deeper analysis
            try:
                tree = ast.parse(content)
                issues.extend(self._check_ast(tree, file_path, lines))
            except SyntaxError:
                pass  # Skip files with syntax errors
            
            # Line-by-line checks
            for i, line in enumerate(lines, 1):
                issues.extend(self._check_line(line, i, file_path))
            
            # Content-level checks
            issues.extend(self._check_content(content, file_path))
            
        except Exception as e:
            print(f"Error checking {file_path}: {e}")
        
        return issues
    
    def _check_ast(self, tree: ast.AST, file_path: Path, lines: List[str]) -> List[SecurityIssue]:
        """Check AST for security issues."""
        issues = []
        
        class SecurityVisitor(ast.NodeVisitor):
            def __init__(self, checker, file_path, lines):
                self.checker = checker
                self.file_path = file_path
                self.lines = lines
                self.issues = []
            
            def visit_Call(self, node):
                # Check subprocess calls
                if isinstance(node.func, ast.Attribute):
                    if (hasattr(node.func.value, 'id') and 
                        node.func.value.id == 'subprocess' and 
                        node.func.attr in ['run', 'call', 'Popen']):
                        
                        # Check for shell=True
                        for keyword in node.keywords:
                            if keyword.arg == 'shell' and self._is_true(keyword.value):
                                self.issues.append(SecurityIssue(
                                    severity='critical',
                                    category='command_injection',
                                    file_path=str(self.file_path),
                                    line_number=node.lineno,
                                    code_snippet=self.lines[node.lineno-1].strip() if node.lineno <= len(self.lines) else '',
                                    description='subprocess with shell=True is vulnerable to command injection',
                                    recommendation='Use shell=False and pass arguments as a list, or use SecureCommandExecutor'
                                ))
                
                # Check eval/exec usage
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        self.issues.append(SecurityIssue(
                            severity='critical',
                            category='code_injection',
                            file_path=str(self.file_path),
                            line_number=node.lineno,
                            code_snippet=self.lines[node.lineno-1].strip() if node.lineno <= len(self.lines) else '',
                            description=f'{node.func.id}() can execute arbitrary code',
                            recommendation=f'Avoid {node.func.id}() or use ast.literal_eval() for safe evaluation'
                        ))
                
                self.generic_visit(node)
            
            def visit_Import(self, node):
                # Check for pickle imports (can execute arbitrary code)
                for alias in node.names:
                    if alias.name == 'pickle':
                        self.issues.append(SecurityIssue(
                            severity='high',
                            category='unsafe_deserialization',
                            file_path=str(self.file_path),
                            line_number=node.lineno,
                            code_snippet=self.lines[node.lineno-1].strip() if node.lineno <= len(self.lines) else '',
                            description='pickle can execute arbitrary code during deserialization',
                            recommendation='Use JSON or other safe serialization formats'
                        ))
                
                self.generic_visit(node)
            
            def _is_true(self, node):
                """Check if a node evaluates to True."""
                if isinstance(node, ast.Constant):
                    return node.value is True
                elif isinstance(node, ast.NameConstant):
                    return node.value is True
                return False
        
        visitor = SecurityVisitor(self, file_path, lines)
        visitor.visit(tree)
        return visitor.issues
    
    def _check_line(self, line: str, line_num: int, file_path: Path) -> List[SecurityIssue]:
        """Check a single line for security issues."""
        issues = []
        
        # Skip comments and empty lines
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            return issues
        
        # Check for hardcoded secrets
        secret_patterns = [
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key'),
            (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'Hardcoded token'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'Hardcoded secret'),
        ]
        
        for pattern, desc in secret_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                # Skip if it's loading from env
                if 'os.environ' not in line and 'getenv' not in line:
                    issues.append(SecurityIssue(
                        severity='high',
                        category='hardcoded_secrets',
                        file_path=str(file_path),
                        line_number=line_num,
                        code_snippet=stripped[:80] + '...' if len(stripped) > 80 else stripped,
                        description=desc,
                        recommendation='Use environment variables or secure key management'
                    ))
        
        # Check for unsafe file operations
        if 'open(' in line and 'w' in line and '/tmp' not in line:
            if not any(safe in line for safe in ['with', 'safe', 'secure']):
                issues.append(SecurityIssue(
                    severity='medium',
                    category='unsafe_file_operation',
                    file_path=str(file_path),
                    line_number=line_num,
                    code_snippet=stripped[:80] + '...' if len(stripped) > 80 else stripped,
                    description='File write operation without clear safety checks',
                    recommendation='Validate file paths and use context managers'
                ))
        
        return issues
    
    def _check_content(self, content: str, file_path: Path) -> List[SecurityIssue]:
        """Check entire file content for patterns."""
        issues = []
        
        # Check for missing input validation in command agents
        if 'Agent' in str(file_path) and 'subprocess' in content:
            if 'validate' not in content and 'CommandValidator' not in content:
                issues.append(SecurityIssue(
                    severity='critical',
                    category='missing_validation',
                    file_path=str(file_path),
                    line_number=0,
                    code_snippet='',
                    description='Agent executes commands without validation',
                    recommendation='Implement CommandValidator or use SafeCommandAgent base class'
                ))
        
        # Check for unbounded loops
        if 'while True:' in content:
            if 'timeout' not in content and 'max_iterations' not in content:
                issues.append(SecurityIssue(
                    severity='medium',
                    category='unbounded_loop',
                    file_path=str(file_path),
                    line_number=0,
                    code_snippet='',
                    description='Unbounded loop without timeout or iteration limit',
                    recommendation='Add timeout or max_iterations to prevent infinite loops'
                ))
        
        # Check for missing error handling
        if 'try:' not in content and ('subprocess' in content or 'Agent' in str(file_path)):
            issues.append(SecurityIssue(
                severity='medium',
                category='missing_error_handling',
                file_path=str(file_path),
                line_number=0,
                code_snippet='',
                description='Missing error handling for external operations',
                recommendation='Add try-except blocks for subprocess and external calls'
            ))
        
        return issues
    
    def check_project(self, exclude_patterns: List[str] = None) -> Dict[str, Any]:
        """Check entire project for security issues."""
        exclude_patterns = exclude_patterns or ['test_', '__pycache__', '.git', 'venv', '.venv']
        
        self.issues = []
        files_checked = 0
        
        for py_file in self.project_root.rglob("*.py"):
            # Skip excluded patterns
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue
            
            file_issues = self.check_file(py_file)
            self.issues.extend(file_issues)
            files_checked += 1
            
            # Update stats
            for issue in file_issues:
                self.stats[issue.severity] += 1
                self.stats[f'category_{issue.category}'] += 1
        
        # Sort issues by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        self.issues.sort(key=lambda x: (severity_order.get(x.severity, 4), x.file_path))
        
        return {
            'files_checked': files_checked,
            'total_issues': len(self.issues),
            'by_severity': {
                'critical': self.stats.get('critical', 0),
                'high': self.stats.get('high', 0),
                'medium': self.stats.get('medium', 0),
                'low': self.stats.get('low', 0),
            },
            'issues': [issue.to_dict() for issue in self.issues],
        }
    
    def generate_report(self, format: str = 'text') -> str:
        """Generate compliance report."""
        if format == 'json':
            return json.dumps(self.check_project(), indent=2)
        
        # Text report
        report = []
        report.append("=" * 70)
        report.append("SECURITY COMPLIANCE REPORT")
        report.append("=" * 70)
        report.append(f"Project: {self.project_root.absolute()}")
        report.append(f"Date: {Path(__file__).stat().st_mtime}")
        report.append("")
        
        results = self.check_project()
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 30)
        report.append(f"Files checked: {results['files_checked']}")
        report.append(f"Total issues: {results['total_issues']}")
        report.append("")
        report.append("By severity:")
        for severity, count in results['by_severity'].items():
            emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(severity, '⚪')
            report.append(f"  {emoji} {severity.upper()}: {count}")
        report.append("")
        
        # Critical issues detail
        critical_issues = [i for i in self.issues if i.severity == 'critical']
        if critical_issues:
            report.append("CRITICAL ISSUES (Fix immediately)")
            report.append("-" * 50)
            for issue in critical_issues:
                report.append(f"\n📍 {issue.file_path}:{issue.line_number}")
                report.append(f"   Category: {issue.category}")
                report.append(f"   Issue: {issue.description}")
                report.append(f"   Code: {issue.code_snippet}")
                report.append(f"   Fix: {issue.recommendation}")
        
        # High priority issues
        high_issues = [i for i in self.issues if i.severity == 'high']
        if high_issues:
            report.append("\n\nHIGH PRIORITY ISSUES")
            report.append("-" * 50)
            for issue in high_issues[:5]:  # Show first 5
                report.append(f"\n📍 {issue.file_path}:{issue.line_number}")
                report.append(f"   Issue: {issue.description}")
                report.append(f"   Fix: {issue.recommendation}")
            
            if len(high_issues) > 5:
                report.append(f"\n   ... and {len(high_issues) - 5} more high priority issues")
        
        # Recommendations
        report.append("\n\nRECOMMENDATIONS")
        report.append("-" * 30)
        
        if results['total_issues'] == 0:
            report.append("✅ No security issues found! Great job!")
        else:
            if critical_issues:
                report.append("1. Fix all critical issues immediately - they pose immediate security risk")
            report.append("2. Implement SecureCommandExecutor for all command execution")
            report.append("3. Use SafeCommandAgent as base class for new agents")
            report.append("4. Run security tests regularly: ./run_security_tests.sh")
            report.append("5. Enable command auditing in production")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)
    
    def generate_fixes(self) -> Dict[str, str]:
        """Generate automated fixes for common issues."""
        fixes = {}
        
        for issue in self.issues:
            if issue.category == 'command_injection' and 'shell=True' in issue.code_snippet:
                # Generate fix for shell=True
                fixes[f"{issue.file_path}:{issue.line_number}"] = {
                    'original': issue.code_snippet,
                    'fixed': issue.code_snippet.replace('shell=True', 'shell=False'),
                    'note': 'Remember to pass command as list: ["cmd", "arg1", "arg2"]'
                }
            
            elif issue.category == 'missing_validation':
                # Suggest SafeCommandAgent
                fixes[f"{issue.file_path}"] = {
                    'suggestion': 'Inherit from SafeCommandAgent instead of BaseAgent',
                    'example': '''
from safe_command_agent import SafeCommandAgent

class YourAgent(SafeCommandAgent):
    def __init__(self):
        super().__init__(
            command_whitelist_mode=True,
            max_command_memory_mb=512,
        )
'''
                }
        
        return fixes


def main():
    parser = argparse.ArgumentParser(description='Security compliance checker for agent codebase')
    parser.add_argument(
        '--project-root', type=str, default='.',
        help='Project root directory to check'
    )
    parser.add_argument(
        '--format', choices=['text', 'json'], default='text',
        help='Output format'
    )
    parser.add_argument(
        '--output', type=str,
        help='Output file (default: stdout)'
    )
    parser.add_argument(
        '--generate-fixes', action='store_true',
        help='Generate suggested fixes'
    )
    
    args = parser.parse_args()
    
    checker = SecurityComplianceChecker(Path(args.project_root))
    report = checker.generate_report(args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)
    
    if args.generate_fixes:
        fixes = checker.generate_fixes()
        if fixes:
            print("\n\nSUGGESTED FIXES")
            print("=" * 50)
            for location, fix in fixes.items():
                print(f"\n{location}:")
                for key, value in fix.items():
                    print(f"  {key}: {value}")


if __name__ == "__main__":
    main()