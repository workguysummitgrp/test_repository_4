"""Tests for document service — US-007, US-008."""

import pytest
from backend.app.services.document_service import sanitize_filename, validate_file, compute_hash, MIME_TO_FILE_TYPE
from backend.app.models.document import FileType


class TestSanitizeFilename:
    def test_normal_filename(self):
        assert sanitize_filename("report.pdf") == "report.pdf"

    def test_path_traversal_prevention(self):
        result = sanitize_filename("../../etc/passwd")
        assert ".." not in result
        assert "/" not in result
        assert "\\" not in result

    def test_null_bytes_removed(self):
        result = sanitize_filename("file\x00.pdf")
        assert "\x00" not in result

    def test_long_filename_truncated(self):
        long_name = "a" * 300 + ".pdf"
        result = sanitize_filename(long_name)
        assert len(result) <= 255

    def test_special_characters_stripped(self):
        result = sanitize_filename("file<>|name.pdf")
        assert "<" not in result
        assert ">" not in result


class TestValidateFile:
    def test_valid_pdf(self):
        result = validate_file("application/pdf", 1024, b"%PDF-1.4")
        assert result == FileType.PDF

    def test_valid_jpg(self):
        result = validate_file("image/jpeg", 1024, b"\xff\xd8\xff\xe0")
        assert result == FileType.JPG

    def test_valid_png(self):
        result = validate_file("image/png", 1024, b"\x89PNG\r\n\x1a\n")
        assert result == FileType.PNG

    def test_unsupported_type_raises(self):
        with pytest.raises(ValueError, match="Unsupported file type"):
            validate_file("application/exe", 1024, b"MZ")

    def test_oversized_file_raises(self):
        with pytest.raises(ValueError, match="exceeds maximum size"):
            validate_file("application/pdf", 20_000_000, b"%PDF")

    def test_magic_bytes_mismatch_raises(self):
        with pytest.raises(ValueError, match="does not match"):
            validate_file("application/pdf", 1024, b"\x89PNG")


class TestComputeHash:
    def test_hash_deterministic(self):
        content = b"test content"
        h1 = compute_hash(content)
        h2 = compute_hash(content)
        assert h1 == h2

    def test_hash_is_sha256(self):
        h = compute_hash(b"test")
        assert len(h) == 64  # SHA-256 hex digest

    def test_different_content_different_hash(self):
        h1 = compute_hash(b"content1")
        h2 = compute_hash(b"content2")
        assert h1 != h2
