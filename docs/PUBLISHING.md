# Publishing a TidyMate release

A maintainer's checklist for releasing TidyMate to **PyPI** and **GitHub**.
Commands are for Windows PowerShell; macOS/Linux differences are noted where they matter.

> **The two golden rules**
> 1. A version number on PyPI can **never be reused**, even if you delete the release. If something is wrong, fix it and release the next number.
> 2. **Never put a token in code, a commit, an issue or a chat.** Tokens belong in a password manager.

---

## Contents

1. [One-time setup](#1-one-time-setup)
2. [Release checklist](#2-release-checklist)
3. [Build, check and upload](#3-build-check-and-upload)
4. [Tag and publish the GitHub release](#4-tag-and-publish-the-github-release)
5. [After the release](#5-after-the-release)
6. [Optional: automatic publishing (no tokens)](#6-optional-automatic-publishing-no-tokens)
7. [Fixing a bad release](#7-fixing-a-bad-release)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. One-time setup

### PyPI account
1. Register at <https://pypi.org/account/register/> and verify your email.
2. Turn on **two-factor authentication** (Account settings -> Add 2FA). PyPI requires it to publish.

### API token
1. Go to <https://pypi.org/manage/account/#api-tokens> -> **Add API token**.
2. **Name:** `tidymate-publish`. **Scope:** **Project: tidymate**.
3. Copy the token (it starts with `pypi-` and is shown **once**) into a password manager.

> The very first upload of a brand-new project needs a token with **Entire account** scope, because the
> project doesn't exist yet. After that first upload, create a project-scoped token like the one above and
> **remove** the account-wide one. TidyMate is already on PyPI, so you only need the project-scoped token.

### Tools
```powershell
python -m pip install --upgrade build twine
```

### TestPyPI (optional practice site)
<https://test.pypi.org> is a separate site with **separate accounts and separate tokens**. A token from
pypi.org does **not** work there. It's only for rehearsing - you can skip it.

---

## 2. Release checklist

Work through this top to bottom before every release.

- [ ] **Working tree is clean and up to date**
  ```powershell
  git status
  git pull
  ```
- [ ] **Tests pass**
  ```powershell
  python -m unittest discover -s tests -v
  ```
- [ ] **Bump the version** in `pyproject.toml`:
  ```toml
  version = "1.0.2"
  ```
  The version also may appear elsewhere (for example a `__version__` line). Find every copy:
  ```powershell
  Get-ChildItem -Recurse -Include *.py,*.toml | Select-String "1\.0\.1"
  ```
  *(Replace `1.0.1` with the old version. macOS/Linux: `grep -rn "1.0.1" --include="*.py" --include="*.toml" .`)*
- [ ] **README links are full web addresses.** PyPI shows the README as it was at upload time, and relative links
  such as `docs/GLOSSARY.md` break there. Use `https://github.com/Anand2k29/TidyMate/blob/main/...`.
- [ ] **README images exist on GitHub.** They load from `raw.githubusercontent.com/.../main/docs/assets/`, so
  **push your commit before uploading to PyPI**, or the PyPI page will show broken images.
  Rebuild the images with `pip install pillow` then `python docs/assets/build_assets.py` if you changed them.
- [ ] **Commit and push**
  ```powershell
  git add .
  git commit -m "Release 1.0.2: describe what changed"
  git push
  ```
  Check `git status` first: `dist/`, `build/`, virtual environments and `*.egg-info/` must **not** be committed
  (they belong in `.gitignore`).

### Version numbers

TidyMate uses `MAJOR.MINOR.PATCH`:

| Change | Example |
|---|---|
| Bug fix, docs fix | `1.0.1` -> `1.0.2` |
| New feature, still compatible | `1.0.2` -> `1.1.0` |
| Breaking change (a command or behaviour changes) | `1.1.0` -> `2.0.0` |

---

## 3. Build, check and upload

Run these in the project folder (the one that contains `pyproject.toml`).

```powershell
# 1. Remove old build output so you don't upload a stale version
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue

# 2. Build the wheel and the source archive
python -m build

# 3. Check the package metadata and README
python -m twine check dist/*
```
You should see `Successfully built ...` and `PASSED` for both files.

### Look inside the build
```powershell
python -m zipfile -l (Get-ChildItem dist\*.whl).FullName
```
Confirm the list includes `tidymate/__init__.py`, `tidymate/cli.py`, `tidymate/__main__.py`, every tool module
and any `.json` data files, plus `entry_points.txt` in the `dist-info` folder (that creates the `tidymate` command).

### Test the wheel in a clean environment
Run this from a normal folder (**not** `C:\Windows\system32`):
```powershell
python -m venv test_env
.\test_env\Scripts\Activate.ps1
pip install (Get-ChildItem dist\*.whl).FullName
tidymate --help
tidymate doctor
tidymate explain svg
deactivate
Remove-Item -Recurse -Force test_env
```
*(macOS/Linux: `python3 -m venv test_env && . test_env/bin/activate`.)*
If PowerShell blocks `Activate.ps1`, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

### Upload
```powershell
python -m twine upload dist/*
```
At **Enter your API token:** right-click to paste your token (nothing appears on screen - that's normal) and
press <kbd>Enter</kbd>. Success ends with a `View at: https://pypi.org/project/tidymate/<version>/` line.

> **Optional dry run on TestPyPI:** `python -m twine upload --repository testpypi dist/*` with a **TestPyPI** token,
> then `pip install --index-url https://test.pypi.org/simple/ tidymate`. Skip it if you don't have a TestPyPI account.

---

## 4. Tag and publish the GitHub release

```powershell
git tag v1.0.2
git push origin v1.0.2
```

Then on GitHub: **Releases -> Draft a new release**, choose the tag, set the title (for example `TidyMate 1.0.2`),
write a few lines about what changed, and click **Publish release**.

Good release notes are short:
```text
## What's new
- Fixed X
- Added Y

Install or upgrade:  pip install --upgrade tidymate
```

---

## 5. After the release

Check it like a stranger would. In a **new** terminal:
```powershell
python -m venv fresh
.\fresh\Scripts\Activate.ps1
pip install --upgrade tidymate
tidymate --help
pip show tidymate
deactivate
Remove-Item -Recurse -Force fresh
```

Then open <https://pypi.org/project/tidymate/> and check:
- the version number is the new one,
- the banner, demo and images load,
- the links in the README open the right GitHub pages.

A new upload can take a minute or two to appear. If `pip` says "no matching distribution", wait and retry.

---

## 6. Optional: automatic publishing (no tokens)

**Trusted Publishing** lets GitHub publish to PyPI for you, so there is **no token to store or leak**.

### Set it up once
1. On PyPI open your project -> **Manage -> Publishing** -> **Add a new publisher** -> **GitHub**.
2. Fill in:
   | Field | Value |
   |---|---|
   | Owner | `Anand2k29` |
   | Repository name | `TidyMate` |
   | Workflow name | `publish.yml` |
   | Environment name | `pypi` |
3. Create `.github/workflows/publish.yml`:
   ```yaml
   name: Publish to PyPI

   on:
     release:
       types: [published]

   permissions:
     contents: read

   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with:
             python-version: "3.x"
         - run: python -m pip install build
         - run: python -m build
         - uses: actions/upload-artifact@v4
           with:
             name: dist
             path: dist/

     publish:
       needs: build
       runs-on: ubuntu-latest
       environment: pypi
       permissions:
         id-token: write      # required for Trusted Publishing
       steps:
         - uses: actions/download-artifact@v4
           with:
             name: dist
             path: dist/
         - uses: pypa/gh-action-pypi-publish@release/v1
   ```

### Releasing with it
1. Bump the version, commit and push (checklist above).
2. Tag it and publish a GitHub Release (section 4).
3. The workflow runs and uploads to PyPI. Watch it under the repo's **Actions** tab.

Once this works, you can delete your PyPI API token entirely.

---

## 7. Fixing a bad release

PyPI does not let you delete-and-reupload the same version, so:

- **Small mistake (typo, broken README link):** fix it, bump the patch version (`1.0.2` -> `1.0.3`) and release again.
- **A release that should not be installed:** **yank** it. On PyPI go to your project -> **Manage -> Releases ->** the
  version -> **Options -> Yank**. Yanked versions are skipped by `pip install tidymate` unless someone pins that exact
  version. Then release a fixed version.
- **Leaked token:** remove it immediately at <https://pypi.org/manage/account/#api-tokens>, create a new one, and check
  your project's release history for uploads you didn't make.

---

## 8. Troubleshooting

| Message or symptom | What it means and the fix |
|---|---|
| `Source ... does not appear to be a Python project: no pyproject.toml` | You're in the wrong folder (often `C:\Windows\system32`). `cd` into the project folder - `dir` should show `pyproject.toml`. |
| `403 Forbidden` / `Invalid or non-existent authentication information` | The token is wrong, incomplete, deleted, scoped to a different project, or from the wrong site (a pypi.org token does not work on test.pypi.org). Create a fresh one and paste it again. |
| `400 File already exists` | That version was already uploaded. Bump the version and rebuild. |
| `twine check` fails on the README | Fix the markdown it names and rebuild. |
| Installed package is missing files | Check `[tool.setuptools.packages.find]` and `[tool.setuptools.package-data]` in `pyproject.toml`, rebuild, and re-run the wheel listing in section 3. |
| Images are broken on the PyPI page | The images aren't on GitHub `main` yet. Push first, then re-check. If PyPI still shows the old page, release a new patch version - a PyPI page can't be edited after upload. |
| Can't paste the token | Right-click in the terminal, or Shift+Insert. Nothing is shown while pasting; press Enter afterwards. |
| `Activate.ps1 cannot be loaded` | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once. |
| `Access is denied` creating a virtual environment | You're in a protected folder such as `C:\Windows\system32`. Open the terminal in a normal folder. |
| Dependency-conflict warnings after `pip install build twine` | Harmless for publishing; they come from other packages in a shared conda environment. Use a fresh virtual environment to avoid them. |

---

*Questions or improvements? [Open an issue](https://github.com/Anand2k29/TidyMate/issues/new).*
