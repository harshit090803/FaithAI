from pathlib import Path

import pytest

from ingestion.corpus.file_hasher import FileHasher


def test_sha256_existing_file(tmp_path: Path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("FaithAI", encoding="utf-8")

    digest = FileHasher.sha256(file_path)

    assert len(digest) == 64
    assert all(
        character in "0123456789abcdef"
        for character in digest
    )


def test_sha256_is_deterministic(tmp_path: Path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text(
        "FaithAI provenance test",
        encoding="utf-8",
    )

    digest1 = FileHasher.sha256(file_path)
    digest2 = FileHasher.sha256(file_path)

    assert digest1 == digest2


def test_different_files_have_different_hashes(tmp_path: Path):
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"

    file1.write_text("FaithAI A", encoding="utf-8")
    file2.write_text("FaithAI B", encoding="utf-8")

    digest1 = FileHasher.sha256(file1)
    digest2 = FileHasher.sha256(file2)

    assert digest1 != digest2


def test_missing_file_raises_error(tmp_path: Path):
    file_path = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        FileHasher.sha256(file_path)


def test_empty_file_has_valid_sha256(tmp_path: Path):
    file_path = tmp_path / "empty.txt"
    file_path.write_bytes(b"")

    digest = FileHasher.sha256(file_path)

    assert digest == (
        "e3b0c44298fc1c149afbf4c8996fb924"
        "27ae41e4649b934ca495991b7852b855"
    )