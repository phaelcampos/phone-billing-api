# Phone Billing API

RESTful API for managing phone call records and generating bills with time-based pricing.

## Technical Stack
- Python 3.11+
- Django 5.0.1
- Django REST Framework 3.14.0
- PostgreSQL
- Docker

## Quick Start
```bash
# With Docker
docker-compose up --build

# Without Docker
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## API Endpoints

### Call Records
```http
POST /api/call-records/
GET /api/call-records/
```

### Phone Bills
```http
GET /api/phone-bills/{phone_number}/?period=YYYY-MM
```

## Documentation
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI: `/api/schema/`

## Call Record Examples

Start:
```json
{
    "type": "start",
    "timestamp": "2024-01-01T10:00:00Z",
    "source": "11999999999",
    "destination": "11988888888"
}
```

End:
```json
{
    "type": "end",
    "timestamp": "2024-01-01T10:10:00Z",
    "call_id": "uuid-from-start-record"
}
```

## Pricing Rules

### Standard Hours (06:00 - 21:59)
- Fixed rate: R$ 0,36
- Per minute: R$ 0,09
  - Only charged for complete 60-second cycles
  - No fractional charging

### Reduced Hours (22:00 - 05:59)
- Fixed rate: R$ 0,36
- Per minute: R$ 0,00

Notes:
- All calls have a fixed connection fee
- Pricing changes based on call time periods
- Only complete minutes are charged

## Environment Setup
```env
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key
DEBUG=False
```