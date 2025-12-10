# ER-Prioritization

Emergency Room (ER) Prioritization — a small Flask-based prototype that demonstrates simple triage/prioritization logic for emergency cases. The app provides a web UI and an API for assigning priority to incoming emergency reports and storing them in a local SQLite database.

> **Note:** This README is written for the repository layout that contains `app.py`, `triage.py`, `emergency.db`, `templates/`, `static/`, and `requirements.txt`.

---

## Features

* Flask web server with a lightweight web UI (templates + static assets).
* Triage logic contained in `triage.py` (scoring/rules for assigning priority).
* Persistence using a local SQLite database (`emergency.db`).
* Example tests (if present) and a `requirements.txt` for dependencies.

---

## Quickstart (Development)

### Prerequisites

* Python 3.8+ installed
* `pip` available

### Install

1. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate    # macOS / Linux
venv\Scripts\activate     # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Run the app

```bash
python app.py
```

By default the Flask app runs on `http://127.0.0.1:5000/`. Open that in your browser to see the UI.

---

## Project structure

```
ER-Prioritization/
├─ app.py            # Flask app entrypoint (routes, server startup)
├─ triage.py         # Triage/priority logic and helper functions
├─ requirements.txt  # Python dependencies
├─ emergency.db      # SQLite database (sample data)
├─ templates/        # HTML templates for web UI
├─ static/           # CSS, JS, images
└─ database/         # optional DB helpers / migrations
```

---

## How it works

* `app.py` exposes HTTP endpoints used by the UI and/or external clients.
* `triage.py` contains the rules or scoring mechanism that converts an incoming emergency report (symptoms, vitals, keywords) into a priority score or category (e.g., High / Medium / Low).
* When a new emergency is submitted, the server validates the request, calls the triage logic, stores the record in `emergency.db`, and returns the assigned priority.

---

## API (example)

> These are example endpoints — verify exact paths and payloads by opening `app.py`.

### Submit a new emergency

```http
POST /submit
Content-Type: application/json

{ "name": "John Doe", "age": 45, "symptoms": "chest pain, sweating", "vitals": {"bp": "140/90", "pulse": 110} }
```

Response:

```json
{ "id": 12, "priority": "High", "score": 87 }
```

### List all emergencies

```http
GET /emergencies
```

---

## Tests

If tests are included (for example `test_hf.py`), run them with `pytest`:

```bash
pip install pytest
pytest
```

---

## Extending & Contributing

* Improve triage rules in `triage.py` (add weightings, ML model integration, unit tests).
* Replace SQLite with a production DB (Postgres, MySQL) and add migrations.
* Harden input validation and error handling in `app.py`.
* Add Dockerfile & CI (GitHub Actions) for reproducible deployments.

If you'd like, open a PR with a clear description of changes. Keep commits small and tests green.

---

## Security & privacy

This repo may store sensitive demo data in `emergency.db`. Remove or sanitize any real personal data before sharing. If deploying publicly, add proper authentication, input sanitization, and secure storage.

---

## License

Specify a license (e.g., MIT) by adding a `LICENSE` file. If you want, I can add an MIT license text to the repo for you.

---

## Contact / Author

Repository: `9rakrit/ER-Prioritization` — reach out via GitHub issues or PRs for questions or feature requests.

---

*Generated README — tell me if you want me to tweak the wording, add badges, or create a `LICENSE` file.*
