#!/usr/bin/env python3
"""
Pytest integration for Password Scanner
Tests the repository for hardcoded passwords and credentials
"""

import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path to import scan_passwords
sys.path.insert(0, os.path.abspath('..'))
from scan_passwords import PasswordScanner


class TestPasswordSecurity:
    """Test suite for password and credential scanning"""
    
    @pytest.fixture(scope="class")
    def scanner_results(self):
        """Fixture that runs the scanner once and returns results"""
        # Get repository root (3 levels up from tests/utils/test_scripts)
        repo_path = Path(__file__).parent.parent.parent.parent
        
        scanner = PasswordScanner(str(repo_path))
        scanner.scan_repository()
        
        return scanner
    
    def test_no_hardcoded_passwords(self, scanner_results):
        """Test that no hardcoded passwords are found in the repository"""
        high_severity = [f for f in scanner_results.findings if f['severity'] == 'HIGH']
        
        if high_severity:
            error_msg = "\n❌ HIGH SEVERITY: Found hardcoded passwords:\n"
            for finding in high_severity:
                error_msg += f"\n  [{finding['severity']}] {finding['type']}\n"
                error_msg += f"  File: {finding['file']}:{finding['line']}\n"
                error_msg += f"  Content: {finding['content'][:100]}\n"
            
            pytest.fail(error_msg)
    
    def test_no_api_keys(self, scanner_results):
        """Test that no API keys or tokens are hardcoded"""
        api_findings = [
            f for f in scanner_results.findings 
            if 'API Key' in f['type'] or 'Token' in f['type']
        ]
        
        if api_findings:
            error_msg = "\n❌ Found hardcoded API keys or tokens:\n"
            for finding in api_findings:
                error_msg += f"\n  [{finding['severity']}] {finding['type']}\n"
                error_msg += f"  File: {finding['file']}:{finding['line']}\n"
            
            pytest.fail(error_msg)
    
    def test_no_database_credentials(self, scanner_results):
        """Test that no database credentials are hardcoded"""
        db_findings = [
            f for f in scanner_results.findings 
            if 'Database' in f['type'] or 'Connection String' in f['type']
        ]
        
        if db_findings:
            error_msg = "\n❌ Found hardcoded database credentials:\n"
            for finding in db_findings:
                error_msg += f"\n  [{finding['severity']}] {finding['type']}\n"
                error_msg += f"  File: {finding['file']}:{finding['line']}\n"
            
            pytest.fail(error_msg)
    
    def test_no_aws_credentials(self, scanner_results):
        """Test that no AWS credentials are hardcoded"""
        aws_findings = [
            f for f in scanner_results.findings 
            if 'AWS' in f['type']
        ]
        
        if aws_findings:
            error_msg = "\n❌ Found hardcoded AWS credentials:\n"
            for finding in aws_findings:
                error_msg += f"\n  [{finding['severity']}] {finding['type']}\n"
                error_msg += f"  File: {finding['file']}:{finding['line']}\n"
            
            pytest.fail(error_msg)
    
    def test_security_summary(self, scanner_results):
        """Generate a summary report of all findings"""
        findings = scanner_results.findings
        
        if not findings:
            print("\n✅ Security Scan PASSED: No hardcoded credentials found!")
            return
        
        # Print summary
        high = sum(1 for f in findings if f['severity'] == 'HIGH')
        medium = sum(1 for f in findings if f['severity'] == 'MEDIUM')
        low = sum(1 for f in findings if f['severity'] == 'LOW')
        
        summary = f"""
        
📊 SECURITY SCAN SUMMARY:
{'='*60}
  HIGH severity:   {high}
  MEDIUM severity: {medium}
  LOW severity:    {low}
  TOTAL:           {len(findings)}
{'='*60}
"""
        print(summary)
        
        # Print detailed findings
        if findings:
            print("\n🔍 DETAILED FINDINGS:")
            for finding in findings:
                print(f"\n  [{finding['severity']}] {finding['type']}")
                print(f"  File: {finding['file']}:{finding['line']}")
                print(f"  Content: {finding['content'][:80]}...")
        
        # This test always passes - it's just for reporting
        # Individual tests above will fail if issues are found
        assert True


if __name__ == "__main__":
    # Allow running directly with: python test_password_scan.py
    pytest.main([__file__, "-v", "--tb=short"])
