"""
Progress display utilities for user feedback
"""

import sys


class ProgressIndicator:
    """Utility class for real-time progress display"""

    def __init__(self):
        self.animation_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.frame_index = 0

    def show_progress(self, message: str, step: int = 0, total: int = 0) -> None:
        """Display progress"""
        frame = self.animation_frames[self.frame_index % len(self.animation_frames)]
        self.frame_index += 1

        if total > 0 and step > 0:
            progress = f"[{step}/{total}] "
        else:
            progress = ""


    def show_success(self, message: str) -> None:
        """Display success message"""

    def show_error(self, message: str) -> None:
        """Display error message"""

    def show_info(self, message: str) -> None:
        """Display info message"""


# Global progress indicator instance
progress = ProgressIndicator()
