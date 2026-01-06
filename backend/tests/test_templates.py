"""Tests for project templates endpoints."""
import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from app.core.models import ProjectTemplate
from sqlalchemy.orm import Session


def test_create_template(client: TestClient, db_session: Session):
    """Test creating a new template."""
    template_data = {
        "name": "Test Template",
        "version": "1.0.0",
        "description": "Test template",
        "tags": ["test"],
        "config_patch": {
            "team": {"agents_count": 3},
            "quality": {"complexity": "MVP"},
        },
        "is_system": False,
    }

    response = client.post("/api/templates", json=template_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == template_data["name"]
    assert data["version"] == template_data["version"]
    assert "id" in data
    assert "created_at" in data


def test_list_templates(client: TestClient, db_session: Session):
    """Test listing templates."""
    # Create a template
    template = ProjectTemplate(
        id=str(uuid4()),
        name="MVP Test",
        version="1.0.0",
        description="Test",
        tags=["test"],
        config_patch={},
        is_system=True,
    )
    db_session.add(template)
    db_session.commit()

    response = client.get("/api/templates")
    assert response.status_code == 200
    data = response.json()
    assert "templates" in data
    assert "total" in data
    assert data["total"] >= 1


def test_get_template(client: TestClient, db_session: Session):
    """Test getting a specific template."""
    template = ProjectTemplate(
        id=str(uuid4()),
        name="Single Test",
        version="1.0.0",
        description="Test",
        tags=["test"],
        config_patch={},
        is_system=False,
    )
    db_session.add(template)
    db_session.commit()

    response = client.get(f"/api/templates/{template.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == template.id
    assert data["name"] == template.name


def test_get_template_not_found(client: TestClient):
    """Test getting non-existent template."""
    response = client.get(f"/api/templates/nonexistent")
    assert response.status_code == 404
