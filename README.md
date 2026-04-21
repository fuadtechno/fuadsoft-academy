# School Management System

A production-ready, scalable School Management System built with Django and Django REST Framework.

## Features

- **User Management**: Custom user model with RBAC (Admin, Teacher, Student roles)
- **Student Management**: Add, update, delete students with profile management
- **Teacher Management**: Teacher profiles with qualifications
- **Class & Subject Management**: Create classes, sections, subjects
- **Attendance System**: Daily attendance marking with reports
- **Exams & Results**: Create exams, add marks, generate report cards
- **Fees Management**: Fee structures, payments, dues tracking
- **Notifications**: Announcements and email notifications
- **RESTful APIs**: Full API with JWT authentication

## Tech Stack

- Django 5.2+
- Django REST Framework
- PostgreSQL (production) / SQLite (development)
- Bootstrap 5
- JWT Authentication

## Installation

### Requirements

- Python 3.13+
- PostgreSQL 15+ (optional, for production)

### Setup

1. Clone the repository:
```bash
git clone <repo-url>
cd django-project
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
copy .env.example .env
# Edit .env with your settings
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

Access the admin panel at `http://localhost:8000/admin/`

## Docker Deployment

```bash
docker-compose up --build
```

## API Endpoints

- `POST /api/auth/token/` - Obtain JWT token
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/students/` - List students
- `GET /api/teachers/` - List teachers
- `GET /api/attendance/` - List attendance
- `GET /api/exams/` - List exams

## Project Structure

```
school_project/
├── accounts/          # User authentication and profiles
├── students/         # Student management
├── teachers/         # Teacher management
├── classes/         # Class, Section, Subject management
├── attendance/      # Attendance tracking
├── exams/           # Exams and Results
├── fees/            # Fee management
├── notifications/   # Announcements
├── api/             # REST API
├── templates/      # HTML templates
└── school_project/ # Django settings
```

## License

MIT License