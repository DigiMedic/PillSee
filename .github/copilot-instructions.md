---
description: AI rules derived by SpecStory from the project AI interaction history
globs: *
---

## HEADERS

## TECH STACK

## PROJECT DOCUMENTATION & CONTEXT SYSTEM

## CODING STANDARDS

## WORKFLOW & RELEASE RULES

When pushing changes to a shared repository, especially when needing to overwrite the existing content, use the following steps:

1.  **Initialize Git:**
    ```bash
    cd /path/to/your/project
    git init
    git add .
    git commit -m "Initial commit"
    ```
2.  **Connect to Remote Repository:**
    ```bash
    git remote add origin <repository_url>
    git fetch origin
    git checkout -b <branch_name>
    ```
3.  **Overwrite Content (Use with Caution):**
    ```bash
    git push origin <branch_name> --force
    ```
    **Warning:** Using `--force` will overwrite all existing files in the specified branch. Ensure you have a backup if necessary.

A safer approach involves cloning the repository first:

```bash
git clone <repository_url> temp_directory
cd temp_directory
git checkout <branch_name>
# Delete all files except .git
find . -not -path './.git/*' -not -name '.git' -delete
# Copy your project files
cp -r /path/to/your/project/* .
cp -r /path/to/your/project/.[^.]* . 2>/dev/null || true
git add .
git commit -m "Replace project with new implementation"
git push origin <branch_name>
```

When encountering the error "'directory' does not have a commit checked out" during `git add .`, it usually indicates a nested Git repository. Resolve it using one of the following methods:

1.  **Remove the nested Git repository:**
    ```bash
    rm -rf directory/.git
    git add .
    git commit -m "Initial commit"
    ```
2.  **Clean up submodules:**
    ```bash
    rm .gitmodules
    git rm --cached directory
    find . -name ".git" -type d -exec rm -rf {} +
    git add .
    git commit -m "Initial commit"
    ```
3.  **Add as a submodule (if you intend to keep it separate):**
    ```bash
    git submodule add <URL_BACKEND_REPO> directory
    git add .
    git commit -m "Add directory as submodule"
    ```

To completely remove connections to other repositories, ensure only the desired remote repository is connected:

1.  Verify no nested `.git` directories exist (except the root).
2.  Confirm that `.gitmodules` does not exist.
3.  Ensure only one remote is configured, pointing to the desired repository.

To set the upstream tracking for a branch:

```bash
git push -u origin <branch_name>
# or
git branch --set-upstream-to=origin/<branch_name> <branch_name>
```

It is recommended to normalize end-of-line (EOL) characters using `.gitattributes`:

```
*.csv text eol=lf
*.py  text eol=lf
*.ts  text eol=lf
*.tsx text eol=lf
*.json text eol=lf
*.sh text eol=lf
```

## DEBUGGING

When encountering a `ModuleNotFoundError` for `chardet`, follow these steps:

1.  **Activate the virtual environment:**
    ```bash
    cd /path/to/your/project/backend
    source venv/bin/activate
    ```
2.  **Verify the Python and pip versions:**
    ```bash
    which python
    which pip
    python -V
    ```
3.  **Install `chardet`:**
    ```bash
    python -m pip install chardet==5.2.0
    ```
4.  **Verify the installation:**
    ```bash
    python -c "import chardet; print('chardet', chardet.__version__)"
    ```
5.  **Add `chardet` to `requirements.txt`:**
    ```text
    # ...existing code...
    chardet==5.2.0
    # ...existing code...
    ```
6.  If the import still fails, check for `PYTHONPATH` interference or conflicting `chardet.py` files. In VS Code, select the correct interpreter (`venv/bin/python`).
7.  If a `pyproject.toml` specifies a `requires-python` version, ensure the virtual environment uses a compatible Python version.

## BEST PRACTICES

When force-pushing, create a backup of the original repo.