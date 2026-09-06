import sys

import pyperclip

from quiver_to_image.exceptions import ClipboardEmptyError, ClipboardNotAvailableError


def get_clipboard() -> str:
    try:
        text = pyperclip.paste()
    except pyperclip.PyperclipException:
        raise ClipboardNotAvailableError(
            "Failed to read clipboard. "
            "Install xclip/xsel (Linux) or use --no-clipboard."
        )

    if not text or not text.strip():
        raise ClipboardEmptyError("Clipboard is empty")

    return text


def get_stdin() -> str:
    if sys.stdin.isatty():
        return ""

    text = sys.stdin.read()
    if not text or not text.strip():
        raise ClipboardEmptyError("Input is empty")

    return text
