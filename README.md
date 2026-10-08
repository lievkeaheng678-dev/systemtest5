# Group 5: Administration & Identity Management
## ក្រុមទី ៥៖ ប្រព័ន្ធគ្រប់គ្រង និងការគ្រប់គ្រងអត្តសញ្ញាណ

Django project with PostgreSQL, covering:

1. **Django Admin Panel** customised in `accounts/admin.py` (users, groups, profiles, read-only audit log, dashboard statistics)
2. **User authentication**: register, login, logout, password change, and **group permissions**
3. **Sessions and view protection** with `@login_required` and `@permission_required`

## 1. Create the PostgreSQL database

Install PostgreSQL, then open `psql` (or pgAdmin) and run:
```sql
CREATE DATABASE identity_db;
```
The default connection is `postgres` / `postgres` on `localhost:5432`. To use other values, set environment variables
before running Django: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`.

Windows PowerShell example:
```powershell
$env:POSTGRES_PASSWORD = "your-password"
```
macOS/Linux example: `export POSTGRES_PASSWORD="your-password"`

## 2. Setup (with venv)

### Windows (PowerShell)
```powershell
cd identity_project
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations accounts
python manage.py migrate
python manage.py setup_groups
python manage.py createsuperuser
python manage.py runserver
```
If PowerShell blocks activation, run: `Set-ExecutionPolicy -Scope Process RemoteSigned`

### macOS / Linux
```bash
cd identity_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations accounts
python manage.py migrate
python manage.py setup_groups
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ (site) and http://127.0.0.1:8000/admin/ (admin panel).

## Groups created by `setup_groups`

| Group | Can do |
|---|---|
| Administrator | Manage users and groups, view audit log |
| Staff Manager | View/edit users, view audit log |
| Member | Default for new registrations; login-protected pages only |

To give someone admin-panel access: Admin > Users > tick **Staff status** and assign a group.

## Project structure
```
identity_project/
├── manage.py
├── requirements.txt
├── config/            settings.py, urls.py, wsgi.py, asgi.py
├── accounts/
│   ├── models.py      Profile, ActivityLog
│   ├── admin.py       customised Django admin
│   ├── forms.py       register / profile / login lock-out form
│   ├── views.py       @login_required and @permission_required views
│   ├── signals.py     auto-create Profile, audit login/logout/failures
│   └── management/commands/setup_groups.py
├── templates/         base, login, register, dashboard, users, logs, admin/index.html
├── static/css/style.css
└── docs/SECURITY_PLAN.md
```

## Key settings (config/settings.py)
- `SESSION_COOKIE_AGE = 1800` (30-minute idle timeout), `SESSION_EXPIRE_AT_BROWSER_CLOSE = True`
- `LOGIN_MAX_FAILED_ATTEMPTS = 5`, `LOGIN_LOCKOUT_MINUTES = 15`
- `LANGUAGES = English, Khmer` (language switcher in the top bar; Django admin is translated to Khmer automatically)
- Production: `set DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY=<random>`, `DJANGO_ALLOWED_HOSTS=yourdomain.com`

## Page protection summary

| URL | Protection |
|---|---|
| `/dashboard/`, `/profile/`, `/security-plan/` | `@login_required` |
| `/users/` | `@permission_required('auth.view_user')` |
| `/users/<id>/toggle/` | `@permission_required('auth.change_user')` + POST only |
| `/activity/` | `@permission_required('accounts.view_activitylog')` |

## Deploy on Render

1. Push the project to GitHub (include `build.sh`, `requirements.txt`; **do not** commit `venv/`).
2. In Render, open your **Web Service** > **Environment** and add:

| Key | Value |
|---|---|
| `DATABASE_URL` | the **Internal Database URL** from your Render PostgreSQL page (paste it whole) |
| `DJANGO_SECRET_KEY` | a long random string |
| `DJANGO_DEBUG` | `0` |
| `DJANGO_SUPERUSER_USERNAME` | your admin name (optional) |
| `DJANGO_SUPERUSER_EMAIL` | your email (optional) |
| `DJANGO_SUPERUSER_PASSWORD` | a strong password (optional) |

3. Web Service settings:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn config.wsgi:application`
4. Deploy. Then open `https://<your-service>.onrender.com/admin/`.

Do **not** put the full URL in `POSTGRES_HOST`; use `DATABASE_URL` only.
The web service and database must be in the same Render region for the Internal URL to work.
"# systemtest5" 
