import webbrowser
import os
import shutil
import subprocess
import sys
import threading

import tkinter as tk
from tkinter import ttk

from Data import load_data, TinoConfig
from Pages import WelcomePage, UnInstallingPage, FinishPage
from Styles import get_style
from i18n import _, set_language, get_available_languages, get_base_path
from Elevation import check_and_elevate, needs_elevation

class ScriptExecutionError(Exception):
    """Custom exception raised when a pre or post-uninstallation script fails."""
    pass


class TinoDialog(tk.Toplevel):
    """A premium, localizable replacement for standard messageboxes"""
    def __init__(self, parent, title, message, type="ok"):
        """Initialize the TinoDialog."""
        super().__init__(parent)
        self.title(title)
        self.configure(bg="white")
        self.resizable(False, False)
        self.result = None

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self.transient(parent)
        self.grab_set()

        main_frame = ttk.Frame(self, style="Content.TFrame", padding=25)
        main_frame.pack(fill="both", expand=True)

        content_frame = ttk.Frame(main_frame, style="Content.TFrame")
        content_frame.pack(fill="both", expand=True)

        ttk.Label(content_frame, text=message, style="Content.TLabel",
                  wraplength=350, justify="left").pack(pady=(0, 20))

        btn_frame = ttk.Frame(main_frame, style="Content.TFrame")
        btn_frame.pack(fill="x", side="bottom")

        if type == "yesno":
            ttk.Button(btn_frame, text=_("Yes"), width=-10,
                       command=self.on_yes, style="Content.TButton").pack(side="right", padx=5)
            ttk.Button(btn_frame, text=_("No"), width=-10,
                       command=self.on_no, style="Content.TButton").pack(side="right")
        else:
            ttk.Button(btn_frame, text=_("OK"), width=-10,
                       command=self.on_ok, style="Content.TButton").pack(side="right")

        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        py = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{px}+{py}")

        self.wait_window()

    def on_yes(self):
        """Handle the Yes button click."""
        self.result = True
        self.destroy()

    def on_no(self):
        """Handle the No button click."""
        self.result = False
        self.destroy()

    def on_ok(self):
        """Handle the OK button click."""
        self.result = True
        self.destroy()

    def on_cancel(self):
        """Handle the dialog cancellation."""
        self.result = False
        self.destroy()


class App(tk.Tk):
    """Main application class for the Tino Uninstaller wizard."""
    def __init__(self, data: TinoConfig):
        """Initialize the uninstaller application."""
        super().__init__(className="uninstaller")
        self.style = get_style()
        self.data = data

        self.title(_("{} Uninstaller").format(self.data.local.application_name))
        self.wm_protocol("WM_DELETE_WINDOW", self.cancel_setup)
        self.geometry("700x500")
        self.resizable(False, False)

        self.main_area = ttk.Frame(self, style="Content.TFrame")
        self.main_area.pack(side="right", fill="both", expand=True)

        self.content = ttk.Frame(self.main_area, style="Content.TFrame")
        self.content.pack(fill="both", expand=True, padx=20, pady=10)

        ttk.Separator(self.main_area, orient="horizontal").pack(fill="x")

        self.btn_frame = ttk.Frame(self.main_area, style="Content.TFrame")
        self.btn_frame.pack(fill="x", padx=15, pady=15)

        self.app_author_label = ttk.Label(self.btn_frame,
                                      text=_("{} by {}").format(self.data.local.application_name, self.data.application_author),
                                      style="Hyperlink.TLabel", wraplength=300)

        self.next_btn = ttk.Button(self.btn_frame, text=_("Next"), width=-10,
                               command=self.go_next, style="Content.TButton")
        self.cancel_btn = ttk.Button(self.btn_frame, text=_("Cancel"), width=-10,
                                 command=self.cancel_setup, style="Content.TButton")

        self.btn_frame.columnconfigure(1, weight=1)
        self.app_author_label.grid(row=0, column=0, sticky="w")
        self.next_btn.grid(row=0, column=2, padx=5)
        self.cancel_btn.grid(row=0, column=3, padx=(5, 0))

        website_url = self.data.application_website
        if website_url:
            self.app_author_label.config(cursor="hand2")
            self.app_author_label.bind("<Button-1>",
                                       lambda e: webbrowser.open_new(website_url))

        self.page_order = self._build_page_order()
        self.pages = {}
        self.current_page = ""
        self.current_frame = None

        self._failed = False

        self.logo = None
        if self.data.application_icon:
            try:
                raw_logo = tk.PhotoImage(file=os.path.join(get_base_path(), self.data.application_icon))
                natural_h = raw_logo.height()
                factor = max(1, round(natural_h / 120))
                self.logo = raw_logo.subsample(factor, factor)
            except Exception:
                pass

        self.create_pages()
        self.show_page('WelcomePage')

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _build_page_order(self) -> list[str]:
        """Determine the sequence of wizard pages based on configuration."""
        return ["WelcomePage", "UnInstallingPage", "FinishPage"]

    def create_pages(self):
        """Instantiate every page as its own class"""
        for page_name in self.page_order:
            if page_name == "WelcomePage":
                self.pages[page_name] = WelcomePage(self.content, data=self.data, logo=self.logo)
            elif page_name == "UnInstallingPage":
                self.pages[page_name] = UnInstallingPage(self.content, data=self.data)
            elif page_name == "FinishPage":
                self.pages[page_name] = FinishPage(self.content, logo=self.logo)

    def show_page(self, page_name: str):
        """Display the specified wizard page and update navigation buttons."""
        if self.current_frame:
            self.current_frame.pack_forget()

        self.current_page = page_name
        self.current_frame = self.pages[page_name]
        self.current_frame.pack(fill="both", expand=True)

        self.next_btn.config(text=_("Next"), state="normal")

        if self.current_page in ("UnInstallingPage", "FinishPage"):
            self.cancel_btn.grid_remove()
        else:
            self.cancel_btn.grid()

        if self.current_page == "UnInstallingPage":
            self.next_btn.config(state="disabled")
            self.start_uninstallation()
        elif self.current_page == "FinishPage":
            self._configure_finish_page()
            self.next_btn.config(text=_("Finish"), state="normal")
        else:
            self.next_btn.config(text=_("Uninstall"), state="normal")

    def _configure_finish_page(self):
        """Show appropriate text on the finish page"""
        finish = self.pages["FinishPage"]
        if self._failed:
            finish.title_label.config(text=_("Uninstallation Failed"))
            finish.message_label.config(
                text=_("An error occurred during the uninstallation of {}.\n\n"
                       "Some files may have already been removed.\n"
                       "Click Finish to close the uninstaller.").format(self.data.local.application_name)
            )
        else:
            finish.title_label.config(text=_("Uninstallation Complete"))
            finish.message_label.config(
                text=_("{} has been successfully uninstalled.\n\n"
                       "Click Finish to close the uninstaller.").format(self.data.local.application_name)
            )

    def get_next_page(self) -> str | None:
        """Get the name of the next page in the wizard sequence."""
        try:
            idx = self.page_order.index(self.current_page)
            return self.page_order[idx + 1] if idx + 1 < len(self.page_order) else None
        except ValueError:
            return None

    def go_next(self):
        """Navigate to the next page or finish the uninstallation."""
        if self.current_page == "FinishPage":
            self.destroy()
        else:
            if self.current_page == "WelcomePage":
                dialog = TinoDialog(self, _("Confirm Uninstallation"),
                                    _("Are you sure you want to uninstall {}?\n\n"
                                      "All files and data associated with this application will be removed.").format(self.data.local.application_name),
                                    type="yesno")
                if not dialog.result:
                    return
            next_page = self.get_next_page()
            if next_page:
                self.show_page(next_page)

    def start_uninstallation(self):
        """Start the uninstallation process in a background thread."""
        installing_page = self.pages['UnInstallingPage']
        installing_page.update_progress(0)
        installing_page.update_status(_("Starting uninstallation..."))

        threading.Thread(target=self._perform_uninstallation, daemon=True).start()

    def _execute_script(self, script_path: str, cwd: str):
        """Helper to run pre/post script files robustly, ensuring permissions and execution shell."""
        if not os.path.exists(script_path):
            raise ScriptExecutionError(_("Script file not found: {}").format(script_path))

        try:
            os.chmod(script_path, 0o755)
        except Exception:
            pass

        run_cwd = cwd
        if not run_cwd or not os.path.exists(run_cwd):
            run_cwd = "/tmp"

        try:
            if script_path.endswith('.sh'):
                subprocess.run(["/bin/sh", script_path], cwd=run_cwd, check=True)
            else:
                subprocess.run([script_path], cwd=run_cwd, check=True)
        except subprocess.CalledProcessError as e:
            raise ScriptExecutionError(_("Script returned non-zero exit code {}").format(e.returncode))
        except Exception as e:
            raise ScriptExecutionError(str(e))

    def _perform_uninstallation(self):
        """Execute all uninstallation steps in sequence."""
        base_dir = get_base_path()
        installing_page = self.pages['UnInstallingPage']
        steps = []

        if self.data.application_pre_uninstallation_script:
            pre_script_path = os.path.join(base_dir, str(self.data.application_pre_uninstallation_script))
            if not os.path.exists(pre_script_path) and self.data.application_installation_path:
                pre_script_path = os.path.join(self.data.application_installation_path,
                                               str(self.data.application_pre_uninstallation_script))

            steps.append((
                _("Running pre-uninstallation script..."),
                lambda p=pre_script_path: self._execute_script(p, self.data.application_installation_path)
            ))

        if self.data.application_executable_path:
            steps.append((
                _("Removing executable..."),
                lambda p=self.data.application_executable_path: (
                    os.remove(p) if os.path.exists(p) else None
                )
            ))

        if self.data.application_icon_path:
            steps.append((
                _("Removing icon..."),
                lambda p=self.data.application_icon_path: (
                    os.remove(p) if os.path.exists(p) else None
                )
            ))

        if self.data.application_desktop_path:
            steps.append((
                _("Removing desktop shortcut..."),
                lambda p=self.data.application_desktop_path: (
                    os.remove(p) if os.path.exists(p) else None
                )
            ))

        if getattr(self.data, 'application_uninstaller_desktop_path', None):
            steps.append((
                _("Removing uninstaller desktop shortcut..."),
                lambda p=self.data.application_uninstaller_desktop_path: (
                    os.remove(p) if os.path.exists(p) else None
                )
            ))
            
        if getattr(self.data, 'application_uninstaller_icon_path', None):
            steps.append((
                _("Removing uninstaller icon..."),
                lambda p=self.data.application_uninstaller_icon_path: (
                    os.remove(p) if os.path.exists(p) else None
                )
            ))

        if self.data.application_installation_path:
            steps.append((
                _("Removing installation directory..."),
                lambda p=self.data.application_installation_path: (
                    shutil.rmtree(p, ignore_errors=False) if os.path.exists(p) else None
                )
            ))
            
        steps.append((
            _("Removing uninstaller executable..."),
            lambda: (
                os.remove(sys.executable) if getattr(sys, 'frozen', False) and os.path.exists(sys.executable) else None
            )
        ))

        if self.data.application_post_uninstallation_script:
            post_script_path = os.path.join(base_dir, str(self.data.application_post_uninstallation_script))
            if not os.path.exists(post_script_path) and self.data.application_installation_path:
                post_script_path = os.path.join(self.data.application_installation_path,
                                                str(self.data.application_post_uninstallation_script))

            steps.append((
                _("Running post-uninstallation script..."),
                lambda p=post_script_path: self._execute_script(p, base_dir)
            ))

        total_steps = len(steps) if steps else 1

        for i, (msg, func) in enumerate(steps):
            self.after(0, lambda m=msg, idx=i: self._update_progress(
                installing_page, m, int((idx / total_steps) * 100)
            ))

            try:
                func()
            except PermissionError as e:
                self.after(0, lambda err=e: self._show_error_and_finish(err))
                return
            except ScriptExecutionError as e:
                self.after(0, lambda err=e: self._show_error_and_finish(
                    err,
                    message=_("Script execution failed during uninstallation.\n\n"
                              "The uninstallation has been aborted.\n\n"
                              "Details:\n{}").format(err)
                ))
                return
            except Exception:
                pass

        self.after(0, lambda: self._update_progress(
            installing_page, _("Uninstallation complete!"), 100
        ))
        self.after(800, lambda: self.show_page("FinishPage"))

    def _update_progress(self, page, msg, value):
        """Update the progress bar and status text on the uninstallation page."""
        page.update_status(msg)
        page.update_progress(value)

    def _show_error_and_finish(self, error, message=None):
        """Show error dialog and go to finish page with failed state."""
        self._failed = True
        if not message:
            message = _("Permission denied during uninstallation.\n\n"
                        "Some files may have already been removed.\n\n"
                        "Details:\n{}").format(error)
        TinoDialog(self, _("Uninstallation Error"), message)
        self.show_page("FinishPage")

    def cancel_setup(self):
        """Prompt the user and cancel the uninstallation if confirmed."""
        if self.current_page == "UnInstallingPage":
            TinoDialog(self, _("Uninstallation in Progress"),
                       _("The uninstallation process has started and cannot be cancelled."),
                       type="ok")
            return

        self.destroy()


if __name__ == "__main__":

    data = load_data()

    paths_to_check = [
        data.application_installation_path,
        data.application_executable_path,
        data.application_icon_path,
        data.application_desktop_path,
        data.application_uninstaller_desktop_path,
    ]

    if any(p and needs_elevation(p) for p in paths_to_check):
        check_and_elevate()

    available_langs = get_available_languages(data)

    selected_lang = None
    app_dir = data.application_installation_path
    if app_dir and os.path.exists(app_dir):
        for lang in available_langs.keys():
            if os.path.exists(os.path.join(app_dir, lang)):
                selected_lang = lang
                break

    if not selected_lang:
        selected_lang = "en_US" if "en_US" in available_langs else next(iter(available_langs.keys()))

    data.current_lang = selected_lang
    set_language(selected_lang)

    app = App(data=data)

    icon_path = data.application_icon
    if icon_path:
        try:
            img = tk.PhotoImage(file=os.path.join(get_base_path(), icon_path))
            app.iconphoto(True, img)
        except Exception:
            pass

    app.mainloop()