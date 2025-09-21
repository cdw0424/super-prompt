# packages/core-py/super_prompt/utils/helpers.py
"""
공통 유틸리티 함수들
"""

import json
import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional


def text_from(content: Any) -> str:
    """Extract text from TextContent or other content types"""
    try:
        if hasattr(content, 'text'):
            return getattr(content, "text", "") or ""
    except Exception:
        pass
    return "" if content is None else str(content)


def short_description(doc: Optional[str]) -> str:
    """Extract short description from docstring"""
    if not doc:
        return ""
    lines = [line.strip() for line in doc.strip().splitlines() if line.strip()]
    return lines[0] if lines else ""


def safe_string(value: Any) -> str:
    """Convert value to safe string representation"""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return str(value)


# Using system Python (venv functionality removed)





# Legacy MCP server management functions removed
# Use the new stateless mcp_stdio.py approach instead


def get_persona_resource_links(persona_name: str) -> str:
    """페르소나별 유용한 리소스 링크들을 반환"""
    resource_links = {
        "architect": """
📚 **Recommended Resources:**
• [System Design Interview](https://github.com/donnemartin/system-design-primer)
• [Designing Data-Intensive Applications](https://dataintensive.net/)
• [AWS Architecture Center](https://aws.amazon.com/architecture/)
• [Google Cloud Architecture Framework](https://cloud.google.com/architecture/framework)
""",
        "frontend": """
📚 **Recommended Resources:**
• [React Documentation](https://react.dev/)
• [Vue.js Guide](https://vuejs.org/guide/)
• [MDN Web Docs](https://developer.mozilla.org/)
• [Web.dev](https://web.dev/)
• [A11Y Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
""",
        "backend": """
📚 **Recommended Resources:**
• [REST API Design Best Practices](https://restfulapi.net/)
• [GraphQL Specification](https://spec.graphql.org/)
• [Database Design Tutorial](https://www.lucidchart.com/pages/database-diagram/database-design)
• [OWASP API Security](https://owasp.org/www-project-api-security/)
""",
        "security": """
📚 **Recommended Resources:**
• [OWASP Top 10](https://owasp.org/www-project-top-ten/)
• [MITRE CWE Database](https://cwe.mitre.org/)
• [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
• [SANS Security Policy Templates](https://www.sans.org/information-security-policy/)
""",
        "analyzer": """
📚 **Recommended Resources:**
• [Root Cause Analysis Guide](https://asq.org/quality-resources/root-cause-analysis)
• [Debugging Techniques](https://developers.google.com/web/tools/chrome-devtools)
• [Performance Analysis Tools](https://developer.chrome.com/docs/devtools/)
""",
    }
    return resource_links.get(persona_name, "")
