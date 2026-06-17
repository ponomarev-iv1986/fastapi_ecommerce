# FastAPI Ecommerce

Демонстрационное REST API интернет-магазина, реализованное на FastAPI с поддержкой JWT-аутентификации, ролей пользователей, управления товарами, категориями, корзиной, заказами и отзывами.

## Возможности

### Аутентификация и пользователи

* Регистрация пользователей.
* Авторизация по email и паролю.
* JWT Access Token.
* JWT Refresh Token.
* Обновление access и refresh токенов.
* Ролевая модель:

  * `buyer` — покупатель;
  * `seller` — продавец.

### Категории

* Создание категорий.
* Получение списка категорий.
* Обновление категорий.
* Мягкое удаление категорий.

### Товары

* Создание товара продавцом.
* Загрузка изображений товаров.
* Получение списка товаров.
* Фильтрация товаров:

  * по категории;
  * по продавцу;
  * по цене;
  * по наличию.
* Полнотекстовый поиск.
* Пагинация.
* Сортировка.
* Получение карточки товара.
* Обновление товара владельцем.
* Мягкое удаление товара.

### Отзывы

* Добавление отзывов к товарам.
* Получение списка отзывов.
* Управление отзывами.

### Корзина

* Добавление товаров в корзину.
* Просмотр содержимого корзины.
* Изменение количества товаров.
* Удаление товаров из корзины.

### Заказы

* Создание заказа из корзины.
* Просмотр заказов пользователя.
* Управление заказами.

---

## Технологический стек

### Backend

* FastAPI
* SQLAlchemy 2.0
* Alembic
* PostgreSQL
* AsyncPG
* Pydantic v2
* JWT (PyJWT)
* Passlib + BCrypt

### Дополнительно

* Uvicorn
* Python Multipart
* Dotenv

---

## Структура проекта

```text
fastapi_ecommerce/
│
├── app/
│   ├── models/          # SQLAlchemy модели
│   ├── routers/         # API маршруты
│   ├── schemas/         # Pydantic схемы
│   ├── migrations/      # Alembic миграции
│   ├── auth.py          # JWT и авторизация
│   ├── db.py            # Подключение БД
│   ├── config.py        # Настройки приложения
│   └── main.py          # Точка входа
│
├── media/
│   └── products/        # Изображения товаров
│
├── alembic.ini
├── requirements.txt
├── .env.example
└── README.md
```

---

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/ponomarev-iv1986/fastapi_ecommerce.git
cd fastapi_ecommerce
```

### 2. Создание виртуального окружения

Linux / macOS:

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

---

## Настройка окружения

Создайте файл `.env`:

```env
SECRET_KEY=your-secret-key

DATABASE_URL=postgresql+asyncpg://postgres:password@localhost/ecommerce
```

---

## Создание базы данных

Создайте базу PostgreSQL:

```sql
CREATE DATABASE ecommerce;
```

---

## Применение миграций

```bash
alembic upgrade head
```

---

## Запуск приложения

```bash
uvicorn app.main:app --reload
```

После запуска приложение будет доступно по адресу:

```text
http://127.0.0.1:8000
```

---

## Документация API

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## Основные эндпоинты

### Пользователи

| Метод | Endpoint               | Описание                      |
| ----- | ---------------------- | ----------------------------- |
| POST  | `/users/`              | Регистрация                   |
| POST  | `/users/token`         | Авторизация                   |
| POST  | `/users/refresh-token` | Обновление refresh token      |
| POST  | `/users/access-token`  | Получение нового access token |

### Товары

| Метод  | Endpoint         |
| ------ | ---------------- |
| GET    | `/products/`     |
| GET    | `/products/{id}` |
| POST   | `/products/`     |
| PUT    | `/products/{id}` |
| DELETE | `/products/{id}` |

### Категории

| Метод  | Endpoint           |
| ------ | ------------------ |
| GET    | `/categories/`     |
| POST   | `/categories/`     |
| PUT    | `/categories/{id}` |
| DELETE | `/categories/{id}` |

### Отзывы

| Метод | Endpoint                 |
| ----- | ------------------------ |
| GET   | `/products/{id}/reviews` |
| POST  | `/reviews/`              |

### Корзина

| Метод  | Endpoint     |
| ------ | ------------ |
| GET    | `/cart/`     |
| POST   | `/cart/`     |
| DELETE | `/cart/{id}` |

### Заказы

| Метод | Endpoint   |
| ----- | ---------- |
| GET   | `/orders/` |
| POST  | `/orders/` |

---

## Пример авторизации

Получение токена:

```http
POST /users/token
```

```json
{
  "username": "user@example.com",
  "password": "password"
}
```

Ответ:

```json
{
  "access_token": "jwt_token",
  "refresh_token": "jwt_refresh_token",
  "token_type": "bearer"
}
```

Использование:

```http
Authorization: Bearer <access_token>
```

---

## Загрузка изображений товаров

При создании товара можно передавать файл изображения через `multipart/form-data`.

Поддерживаемые форматы:

* JPG
* PNG
* WebP

Максимальный размер файла:

```text
2 MB
```

Файлы сохраняются в:

```text
media/products/
```

---

## Безопасность

* Хеширование паролей через BCrypt.
* JWT-аутентификация.
* Разделение прав доступа по ролям.
* Защита операций изменения товаров.
* Мягкое удаление сущностей.
