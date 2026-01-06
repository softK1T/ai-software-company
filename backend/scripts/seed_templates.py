"""Populate database with default project templates."""
from uuid import uuid4
from app.core.database import get_db_context
from app.core.models import ProjectTemplate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TEMPLATES = [
    {
        "name": "MVP Fast",
        "version": "1.0.0",
        "description": "Quick prototype with minimal team. Perfect for POCs and MVPs.",
        "tags": ["quick", "prototype", "minimal"],
        "is_system": True,
        "config_patch": {
            "team": {
                "agents_count": 3,
                "roles_enabled": {"pm": 1, "dev": 1, "qa": 0},
                "max_parallel_tasks": 5,
            },
            "planning": {
                "target_tasks": 20,
                "max_task_depth": 2,
                "decomposition_style": "feature-first",
            },
            "process": {
                "review_iterations": 1,
                "require_pr_for_tasks": True,
                "merge_policy": "lead_approve_and_green_tests",
                "comment_policy": "minimal",
            },
            "quality": {
                "complexity": "MVP",
                "min_test_coverage": 0.50,
                "require_docs": False,
                "require_ci": False,
                "require_docker": True,
                "require_k8s": False,
                "security": {
                    "enable_sast": True,
                    "enable_dast": False,
                    "enable_dependency_scan": False,
                    "enable_secret_scan": False,
                    "enable_docker_scan": False,
                    "security_gate_policy": "inform",
                },
            },
            "models": {
                "model_by_role": {
                    "pm": "gpt-4o-mini",
                    "dev_lead": "gpt-4o-mini",
                    "dev": "gpt-4o-mini",
                    "qa": "gpt-4o-mini",
                    "docs": "gpt-4o-mini",
                    "devops": "gpt-4o-mini",
                    "security": "gpt-4o-mini",
                },
                "escalation_rules": {},
                "fallback_model": "gpt-4o-mini",
            },
            "github": {
                "use_github_app": True,
                "branch_naming_pattern": "feature/{task_id}-{slug}",
            },
            "budget": {
                "max_usd": 1.0,
                "max_total_tokens": 50000,
                "on_exceed": "stop",
            },
        },
    },
    {
        "name": "Startup Team",
        "version": "1.0.0",
        "description": "Balanced team with quality checks. Great for startup environments.",
        "tags": ["balanced", "startup", "quality"],
        "is_system": True,
        "config_patch": {
            "team": {
                "agents_count": 6,
                "roles_enabled": {"pm": 1, "dev_lead": 1, "dev": 2, "qa": 1, "docs": 1},
                "max_parallel_tasks": 8,
            },
            "planning": {
                "target_tasks": 40,
                "max_task_depth": 3,
                "decomposition_style": "feature-first",
            },
            "process": {
                "review_iterations": 3,
                "require_pr_for_tasks": True,
                "merge_policy": "lead_approve_and_green_tests",
                "comment_policy": "standard",
            },
            "quality": {
                "complexity": "STANDARD",
                "min_test_coverage": 0.70,
                "require_docs": True,
                "require_ci": True,
                "require_docker": True,
                "require_k8s": False,
                "security": {
                    "enable_sast": True,
                    "enable_dast": False,
                    "enable_dependency_scan": True,
                    "enable_secret_scan": True,
                    "enable_docker_scan": False,
                    "security_gate_policy": "block_critical",
                },
            },
            "models": {
                "model_by_role": {
                    "pm": "gpt-4o",
                    "dev_lead": "gpt-4o",
                    "dev": "gpt-4o-mini",
                    "qa": "gpt-4o-mini",
                    "docs": "gpt-4o-mini",
                    "devops": "gpt-4o-mini",
                    "security": "gpt-4o",
                },
                "escalation_rules": {},
                "fallback_model": "gpt-4o-mini",
            },
            "github": {
                "use_github_app": True,
                "branch_naming_pattern": "feature/{task_id}-{slug}",
            },
            "budget": {
                "max_usd": 3.0,
                "max_total_tokens": 150000,
                "on_exceed": "degrade_models",
            },
        },
    },
    {
        "name": "API Quality-First",
        "version": "1.0.0",
        "description": "Quality and testing focused. Best for APIs and critical services.",
        "tags": ["quality", "api", "testing"],
        "is_system": True,
        "config_patch": {
            "team": {
                "agents_count": 7,
                "roles_enabled": {"pm": 1, "dev_lead": 1, "dev": 2, "qa": 2, "docs": 1},
                "max_parallel_tasks": 6,
            },
            "planning": {
                "target_tasks": 50,
                "max_task_depth": 3,
                "decomposition_style": "component-first",
            },
            "process": {
                "review_iterations": 4,
                "require_pr_for_tasks": True,
                "merge_policy": "lead_approve_and_green_tests",
                "comment_policy": "strict",
            },
            "quality": {
                "complexity": "STANDARD",
                "min_test_coverage": 0.80,
                "require_docs": True,
                "require_ci": True,
                "require_docker": True,
                "require_k8s": False,
                "security": {
                    "enable_sast": True,
                    "enable_dast": True,
                    "enable_dependency_scan": True,
                    "enable_secret_scan": True,
                    "enable_docker_scan": False,
                    "security_gate_policy": "block_critical",
                },
            },
            "models": {
                "model_by_role": {
                    "pm": "gpt-4o",
                    "dev_lead": "gpt-4o",
                    "dev": "gpt-4o",
                    "qa": "gpt-4o",
                    "docs": "gpt-4o-mini",
                    "devops": "gpt-4o-mini",
                    "security": "gpt-4o",
                },
                "escalation_rules": {},
                "fallback_model": "gpt-4o-mini",
            },
            "github": {
                "use_github_app": True,
                "branch_naming_pattern": "feature/{task_id}-{slug}",
            },
            "budget": {
                "max_usd": 5.0,
                "max_total_tokens": 250000,
                "on_exceed": "degrade_models",
            },
        },
    },
    {
        "name": "Full-Stack App",
        "version": "1.0.0",
        "description": "Complete full-stack development with UI, API, and infrastructure.",
        "tags": ["fullstack", "ui", "api"],
        "is_system": True,
        "config_patch": {
            "team": {
                "agents_count": 8,
                "roles_enabled": {"pm": 1, "dev_lead": 1, "dev": 3, "qa": 2, "docs": 1, "devops": 1},
                "max_parallel_tasks": 8,
            },
            "planning": {
                "target_tasks": 70,
                "max_task_depth": 3,
                "decomposition_style": "component-first",
            },
            "process": {
                "review_iterations": 3,
                "require_pr_for_tasks": True,
                "merge_policy": "lead_approve_and_green_tests",
                "comment_policy": "standard",
            },
            "quality": {
                "complexity": "STANDARD",
                "min_test_coverage": 0.75,
                "require_docs": True,
                "require_ci": True,
                "require_docker": True,
                "require_k8s": False,
                "security": {
                    "enable_sast": True,
                    "enable_dast": False,
                    "enable_dependency_scan": True,
                    "enable_secret_scan": True,
                    "enable_docker_scan": True,
                    "security_gate_policy": "block_critical",
                },
            },
            "models": {
                "model_by_role": {
                    "pm": "gpt-4o",
                    "dev_lead": "gpt-4o",
                    "dev": "gpt-4o-mini",
                    "qa": "gpt-4o-mini",
                    "docs": "gpt-4o-mini",
                    "devops": "gpt-4o",
                    "security": "gpt-4o",
                },
                "escalation_rules": {},
                "fallback_model": "gpt-4o-mini",
            },
            "github": {
                "use_github_app": True,
                "branch_naming_pattern": "feature/{task_id}-{slug}",
            },
            "budget": {
                "max_usd": 8.0,
                "max_total_tokens": 400000,
                "on_exceed": "degrade_models",
            },
        },
    },
    {
        "name": "Enterprise Strict",
        "version": "1.0.0",
        "description": "Enterprise-grade with all security and compliance gates. Production-ready.",
        "tags": ["enterprise", "compliance", "security"],
        "is_system": True,
        "config_patch": {
            "team": {
                "agents_count": 9,
                "roles_enabled": {"pm": 1, "dev_lead": 1, "dev": 2, "qa": 2, "docs": 1, "devops": 1, "security": 1},
                "max_parallel_tasks": 4,
            },
            "planning": {
                "target_tasks": 100,
                "max_task_depth": 4,
                "decomposition_style": "component-first",
            },
            "process": {
                "review_iterations": 5,
                "require_pr_for_tasks": True,
                "merge_policy": "lead_approve_and_green_tests",
                "comment_policy": "strict",
            },
            "quality": {
                "complexity": "ENTERPRISE",
                "min_test_coverage": 0.85,
                "require_docs": True,
                "require_ci": True,
                "require_docker": True,
                "require_k8s": True,
                "security": {
                    "enable_sast": True,
                    "enable_dast": True,
                    "enable_dependency_scan": True,
                    "enable_secret_scan": True,
                    "enable_docker_scan": True,
                    "security_gate_policy": "block_all",
                },
            },
            "models": {
                "model_by_role": {
                    "pm": "gpt-4o",
                    "dev_lead": "gpt-4o",
                    "dev": "gpt-4o",
                    "qa": "gpt-4o",
                    "docs": "gpt-4o",
                    "devops": "gpt-4o",
                    "security": "gpt-4o",
                },
                "escalation_rules": {},
                "fallback_model": "gpt-4o",
            },
            "github": {
                "use_github_app": True,
                "branch_naming_pattern": "feature/{task_id}-{slug}",
            },
            "budget": {
                "max_usd": 15.0,
                "max_total_tokens": 600000,
                "on_exceed": "stop",
            },
        },
    },
]


def seed_templates():
    """Seed default templates into database."""
    with get_db_context() as db:
        for template_data in TEMPLATES:
            # Check if template already exists
            existing = db.query(ProjectTemplate).filter(
                ProjectTemplate.name == template_data["name"],
                ProjectTemplate.version == template_data["version"],
            ).first()

            if existing:
                logger.info(f"✓ Template already exists: {template_data['name']} v{template_data['version']}")
                continue

            template = ProjectTemplate(
                id=str(uuid4()),
                name=template_data["name"],
                version=template_data["version"],
                description=template_data["description"],
                tags=template_data["tags"],
                config_patch=template_data["config_patch"],
                is_system=template_data["is_system"],
            )
            db.add(template)
            logger.info(f"✅ Created template: {template_data['name']} v{template_data['version']}")

        db.commit()
        logger.info("✓ All templates seeded successfully")


if __name__ == "__main__":
    seed_templates()
