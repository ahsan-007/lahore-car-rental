# Lahore Car Rental API

A Django REST Framework API for managing car rental bookings in Lahore.


## Tech Stack

- **Backend**: Django 5.2.4, Django REST Framework
- **Database**: SQLite (development)
- **Testing**: Django's built-in testing framework


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
   - Admin Panel: http://localhost:8000/admin/


## Testing

Run tests:
```bash
python manage.py test
```

## Development

### Code Style
- Follows PEP 8 standards
- Configured with autopep8 and isort
- Comprehensive docstrings and comments
