# Lahore Car Rental API

A Django REST Framework API for managing car rental bookings in Lahore.

## Features

- **User Authentication**: JWT-based authentication with registration and login
- **API Documentation**: Swagger/OpenAPI documentation
- **Comprehensive Testing**: Unit tests for models, serializers, and views

## Tech Stack

- **Backend**: Django 5.2.4, Django REST Framework
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Database**: SQLite (development)
- **Testing**: Django's built-in testing framework

## API Endpoints

### Authentication
- `POST /register/` - User registration
- `POST /login/` - User login (JWT token)

### Documentation
- `/swagger/` - Swagger UI
- `/redoc/` - ReDoc documentation

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ahsan-007/lahore-car-rental.git
   cd lahore-car-rental
   ```

2. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   cd lahore_car_rental
   python manage.py migrate
   ```

5. Create superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. Run development server:
   ```bash
   python manage.py runserver
   ```

7. Access the API:
   - API Root: http://localhost:8000/
   - Swagger Documentation: http://localhost:8000/swagger/
   - Admin Panel: http://localhost:8000/admin/


## Testing

Run tests:
```bash
python manage.py test
```

Run specific app tests:
```bash
python manage.py test authentication
```


### Security
- JWT-based authentication
- User-specific data access
- Input validation and sanitization

## Development


### Testing Strategy
- Unit tests for models, serializers, and views
- Integration tests for API workflows
- Edge case testing for business logic
