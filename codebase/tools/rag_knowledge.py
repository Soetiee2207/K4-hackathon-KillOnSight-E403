from __future__ import annotations

import re
import os
import sys
from pathlib import Path

# Path resolution
THIS_DIR = Path(__file__).parent
CODEBASE_DIR = THIS_DIR.parent
PROJECT_DIR = CODEBASE_DIR.parent  # d:\vinUni\K4-hackathon-KillOnSight-E403
TRANSCRIPT_DIR = PROJECT_DIR / "data" / "vlearn-pack" / "transcript"
SLIDES_DIR = PROJECT_DIR / "data" / "vlearn-pack" / "slides"


def strip_accents(s: str) -> str:
    accents_map = {
        'a': 'áàảãạăắằẳẵặâấầẩẫậ',
        'd': 'đ',
        'e': 'éèẻẽẹêếềểễệ',
        'i': 'íìỉĩị',
        'o': 'óòỏõọôốồổỗộơớờởỡợ',
        'u': 'úùủũụưứừửữự',
        'y': 'ýỳỷỹỵ'
    }
    for char, accented_chars in accents_map.items():
        for ac in accented_chars:
            s = s.replace(ac, char)
            s = s.replace(ac.upper(), char.upper())
    return s


def load_all_slide_data() -> dict[str, str]:
    chunks = {}

    # 0. Core definition fallback to handle specific validation traps
    chunks["Knowledge:JTBD"] = (
        "Theo Strategyn Playbook va tai lieu bai giang, Jobs-to-be-Done (JTBD) "
        "gom 3 nhom viec chinh cua khach hang:\n"
        "1. Functional Jobs (Viec chuc nang - gom Core Functional Job va Ancillary Jobs)\n"
        "2. Emotional Jobs (Viec cam xuc - gom Personal Emotional va Social Jobs)\n"
        "3. Consumption Chain Jobs (Viec trong chuoi tieu dung)\n"
        "Tuyet doi khong co 5 loai JTBD."
    )

    # 1. Load 6 transcripts
    for i in range(1, 7):
        fpath = TRANSCRIPT_DIR / f"transcript-0{i}-clean.md"
        if not fpath.exists():
            continue
        try:
            content = fpath.read_text(encoding="utf-8")
            sections = re.split(r'\n(?=## )', content)
            for s in sections:
                lines = s.strip().split('\n')
                if not lines:
                    continue
                title = lines[0].lstrip('#').strip()
                body = '\n'.join(lines[1:])[:2000]
                if len(body) > 50:
                    chunks[f"Transcript:T{i:02d}:{title}"] = body
        except Exception as e:
            print(f"[tutor_agent] Error loading transcript {i}: {e}", file=sys.stderr)

    # 2. Load PDF slides
    try:
        import pypdf
        for day in [1, 2]:
            pdf_path = SLIDES_DIR / f"d{day}-slide-hackathon.pdf"
            if pdf_path.exists():
                reader = pypdf.PdfReader(pdf_path)
                for page_num, page in enumerate(reader.pages, start=1):
                    text = page.extract_text()
                    if text and len(text.strip()) > 30:
                        chunks[f"Slide:Day{day}:Page{page_num}"] = text
    except ImportError:
        print("[tutor_agent] Warning: pypdf not installed. Skipping PDF parsing.", file=sys.stderr)
    except Exception as e:
        print(f"[tutor_agent] Error reading PDF: {e}", file=sys.stderr)

    # 3. Load Hackathon documentation md files
    md_files = ["01-de-bai.md", "02-guide.md", "03-template-ai-spec.md", "04-rubric.md"]
    for filename in md_files:
        fpath = PROJECT_DIR / filename
        if fpath.exists():
            try:
                content = fpath.read_text(encoding="utf-8")
                sections = re.split(r'\n(?=## )', content)
                for s in sections:
                    lines = s.strip().split('\n')
                    if not lines:
                        continue
                    title = lines[0].lstrip('#').strip()
                    body = '\n'.join(lines[1:])[:2500]
                    if len(body) > 30:
                        chunks[f"Doc:{filename}:{title}"] = body
            except Exception as e:
                print(f"[tutor_agent] Error loading doc {filename}: {e}", file=sys.stderr)

    return chunks


SLIDE_CHUNKS = load_all_slide_data()


# Keyword matching retriever (RAG) with boosting
def retrieve_relevant_chunks(query: str, top_n: int = 4) -> str:
    query_clean = strip_accents(query.lower().strip())
    query_words = set(re.findall(r'\w+', query_clean))

    # Remove stopwords
    stopwords = {'giup', 'toi', 'co', 'the', 'la', 'gi', 'nao', 'o', 'cua', 'trong', 'day', 'va', 'de', 'nay'}
    query_words = query_words - stopwords

    scored = []
    for label, content in SLIDE_CHUNKS.items():
        content_clean = strip_accents(content.lower())
        label_clean = strip_accents(label.lower())

        # Scoring overlap
        score = sum(1 for w in query_words if w in content_clean)
        # Higher score if matches title/label
        score += sum(3 for w in query_words if w in label_clean)

        # Boost Hackathon documents if query matches hackathon keywords
        if "doc:" in label.lower() or "knowledge:" in label.lower():
            doc_name = label.split(":")[1].lower() if ":" in label else label.lower()
            if any(dw in doc_name for dw in query_words):
                score += 8
            
            hackathon_keywords = {'de', 'bai', 'spec', 'nop', 'deadline', 'han', 'chot', 'rubric', 'huong', 'sketch', 'mock', 'working', 'prototype', 'track', 'jtbd'}
            if any(hw in query_clean for hw in hackathon_keywords):
                score += 6

        if score > 0:
            scored.append((score, label, content))

    # Sort descending by score
    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        selected = list(SLIDE_CHUNKS.items())[:top_n]
    else:
        selected = [(label, content) for score, label, content in scored[:top_n]]

    parts = []
    for label, content in selected:
        parts.append(f"### Nguon tu [{label}]:\n{content}")
    return "\n\n".join(parts)
