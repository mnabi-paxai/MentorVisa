# services/policy_loader.py
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Tuple
import re
import json

# Chunking defaults
MAX_LEN = 800
OVERLAP = 300

def _parse_front_matter(text: str) -> Tuple[Dict, str]:
    """
    Parse simple front matter delimited by:
    ---
    key: value
    ...
    ---
    Returns (meta_dict, body_without_front_matter)
    """
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    raw, body = m.group(1), m.group(2)
    meta: Dict = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        # crude parser for lists/bools/numbers/strings
        if v.lower() in {"true", "false"}:
            meta[k] = v.lower() == "true"
        elif re.fullmatch(r"-?\d+(\.\d+)?", v):
            meta[k] = float(v) if "." in v else int(v)
        elif v.startswith("[") and v.endswith("]"):
            try:
                meta[k] = json.loads(v.replace("'", '"'))
            except Exception:
                meta[k] = v
        else:
            meta[k] = v.strip('"').strip("'")
    return meta, body

def _split_by_size(text: str, max_len: int = MAX_LEN, overlap: int = OVERLAP) -> List[str]:
    """Greedy splitter with overlap; normalizes whitespace."""
    text = " ".join(text.split())
    if not text:
        return []
    if len(text) <= max_len:
        return [text]
    chunks, i = [], 0
    while i < len(text):
        j = min(i + max_len, len(text))
        chunks.append(text[i:j])
        i = max(j - overlap, 0)
        if i >= len(text):
            break
    return [c.strip() for c in chunks if c.strip()]

def _chunk_markdown(body: str, base_meta: Dict, source_name: str) -> List[Dict]:
    """Chunk by H2 sections and paragraphs, attach meta to each chunk."""
    chunks: List[Dict] = []
    section = "Intro"
    buf: List[str] = []

    def flush():
        if not buf:
            return
        paragraph = " ".join(buf).strip()
        for piece in _split_by_size(paragraph):
            chunks.append({
                "text": piece,
                "source": source_name,
                "source_title": base_meta.get("title", source_name),
                "section": section,
                "is_catalog": bool(base_meta.get("is_catalog", False)) or ("catalog" in base_meta.get("title", "").lower()),
                "weight": float(base_meta.get("retrieval_weight", 1.0)),
            })
        buf.clear()

    for line in body.splitlines():
        if line.startswith("# "):   # ignore H1 titles
            continue
        if line.startswith("## "):
            flush()
            section = line[3:].strip()
            continue
        if not line.strip():
            flush()
        else:
            buf.append(line.strip())
    flush()
    return chunks

def load_policy_dir(path: str = "./data/policies") -> List[Dict]:
    """
    Load all .md files in a directory, parse front matter, chunk content,
    and return a list of chunk dicts.
    """
    root = Path(path)
    files = sorted(root.glob("*.md"))
    chunks: List[Dict] = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        meta, body = _parse_front_matter(text)
        # If it looks like a catalog but no weight given, give it a mild penalty by default
        if ("catalog" in meta.get("title", "").lower()) and ("retrieval_weight" not in meta):
            meta["retrieval_weight"] = 0.6
        chunks.extend(_chunk_markdown(body, meta, f.stem))
    return chunks
