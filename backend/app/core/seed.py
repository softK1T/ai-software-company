import asyncio
import logging
from uuid import uuid4
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.models import ProjectTemplate, ProjectStatus
from app.core.schemas import ProjectTemplateCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INITIAL_TEMPLATES = [
    {
        "name": "MVP Fast Track",
        "version": "1.0.0",
        "description": "Rapid prototyping template for validting ideas quickly. Minimal process overhead.",
        "tags": ["mvp", "prototype", "fast"],
        "is_system": True,
        "config_patch": {
            "team": {
                "agents_count": 2, 
                "roles_enabled": {"pm": 1, "dev": 1}
            },
            "process": {
                "review_iterations": 1,
                "require_pr_for_tasks": False,
                "comment_policy": "minimal"
            },
            "quality": {
                "complexity": "MVP",
                "min_test_coverage": 0.3,
                "require_docs": False,
                "require_k8s": False
            },
            "budget": {
                "max_usd": 5.0,
                "on_exceed": "stop"
            }
        }
    },
    {
        "name": "Standard Web App",
        "version": "1.0.0",
        "description": "Standard setup for production-grade web applications with CI/CD and tests.",
        "tags": ["web", "production", "standard"],
        "is_system": True,
        "config_patch": {
            "team": {
                "agents_count": 3,
                "roles_enabled": {"pm": 1, "lead": 1, "dev": 1}
            },
            "process": {
                "review_iterations": 2,
                "require_pr_for_tasks": True,
                "merge_policy": "lead_approve_and_green_tests"
            },
            "quality": {
                "complexity": "STANDARD",
                "min_test_coverage": 0.8,
                "require_docker": True
            }
        }
    },
    {
        "name": "Data Pipeline",
        "version": "1.0.0",
        "description": "Template for ETL/ELT pipelines with robust logging and validation.",
        "tags": ["data", "etl", "pipeline"],
        "is_system": True,
        "config_patch": {
            "team": {
                "agents_count": 2,
                "roles_enabled": {"data_eng": 1, "qa": 1}
            },
            "quality": {
                "complexity": "STANDARD",
                "min_test_coverage": 0.7,
                "require_docs": True
            }
        }
    }
]

def seed_templates(db: Session):
    logger.info("Checking for existing templates...")
    count = 0
    for t_data in INITIAL_TEMPLATES:
        existing = db.query(ProjectTemplate).filter(
            ProjectTemplate.name == t_data["name"],
            ProjectTemplate.version == t_data["version"]
        ).first()
        
        if not existing:
            logger.info(f"Creating template: {t_data['name']}")
            template = ProjectTemplate(
                id=uuid4(),
                name=t_data["name"],
                version=t_data["version"],
                description=t_data["description"],
                tags=t_data["tags"],
                config_patch=t_data["config_patch"],
                is_system=t_data["is_system"]
            )
            db.add(template)
            count += 1
        else:
            logger.info(f"Skipping existing: {t_data['name']}")
    
    db.commit()
    logger.info(f"Seeding complete. Added {count} templates.")

if __name__ == "__main__":
    logger.info("Initializing database session...")
    db = SessionLocal()
    try:
        seed_templates(db)
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()
