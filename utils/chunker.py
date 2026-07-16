from typing import List, Dict

def chunk_text(text: str, chunk_size: int = 3000, overlap: int = 400) -> List[Dict]:
    if not text or not text.strip():
        return []
    overlap = min(overlap, chunk_size // 2)
    step = max(chunk_size - overlap, chunk_size // 2)
    text_length = len(text)

    # Phase 1: range() — mathematisch garantiert endlich
    raw_anchors = list(range(0, text_length, step))

    # Phase 2: Snapping ans naechste Satzende (nur vorwaerts, max 300 Zeichen)
    snapped = []
    for anchor in raw_anchors:
        search_end = min(anchor + 300, text_length)
        p = text.find(". ", anchor, search_end)
        n = text.find("\n",  anchor, search_end)
        candidates = [x for x in [p, n] if x != -1]
        snapped.append(min(candidates) + 1 if candidates else anchor)
    snapped = sorted(set(snapped))

    # Phase 3: Chunks bauen
    total = len(snapped)
    chunks = []
    for i, start in enumerate(snapped):
        content = text[start : min(start + chunk_size, text_length)].strip()
        if not content:
            continue
        if i == 0:               pos = "beginning"
        elif i == total - 1:     pos = "end"
        elif i < total // 3:     pos = "early"
        elif i < 2 * total // 3: pos = "middle"
        else:                    pos = "late"
        chunks.append({
            "id": f"chunk_{len(chunks)+1:03d}",
            "index": len(chunks),
            "text": content,
            "total_chunks": total,
            "position": pos,
            "char_start": start,
            "char_end": min(start + chunk_size, text_length),
            "word_count": len(content.split()),
        })
    for c in chunks:
        c["total_chunks"] = len(chunks)
    return chunks

def get_context_window(chunks: List[Dict], current_index: int, window: int = 1) -> str:
    start = max(0, current_index - window)
    end   = min(len(chunks), current_index + window + 1)
    parts = []
    for i in range(start, end):
        label = ">>> AKTUELLER CHUNK <<<" if i == current_index else f"[Kontext {i+1}]"
        parts.append(f"{label}\n{chunks[i]['text']}")
    return "\n\n---\n\n".join(parts)
