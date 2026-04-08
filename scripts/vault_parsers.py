"""
vault_parsers.py — Universal file parser framework for The Vault.

Converts any file type into PreDocument objects for vault_api.ingest().
Each parser handles a specific format; ParserRouter dispatches to the right one.

Usage:
    # As library
    from vault_parsers import ParserRouter, PreDocument
    router = ParserRouter()
    docs = router.route("path/to/file.pdf")
    docs = router.route_directory("~/Desktop/important_docs/")

    # As CLI
    python vault_parsers.py absorb ~/Desktop/important_docs/
    python vault_parsers.py absorb ~/research/paper.pdf --dry-run
    python vault_parsers.py parsers   # list available parsers

Requires: oracledb (for vault integration), fitz/PyMuPDF (for PDF), Pillow (for images)
"""
from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", ".tox",
    ".mypy_cache", ".pytest_cache", ".next", "dist", "build",
    ".idea", ".vscode", ".vs", "bin", "obj",
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB — skip files larger than this
CHUNK_SIZE = 4000  # characters per chunk for large files

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".c", ".cpp",
    ".h", ".hpp", ".cs", ".rb", ".php", ".swift", ".kt", ".scala", ".r",
    ".sql", ".sh", ".bash", ".zsh", ".bat", ".ps1", ".psm1",
}

CONFIG_EXTENSIONS = {
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".env", ".properties", ".xml",
}

TEXT_EXTENSIONS = {
    ".txt", ".md", ".rst", ".csv", ".tsv", ".log", ".readme",
}


# ---------------------------------------------------------------------------
# PreDocument — universal intermediate format
# ---------------------------------------------------------------------------

@dataclass
class PreDocument:
    """Standard output from any parser. Input to vault_api.ingest()."""
    title: str
    content: str
    doc_type: str
    occurred_at: datetime | None = None
    ownership: str = "self"
    privacy_level: str = "internal"
    fidelity: str = "high"
    language: str = "en"
    original_path: str | None = None
    source_info: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    chunks: list[str] | None = None
    # Email promoted fields
    email_from: str | None = None
    email_importance: str | None = None
    email_direction: str | None = None
    # Versioning
    parent_doc_id: int | None = None
    version: int = 1

    def to_ingest_kwargs(self) -> dict[str, Any]:
        """Convert to kwargs for vault_api.Vault.ingest()."""
        meta = dict(self.metadata or {})
        return {
            "content": self.content,
            "doc_type": self.doc_type,
            "meta": meta,
            "source_info": self.source_info,
            "title": self.title,
            "occurred_at": self.occurred_at,
            "privacy_level": self.privacy_level,
            "language": self.language,
            # v11 promoted columns — passed directly, not via meta
            "ownership": self.ownership,
            "email_from": self.email_from,
            "email_importance": self.email_importance,
            "email_direction": self.email_direction,
            "fidelity": self.fidelity,
            "original_path": self.original_path,
            "parent_doc_id": self.parent_doc_id,
            "version": self.version,
        }


# ---------------------------------------------------------------------------
# BaseParser
# ---------------------------------------------------------------------------

class BaseParser:
    """All parsers inherit from this."""
    name: str = "base"
    supported_extensions: list[str] = []
    supported_mime_types: list[str] = []
    priority: int = 100  # lower = matched first

    def can_handle(self, source: str, **kwargs) -> bool:
        """Return True if this parser can process the given source."""
        ext = Path(source).suffix.lower()
        return ext in self.supported_extensions

    def parse(self, source: str, **kwargs) -> list[PreDocument]:
        """Parse source into PreDocuments."""
        raise NotImplementedError(f"{self.name} parser has no parse() implementation")

    def _file_meta(self, path: str) -> dict[str, Any]:
        """Common file metadata."""
        p = Path(path)
        stat = p.stat()
        return {
            "filename": p.name,
            "extension": p.suffix.lower(),
            "size_bytes": stat.st_size,
            "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "created_at": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# Parser Implementations
# ---------------------------------------------------------------------------

class TextFileParser(BaseParser):
    """Parse plain text, markdown, code, config, and log files."""
    name = "text"
    supported_extensions = sorted(TEXT_EXTENSIONS | CODE_EXTENSIONS | CONFIG_EXTENSIONS)
    priority = 50

    def parse(self, source: str, **kwargs) -> list[PreDocument]:
        p = Path(source)
        ext = p.suffix.lower()
        if p.stat().st_size > MAX_FILE_SIZE:
            return [PreDocument(
                title=f"[SKIPPED] {p.name} ({p.stat().st_size / 1024 / 1024:.1f}MB)",
                content=f"File too large to ingest: {p.stat().st_size} bytes",
                doc_type="file", fidelity="metadata_only",
                original_path=str(p), metadata=self._file_meta(source),
            )]

        # Read with encoding fallback
        content = self._read_text(source)
        if content is None:
            return [PreDocument(
                title=f"[ENCODING ERROR] {p.name}",
                content=f"Could not decode file: {source}",
                doc_type="file", fidelity="metadata_only",
                original_path=str(p), metadata=self._file_meta(source),
            )]

        # Determine doc_type
        if ext in CODE_EXTENSIONS:
            doc_type = "code_artifact"
        elif ext in CONFIG_EXTENSIONS:
            doc_type = "file"
        elif ext == ".md" or ext == ".rst":
            doc_type = "note"
        elif ext == ".log":
            doc_type = "file"
        elif ext == ".csv" or ext == ".tsv":
            doc_type = "spreadsheet"
        else:
            doc_type = "note"

        meta = self._file_meta(source)
        if ext in CODE_EXTENSIONS:
            meta["language"] = ext.lstrip(".")

        # Chunk large files
        chunks = None
        if len(content) > CHUNK_SIZE * 2:
            chunks = [content[i:i + CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]

        mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)

        return [PreDocument(
            title=p.name,
            content=content,
            doc_type=doc_type,
            occurred_at=mtime,
            original_path=str(p),
            source_info={"type": "file_system", "uri": f"file://{p.as_posix()}"},
            metadata=meta,
            chunks=chunks,
            fidelity="full",
        )]

    @staticmethod
    def _read_text(path: str) -> str | None:
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                return Path(path).read_text(encoding=enc)
            except (UnicodeDecodeError, ValueError):
                continue
        return None


class PdfParser(BaseParser):
    """Parse PDF files using PyMuPDF (fitz)."""
    name = "pdf"
    supported_extensions = [".pdf"]
    priority = 40

    def can_handle(self, source: str, **kwargs) -> bool:
        return Path(source).suffix.lower() == ".pdf"

    def parse(self, source: str, **kwargs) -> list[PreDocument]:
        p = Path(source)
        if p.stat().st_size > MAX_FILE_SIZE:
            return [PreDocument(
                title=f"[SKIPPED] {p.name}", content=f"PDF too large: {p.stat().st_size} bytes",
                doc_type="pdf", fidelity="metadata_only",
                original_path=str(p), metadata=self._file_meta(source),
            )]

        try:
            import fitz  # PyMuPDF
        except ImportError:
            return [PreDocument(
                title=p.name, content=f"[PDF not parsed — PyMuPDF not installed] {p.name}",
                doc_type="pdf", fidelity="metadata_only",
                original_path=str(p),
                metadata={**self._file_meta(source), "error": "PyMuPDF (fitz) not installed"},
            )]

        # H4 audit fix: use context manager to prevent file handle leak on exception
        with fitz.open(str(p)) as doc:
            pages_text = []
            for page in doc:
                text = page.get_text()
                if text.strip():
                    pages_text.append(text)

            full_text = "\n\n".join(pages_text)
            meta = {
                **self._file_meta(source),
                "pages": doc.page_count,
                "author": doc.metadata.get("author", ""),
                "creator": doc.metadata.get("creator", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
            }

        if not full_text.strip():
            return [PreDocument(
                title=p.name, content=f"[Scanned PDF — no extractable text] {p.name}",
                doc_type="pdf", fidelity="metadata_only",
                original_path=str(p), metadata=meta,
            )]

        # Detect if it's a research paper (has "Abstract" section)
        doc_type = "research_paper" if re.search(r"\babstract\b", full_text[:3000], re.I) else "pdf"

        # Chunks = one per page
        chunks = pages_text if len(pages_text) > 1 else None

        mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)

        return [PreDocument(
            title=p.stem,
            content=full_text,
            doc_type=doc_type,
            occurred_at=mtime,
            original_path=str(p),
            source_info={"type": "file_system", "uri": f"file://{p.as_posix()}"},
            metadata=meta,
            chunks=chunks,
            fidelity="full",
        )]


class EmailParser(BaseParser):
    """Parse .eml and .mbox email files."""
    name = "email"
    supported_extensions = [".eml", ".mbox"]
    priority = 30

    def parse(self, source: str, **kwargs) -> list[PreDocument]:
        p = Path(source)
        ext = p.suffix.lower()

        if ext == ".mbox":
            return self._parse_mbox(source, **kwargs)
        else:
            return self._parse_eml(source, **kwargs)

    def _parse_eml(self, source: str, **kwargs) -> list[PreDocument]:
        import email
        from email import policy

        p = Path(source)
        raw = p.read_bytes()
        msg = email.message_from_bytes(raw, policy=policy.default)
        return [self._msg_to_predoc(msg, source)]

    def _parse_mbox(self, source: str, **kwargs) -> list[PreDocument]:
        import mailbox
        results = []
        mbox = mailbox.mbox(source)
        for i, msg in enumerate(mbox):
            try:
                results.append(self._msg_to_predoc(msg, source, index=i))
            except Exception as e:
                results.append(PreDocument(
                    title=f"[PARSE ERROR] mbox message #{i}",
                    content=f"Failed to parse message: {e}",
                    doc_type="email", fidelity="metadata_only",
                    original_path=source,
                ))
        mbox.close()
        return results

    def _msg_to_predoc(self, msg, source: str, index: int = 0) -> PreDocument:
        subject = str(msg.get("Subject", "No Subject"))
        sender = str(msg.get("From", ""))
        to = str(msg.get("To", ""))
        cc = str(msg.get("Cc", ""))
        date_str = str(msg.get("Date", ""))
        message_id = str(msg.get("Message-ID", ""))
        in_reply_to = str(msg.get("In-Reply-To", ""))

        # Extract body
        body = ""
        if hasattr(msg, "get_body"):
            text_part = msg.get_body(preferencelist=("plain", "html"))
            if text_part:
                body = text_part.get_content()
                if text_part.get_content_type() == "text/html":
                    body = self._strip_html(body)
        else:
            # Fallback for mailbox messages
            if msg.is_multipart():
                for part in msg.walk():
                    ct = part.get_content_type()
                    if ct == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode("utf-8", errors="replace")
                            break
                    elif ct == "text/html" and not body:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = self._strip_html(payload.decode("utf-8", errors="replace"))
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode("utf-8", errors="replace")

        # Parse date
        occurred_at = None
        if date_str:
            try:
                from email.utils import parsedate_to_datetime
                occurred_at = parsedate_to_datetime(date_str)
            except Exception:
                pass

        # Detect direction
        user_email = kwargs.get("user_email", "")
        if user_email and user_email.lower() in sender.lower():
            direction = "outbound"
        else:
            direction = "inbound"

        # Detect importance
        priority_header = str(msg.get("X-Priority", "3"))
        if "1" in priority_header or "2" in priority_header:
            importance = "high"
        elif "4" in priority_header or "5" in priority_header:
            importance = "low"
        else:
            importance = "normal"

        # Count attachments
        attachment_count = 0
        if hasattr(msg, "iter_attachments"):
            try:
                attachment_count = len(list(msg.iter_attachments()))
            except Exception:
                pass

        return PreDocument(
            title=subject,
            content=body,
            doc_type="email",
            occurred_at=occurred_at,
            original_path=f"{source}#{index}" if index else source,
            source_info={"type": "email_file", "uri": f"file://{Path(source).as_posix()}"},
            metadata={
                "to": to, "cc": cc,
                "message_id": message_id,
                "in_reply_to": in_reply_to,
                "has_attachments": attachment_count > 0,
                "attachment_count": attachment_count,
            },
            email_from=sender,
            email_direction=direction,
            email_importance=importance,
            ownership="work",
            fidelity="full" if body.strip() else "metadata_only",
        )

    @staticmethod
    def _strip_html(html: str) -> str:
        """Crude HTML tag stripper."""
        text = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.S)
        text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()


class LineParser(BaseParser):
    """Parse LINE chat export text files."""
    name = "line"
    supported_extensions = [".txt"]
    priority = 20  # higher priority than TextFileParser for .txt with LINE format

    # LINE export format: date lines like "2024/01/15 Monday" or "2024/01/15(Mon)"
    _DATE_PATTERN = re.compile(r"^(\d{4}/\d{2}/\d{2})")
    _MSG_PATTERN = re.compile(r"^(\d{1,2}:\d{2})\t(.+?)\t(.+)$")

    def can_handle(self, source: str, **kwargs) -> bool:
        if Path(source).suffix.lower() != ".txt":
            return False
        if kwargs.get("parser") == "line":
            return True
        # Auto-detect LINE format by reading first 20 lines
        try:
            with open(source, encoding="utf-8") as f:
                head = "".join(f.readline() for _ in range(20))
            return bool(self._DATE_PATTERN.search(head) and self._MSG_PATTERN.search(head))
        except Exception:
            return False

    def parse(self, source: str, **kwargs) -> list[PreDocument]:
        p = Path(source)
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()

        # Extract chat name from first line (usually "[LINE] Chat with XXX")
        chat_name = lines[0].strip() if lines else p.stem
        if chat_name.startswith("[LINE]"):
            chat_name = chat_name[6:].strip()

        # Group messages by date
        days: dict[str, list[str]] = {}
        current_date = None
        participants = set()

        for line in lines:
            date_match = self._DATE_PATTERN.match(line)
            if date_match:
                current_date = date_match.group(1)
                if current_date not in days:
                    days[current_date] = []
                continue

            msg_match = self._MSG_PATTERN.match(line)
            if msg_match and current_date:
                time_str, sender, message = msg_match.groups()
                participants.add(sender)
                days[current_date].append(f"[{time_str}] {sender}: {message}")
            elif current_date and line.strip():
                # Continuation of previous message
                if current_date in days and days[current_date]:
                    days[current_date][-1] += "\n" + line.strip()

        results = []
        for date_str, messages in days.items():
            try:
                occurred = datetime.strptime(date_str, "%Y/%m/%d").replace(tzinfo=timezone.utc)
            except ValueError:
                occurred = None

            content = "\n".join(messages)
            results.append(PreDocument(
                title=f"LINE: {chat_name} - {date_str}",
                content=content,
                doc_type="conversation",
                occurred_at=occurred,
                original_path=str(p),
                source_info={"type": "chat_export", "uri": f"line://{p.stem}/{date_str}"},
                metadata={
                    "platform": "line",
                    "chat_name": chat_name,
                    "participants": sorted(participants),
                    "message_count": len(messages),
                    "date": date_str,
                },
                ownership="shared",
                privacy_level="internal",
                fidelity="high",
            ))

        return results


class FacebookParser(BaseParser):
    """Parse Facebook data export JSON (posts)."""
    name = "facebook"
    supported_extensions = [".json"]
    priority = 25

    def can_handle(self, source: str, **kwargs) -> bool:
        if kwargs.get("parser") == "facebook":
            return True
        if Path(source).suffix.lower() != ".json":
            return False
        # H7 audit fix: only read first 8KB for detection, don't load entire file
        try:
            p = Path(source)
            if p.stat().st_size > MAX_FILE_SIZE:
                return False
            with open(source, encoding="utf-8") as f:
                head = f.read(8192)
            # Facebook posts export starts with [{"timestamp": ...}]
            return '"timestamp"' in head and ('"data"' in head or '"attachments"' in head) and head.lstrip().startswith("[")
        except Exception:
            return False

    def parse(self, source: str, **kwargs) -> list[PreDocument]:
        p = Path(source)
        with open(source, encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            data = [data]

        results = []
        for post in data:
            timestamp = post.get("timestamp", 0)
            occurred = datetime.fromtimestamp(timestamp, tz=timezone.utc) if timestamp else None

            # Extract post text
            text_parts = []
            for d in post.get("data", []):
                if "post" in d:
                    text_parts.append(d["post"])

            text = "\n".join(text_parts)
            if not text:
                text = "[No text content]"

            title = text[:80].replace("\n", " ").strip() or "Facebook Post"

            # Media info
            media_count = len(post.get("attachments", []))

            results.append(PreDocument(
                title=title,
                content=text,
                doc_type="social_post",
                occurred_at=occurred,
                original_path=str(p),
                source_info={"type": "social_export", "uri": f"facebook://post/{timestamp}"},
                metadata={
                    "platform": "facebook",
                    "media_count": media_count,
                    "tags": post.get("tags", []),
                },
                ownership="self",
                privacy_level="public",
                fidelity="full" if text != "[No text content]" else "metadata_only",
            ))

        return results


class ImageParser(BaseParser):
    """Parse image files — extract EXIF metadata."""
    name = "image"
    supported_extensions = [".jpg", ".jpeg", ".png", ".heic", ".webp", ".gif", ".bmp", ".tiff"]
    priority = 60

    def parse(self, source: str, **kwargs) -> list[PreDocument]:
        p = Path(source)
        meta = self._file_meta(source)

        try:
            from PIL import Image
            from PIL.ExifTags import TAGS

            img = Image.open(str(p))
            meta["width"] = img.width
            meta["height"] = img.height
            meta["format"] = img.format
            meta["mode"] = img.mode

            # Extract EXIF
            exif_data = img.getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, str(tag_id))
                    if tag_name in ("DateTime", "DateTimeOriginal", "Make", "Model",
                                    "ImageDescription", "UserComment"):
                        try:
                            meta[tag_name.lower()] = str(value)
                        except Exception:
                            pass

                # GPS
                gps_info = exif_data.get(0x8825)  # GPSInfo tag
                if gps_info:
                    meta["has_gps"] = True

            img.close()

        except ImportError:
            meta["error"] = "Pillow not installed"
        except Exception as e:
            meta["error"] = str(e)

        # Build content from available metadata
        content_parts = [f"[Image: {p.name}]"]
        if "imagedescription" in meta:
            content_parts.append(meta["imagedescription"])
        if "usercomment" in meta:
            content_parts.append(meta["usercomment"])
        content_parts.append(f"Dimensions: {meta.get('width', '?')}x{meta.get('height', '?')}")
        if "make" in meta:
            content_parts.append(f"Camera: {meta.get('make', '')} {meta.get('model', '')}")

        content = "\n".join(content_parts)

        # Parse taken_at from EXIF datetime
        taken_at = None
        for key in ("datetimeoriginal", "datetime"):
            if key in meta:
                try:
                    taken_at = datetime.strptime(meta[key], "%Y:%m:%d %H:%M:%S").replace(tzinfo=timezone.utc)
                    break
                except ValueError:
                    pass
        if not taken_at:
            taken_at = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)

        has_text = "imagedescription" in meta or "usercomment" in meta
        fidelity = "low" if has_text else "metadata_only"

        return [PreDocument(
            title=p.name,
            content=content,
            doc_type="image",
            occurred_at=taken_at,
            original_path=str(p),
            source_info={"type": "file_system", "uri": f"file://{p.as_posix()}"},
            metadata=meta,
            fidelity=fidelity,
        )]


class MeetingParser(BaseParser):
    """Parse meeting transcript files (.vtt, .srt)."""
    name = "meeting"
    supported_extensions = [".vtt", ".srt"]
    priority = 55

    def parse(self, source: str, **kwargs) -> list[PreDocument]:
        p = Path(source)
        text = p.read_text(encoding="utf-8", errors="replace")
        ext = p.suffix.lower()

        if ext == ".vtt":
            segments = self._parse_vtt(text)
        else:
            segments = self._parse_srt(text)

        # Merge adjacent segments from same speaker
        merged = self._merge_segments(segments)
        content = "\n".join(f"{s['speaker']}: {s['text']}" if s.get("speaker") else s["text"]
                           for s in merged)

        speakers = sorted(set(s.get("speaker", "") for s in merged if s.get("speaker")))
        mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)

        return [PreDocument(
            title=p.stem,
            content=content,
            doc_type="meeting_transcript",
            occurred_at=mtime,
            original_path=str(p),
            source_info={"type": "meeting_export", "uri": f"file://{p.as_posix()}"},
            metadata={
                **self._file_meta(source),
                "format": ext.lstrip("."),
                "segment_count": len(segments),
                "speakers": speakers,
            },
            fidelity="medium",  # auto-transcription has errors
        )]

    @staticmethod
    def _parse_vtt(text: str) -> list[dict]:
        """Parse WebVTT format."""
        segments = []
        blocks = text.split("\n\n")
        for block in blocks:
            lines = block.strip().split("\n")
            # Skip WEBVTT header and NOTE blocks
            if not lines or lines[0].startswith("WEBVTT") or lines[0].startswith("NOTE"):
                continue
            # Find timestamp line
            text_lines = []
            for line in lines:
                if "-->" in line:
                    continue
                if re.match(r"^\d+$", line.strip()):
                    continue
                text_lines.append(line.strip())
            if text_lines:
                full = " ".join(text_lines)
                # Try to extract speaker: "Speaker Name: text"
                m = re.match(r"^<v\s+([^>]+)>(.+)$", full)
                if m:
                    segments.append({"speaker": m.group(1).strip(), "text": m.group(2).strip()})
                elif ": " in full[:50]:
                    sp, tx = full.split(": ", 1)
                    segments.append({"speaker": sp.strip(), "text": tx.strip()})
                else:
                    segments.append({"speaker": "", "text": full})
        return segments

    @staticmethod
    def _parse_srt(text: str) -> list[dict]:
        """Parse SRT subtitle format."""
        segments = []
        blocks = text.strip().split("\n\n")
        for block in blocks:
            lines = block.strip().split("\n")
            text_lines = []
            for line in lines:
                if re.match(r"^\d+$", line.strip()):
                    continue
                if "-->" in line:
                    continue
                text_lines.append(line.strip())
            if text_lines:
                segments.append({"speaker": "", "text": " ".join(text_lines)})
        return segments

    @staticmethod
    def _merge_segments(segments: list[dict]) -> list[dict]:
        """Merge adjacent segments from same speaker."""
        if not segments:
            return []
        merged = [segments[0].copy()]
        for s in segments[1:]:
            if s.get("speaker") and s["speaker"] == merged[-1].get("speaker"):
                merged[-1]["text"] += " " + s["text"]
            else:
                merged.append(s.copy())
        return merged


class WebParser(BaseParser):
    """Parse web pages (HTML files) or fetch URLs."""
    name = "web"
    supported_extensions = [".html", ".htm"]
    priority = 70

    def can_handle(self, source: str, **kwargs) -> bool:
        if kwargs.get("parser") == "web":
            return True
        if source.startswith("http://") or source.startswith("https://"):
            return True
        return Path(source).suffix.lower() in self.supported_extensions

    def parse(self, source: str, **kwargs) -> list[PreDocument]:
        if source.startswith("http://") or source.startswith("https://"):
            return self._parse_url(source, **kwargs)
        return self._parse_file(source, **kwargs)

    def _parse_file(self, source: str, **kwargs) -> list[PreDocument]:
        p = Path(source)
        html = p.read_text(encoding="utf-8", errors="replace")
        return self._html_to_predoc(html, source=str(p),
                                     uri=f"file://{p.as_posix()}",
                                     occurred_at=datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc))

    # H5 audit fix: SSRF protection — block internal/metadata URLs
    _BLOCKED_HOSTS = {"169.254.169.254", "metadata.google.internal", "100.100.100.200"}
    _BLOCKED_PREFIXES = ("http://localhost", "http://127.0.0.1", "http://0.0.0.0",
                         "http://[::1]", "http://10.", "http://172.16.", "http://192.168.")

    def _parse_url(self, url: str, **kwargs) -> list[PreDocument]:
        # SSRF check
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.hostname in self._BLOCKED_HOSTS:
            return [PreDocument(
                title=url, content=f"[BLOCKED] Internal/metadata URL not allowed: {url}",
                doc_type="webpage", fidelity="metadata_only", metadata={"url": url, "blocked": "ssrf"},
            )]
        if any(url.lower().startswith(p) for p in self._BLOCKED_PREFIXES):
            return [PreDocument(
                title=url, content=f"[BLOCKED] Private network URL not allowed: {url}",
                doc_type="webpage", fidelity="metadata_only", metadata={"url": url, "blocked": "ssrf"},
            )]

        try:
            import requests
            resp = requests.get(url, timeout=30, headers={"User-Agent": "Clawd-Lobster/1.0"},
                                allow_redirects=False)
            resp.raise_for_status()
            return self._html_to_predoc(resp.text, source=url, uri=url)
        except ImportError:
            return [PreDocument(
                title=url, content=f"[URL not fetched — requests not installed] {url}",
                doc_type="webpage", fidelity="metadata_only",
                metadata={"url": url, "error": "requests not installed"},
            )]
        except Exception as e:
            return [PreDocument(
                title=url, content=f"[Fetch error] {e}",
                doc_type="webpage", fidelity="metadata_only",
                metadata={"url": url, "error": str(e)},
            )]

    def _html_to_predoc(self, html: str, source: str = "", uri: str = "",
                         occurred_at: datetime | None = None) -> list[PreDocument]:
        # Extract title
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
        title = title_match.group(1).strip() if title_match else source

        # Strip HTML → text
        text = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.S)
        text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.S)
        text = re.sub(r"<nav[^>]*>.*?</nav>", "", text, flags=re.S)
        text = re.sub(r"<footer[^>]*>.*?</footer>", "", text, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        # Extract domain
        domain = ""
        if uri.startswith("http"):
            from urllib.parse import urlparse
            domain = urlparse(uri).netloc

        return [PreDocument(
            title=title,
            content=text,
            doc_type="webpage",
            occurred_at=occurred_at,
            original_path=source,
            source_info={"type": "web", "uri": uri},
            metadata={"url": uri, "domain": domain},
            ownership="external",
            fidelity="high" if len(text) > 200 else "low",
        )]


class VoiceMemoParser(BaseParser):
    """Parse audio files — transcribe using Whisper if available."""
    name = "voice_memo"
    supported_extensions = [".m4a", ".wav", ".mp3", ".ogg", ".flac"]
    priority = 80

    def parse(self, source: str, **kwargs) -> list[PreDocument]:
        p = Path(source)
        meta = self._file_meta(source)
        mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)

        # Try whisper transcription
        try:
            import whisper
            model = whisper.load_model("base")
            result = model.transcribe(str(p))
            text = result.get("text", "")
            meta["language"] = result.get("language", "")
            meta["whisper_model"] = "base"
            fidelity = "medium"
            title = text[:80].strip() or p.stem
        except ImportError:
            text = f"[Audio not transcribed — whisper not installed] {p.name}"
            fidelity = "metadata_only"
            title = p.stem
        except Exception as e:
            text = f"[Transcription error] {e}"
            fidelity = "metadata_only"
            title = p.stem
            meta["error"] = str(e)

        return [PreDocument(
            title=title,
            content=text,
            doc_type="voice_memo",
            occurred_at=mtime,
            original_path=str(p),
            source_info={"type": "audio_file", "uri": f"file://{p.as_posix()}"},
            metadata=meta,
            fidelity=fidelity,
        )]


class DebateParser(BaseParser):
    """Parse AI roundtable debate markdown files."""
    name = "debate"
    supported_extensions = [".md"]
    priority = 15  # high priority for debate detection

    _DEBATE_INDICATORS = ["round", "consensus", "participants", "confidence score"]

    def can_handle(self, source: str, **kwargs) -> bool:
        if kwargs.get("parser") == "debate":
            return True
        if Path(source).suffix.lower() != ".md":
            return False
        try:
            with open(source, encoding="utf-8") as f:
                head = f.read(2000).lower()
            matches = sum(1 for indicator in self._DEBATE_INDICATORS if indicator in head)
            return matches >= 2
        except Exception:
            return False

    def parse(self, source: str, **kwargs) -> list[PreDocument]:
        p = Path(source)
        content = p.read_text(encoding="utf-8", errors="replace")

        # Extract round number from filename or title
        round_match = re.search(r"round\s*(\d+)", content[:500], re.I)
        round_num = int(round_match.group(1)) if round_match else None

        # Extract participants
        participants = []
        part_match = re.search(r"participants?[:\s]+(.+?)(?:\n|$)", content[:1000], re.I)
        if part_match:
            participants = [p.strip() for p in part_match.group(1).split(",")]

        # Extract topics (## headings)
        topics = re.findall(r"^##\s+(.+)$", content, re.M)

        mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)

        return [PreDocument(
            title=f"Vault Roundtable: {p.stem}",
            content=content,
            doc_type="debate_transcript",
            occurred_at=mtime,
            original_path=str(p),
            source_info={"type": "debate", "uri": f"debate://{p.stem}"},
            metadata={
                "round_number": round_num,
                "participants": participants,
                "topics": topics[:20],
                "has_consensus": "consensus" in content.lower(),
            },
            fidelity="full",
        )]


# ---------------------------------------------------------------------------
# ParserRouter — dispatch to correct parser
# ---------------------------------------------------------------------------

class ParserRouter:
    """Routes sources to the correct parser."""

    def __init__(self):
        self._parsers: list[BaseParser] = []

    def register(self, parser: BaseParser):
        self._parsers.append(parser)
        self._parsers.sort(key=lambda p: p.priority)

    def register_defaults(self):
        """Register all built-in parsers."""
        for cls in [DebateParser, LineParser, FacebookParser, EmailParser,
                    PdfParser, TextFileParser, ImageParser, MeetingParser,
                    WebParser, VoiceMemoParser]:
            self.register(cls())

    def list_parsers(self) -> list[dict]:
        """List registered parsers."""
        return [
            {"name": p.name, "extensions": p.supported_extensions, "priority": p.priority}
            for p in self._parsers
        ]

    def route(self, source: str, **kwargs) -> list[PreDocument]:
        """Route a single file/URL to the right parser."""
        for parser in self._parsers:
            if parser.can_handle(source, **kwargs):
                return parser.parse(source, **kwargs)
        # No parser found — create metadata-only doc
        p = Path(source)
        if p.exists():
            return [PreDocument(
                title=p.name,
                content=f"[No parser for {p.suffix}] {p.name}",
                doc_type="file",
                fidelity="metadata_only",
                original_path=str(p),
                metadata={"extension": p.suffix.lower(), "size_bytes": p.stat().st_size},
            )]
        return []

    def route_directory(self, directory: str, recursive: bool = True,
                        **kwargs):
        """Walk a directory and yield PreDocuments (generator — M10 audit fix: no OOM)."""
        dir_path = Path(directory)
        if not dir_path.is_dir():
            yield from self.route(directory, **kwargs)
            return

        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fname in files:
                fpath = os.path.join(root, fname)
                fp = Path(fpath)

                # Skip hidden files and too-large files
                if fname.startswith("."):
                    continue
                try:
                    if fp.stat().st_size > MAX_FILE_SIZE:
                        continue
                    if fp.stat().st_size == 0:
                        continue
                except OSError:
                    continue

                try:
                    yield from self.route(fpath, **kwargs)
                except Exception as e:
                    yield PreDocument(
                        title=f"[PARSE ERROR] {fname}",
                        content=f"Failed to parse: {e}",
                        doc_type="file",
                        fidelity="metadata_only",
                        original_path=fpath,
                    )

            if not recursive:
                break


# ---------------------------------------------------------------------------
# DedupEngine — 3-layer deduplication
# ---------------------------------------------------------------------------

class DedupEngine:
    """Three-layer deduplication for absorb."""

    def __init__(self, vault=None):
        self.vault = vault
        self._seen_hashes: set[str] = set()  # in-session dedup

    def check(self, pre_doc: PreDocument) -> tuple[str, int | None]:
        """Check if document should be ingested.
        Returns (action, existing_doc_id).
            action: 'skip' | 'version' | 'new'
        """
        content_hash = hashlib.sha256(pre_doc.content.encode("utf-8")).hexdigest()

        # In-session dedup (no DB needed)
        if content_hash in self._seen_hashes:
            return ("skip", None)
        self._seen_hashes.add(content_hash)

        # If no vault connection, can't check DB
        if not self.vault:
            return ("new", None)

        # Layer 1: exact content match → skip
        existing = self.vault.find_by_hash(content_hash)
        if existing:
            return ("skip", existing.get("id"))

        # Layer 2: same path, different content → new version
        if pre_doc.original_path:
            prev = self.vault.find_by_path(pre_doc.original_path)
            if prev:
                pre_doc.parent_doc_id = prev.get("id")
                pre_doc.version = (prev.get("version") or 1) + 1
                return ("version", prev.get("id"))

        # Layer 3: truly new
        return ("new", None)


# ---------------------------------------------------------------------------
# absorb() — main entry point
# ---------------------------------------------------------------------------

def absorb(source: str, dry_run: bool = False, recursive: bool = True,
           vault=None, **kwargs) -> dict:
    """Universal ingestion entry point.

    Args:
        source: File path, directory path, or URL.
        dry_run: If True, parse but don't ingest.
        recursive: If True, recurse into subdirectories.
        vault: Vault instance (optional — falls back to no-op if None).
        **kwargs: Passed to parser (e.g., parser='line', user_email='ted@...')

    Returns:
        Summary dict: {total, new, versioned, skipped, errors, by_type: {doc_type: count}}
    """
    router = ParserRouter()
    router.register_defaults()

    # Parse (generator — streams docs one at a time to avoid OOM)
    source_path = Path(source)
    if source_path.is_dir():
        doc_stream = router.route_directory(str(source_path), recursive=recursive, **kwargs)
    else:
        doc_stream = router.route(source, **kwargs)

    # Dedup + Ingest
    dedup = DedupEngine(vault)
    summary = {
        "source": source,
        "total": 0,
        "new": 0,
        "versioned": 0,
        "skipped": 0,
        "errors": [],
        "by_type": {},
    }

    for doc in doc_stream:
        summary["total"] += 1
        # Count by type
        summary["by_type"][doc.doc_type] = summary["by_type"].get(doc.doc_type, 0) + 1

        action, existing_id = dedup.check(doc)

        if action == "skip":
            summary["skipped"] += 1
            continue

        if dry_run:
            if action == "version":
                summary["versioned"] += 1
            else:
                summary["new"] += 1
            continue

        # Actually ingest
        if vault:
            try:
                vault.ingest(**doc.to_ingest_kwargs())
                if action == "version":
                    summary["versioned"] += 1
                else:
                    summary["new"] += 1
            except Exception as e:
                summary["errors"].append(f"{doc.title}: {e}")
        else:
            # No vault — just count (useful for dry-run or L1/L2 fallback)
            if action == "version":
                summary["versioned"] += 1
            else:
                summary["new"] += 1

    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_summary(summary: dict, dry_run: bool = False):
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{prefix}Absorbed from: {summary['source']}")
    print(f"|-- {summary['total']:>5} total files parsed")
    print(f"|-- {summary['new']:>5} new documents")
    print(f"|-- {summary['versioned']:>5} version updates")
    print(f"|-- {summary['skipped']:>5} skipped (duplicates)")
    if summary["errors"]:
        print(f"\\-- {len(summary['errors']):>5} errors")
        for err in summary["errors"][:10]:
            print(f"      - {err}")
    print()
    if summary["by_type"]:
        print("By type:")
        for dtype, count in sorted(summary["by_type"].items(), key=lambda x: -x[1]):
            print(f"  {dtype:25s} {count:>5}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Vault Parsers — Universal file ingestion for The Vault",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    # absorb subcommand
    absorb_cmd = sub.add_parser("absorb", help="Absorb files/directories into the Vault")
    absorb_cmd.add_argument("source", help="File, directory, or URL to absorb")
    absorb_cmd.add_argument("--dry-run", action="store_true", help="Preview without ingesting")
    absorb_cmd.add_argument("--no-recurse", action="store_true", help="Don't recurse into subdirectories")
    absorb_cmd.add_argument("--parser", help="Force a specific parser (line, facebook, debate, etc.)")
    absorb_cmd.add_argument("--ownership", default="self", help="Ownership: self/work/external/shared")
    absorb_cmd.add_argument("--privacy", default="internal", help="Privacy: public/internal/restricted/secret")
    absorb_cmd.add_argument("--vault", action="store_true", help="Connect to Oracle Vault for dedup + ingest")

    # parsers subcommand
    sub.add_parser("parsers", help="List available parsers")

    args = parser.parse_args()

    if args.command == "parsers":
        router = ParserRouter()
        router.register_defaults()
        print("Available parsers:\n")
        for p in router.list_parsers():
            exts = ", ".join(p["extensions"][:8])
            if len(p["extensions"]) > 8:
                exts += f" (+{len(p['extensions']) - 8} more)"
            print(f"  {p['name']:20s}  P{p['priority']:<3d}  {exts}")
        return

    if args.command == "absorb":
        vault_instance = None
        if args.vault:
            try:
                from vault_api import Vault
                vault_instance = Vault()
                print("Connected to Oracle Vault")
            except Exception as e:
                print(f"Warning: Could not connect to Vault ({e}). Running without dedup.")

        kw = {}
        if args.parser:
            kw["parser"] = args.parser

        summary = absorb(
            args.source,
            dry_run=args.dry_run,
            recursive=not args.no_recurse,
            vault=vault_instance,
            **kw,
        )
        _print_summary(summary, dry_run=args.dry_run)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
