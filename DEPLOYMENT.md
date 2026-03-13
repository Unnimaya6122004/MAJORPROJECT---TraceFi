# TraceFi Deployment Guide

This project can be deployed for free on PythonAnywhere and used with the local Chrome extension.

## 1. Prepare the project locally

Make sure these files and folders are included in your repository:

- `app.py`
- `requirements.txt`
- `templates/`
- `static/`
- `model/`
- `tracefi-extension/`

Install dependencies and test locally:

```powershell
pip install -r requirements.txt
python app.py
```

Open:

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/dashboard`

## 2. Push the project to GitHub

Create a GitHub repository and push this project.

Example:

```powershell
git init
git add .
git commit -m "Prepare TraceFi for deployment"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

## 3. Create a free PythonAnywhere account

1. Sign in to PythonAnywhere.
2. Open a Bash console.

## 4. Clone the repository on PythonAnywhere

```bash
git clone <your-github-repo-url>
cd TRACEFI
```

## 5. Create a virtual environment and install packages

Use the Python version available in your PythonAnywhere account.

```bash
mkvirtualenv --python=/usr/bin/python3.10 tracefi-env
pip install -r requirements.txt
```

If `mkvirtualenv` is unavailable, use:

```bash
python3.10 -m venv ~/.virtualenvs/tracefi-env
source ~/.virtualenvs/tracefi-env/bin/activate
pip install -r requirements.txt
```

## 6. Create the web app

1. Go to the `Web` tab.
2. Click `Add a new web app`.
3. Choose your free domain, for example:
   `yourusername.pythonanywhere.com`
4. Choose `Manual configuration`.
5. Select the same Python version used for the virtualenv.

## 7. Configure the web app paths

Set these values in the `Web` tab:

- Source code:
  `/home/yourusername/TRACEFI`
- Working directory:
  `/home/yourusername/TRACEFI`
- Virtualenv:
  `/home/yourusername/.virtualenvs/tracefi-env`

Adjust `TRACEFI` if your repository folder name is different.

## 8. Update the WSGI file

Open the WSGI configuration file from the `Web` tab and replace its contents with:

```python
import sys

project_home = "/home/yourusername/TRACEFI"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import app as application
```

Replace `yourusername` with your PythonAnywhere username.

## 9. Reload the app

Click `Reload` in the `Web` tab, then open:

```text
https://yourusername.pythonanywhere.com
```

## 10. Update the Chrome extension backend URL

After deployment, edit:

- `tracefi-extension/popup.js`

Change:

```javascript
const BACKEND_URL = "http://127.0.0.1:5000";
```

to:

```javascript
const BACKEND_URL = "https://yourusername.pythonanywhere.com";
```

## 11. Load the extension locally

1. Open `chrome://extensions`
2. Turn on `Developer mode`
3. Click `Load unpacked`
4. Select the `tracefi-extension` folder

## 12. Recommended production follow-ups

These are not required for the free deployment, but they will help:

1. Replace `/simulate` with real live data ingestion.
2. Persist `attack_logs` in a database or file instead of memory.
3. Add `host_permissions` and a background worker to the extension for real-time status polling.
4. Add authentication before exposing the dashboard publicly.

## Troubleshooting

### Module not found

Re-open the PythonAnywhere Bash console, activate the virtualenv, and run:

```bash
pip install -r requirements.txt
```

### App reloads but gives an error page

Check the PythonAnywhere error log from the `Web` tab.

### Extension still points to localhost

Make sure `tracefi-extension/popup.js` uses your deployed HTTPS URL and then reload the extension in Chrome.
