# Personal Expense Tracker API

A production-ready Django REST Framework API for tracking personal expenses, built according to OpenAPI 3.0 specifications.

## Features

- **Authentication**: JWT-based authentication with token blacklisting
- **User Management**: Custom user model with UUID primary keys
- **Income Tracking**: CRUD operations for income records
- **Expense Tracking**: CRUD operations for expenditure records
- **API Documentation**: Auto-generated Swagger UI and ReDoc documentation
- **Comprehensive Testing**: Full test coverage with pytest
- **Code Quality**: Pre-commit hooks with ruff and black

## Quick Start

### Prerequisites

- Python 3.11+
- pip or poetry
- Docker (optional)

### Installation

#### Option 1: Local Development

1. **Clone and setup environment**:
   ```bash
   git clone <repository-url>
   cd finance_tracker
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   make install
   # or: pip install -e .
   ```

3. **Environment setup**:
   ```bash
   cp .env.example .env
   # Edit .env with the settings
   ```

4. **Database setup**:
   ```bash
   make migrate
   make superuser
   ```

5. **Run the server**:
   ```bash
   make run
   ```

#### Option 2: Docker Development

1. **Build and start containers**:
   ```bash
   make docker-build
   make docker-up
   ```

2. **Run migrations**:
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

3. **Access the application**:
   - API: http://localhost:8000/
   - Admin: http://localhost:8000/admin/

4. **Stop containers**:
   ```bash
   make docker-down
   ```

The API will be available at `http://localhost:8000/`

## API Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Authentication Flow

### 1. Sign Up
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe", 
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

### 3. Use Access Token
```bash
curl -X GET http://localhost:8000/user/income \
  -H "Authorization: Bearer <access_token>"
```

### 4. Logout
```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

## API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user

### User Profile
- `GET /auth/user/{userID}/profile` - Get user profile
- `PUT /auth/user/{userID}/profile` - Update user profile

### Income Management
- `GET /user/income` - List user's income records
- `POST /user/income` - Create new income record
- `GET /user/income/{incomeID}` - Get specific income record
- `PUT /user/income/{incomeID}` - Update income record
- `DELETE /user/income/{incomeID}` - Delete income record

### Expenditure Management
- `GET /user/expenditure` - List user's expenditure records
- `POST /user/expenditure` - Create new expenditure record
- `GET /user/expenditure/{expenditureID}` - Get specific expenditure record
- `PUT /user/expenditure/{expenditureID}` - Update expenditure record
- `DELETE /user/expenditure/{expenditureID}` - Delete expenditure record

## Development

### Running Tests
```bash
make test
```

### Code Formatting
```bash
make fmt
```

### Linting
```bash
make lint
```

### Database Operations
```bash
make migrate      # Run migrations
make superuser    # Create superuser
make schema       # Generate OpenAPI schema
```

### Docker Commands
```bash
make docker-build  # Build Docker image
make docker-up     # Start containers
make docker-down   # Stop containers
make docker-logs   # View logs
make docker-shell  # Access container shell
```

## Project Structure

```
finance_tracker/
├── expense_tracker/          # Django project settings
├── accounts/                 # User authentication app
├── finance/                  # Income/expenditure app
├── tests/                    # Test suite
├── openapi/                  # OpenAPI specification
├── pyproject.toml           # Project dependencies
├── Makefile                  # Development commands
└── README.md                 # This file
```

## Technology Stack

- **Framework**: Django 5.x + Django REST Framework 3.15+
- **Authentication**: JWT with djangorestframework-simplejwt
- **Documentation**: drf-spectacular
- **Testing**: pytest + pytest-django + model-bakery
- **Code Quality**: ruff + black + pre-commit
- **Database**: SQLite (development) / PostgreSQL (production)

## Contributing

1. Install pre-commit hooks: `pre-commit install`
2. Run tests: `make test`
3. Format code: `make fmt`
4. Submit a pull request

## License

Apache 2.0 License
