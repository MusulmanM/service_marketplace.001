# Service Marketplace (Django)

Рабочий каркас маркетплейса услуг на Django.
База — **SQLite** (файл `db.sqlite3`), PostgreSQL не нужен.

## Структура

```
django_app/
├── config/          # настройки
├── users/           # User, UserProfile, UserOTP (телефон + OTP)
├── masters/         # MasterProfile, ServiceCategory, MasterService
├── orders/          # Order, OrderStatusHistory
├── manage.py
└── requirements.txt
```

## Запуск в VS Code (Windows)

```bash
cd django_app

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Админка: http://127.0.0.1:8000/admin/

При `createsuperuser` логин = **номер телефона** (например `+998901234567`).

## Модели

- **User** — кастомный пользователь (телефон = логин, UUID, роли CLIENT/MASTER/ADMIN)
- **UserProfile** — профиль
- **UserOTP** — одноразовые коды
- **MasterProfile** — профиль мастера
- **ServiceCategory / MasterService** — услуги
- **Order** — заказы + история статусов
