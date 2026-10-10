# Publishing TidyMate (for maintainers)

Do this once. After it, anyone can install with `pip install tidymate` or the one-line installer.

## 1. Put the code on GitHub

Upload the **contents of the `tidymate` folder** (the folder that contains `pyproject.toml`).
`pyproject.toml` must be at the top level of the repository.

**Upload:** everything in that folder, including the hidden `.github` and `.gitignore`.

**Do not upload:** `dist/`, `build/`, `__pycache__/`, `*.egg-info/`, `.organizer_logs/`,
`last_error.txt`, or any `.zip` file. The included `.gitignore` already excludes them.

### Recommended: git on the command line (keeps `.github` and file permissions)

1. On github.com click **New repository**, name it `tidymate`, leave it **empty** (no README), click **Create**.
2. In a terminal, inside the `tidymate` folder:

```bash
git init
git add .
git commit -m "TidyMate 1.0.0"
git branch -M main
git remote add origin https://github.com/YOUR-GITHUB-USER/tidymate.git
git push -u origin main
```

> Browser drag-and-drop upload also works, but it can skip hidden folders such as `.github`.
> If you use it, check afterwards that `.github/workflows/` appears in the repository.
> GitHub Desktop is another easy option.

## 2. Replace the placeholder

The files contain `YOUR-GITHUB-USER`. Replace it with your real GitHub username:

- **Mac / Linux:** `grep -rl YOUR-GITHUB-USER . | xargs sed -i 's/YOUR-GITHUB-USER/your-real-username/g'`
  (on macOS use `sed -i ''`)
- **Windows (PowerShell):**
  ```powershell
  Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch '\\\.git\\' } | ForEach-Object {
      (Get-Content $_.FullName -Raw) -replace 'YOUR-GITHUB-USER','your-real-username' | Set-Content $_.FullName -NoNewline
  }
  ```

Files affected: `README.md`, `pyproject.toml`, `install.sh`, `install.ps1`.
Then commit and push:

```bash
git add . && git commit -m "Set GitHub username" && git push
```

The one-line installers now work (the repository must be **public**).

## 3. Publish to PyPI (makes `pip install tidymate` work)

1. Create an account at <https://pypi.org> and turn on two-factor authentication.
2. Add a **trusted publisher**: pypi.org -> *Your account* -> *Publishing* -> *Add a new pending publisher*
   - PyPI project name: `tidymate`
   - Owner: your GitHub username - Repository: `tidymate`
   - Workflow name: `publish.yml` - Environment name: `pypi`
3. On GitHub: **Releases -> Draft a new release**, tag `v1.0.0`, click **Publish release**.
   The `publish` workflow builds the package and uploads it. No passwords or tokens needed.
4. Check <https://pypi.org/project/tidymate/>, then try `pip install tidymate` on a clean machine.

**Manual alternative** (no GitHub Action):

```bash
python -m pip install build twine
python -m build
twine upload dist/*
```

> The name `tidymate` was unused on PyPI when this was written. A name is only yours once you publish.

## 4. Releasing a new version

1. Change the version in **both** `pyproject.toml` and `tidymate/__init__.py`.
2. Run the tests: `python -m unittest discover -s tests -v`
3. Commit, push, then create a new GitHub Release with a tag such as `v1.0.1`.

PyPI never accepts the same version twice, so always bump the number.

## 5. Optional extras

- **Badges** in the README start working after the first PyPI release and the first passing test run.
- **Social preview / screenshot:** record a short terminal GIF (e.g. with
  [asciinema](https://asciinema.org) or [VHS](https://github.com/charmbracelet/vhs)) and add it to
  the top of the README.
- **Topics:** on the repository page add topics like `file-organizer`, `cli`, `python`, `productivity`.
