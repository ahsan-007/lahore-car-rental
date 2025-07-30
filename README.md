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


## Assumptions
- Booking must be for at least 1 hour.
- Booking must be for 30 days at max.
- User can book multiple vehicles even for same start and end dates
- Users can see any vehicle details
- Vehicle year should be between 1950  to Current Year + 1
- A user should be able to see detail of any vehicle usinge GET /vehicles/{id} in order to see the details of the vehicle that the user booked.
- User should be able to see list of vehicles that are available in fleet of other users by using user_id query parameter in order to see fleet of a specific owner.


## About 1Now
#### What 1Now does?
1Now offers a platform empowering private rentals for car owners on Turo. Owners can take 1Now subscription and 1Now will create a new website for each owner. Owners can use that website to take  private rental orders. Owners also get access to multiple features like expense tracking, fleet management and so on.
	
#### Who it serves
It servers car owners that are making money by renting out thier cars
	
##### How your backend could connect to the frontend of LahoreCarRental.com
- Vehicle Management can be used for fleet management. It can also be used by other users to see details of a car they booked or list of detail of cars that are available in the fleet of a specific owner.
- Booking Management can be used by people to book cars.

## API Usage Examples

### Authentication

#### Register a new user:
Request
```bash
curl -X 'POST' \
  'http://localhost:8000/register/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "ali",
  "email": "ali@gmail.com",
  "password": "Password248",
  "password2": "Password248"
}'
```
Response
```
{
  "message": "User registered successfully",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzOTgxNjY1LCJpYXQiOjE3NTM4OTUyNjUsImp0aSI6IjA5ZGY0MGJkN2VlMzQ2ODJiZjBhNjIzOTlhYmFiY2NjIiwidXNlcl9pZCI6IjUifQ.XMaiDce6bkryD6mWYrHyV9kKrimJURg-kqTnv6MFxIg",
  "user": {
    "id": 5,
    "username": "ali",
    "email": "ali@gmail.com"
  }
}
```

#### Login:
Request
```bash
curl -X 'POST' \
  'http://localhost:8000/login/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "ali",
  "password": "Password248"
}'
```
Response
```
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzOTgxOTgxLCJpYXQiOjE3NTM4OTU1ODEsImp0aSI6Ijg1MmNiNTM3OGFiNjQ1Yzc4ZTRmZWVmOWU0YjI0YTQ5IiwidXNlcl9pZCI6IjUifQ.N-Nbp8N4usXkv8NTmbgj8siJ6pR2YebPjpbtqOejlfE",
  "user": {
    "id": 5,
    "username": "ali",
    "email": "ali@gmail.com"
  }
}
```

### Vehicles

#### GET Vehicles
Reqeust
```
curl -X 'GET' \
  'http://localhost:8000/vehicles/?user_id=1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzOTgyMTE2LCJpYXQiOjE3NTM4OTU3MTYsImp0aSI6IjcxZGFhODc2ODA3ZDRmNDVhYWI4YTJjY2EwZTI2NzVkIiwidXNlcl9pZCI6IjEifQ.zeATJ8lN9mUzZrALIErX0so6FZDcxJroK1u8-wIyOlY' \
```
Response
```
[
  {
    "id": 3,
    "make": "Honda",
    "model": "Civic",
    "year": 2023,
    "plate": "LEH-23-001"
  },
  {
    "id": 4,
    "make": "Honda",
    "model": "Fit",
    "year": 2021,
    "plate": "LEH-21-001"
  },
  {
    "id": 5,
    "make": "Toyota",
    "model": "Corolla",
    "year": 2018,
    "plate": "LEH-18-001"
  }
]
```

#### POST Vehicles
Request
```
curl -X 'POST' \
  'http://localhost:8000/vehicles/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzOTgzMTE1LCJpYXQiOjE3NTM4OTY3MTUsImp0aSI6IjViMTNiYzM1OTU0ZTQ5YzFhZjZhZDZiOWIzNDQ0ZTI3IiwidXNlcl9pZCI6IjEifQ.VS_-4AhsIpyL4GqfcYsWir9PHAYxC6WE3YK5oNorij8' \
  -H 'Content-Type: application/json' \
  -d '{
  "make": "Honda",
  "model": "Civic",
  "year": 2018,
  "plate": "LEH-18-2942"
}'
```
Response
```
{
  "id": 1,
  "make": "Honda",
  "model": "Civic",
  "year": 2018,
  "plate": "LEH-18-2942"
}
```
#### PUT Vehicles
Request
```
curl -X 'PUT' \
  'http://localhost:8000/vehicles/1/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzOTgzMTE1LCJpYXQiOjE3NTM4OTY3MTUsImp0aSI6IjViMTNiYzM1OTU0ZTQ5YzFhZjZhZDZiOWIzNDQ0ZTI3IiwidXNlcl9pZCI6IjEifQ.VS_-4AhsIpyL4GqfcYsWir9PHAYxC6WE3YK5oNorij8' \
  -H 'Content-Type: application/json' \
  -d '{
  "make": "Toyota",
  "model": "Corolla",
  "year": 2020,
  "plate": "LEK-20-2242"
}'
```
Response
```
{
  "id": 1,
  "make": "Toyota",
  "model": "Corolla",
  "year": 2020,
  "plate": "LEK-20-2242"
}
```

#### DELETE Vehicles
Request
```
curl -X 'DELETE' \
  'http://localhost:8000/vehicles/1/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzOTgzMTE1LCJpYXQiOjE3NTM4OTY3MTUsImp0aSI6IjViMTNiYzM1OTU0ZTQ5YzFhZjZhZDZiOWIzNDQ0ZTI3IiwidXNlcl9pZCI6IjEifQ.VS_-4AhsIpyL4GqfcYsWir9PHAYxC6WE3YK5oNorij8'
```
Response
```
{
  "detail": "Vehicle deleted successfully."
}
```

### Bookings

#### POST Bookings
Request
```
curl -X 'POST' \
  'http://localhost:8000/bookings/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzOTgzMTE1LCJpYXQiOjE3NTM4OTY3MTUsImp0aSI6IjViMTNiYzM1OTU0ZTQ5YzFhZjZhZDZiOWIzNDQ0ZTI3IiwidXNlcl9pZCI6IjEifQ.VS_-4AhsIpyL4GqfcYsWir9PHAYxC6WE3YK5oNorij8' \
  -H 'Content-Type: application/json' \
  -d '{
  "vehicle": 3,
  "start_date": "2025-07-30T20:01:48.582Z",
  "end_date": "2025-07-31T18:01:48.582Z"
}'
```
Response
```
{
  "vehicle": 3,
  "user": 1,
  "start_date": "2025-07-30T20:01:48.582000Z",
  "end_date": "2025-07-31T18:01:48.582000Z"
}
```

#### GET Bookings
Request
```
curl -X 'GET' \
  'http://localhost:8000/bookings/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzOTgzMTE1LCJpYXQiOjE3NTM4OTY3MTUsImp0aSI6IjViMTNiYzM1OTU0ZTQ5YzFhZjZhZDZiOWIzNDQ0ZTI3IiwidXNlcl9pZCI6IjEifQ.VS_-4AhsIpyL4GqfcYsWir9PHAYxC6WE3YK5oNorij8'
```
Response
```
[
  {
    "vehicle": 3,
    "user": 1,
    "start_date": "2025-07-30T20:01:48.582000Z",
    "end_date": "2025-07-31T18:01:48.582000Z"
  }
]
```
