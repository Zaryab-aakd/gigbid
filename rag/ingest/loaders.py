import json
import os
import glob
from typing import List, Dict, Any

class PortfolioIngestion:
    @staticmethod
    def load_all_persona_chunks(persona_id: str = "ai_ml_engineer") -> List[Dict[str, Any]]:
        chunks = []
        base_dir = f"data/personas/{persona_id}"

        # 1. Ingest Case Studies
        case_files = glob.glob(f"{base_dir}/case_studies/*.md")
        for fpath in case_files:
            with open(fpath) as f:
                content = f.read()
            filename = os.path.basename(fpath)
            case_id = filename.replace(".md", "")
            
            # Extract frontmatter if present
            title = case_id
            skills = []
            outcome = "Verified Production Delivery"
            lines = content.split("\n")
            for line in lines:
                if line.startswith("id:"):
                    case_id = line.replace("id:", "").strip()
                elif line.startswith("title:"):
                    title = line.replace("title:", "").strip().strip('"')
                elif line.startswith("skills:"):
                    try:
                        skills = json.loads(line.replace("skills:", "").strip())
                    except Exception:
                        pass
                elif line.startswith("outcome:"):
                    outcome = line.replace("outcome:", "").strip().strip('"')

            chunks.append({
                "chunk_id": f"chunk-case-{case_id}",
                "evidence_id": case_id,
                "persona": persona_id,
                "type": "case_study",
                "title": title,
                "skills": skills,
                "outcome": outcome,
                "text": content,
                "source": f"file://{fpath}"
            })

        # 2. Ingest Past Proposals
        prop_path = f"{base_dir}/past_proposals.json"
        if os.path.exists(prop_path):
            with open(prop_path) as f:
                proposals = json.load(f)
            for p in proposals:
                chunks.append({
                    "chunk_id": f"chunk-{p['proposal_id']}",
                    "evidence_id": p.get("evidence_used", [p["proposal_id"]])[0] if p.get("evidence_used") else p["proposal_id"],
                    "persona": persona_id,
                    "type": "past_proposal",
                    "title": p.get("job_title", "Past Proposal"),
                    "skills": p.get("skills_referenced", []),
                    "outcome": p.get("outcome", "unknown"),
                    "text": p.get("cover_letter", ""),
                    "source": f"past_proposal://{p['proposal_id']}"
                })

        # 3. Ingest CV
        cv_path = f"{base_dir}/cv.md"
        if os.path.exists(cv_path):
            with open(cv_path) as f:
                cv_text = f.read()
            chunks.append({
                "chunk_id": f"chunk-cv-{persona_id}",
                "evidence_id": f"cv-{persona_id}",
                "persona": persona_id,
                "type": "cv",
                "title": f"CV of {persona_id}",
                "skills": [],
                "outcome": "professional_background",
                "text": cv_text,
                "source": f"file://{cv_path}"
            })

        # 4. Ingest Repos README
        repo_path = f"{base_dir}/repos/README.md"
        if os.path.exists(repo_path):
            with open(repo_path) as f:
                repo_text = f.read()
            chunks.append({
                "chunk_id": f"chunk-repo-{persona_id}",
                "evidence_id": f"repo-{persona_id}",
                "persona": persona_id,
                "type": "code_repo",
                "title": "Core Repository Architecture",
                "skills": [],
                "outcome": "production_codebase",
                "text": repo_text,
                "source": f"file://{repo_path}"
            })

        return chunks
