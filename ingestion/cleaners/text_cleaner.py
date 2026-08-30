import re
import unicodedata
from dataclasses import dataclass


@dataclass
class CleanedText:
    """
    Contains both the untouched original text
    and its normalized representation.
    """

    original_text: str
    normalized_text: str


class TextCleaner:
    """
    Cleans and normalizes religious text without
    modifying the original source text.
    """

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """
        Normalize Unicode characters using NFC.

        NFC is deliberately used instead of aggressive
        normalization so that religious scripts are
        preserved as faithfully as possible.
        """

        return unicodedata.normalize("NFC", text)

    @staticmethod
    def remove_control_characters(text: str) -> str:
        """
        Remove unwanted Unicode control characters while
        preserving normal whitespace such as spaces,
        tabs and newlines.
        """

        return "".join(
            character
            for character in text
            if (
                unicodedata.category(character) != "Cc"
                or character in "\n\t\r"
            )
        )

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalize repeated spaces and excessive blank lines.
        """

        # Normalize spaces/tabs within lines
        lines = []

        for line in text.splitlines():
            line = re.sub(r"[ \t]+", " ", line)
            line = line.strip()

            if line:
                lines.append(line)

        # Preserve paragraph boundaries
        return "\n".join(lines)

    @classmethod
    def clean(cls, text: str) -> CleanedText:
        """
        Return the untouched original text together with
        a normalized copy.
        """

        if not isinstance(text, str):
            raise TypeError("Text must be a string.")

        original_text = text

        normalized_text = cls.normalize_unicode(text)
        normalized_text = cls.remove_control_characters(
            normalized_text
        )
        normalized_text = cls.normalize_whitespace(
            normalized_text
        )

        return CleanedText(
            original_text=original_text,
            normalized_text=normalized_text,
        )


if __name__ == "__main__":
    sample_text = """
    بِسْمِ اللَّهِ

    This   is    a   test.

    Multiple      spaces
    should be normalized.
    """

    result = TextCleaner.clean(sample_text)

    print("=== ORIGINAL TEXT ===")
    print(result.original_text)

    print("\n=== NORMALIZED TEXT ===")
    print(result.normalized_text)