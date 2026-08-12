# My First Project

A beginner-friendly Python workspace with a CLI greeting, a hydropower capacity calculator, and a simple GUI project estimator.

## Project contents

- `hello.py` - a greeting example that works with or without command-line input
- `power_calc.py` - hydropower capacity calculator with both interactive and CLI modes
- `app.py` - command-line greeting app with a friendly default name
- `README.md` - project overview and usage instructions
- `.gitignore` - excludes Python caches, environment files, and secrets

## Usage

Run the greeting app:

```powershell
python .\app.py --name Lenovo
```

Run the simple hello example:

```powershell
python .\hello.py
```

Run the hydropower calculator in CLI mode:

```powershell
python .\power_calc.py --flow 12 --head 80 --efficiency 0.85
```

Or run the calculator interactively:

```powershell
python .\power_calc.py
```

## Tests

A small test suite is included for the hydropower calculator.

```powershell
python -m pytest
```

## GitHub publishing

This repository is ready to be pushed to GitHub. Once you have created a public repository named `my-first-project`, run:

```powershell
git remote add origin https://github.com/<your-username>/my-first-project.git
git push -u origin main
```

## What this project demonstrates

- use of Python functions and modules
- a command-line interface with `argparse`
- basic test coverage using pytest
- a documented GitHub-friendly project structure

## Learning path

As you grow toward AI integration and architecture roles, keep building and publishing small projects like this one. Add documentation for each project, and show how it integrates services or solves a real problem.
