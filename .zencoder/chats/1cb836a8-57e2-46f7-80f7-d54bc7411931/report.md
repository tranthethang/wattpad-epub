# Implementation Report - Update README

## What was implemented
- Updated `README.md` to reflect the latest CLI command parameters and features.
- Added details about the new `--input`, `--output`, `--title`, `--author`, and `--cover` options for the `convert` command.
- Mentioned that the `download` command now automatically skips already downloaded chapters.
- Documented shortcut options like `-o`, `-i`, `-t`, `-a`, and `-c`.
- Updated the "Project Structure" section to include the `logs/` directory and details about `main.py` commands.

## How the solution was tested
- Manually verified the command parameters against the source code in `src/main.py`.
- Checked the generated `README.md` for accuracy and formatting.

## The biggest issues or challenges encountered
- Ensuring all new shortcuts and default values in `src/main.py` were correctly documented in the `README.md`.
