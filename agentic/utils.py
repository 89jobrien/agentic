import re
from typing import Iterable

def smart_code_splitter(
    code: str, file_path: str, 
    max_chunk_size: int = 800, 
    overlap: int = 100
) -> Iterable[dict]:
    """
    Splits code into chunks of (up to) max_chunk_size, using function/class/section boundaries if possible.
    Includes context overlap for caller/callee context. Yields dicts with file_path and chunk.
    """
    # Attempt to split on function/class definitions (works for Python)
    section_points = [m.start() for m in re.finditer(r"^(\s*)(def|class)\s", code, re.MULTILINE)]
    section_points.append(len(code))

    chunks = []
    for i in range(len(section_points)-1):
        chunk = code[section_points[i]:section_points[i+1]]
        # Skip empty or ultra-short pieces
        if chunk.strip():
            chunks.append(chunk)
    
    # If not enough sections found (not a code file), fallback to line splitting
    if len(chunks) <= 1:
        lines = code.splitlines()
        # Text splitter with overlap by lines
        for i in range(0, len(lines), max_chunk_size - overlap):
            piece = "\n".join(lines[i:i+max_chunk_size])
            yield {"file_path": file_path, "chunk": piece}
        return

    # Now break large sections if needed, and apply overlap ("sliding window")
    buffer = []
    buf_len = 0
    i = 0
    while i < len(chunks):
        chunk = chunks[i]
        chunk_len = len(chunk)
        if buf_len + chunk_len <= max_chunk_size or not buffer:
            buffer.append(chunk)
            buf_len += chunk_len
            i += 1
        else:
            merged = "".join(buffer)
            yield {"file_path": file_path, "chunk": merged}
            # slide window back by overlap
            merged_lines = merged.splitlines()
            buffer = ["\n".join(merged_lines[-overlap:])]
            buf_len = len(buffer[0])
    # Yield any remaining buffer
    if buffer:
        merged = "".join(buffer)
        yield {"file_path": file_path, "chunk": merged}

def chunk_code(code: str, file_path: str) -> Iterable[dict]:
    """
    Convenience function to call advanced splitter.
    """
    return smart_code_splitter(code, file_path)