#!/usr/bin/env python3
"""
SAS Viya Repository Password Scanner
Scans files for hardcoded passwords and sensitive credentials
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class PasswordScanner:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.findings = []
        
        # File extensions to scan
        self.scan_extensions = {
            '.py', '.yaml', '.yml', '.json', '.xml', '.properties',
            '.conf', '.config', '.sh', '.bash', '.env', '.txt',
            '.js', '.ts', '.java', '.sql', '.sas', '.properties'
        }
        
        # Directories to skip
        self.skip_dirs = {
            '.git', 'node_modules', '__pycache__', '.venv', 
            'venv', 'build', 'dist', '.pytest_cache'
        }
        
        # Patterns for detecting hardcoded credentials
        self.patterns = [
            # Password patterns
            (r'password\s*=\s*["\']([^"\']+)["\']', 'Hardcoded Password'),
            (r'passwd\s*=\s*["\']([^"\']+)["\']', 'Hardcoded Password'),
            (r'pwd\s*=\s*["\']([^"\']+)["\']', 'Hardcoded Password'),
            
            # API keys and tokens
            (r'api[_-]?key\s*=\s*["\']([^"\']+)["\']', 'API Key'),
            (r'apikey\s*=\s*["\']([^"\']+)["\']', 'API Key'),
            (r'access[_-]?token\s*=\s*["\']([^"\']+)["\']', 'Access Token'),
            (r'secret[_-]?key\s*=\s*["\']([^"\']+)["\']', 'Secret Key'),
            (r'auth[_-]?token\s*=\s*["\']([^"\']+)["\']', 'Auth Token'),
            
            # Database credentials
            (r'db[_-]?password\s*=\s*["\']([^"\']+)["\']', 'Database Password'),
            (r'database[_-]?password\s*=\s*["\']([^"\']+)["\']', 'Database Password'),
            
            # SAS specific
            (r'sas[_-]?password\s*=\s*["\']([^"\']+)["\']', 'SAS Password'),
            (r'admin[_-]?password\s*=\s*["\']([^"\']+)["\']', 'Admin Password'),
            
            # AWS credentials
            (r'aws[_-]?access[_-]?key[_-]?id\s*=\s*["\']([^"\']+)["\']', 'AWS Access Key'),
            (r'aws[_-]?secret[_-]?access[_-]?key\s*=\s*["\']([^"\']+)["\']', 'AWS Secret Key'),
            
            # Generic secrets
            (r'secret\s*=\s*["\']([^"\']+)["\']', 'Secret'),
            (r'token\s*=\s*["\']([^"\']+)["\']', 'Token'),
            
            # Connection strings with credentials
            (r'://[^:]+:([^@]+)@', 'Credentials in Connection String'),
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), desc) 
            for pattern, desc in self.patterns
        ]
        
        # Common false positives to filter out
        self.false_positives = {
            'password', 'your_password', 'changeme', 'example', 
            'secret', 'xxxx', '****', 'placeholder', 'none',
            'null', 'dummy', 'test', 'sample', '<password>',
            '${password}', '$PASSWORD', '{password}'
        }
    
    def is_likely_false_positive(self, value: str) -> bool:
        """Check if the value is likely a placeholder or example"""
        if not value or len(value) < 3:
            return True
        
        value_lower = value.lower()
        
        # Check against known false positives
        if value_lower in self.false_positives:
            return True
        
        # Check for placeholder patterns
        if re.match(r'^[\*x]+$', value_lower):
            return True
        
        # Check for variable references
        if re.match(r'^\$\{.+\}$', value) or re.match(r'^\$.+$', value):
            return True
        
        return False
    
    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for hardcoded passwords"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                for pattern, description in self.compiled_patterns:
                    matches = pattern.finditer(line)
                    for match in matches:
                        # Extract the actual credential value if captured
                        if match.groups():
                            credential = match.group(1)
                        else:
                            credential = match.group(0)
                        
                        # Skip false positives
                        if self.is_likely_false_positive(credential):
                            continue
                        
                        findings.append({
                            'file': str(file_path.relative_to(self.repo_path)),
                            'line': line_num,
                            'type': description,
                            'content': line.strip(),
                            'severity': self.get_severity(description)
                        })
        
        except Exception as e:
            print(f"Error scanning {file_path}: {e}", file=sys.stderr)
        
        return findings
    
    def get_severity(self, finding_type: str) -> str:
        """Determine severity based on finding type"""
        high_severity = ['password', 'secret key', 'aws secret']
        medium_severity = ['api key', 'token', 'credentials']
        
        finding_lower = finding_type.lower()
        
        if any(hs in finding_lower for hs in high_severity):
            return 'HIGH'
        elif any(ms in finding_lower for ms in medium_severity):
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def scan_repository(self):
        """Recursively scan the repository"""
        if not self.repo_path.exists():
            print(f"Error: Repository path '{self.repo_path}' does not exist")
            sys.exit(1)
        
        print(f"Scanning repository: {self.repo_path}")
        print("-" * 60)
        
        files_scanned = 0
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # Check if file extension should be scanned
                if file_path.suffix.lower() in self.scan_extensions or file.startswith('.env'):
                    files_scanned += 1
                    file_findings = self.scan_file(file_path)
                    self.findings.extend(file_findings)
        
        print(f"\nScanned {files_scanned} files")
        print(f"Found {len(self.findings)} potential issues\n")
    
    def generate_report(self):
        """Generate a report of findings"""
        if not self.findings:
            print("✓ No hardcoded passwords found!")
            return
        
        # Sort by severity and file
        severity_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        self.findings.sort(key=lambda x: (severity_order[x['severity']], x['file']))
        
        print("=" * 60)
        print("FINDINGS REPORT")
        print("=" * 60)
        
        for finding in self.findings:
            print(f"\n[{finding['severity']}] {finding['type']}")
            print(f"File: {finding['file']}:{finding['line']}")
            print(f"Content: {finding['content'][:100]}")
            print("-" * 60)
        
        # Summary by severity
        high = sum(1 for f in self.findings if f['severity'] == 'HIGH')
        medium = sum(1 for f in self.findings if f['severity'] == 'MEDIUM')
        low = sum(1 for f in self.findings if f['severity'] == 'LOW')
        
        print(f"\nSUMMARY:")
        print(f"  HIGH severity:   {high}")
        print(f"  MEDIUM severity: {medium}")
        print(f"  LOW severity:    {low}")
        print(f"  TOTAL:           {len(self.findings)}")
        
        if high > 0:
            print(f"\n⚠ WARNING: {high} high severity findings require immediate attention!")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scan_passwords.py <repository_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    scanner = PasswordScanner(repo_path)
    scanner.scan_repository()
    scanner.generate_report()

if __name__ == "__main__":
    main()
