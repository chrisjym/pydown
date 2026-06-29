"""Abstract base class for all format converters.

Implements the Template Method pattern: the public ``convert`` method handles
validation that is common to every format (does the file exist? is the extension
one this converter supports?), then delegates the format-specific extraction work
to the abstract ``_convert`` hook that each subclass implements.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple


class BaseConverter(ABC):
    """Base class for converters that turn a file into a Markdown string.

    Subclasses declare the extensions they handle via the ``extensions`` class
    attribute and implement :meth:`_convert`.
    """

    #: File extensions (lowercase, dot-prefixed) this converter accepts.
    extensions: Tuple[str, ...] = ()

    def convert(self, file_path: str) -> str:
        """Validate ``file_path`` and return its Markdown representation.

        Raises:
            FileNotFoundError: if the path does not exist or is not a file.
            ValueError: if the file's extension is not supported by this converter.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()
        if ext not in self.extensions:
            raise ValueError(
                f"{type(self).__name__} does not support '{ext}' files "
                f"(supported: {', '.join(self.extensions)})"
            )

        return self._convert(file_path)

    @abstractmethod
    def _convert(self, file_path: str) -> str:
        """Extract Markdown from ``file_path``. Implemented by each subclass."""
        raise NotImplementedError
