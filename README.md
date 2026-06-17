<p align="center">
  <img style="width: auto; max-width: 50%; height: auto;" alt="Tino Uninstaller logo" src="Tino Uninstaller.png">
</p>

<h2 align="center">Tino Uninstaller</h2>
<h3 align="center"><em>One-click graphical uninstaller for Linux</em></h3>

**Tino Uninstaller** is the end-user facing removal tool in the **Tino Setup** suite. It is bundled alongside installed applications by the **Tino Installer** and provides a guided, graphical uninstallation experience.

---

### 🎯 What It Does

When an end-user runs the Tino Uninstaller, it:

1. **Displays a confirmation page** showing the application that will be removed.
2. **Removes all installed files** that were placed during installation.
3. **Cleans up desktop shortcuts** (`.desktop` files) and menu entries.
4. **Handles privilege elevation** via `sudo` or `pkexec` if the application was installed system-wide.
5. **Shows a completion summary** once uninstallation is finished.

---

### 🗑️ Usage (For End-Users)

#### Just click on the uninstaller and run it

#### And if you want to execute it via terminal:
```bash
chmod +x YourApp-Uninstaller
./YourApp-Uninstaller
```

The graphical wizard will guide you through the removal process.

---

### 🧩 Architecture

| File | Purpose |
|------|---------|
| `Wizard.py` | Main uninstaller window and page navigation logic |
| `Pages.py` | Individual wizard pages (Confirmation, Progress, Finish) |
| `Data.py` | Reads the installation manifest to determine what to remove |
| `Elevation.py` | Privilege escalation helper for system-wide uninstalls |
| `Styles.py` | Tkinter theme and styling definitions |
| `i18n.py` | Internationalization / locale support |

---

### 🛠️ Technology Stack
- **Python 3** & **Tkinter** (Uninstaller GUI)
- **PyInstaller** (Packaged into a standalone executable by Tino Wizard)


### 🧩 Contributing

Pull requests and Issues are welcome. For major changes, please open an issue first to discuss what you would like to change.

### 📄 License

**[GNU GPL 3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)**