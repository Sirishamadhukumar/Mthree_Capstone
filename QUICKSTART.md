# Run the Meridian Support Assistant

## Windows
1. Extract this zip to a writable folder.
2. Install Python 3.11 or newer and ensure `python` is on PATH.
3. Double-click `run.bat`. It creates a virtual environment, installs the two small core dependencies, and starts the offline demo.

## macOS / Linux
From this folder run `bash run.sh`.

## Run manually
Install `requirements-minimal.txt`, then run `python assignments/capstone/app.py --demo`. No API key, `.env` file, hosted model, or cloud service is required. The complete training dependencies are listed in `requirements.txt`. To run the public capstone checks, use `python -m autograde.run --capstone --root . -v`. To simulate an outage, set `GAMEDAY_FAULT=tool_outage` before running the demo; it will print a degraded handover.

This is a fictional-bank training project. Backends and account data are synthetic, and it must not be connected to real customer or financial systems.
