import re
from typing import List, Dict, Any, Optional
from app.schemas import InlineSuggestion, ReviewCategory, Severity
from app.services.diff_parser import FileChange

class SecurityScanner:
    """
    Deterministic static vulnerability and secret scanner.
    Detects OWASP Top 10 hazards, leaked credentials, injection vectors,
    and dangerous execution sinks on added/modified diff lines.
    """

    PATTERNS = [
        # --- SECRETS & LEAKED TOKENS ---
        {
            "id": "SEC-001",
            "regex": r"(?:AKIA[0-9A-Z]{16})",
            "category": ReviewCategory.SECURITY,
            "severity": Severity.CRITICAL,
            "title": "Hardcoded AWS Access Key Exposed",
            "desc": "An AWS Access Key ID was detected in plaintext. Hardcoded credentials risk account compromise. Store credentials in environment variables or cloud secret managers (AWS Secrets Manager, Doppler, Vault).",
            "fix": 'aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")'
        },
        {
            "id": "SEC-002",
            "regex": r"(?:ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{82})",
            "category": ReviewCategory.SECURITY,
            "severity": Severity.CRITICAL,
            "title": "Exposed GitHub Personal Access Token",
            "desc": "A GitHub personal access token was committed to the repository. This token must be revoked immediately and loaded via repository secrets.",
            "fix": 'github_token = os.environ.get("GITHUB_TOKEN")'
        },
        {
            "id": "SEC-003",
            "regex": r"(?:sk-[a-zA-Z0-9]{32,}|sk-proj-[a-zA-Z0-9_\-]{32,})",
            "category": ReviewCategory.SECURITY,
            "severity": Severity.CRITICAL,
            "title": "Hardcoded OpenAI / AI API Key Detected",
            "desc": "An active OpenAI secret key was found in source code. If committed, automated bot scanners will compromise the key within minutes.",
            "fix": 'openai_api_key = os.environ.get("OPENAI_API_KEY")'
        },
        {
            "id": "SEC-004",
            "regex": r"-----BEGIN (?:RSA|EC|DSA|OPENSSH) PRIVATE KEY-----",
            "category": ReviewCategory.SECURITY,
            "severity": Severity.CRITICAL,
            "title": "Cryptographic Private Key Committed",
            "desc": "A private cryptographic key is embedded in code. Private keys must never be committed to git history.",
            "fix": '# Load private key from secure vault or mounted secret volume'
        },
        {
            "id": "SEC-005",
            "regex": r"(?:password|passwd|secret_key|api_secret)\s*=\s*['\"][A-Za-z0-9@#$%^&+=_-]{8,}['\"]",
            "category": ReviewCategory.SECURITY,
            "severity": Severity.CRITICAL,
            "title": "Hardcoded Password / Secret Assignment",
            "desc": "Plaintext secret or password assigned directly in code. Use environment variables (e.g., os.getenv or pydantic-settings).",
            "fix": 'secret_value = os.getenv("SECRET_NAME")'
        },

        # --- INJECTION VULNERABILITIES ---
        {
            "id": "SEC-010",
            "regex": r"(?:(?:execute|cursor\.execute)\s*\(\s*f?[\"'].*?(?:SELECT|INSERT|UPDATE|DELETE)|f[\"'].*?(?:SELECT|INSERT|UPDATE|DELETE|FROM|WHERE).*?\{)",
            "category": ReviewCategory.SECURITY,
            "severity": Severity.CRITICAL,
            "title": "SQL Injection (CWE-89): Formatted Query String",
            "desc": "User parameters are being directly concatenated or interpolated into a SQL statement using f-strings. This allows attackers to manipulate queries and dump database tables. Always use parameterized queries.",
            "fix": 'cursor.execute("SELECT * FROM table WHERE id = %s", (user_id,))'
        },
        {
            "id": "SEC-011",
            "regex": r"(?:eval|exec)\s*\(",
            "category": ReviewCategory.SECURITY,
            "severity": Severity.CRITICAL,
            "title": "Remote Code Execution (CWE-95): Unsafe eval/exec",
            "desc": "Usage of `eval()` or `exec()` executes arbitrary strings as system code. If input originates from user requests, it leads to full server takeover. Use `ast.literal_eval` or structured JSON parsers.",
            "fix": 'import ast\nsafe_value = ast.literal_eval(user_input)'
        },
        {
            "id": "SEC-012",
            "regex": r"pickle\.(?:loads|load)\s*\(",
            "category": ReviewCategory.SECURITY,
            "severity": Severity.CRITICAL,
            "title": "Insecure Deserialization (CWE-502): Python pickle",
            "desc": "Python's `pickle` library is insecure for untrusted inputs and can execute arbitrary payloads during deserialization. Use JSON, Protocol Buffers, or safe serialization formats.",
            "fix": 'import json\ndata = json.loads(payload)'
        },
        {
            "id": "SEC-013",
            "regex": r"(?:subprocess\.Popen|subprocess\.run|subprocess\.call|os\.system)\s*\([^)]*shell\s*=\s*True",
            "category": ReviewCategory.SECURITY,
            "severity": Severity.CRITICAL,
            "title": "Command Injection (CWE-78): Shell=True Execution",
            "desc": "Executing shell commands with `shell=True` passes commands through system shells (/bin/sh or cmd.exe), enabling command chaining with semicolons or backticks. Pass arguments as a list with `shell=False`.",
            "fix": 'subprocess.run(["command", arg1, arg2], check=True)'
        },
        {
            "id": "SEC-014",
            "regex": r"yaml\.load\s*\([^,)]*\)",
            "category": ReviewCategory.SECURITY,
            "severity": Severity.CRITICAL,
            "title": "Insecure YAML Deserialization",
            "desc": "Default `yaml.load()` in PyYAML can instantiate arbitrary Python objects. Use `yaml.safe_load()` instead.",
            "fix": 'yaml.safe_load(stream)'
        },

        # --- WEB & NETWORK MISCONFIGURATIONS ---
        {
            "id": "SEC-020",
            "regex": r"verify\s*=\s*False",
            "category": ReviewCategory.SECURITY,
            "severity": Severity.WARNING,
            "title": "TLS/SSL Certificate Validation Disabled",
            "desc": "Setting `verify=False` in HTTP clients (requests/httpx) disables SSL certificate verification, making the communication vulnerable to Man-In-The-Middle (MITM) attacks.",
            "fix": 'verify=True'
        },
        {
            "id": "SEC-021",
            "regex": r"(?:DEBUG\s*=\s*True|app\.run\([^)]*debug\s*=\s*True)",
            "category": ReviewCategory.SECURITY,
            "severity": Severity.WARNING,
            "title": "Production Debug Mode Enabled",
            "desc": "Debug mode exposes interactive web debuggers, stack traces, and environment variables to users. Ensure debug mode is toggled via environment variable.",
            "fix": 'debug = os.getenv("ENVIRONMENT") == "development"'
        },
        {
            "id": "SEC-022",
            "regex": r"dangerouslySetInnerHTML\s*=\s*\{\s*__html\s*:",
            "category": ReviewCategory.SECURITY,
            "severity": Severity.WARNING,
            "title": "Cross-Site Scripting (XSS) Hazard: dangerouslySetInnerHTML",
            "desc": "Rendering raw unescaped HTML allows malicious script execution in the user's browser. Sanitize strings using DOMPurify before injection.",
            "fix": 'dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userContent) }}'
        }
    ]

    def scan_file(self, file_change: FileChange) -> List[InlineSuggestion]:
        findings: List[InlineSuggestion] = []

        for added in file_change.added_lines:
            line_no = added.get("line_no")
            content = added.get("content", "")

            # Ignore comments
            stripped = content.strip()
            if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*"):
                continue

            for rule in self.PATTERNS:
                if re.search(rule["regex"], content, re.IGNORECASE):
                    findings.append(InlineSuggestion(
                        file_path=file_change.file_path,
                        line_number=line_no,
                        category=rule["category"],
                        severity=rule["severity"],
                        title=rule["title"],
                        description=rule["desc"],
                        original_code=content.strip(),
                        suggested_code=rule["fix"]
                    ))
                    break  # One finding per rule match per line

        return findings

    def scan_diff(self, file_changes: List[FileChange]) -> List[InlineSuggestion]:
        all_findings: List[InlineSuggestion] = []
        for fc in file_changes:
            all_findings.extend(self.scan_file(fc))
        return all_findings

security_scanner_service = SecurityScanner()
