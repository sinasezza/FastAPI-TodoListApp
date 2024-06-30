# FastAPI-TodoListApp

a simple todolist app endpoints and templates written using fast api, pydantic, sqlalchemy and alembic

## Required Software

Ensure you have the following software installed:

- [Python 3.10](https://www.python.org/downloads/) or newer
- [Node.js 18.15 LTS](https://nodejs.org/) or newer (required for Tailwind CSS)
- [Git](https://git-scm.com/)

## Get Started

### Get The Repository

```bash
https://github.com/sinasezza/FastAPI-TodoListApp.git
cd FastAPI-TodoListApp
```

### Configure Environment

#### macOS/Linux Users

```bash
python manage.py -m venv venv
source ./venv/bin/activate
pip install uv
uv pip install -r requirements.txt --upgrade
```

#### Windows Users

```bash
python manage.py -m venv venv
venv\scripts\activate
pip install uv
uv pip install -r requirements.txt --upgrade
```

### Configure and Run TailwindCss

in another terminal, run the tailwind dev:

```bash
cd frontend_tailwind
npm run dev
```

### Configure Environment Variables

Create `.env` file on the backend directory and use following content:

- dotenv is used to hide sensitive information like database password from public access.

- you can use .samples as template for your own environment variables.

- rename the .env.sample file to '.env' and configure it as you wish.

### Run The fastapi Server

```bash
uvicorn backend.main:app --reload
```
