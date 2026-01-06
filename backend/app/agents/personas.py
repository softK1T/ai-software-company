import os
from typing import Optional, List, Dict, Any
from enum import Enum
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class AgentRole(str, Enum):
    PM = "PRODUCT_MANAGER"
    LEAD = "TECH_LEAD"
    DEV = "DEVELOPER" 
    QA = "QA_ENGINEER"
    DEVOPS = "DEVOPS_ENGINEER"
    SECURITY = "SECURITY_SPECIALIST"
    REVIEWER = "CODE_REVIEWER"

class AgentPersona(BaseModel):
    name: str
    role: AgentRole
    system_prompt: str
    tools: List[str]
    temperature: float = 0.7

# --- Prompts ---

PM_PROMPT = """You are an expert Product Manager. 
Your goal is to break down high-level requirements into clear, actionable development tasks.
Analyze the user's request and the project template constraints.
Output a list of tasks with:
- Clear title
- Detailed description
- Acceptance criteria
- Dependencies
- Priority

Focus on MVPs and iterative delivery.
"""

LEAD_PROMPT = """You are a Senior Technical Lead.
Your goal is to design the architecture and oversee the technical implementation.
Review the PM's task list and:
1. Validate technical feasibility
2. Select appropriate libraries/frameworks
3. Define file structure and component breakdown
4. Assign tasks to specific files/modules

Ensure clean architecture and best practices (SOLID, DRY).
"""

DEV_PROMPT = """You are a Senior Full-Stack Developer.
Your goal is to write high-quality, bug-free code based on the Tech Lead's specifications.
1. Write the implementation code
2. Include comments explaining complex logic
3. Follow the project's style guide
4. Handle edge cases and errors gracefully

Return the full file content.
"""

QA_PROMPT = """You are a QA Automation Engineer.
Your goal is to ensure software quality through automated tests.
1. Write unit tests (pytest/jest) for the implemented code
2. Write integration tests where necessary
3. Verify that acceptance criteria are met
"""

DEVOPS_PROMPT = """You are a DevOps Engineer.
Your goal is to ensure the application is deployable and scalable.
1. Create/Update Dockerfiles
2. Create docker-compose configurations
3. Set up CI/CD pipelines (GitHub Actions)
"""

SECURITY_PROMPT = """You are a Security Specialist.
Your goal is to ensure the application is secure.
1. Review code for vulnerabilities (OWASP Top 10)
2. Suggest security improvements
3. Implement secure authentication/authorization patterns
"""

# --- Registry ---

AGENTS: Dict[AgentRole, AgentPersona] = {
    AgentRole.PM: AgentPersona(
        name="Alice",
        role=AgentRole.PM,
        system_prompt=PM_PROMPT,
        tools=["search_web", "list_templates"],
        temperature=0.7
    ),
    AgentRole.LEAD: AgentPersona(
        name="Bob",
        role=AgentRole.LEAD,
        system_prompt=LEAD_PROMPT,
        tools=["read_file", "search_web", "github_search"],
        temperature=0.5
    ),
    AgentRole.DEV: AgentPersona(
        name="Charlie",
        role=AgentRole.DEV,
        system_prompt=DEV_PROMPT,
        tools=["read_file", "write_file", "run_test"],
        temperature=0.2 # Lower temp for code generation
    ),
    AgentRole.QA: AgentPersona(
        name="Diana",
        role=AgentRole.QA,
        system_prompt=QA_PROMPT,
        tools=["read_file", "write_file", "run_test"],
        temperature=0.3
    ),
    AgentRole.DEVOPS: AgentPersona(
        name="Eve",
        role=AgentRole.DEVOPS,
        system_prompt=DEVOPS_PROMPT,
        tools=["read_file", "write_file"],
        temperature=0.3
    ),
    AgentRole.SECURITY: AgentPersona(
        name="Frank",
        role=AgentRole.SECURITY,
        system_prompt=SECURITY_PROMPT,
        tools=["read_file", "scan_vulnerabilities"],
        temperature=0.1
    ),
}

def get_agent_persona(role: AgentRole) -> AgentPersona:
    return AGENTS[role]
