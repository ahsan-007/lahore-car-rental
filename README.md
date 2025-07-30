# Lahore Car Rental API

A Django REST Framework API for managing car rental bookings in Lahore.

## Features

- **User Authentication**: JWT-based authentication with registration and login
- **Vehicle Management**: CRUD operations for vehicles with user ownership
- **Booking System**: Create and manage car rental bookings
- **Filtering**: Filter vehicles by make and/or year, Filter bookings by from_date and/or to_date
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

### Vehicles
- `GET /vehicles/` - List user's vehicles (with filtering)
- `POST /vehicles/` - Create new vehicle
- `GET /vehicles/{id}/` - Get vehicle details
- `PUT /vehicles/{id}/` - Update vehicle
- `DELETE /vehicles/{id}/` - Delete vehicle

### Bookings
- `GET /bookings/` - List user's bookings (with date filtering)
- `POST /bookings/` - Create new booking

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
python manage.py test vehicles
python manage.py test bookings
```

## Features Detail

### Business Logic
- **Booking Validation**: Prevents overlapping bookings for the same vehicle
- **Date Validation**: Ensures bookings are at least 1 hour in the future
- **Duration Limits**: Minimum 1 hour, maximum 30 days
- **User Isolation**: Users can only see and manage their own vehicles and bookings

### Security
- JWT-based authentication
- User-specific data access
- Input validation using bulti-in and custom validators

## Development


### Testing Strategy
- Unit tests for models, serializers, and views
- Integration tests for API workflows
- Edge case testing for business logic
