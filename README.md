# Service Marketplace

Django REST API + React master portal for home services in Tashkent.

## Structure

| Path | Description |
|------|-------------|
| `django_app/` | DRF backend (users, masters, orders) |
| `service-masters-web/` | Vite + React master portal |

## Demo accounts

Password for all seeded users: **`Demo1234!`**

| Role   | Phone           |
|--------|-----------------|
| Master | `+998902000001` … `+998902000010` |
| Client | `+998901000001` … `+998901000010` |

Primary test master: `+998902000001` / `Demo1234!`

## Backend setup

```bash
cd django_app
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

API base: `http://localhost:8000/api`

Re-running `seed_demo` is safe (idempotent). Optional wipe:

```bash
python manage.py seed_demo --clear
```

### Useful API routes

```
POST   /api/users/token/              # phone + password → JWT
POST   /api/users/token/refresh/
GET    /api/users/me/
GET    /api/orders/
GET    /api/orders/:id/
PATCH  /api/orders/:id/status/
POST   /api/orders/:id/photos/        # multipart FormData (image, kind)
POST   /api/orders/:id/report/
```

## Frontend setup

```bash
cd service-masters-web
npm install
cp .env.example .env   # VITE_API_URL=http://localhost:8000/api
npm run dev
```

Open http://localhost:3000

Backend CORS already allows `localhost:3000` and `5173`.

### Master flow checklist

1. Log in as `+998902000001` / `Demo1234!`
2. Open `/orders` — seeded jobs with real number, title, client, address, price, status
3. Open an order → advance status (Accept → En Route → On Site → In Progress)
4. Upload before/after photos
5. Submit report → order moves to **completed**

## Seed contents

`python manage.py seed_demo` creates:

- 10 service categories, 10 Tashkent districts (cities)
- 10 clients, 10 masters + MasterProfiles (rating 4.2–5.0)
- 10+ orders with mixed statuses (`new` … `completed`)
- OrderPhoto (before/after), OrderReport, OrderReview samples
