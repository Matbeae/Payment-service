# Асинхронное веб-приложение (Backend, Python)

## Описание проекта
Это асинхронное веб-приложение, реализующее REST API для работы с пользователями, администраторами, счетами и платежами. 
Проект включает следующие функциональности:
- Авторизация и управление пользователями
- Управление счетами и балансами
- Обработка платежей через вебхук

## Стек технологий

- **Python 3.12**
- **Sanic** (для реализации REST API)
- **SQLAlchemy** (для работы с базой данных PostgreSQL)
- **PostgreSQL** (в качестве базы данных)
- **Docker Compose** (для упрощенного развертывания)

## Сущности

1. **Пользователь**:
   - Авторизация по email/password.
   - Получение данных о себе (id, email, full_name).
   - Получение списка счетов и балансов.
   - Получение списка своих платежей.

2. **Администратор**:
   - Авторизация по email/password.
   - Получение данных о себе (id, email, full_name).
   - Создание, удаление и обновление пользователей.
   - Получение списка пользователей с их счетами и балансами.

3. **Счет**:
   - Привязан к пользователю и имеет баланс.

4. **Платеж**:
   - Содержит уникальный идентификатор транзакции и сумму пополнения счета.

5. **Webhook для обработки платежей**:
   - Платежи обрабатываются через вебхук, который проверяет подпись и начисляет средства на счет пользователя.
## Развертывание

### Docker Compose

1. Убедитесь, что на вашем компьютере установлен [Docker](https://www.docker.com/get-started) и [Docker Compose](https://docs.docker.com/compose/).
2. Клонируйте репозиторий:
3. Сборка и запуск контейнеров:

```bash
docker-compose up --build
```

4. После сборки и запуска, приложение будет доступно на [http://localhost:8000](http://localhost:8000).

5. Миграции данных и создание тестовых пользователей произойдут автоматически при старте приложения.
## Тестовые данные

После развертывания, в миграциях создаются следующие тестовые пользователи и счета:

* **Тестовый пользователь**:

  * Email: `user@example.com`
  * Пароль: `userpass`

* **Тестовый администратор**:

  * Email: `admin@example.com`
  * Пароль: `adminpass`

## Примеры запросов

### Авторизация (POST `/auth/login`):
**HTTP метод**: `POST`

**URL**: `http://localhost:8000/auth/login`

**Тело запроса (Body)**:

* Выберите тип **raw** и **JSON**.
* Введите следующий JSON:

```json
{
  "email": "user@example.com",
  "password": "userpass"
}
```

**Результат**:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzU4Mjk3Mzc0fQ.Sn0R1ERntlsyE9Y3sdKLAeXkM7135Fk0i88J7gmfwOs",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "full_name": "Test User"
    }
}
```
### Получение данных о пользователе (GET `/user/me`):
**HTTP метод**: `GET`

**URL**: `http://localhost:8000/user/me`

**Заголовок**:

* Название заголовка: `Authorization`
* Значение: `Bearer <YOUR_ACCESS_TOKEN>`, где `<YOUR_ACCESS_TOKEN>` — это токен, полученный на предыдущем шаге.

**Результат**:

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe"
}
```
### Получение списка счетов пользователя (GET `/user/accounts`)
**HTTP метод**: `GET`

**URL**: `http://localhost:8000/user/accounts`

**Заголовок**:

* Название заголовка: `Authorization`
* Значение: `Bearer <YOUR_ACCESS_TOKEN>`

**Результат**:

```json
{
    "accounts": [
        {
            "id": 1,
            "balance": 100.0
        }
    ]
}
```
### Получение списка пользователей (для админа) (GET `/admin/users`):
**HTTP метод**: `GET`

**URL**: `http://localhost:8000/admin/users`

**Заголовок**:

* Название заголовка: `Authorization`
* Значение: `Bearer <YOUR_ADMIN_ACCESS_TOKEN>`

**Результат**:
```json
{
    "users": [
        {
            "id": 1,
            "email": "user@example.com",
            "full_name": "Test User",
            "accounts": [
                {
                    "id": 1,
                    "balance": 100.0
                }
            ]
        },
        {
            "id": 2,
            "email": "admin@example.com",
            "full_name": "Admin User",
            "accounts": []
        }
    ]
}
```

### Обработка платежа (POST `/webhook/payment`):
**HTTP метод**: `POST`

**URL**: `http://localhost:8000/webhook/payment`

**Тело запроса (Body)**:

* Выберите тип **raw** и **JSON**.
* Введите следующий JSON:

```json
{
  "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
  "user_id": 1,
  "account_id": 1,
  "amount": 100,
  "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
}
```
**Результат**:

```json
{
  "status": "ok"
}
```






