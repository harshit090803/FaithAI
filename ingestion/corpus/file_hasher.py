import hashlib
from pathlib import Path


class FileHasher:
    """
    Calculates cryptographic hashes for corpus files.

    FaithAI currently uses SHA-256 for file integrity tracking.
    """

    @staticmethod
    def sha256(file_path: str | Path) -> str:
        """
        Calculate the SHA-256 hash of a file.

        Args:
            file_path:
                Path to the file.

        Returns:
            Lowercase hexadecimal SHA-256 digest.

        Raises:
            FileNotFoundError:
                If the file does not exist.

            ValueError:
                If the path is not a file.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File does not exist: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Path is not a file: {path}"
            )

        digest = hashlib.sha256()

        with path.open("rb") as file:
            for chunk in iter(
                lambda: file.read(1024 * 1024),
                b"",
            ):
                digest.update(chunk)

        return digest.hexdigest()