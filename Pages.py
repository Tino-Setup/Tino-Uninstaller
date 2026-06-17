import tkinter as tk
from tkinter import ttk

from i18n import _


class WelcomePage(ttk.Frame):
    """The initial welcome page of the uninstaller."""
    def __init__(self, parent, data, logo=None):
        """Initialize the WelcomePage."""
        super().__init__(parent, style="Content.TFrame")

        if logo:
            self.logo_label = ttk.Label(self, image=logo, style="Logo.TLabel")
            self.logo_label.pack(pady=(20, 0))

        ttk.Label(self, text=_("Welcome to the {} Uninstaller").format(data.local.application_name),
              style="Title.TLabel", wraplength=600, justify="center").pack(pady=(20, 10))
        ttk.Label(self, text=_("This uninstaller will guide you through the removal of\n"
                         "{} and its data from your computer.\n\n"
                         "Click Uninstall to continue or Cancel to abort the uninstallation.").format(data.local.application_name),
              style="Content.TLabel", justify="center", wraplength=600).pack(pady=10)


class UnInstallingPage(ttk.Frame):
    """Exposes clean update methods instead of raw widget access."""
    def __init__(self, parent, data):
        """Initialize the UnInstallingPage."""
        super().__init__(parent, style="Content.TFrame")
        ttk.Label(self, text=_("Uninstalling {}...").format(data.local.application_name),
              style="Heading.TLabel").pack(pady=20)

        self._progress = ttk.Progressbar(self, mode="determinate", length=400,
                                    style="TProgressbar")
        self._progress.pack(pady=10)

        self._status_label = ttk.Label(self, text=_("Preparing..."),
                                  style="Content.TLabel")
        self._status_label.pack()

    def update_progress(self, value: float):
        """Set progress bar value (0-100)."""
        self._progress["value"] = value

    def update_status(self, text: str):
        """Set the status label text."""
        self._status_label.config(text=text)


class FinishPage(ttk.Frame):
    """The final page displayed when uninstallation completes or fails."""
    def __init__(self, parent, logo=None):
        """Initialize the FinishPage."""
        super().__init__(parent, style="Content.TFrame")

        if logo:
            self.logo_label = ttk.Label(self, image=logo, style="Logo.TLabel")
            self.logo_label.pack(pady=(30, 0))

        self.title_label = ttk.Label(self, text="", style="Title.TLabel", justify="center")
        self.title_label.pack(pady=(20, 10))
        self.message_label = ttk.Label(self, text="", style="Content.TLabel",
                                       justify="center", wraplength=550)
        self.message_label.pack(pady=10)
