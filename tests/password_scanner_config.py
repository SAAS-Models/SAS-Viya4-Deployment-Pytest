"""
Password Scanner Configuration
Customize skip patterns and false positives here
"""

# Directories to completely skip during scanning
SKIP_DIRECTORIES = {
    '.git',
    'node_modules',
    '__pycache__',
    '.venv',
    'venv',
    'build',
    'dist',
    '.pytest_cache',
    'test_scripts',
    'test_data',
    'fixtures',
    'mock_data'
}

# Path patterns to skip (files containing these patterns will be ignored)
SKIP_PATH_PATTERNS = [
    '/tests/utils/bin/',      # Test utility files
    '/test_cases/',           # Test case files
    '/fixtures/',             # Test fixtures
    '/mock_data/',            # Mock data
    '/test_data/',            # Test data
    '/examples/',             # Example files
    '.example.',              # Example config files
    '.sample.',               # Sample files
]

# File extensions to scan
SCAN_EXTENSIONS = {
    '.py', '.yaml', '.yml', '.json', '.xml', '.properties',
    '.conf', '.config', '.sh', '.bash', '.env', '.txt',
    '.js', '.ts', '.java', '.sql', '.sas'
}

# Known false positive values
FALSE_POSITIVES = {
    'password', 'your_password', 'changeme', 'example',
    'secret', 'xxxx', '****', 'placeholder', 'none',
    'null', 'dummy', 'test', 'sample', '<password>',
    '${password}', '$PASSWORD', '{password}',
    'p@ssw0rd', 'p@$$w0rd', 'testpassword', 'dummypassword',
    'your_api_key', 'your_secret', 'insert_key_here',
    'my_secret_key', 'replace_me', 'mysecretkey',
    'examplekey', 'yourkeyhere', 'your-key-here'
}

# Regex patterns for detecting credentials
# Format: (pattern, description)
CREDENTIAL_PATTERNS = [
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
