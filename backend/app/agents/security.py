# ... (existing imports)

class SecurityAgent:
    """
    Security Specialist Agent logic.
    Focuses on SAST (Static Application Security Testing) and secure coding patterns.
    """
    
    def __init__(self, run_id: str):
        self.run_id = run_id
        
    async def scan_code(self, file_content: str, language: str) -> List[str]:
        """
        Simulate a SAST scan on code content.
        In Phase 2 MVP, this uses keyword matching for common vulnerabilities.
        """
        issues = []
        
        # SQL Injection detection (basic)
        if language == "python":
            if "execute(" in file_content and "%" in file_content:
                issues.append("Potential SQL Injection: Use parameterized queries instead of string formatting.")
            if "eval(" in file_content:
                issues.append("Dangerous Function: Avoid using eval() as it allows arbitrary code execution.")
            if "subprocess.call(" in file_content and "shell=True" in file_content:
                issues.append("Command Injection: Avoid shell=True in subprocess calls.")

        # Hardcoded secrets
        if "password =" in file_content or "api_key =" in file_content:
            issues.append("Secret Exposure: Hardcoded credentials detected. Use environment variables.")
            
        return issues

    async def generate_security_policy(self) -> str:
        """Generates a standard SECURITY.md"""
        return """# Security Policy

## Reporting a Vulnerability

Please report security issues to security@example.com.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
"""
