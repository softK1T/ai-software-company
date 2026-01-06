import logging
import httpx
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class GitHubClient:
    """
    Client for interacting with GitHub API (Apps).
    """
    
    def __init__(self, token: str, repo_owner: str, repo_name: str):
        self.token = token
        self.owner = repo_owner
        self.repo = repo_name
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    async def create_branch(self, branch_name: str, from_sha: str = None) -> Optional[Dict]:
        """Create a new branch from main or specified SHA."""
        if not from_sha:
            # Get main branch SHA
            ref = await self.get_ref("heads/main")
            if not ref:
                logger.error("Could not find main branch")
                return None
            from_sha = ref['object']['sha']

        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/git/refs"
        data = {
            "ref": f"refs/heads/{branch_name}",
            "sha": from_sha
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=self.headers, json=data)
            if resp.status_code == 201:
                logger.info(f"Created branch {branch_name}")
                return resp.json()
            else:
                logger.error(f"Failed to create branch: {resp.text}")
                return None

    async def get_ref(self, ref: str) -> Optional[Dict]:
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/git/refs/{ref}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            if resp.status_code == 200:
                return resp.json()
            return None

    async def create_pr(self, title: str, body: str, head: str, base: str = "main") -> Optional[Dict]:
        """Create a Pull Request."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=self.headers, json=data)
            if resp.status_code == 201:
                logger.info(f"Created PR: {title}")
                return resp.json()
            else:
                logger.error(f"Failed to create PR: {resp.text}")
                return None

    async def commit_files(self, branch: str, message: str, files: Dict[str, str]) -> bool:
        """
        Commit multiple files to a branch.
        Simplified flow: Get SHA -> Create Tree -> Commit -> Update Ref
        Note: For Phase 2 MVP we might use simple single-file updates or use PyGithub if complexity grows.
        """
        # TODO: Implement full git tree workflow for multi-file commits
        # For now, just a placeholder to define interface
        logger.info(f"Committing {len(files)} files to {branch}")
        return True
