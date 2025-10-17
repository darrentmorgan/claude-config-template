"""Execution signals parser: Extract file references from logs."""

import re
from pathlib import Path


class ExecutionSignalParser:
    """Parse execution signals from error logs and test failures."""

    # Regex patterns for file references
    PYTHON_TRACEBACK = re.compile(r'File "([^"]+)", line (\d+)')
    PYTEST_FAILURE = re.compile(r'([^:]+\.py):(\d+)')

    def parse_error_log(self, log_content: str) -> dict[str, float]:
        """Parse error log for file references.

        Args:
            log_content: Error log or stack trace content

        Returns:
            Dict mapping file paths to signal scores
        """
        file_scores: dict[str, float] = {}

        # Parse Python tracebacks
        for match in self.PYTHON_TRACEBACK.finditer(log_content):
            file_path = match.group(1)
            file_scores[file_path] = file_scores.get(file_path, 0.0) + 1.0

        # Parse pytest failures
        for match in self.PYTEST_FAILURE.finditer(log_content):
            file_path = match.group(1)
            file_scores[file_path] = file_scores.get(file_path, 0.0) + 0.8

        # Normalize scores
        if file_scores:
            max_score = max(file_scores.values())
            return {k: v / max_score for k, v in file_scores.items()}

        return {}

    def get_signal_score(self, file_path: str, log_content: str) -> float:
        """Get execution signal score for a specific file.

        Args:
            file_path: File path to check
            log_content: Error log content

        Returns:
            Signal score [0, 1]
        """
        file_scores = self.parse_error_log(log_content)
        return file_scores.get(file_path, 0.0)
