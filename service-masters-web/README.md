# Service Masters — Web Frontend

Master portal for the Service Masters marketplace (Uzbekistan).

See the [root README](../README.md) for backend setup, `seed_demo`, and full run steps.

## Stack

- React 19 + Vite + TypeScript
- Tailwind CSS 4 (design tokens from Stitch)
- React Router 7
- Zustand (auth)
- Axios + JWT refresh
- i18next (ru / en / uz)

## Screens

| Route | Description |
|-------|-------------|
| `/login` | Phone + password → JWT (protected routes redirect here) |
| `/orders` | List — number, title, client_name, address, price, status |
| `/orders/:id` | Detail + status advance |
| `/orders/:id/photos` | Before / After FormData upload |
| `/orders/:id/report` | Report submit → status `completed` |
| `/schedule` | Agenda placeholder |
| `/earnings` | Stats + payout UI |
| `/profile` | Profile, language, logout |

## Run

```bash
# Backend first (from repo root / django_app):
#   pip install -r requirements.txt
#   python manage.py migrate
#   python manage.py seed_demo
#   python manage.py runserver

npm install
cp .env.example .env   # VITE_API_URL=http://localhost:8000/api
npm run dev
```

Open http://localhost:3000

### Demo login

| Role   | Phone         | Password  |
|--------|---------------|-----------|
| Master | +998902000001 | Demo1234! |
| Client | +998901000001 | Demo1234! |

### Checklist

1. Log in as master
2. Orders list shows seeded API fields + status badges
3. Open order → upload photos → submit report → completed
