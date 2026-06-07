# GFC Nepal Django + GeoDjango

This is a Django + GeoDjango structure for the previous Flask `app.py` features.

## Features Included

- GFC Nepal Home, Services, About, Contact pages
- Logo and auto-changing natural photo background
- Nepali / English one-click text toggle
- Services-only tool entry points
- One-time Codepass / Token system
- Token usage log: who used the token, email, IP and date
- Work history: latest work first
- Delete to Recycle Bin
- Recycle Bin older than 30 days moves to Admin Recycle Bin
- Recycle Bin delete moves to Admin Recycle Bin, not permanent delete
- Admin control dashboard
- Promo code system for all users or limited users
- GeoDjango models:
  - `ForestArea` with `MultiPolygonField`
  - `ServiceLocation` with `PointField`

## Run Locally

```powershell
cd gfc_geodjango
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:

- Site: http://127.0.0.1:8000/
- Admin dashboard: http://127.0.0.1:8000/control/
- Django admin: http://127.0.0.1:8000/admin/

## PostGIS / GeoDjango

GeoDjango needs a spatial database. Create a PostGIS database and set:

```powershell
$env:POSTGIS_DB="gfc_db"
$env:POSTGIS_USER="postgres"
$env:POSTGIS_PASSWORD="your-password"
$env:POSTGIS_HOST="localhost"
$env:POSTGIS_PORT="5432"
```

Then run migrations again.

For quick UI-only experiments without geometry migrations, you can set `USE_SQLITE=1`, but real GeoDjango map fields should use PostGIS.

## 30-Day Recycle Bin Cleanup

Run manually or schedule daily:

```powershell
python manage.py cleanup_recycle_bin
```

## Important Next Step

The old Flask app contains a large pandas/XLSX report generator. This Django version has the correct token gate and work-history flow. The report-generation functions from `app.py` can now be moved into a `portal/reports.py` file and called inside `tool_view`.
