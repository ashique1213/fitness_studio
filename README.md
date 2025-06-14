# Fitness Studio Booking API

A Django REST Framework-based API for a fictional fitness studio, allowing clients to view upcoming classes, book spots, and retrieve bookings. This README focuses on setting up the project and testing the `POST /api/book/` endpoint, as no endpoint exists to add classes (`POST /classes/`).

## Project Overview
The API provides three endpoints:
- `GET /api/classes/`: List upcoming fitness classes (name, date/time, instructor, available slots).
- `POST /api/book/`: Book a spot in a class.
- `GET /api/bookings/`: List bookings for a client by email.

Since there’s no `POST /classes/` endpoint, this README explains how to populate the database with sample classes using the provided `seed_data.py` script or manual methods to enable testing of the `POST /api/book/` endpoint.

## Prerequisites
- Python 3.8+
- Git
- A tool like cURL or Postman for API testing

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/ashique1213/fitness_studio.git
cd fitness_studio
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
Ensure `requirements.txt` contains:
```text
asgiref==3.8.1
Django==5.2.1
django-cors-headers==4.7.0
djangorestframework==3.16.0
python-decouple==3.8
python-dotenv==1.1.0
pytz==2024.1
tzdata==2025.2
```
Install them:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root to store sensitive settings (used by `python-dotenv` and `python-decouple`):
```text
SECRET_KEY=your-secret-key-here  # Replace with a secure key (e.g., generate using an online Django secret key generator)
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```
- Ensure `settings.py` uses `os.getenv` to load these variables:
  ```python
  import os
  from dotenv import load_dotenv
  SECRET_KEY = os.getenv('SECRET_KEY')
  DEBUG = os.getenv('DEBUG', 'False') == 'True'
  ```

### 5. Apply Migrations
Create the database schema:
```bash
python manage.py migrate
```

### 6. Populate the Database
Since there’s no `POST /classes/` endpoint, use the `seed_data.py` script to create sample classes:
- Open the Django shell:
  ```bash
  python manage.py shell
  ```
- Run the seed data script:
  ```python
  from api.seed_data import seed_data
  seed_data()
  ```
- This creates three classes (Yoga, Zumba, HIIT) with available slots. Output:
  ```
  Seed data created successfully!
  ```
- **Alternative**: Manually create a class in the Django shell:
  ```python
  from api.models import FitnessClass
  from django.utils import timezone
  FitnessClass.objects.create(
      name="Test Yoga",
      date_time=timezone.now() + timezone.timedelta(hours=1),
      instructor="Test Instructor",
      total_slots=5,
      available_slots=5
  )
  ```

### 7. Run the Server
```bash
python manage.py runserver
```
The API will be available at `http://localhost:8000`.

## Testing the `POST /api/book/` Endpoint

### Step 1: Verify Available Classes
Check available classes to get a valid `fitness_class` ID:
```bash
curl http://localhost:8000/api/classes/?timezone=Asia/Kolkata
```
**Sample Response** (assuming seed data was run on June 4, 2025, 8:45 PM IST):
```json
[
  {
    "id": 1,
    "name": "Yoga",
    "date_time": "2025-06-05T20:45:00+05:30",
    "instructor": "John Doe",
    "available_slots": 10
  },
  {
    "id": 2,
    "name": "Zumba",
    "date_time": "2025-06-06T20:45:00+05:30",
    "instructor": "Jane Smith",
    "available_slots": 15
  },
  {
    "id": 3,
    "name": "HIIT",
    "date_time": "2025-06-07T20:45:00+05:30",
    "instructor": "Mike Brown",
    "available_slots": 8
  }
]
```
- Note the `id` (e.g., `1` for Yoga) for the booking request.

### Step 2: Test `POST /api/book/`
Send a booking request for a class with available slots.

#### Success Case
**Request**:
```bash
curl -X POST http://localhost:8000/api/book/ \
     -H "Content-Type: application/json" \
     -d '{"fitness_class": 1, "client_name": "Alice", "client_email": "alice@example.com"}'
```
**Expected Response**:
```json
{"message": "Booking successful"}
```
- **Status Code**: `201 Created`
- The `available_slots` for the class (ID=1) decreases by 1.

**Verify in Database**:
- Open the Django shell:
  ```bash
  python manage.py shell
  ```
- Check slots:
  ```python
  from api.models import FitnessClass
  FitnessClass.objects.get(id=1).available_slots
  ```
  - Should return `9` (originally `10`).
- Check booking:
  ```python
  from api.models import Booking
  Booking.objects.all()
  ```
  - Should show: `<QuerySet [<Booking: Alice booked Yoga>]>`

#### Error Cases
1. **No Slots Available**:
   - Set `available_slots` to 0:
     ```python
     from api.models import FitnessClass
     fitness_class = FitnessClass.objects.get(id=1)
     fitness_class.available_slots = 0
     fitness_class.save()
     ```
   - Send the booking request:
     ```bash
     curl -X POST http://localhost:8000/api/book/ \
          -H "Content-Type: application/json" \
          -d '{"fitness_class": 1, "client_name": "Bob", "client_email": "bob@example.com"}'
     ```
   - **Expected Response**:
     ```json
     {"error": "No slots available"}
     ```
     - **Status Code**: `400 Bad Request`

2. **Invalid Email**:
   ```bash
   curl -X POST http://localhost:8000/api/book/ \
        -H "Content-Type: application/json" \
        -d '{"fitness_class": 1, "client_name": "Bob", "client_email": "invalid-email"}'
   ```
   - **Expected Response**:
     ```json
     {"client_email": ["Invalid email format."]}
     ```
     - **Status Code**: `400 Bad Request`

3. **Invalid Class ID**:
   ```bash
   curl -X POST http://localhost:8000/api/book/ \
        -H "Content-Type: application/json" \
        -d '{"fitness_class": 999, "client_name": "Bob", "client_email": "bob@example.com"}'
   ```
   - **Expected Response**:
     ```json
     {"fitness_class": ["Invalid pk \"999\" - object does not exist."]}
     ```
     - **Status Code**: `400 Bad Request`

### Step 3: Verify Bookings
Check the created booking using `GET /api/bookings/`:
```bash
curl http://localhost:8000/api/bookings/?email=alice@example.com&timezone=Asia/Kolkata
```
**Expected Response**:
```json
[
  {
    "id": 1,
    "fitness_class": 1,
    "client_name": "Alice",
    "client_email": "alice@example.com",
    "created_at": "2025-06-04T20:45:00+05:30",
    "class_name": "Yoga",
    "class_date_time": "2025-06-05T20:45:00+05:30"
  }
]
```

## Testing with Postman
1. Open Postman and create a new request.
2. Set method to `POST` and URL to `http://localhost:8000/api/book/`.
3. Add header: `Content-Type: application/json`.
4. Set body to raw JSON:
   ```json
   {
     "fitness_class": 1,
     "client_name": "Alice",
     "client_email": "alice@example.com"
   }
   ```
5. Send and verify the response (`201 Created` or `400 Bad Request` for errors).
6. Test error cases by modifying the body (e.g., invalid email or class ID).

## Timezone Management
- Class times are stored in UTC in the database.
- The `GET /api/classes/` and `GET /api/bookings/` endpoints display times in the requested timezone (default: `Asia/Kolkata` for IST).
- Use the `timezone` query parameter (e.g., `America/New_York`) to adjust the display.
- The `POST /api/book/` endpoint doesn’t require timezone input, as it uses the class ID.

## Error Handling
- Missing fields or invalid email formats return `400 Bad Request`.
- No available slots return `400 Bad Request`.
- Invalid class IDs return `400 Bad Request`.
- Invalid timezones (for `GET` endpoints) return `400 Bad Request`.

## Logging
- Logs are saved to `debug.log` in the project root.
- Example log entries:
  - Successful booking: `INFO api: Booking created for alice@example.com in class 1`
  - Failed booking (no slots): `ERROR api: Booking failed: No slots available for class 1`
  - Failed booking (invalid email): `ERROR api: Booking failed: {'client_email': [ErrorDetail(string='Invalid email format.', code='invalid')]}`

## Running Unit Tests
Unit tests in `api/tests.py` cover the `POST /api/book/` endpoint:
```bash
python manage.py test
```
Tests verify:
- Successful bookings (status `201`, slots decrease).
- No slots available (status `400`).
- Invalid email format (status `400`).
- Invalid or missing parameters.

## Notes
- The API uses SQLite for simplicity.
- The absence of a `POST /classes/` endpoint is per the requirements; classes are created via the seed script, Django shell, or admin interface.
- The code is modular, with separate files for models, serializers, views, and tests.
- Timezone handling is implemented for display in `GET` endpoints using `pytz` and `tzdata`.
- Current date: June 4, 2025, 8:45 PM IST.

## Troubleshooting
- **No Classes Available**:
  - Run `seed_data.py` or create a class manually.
  - Verify with `GET /api/classes/`.
- **Invalid Class ID**:
  - Check class IDs via `GET /api/classes/` or Django shell.
- **Server Issues**:
  - Ensure the server is running (`python manage.py runserver`).
  - Verify `.env` file settings.
- **Validation Errors**:
  - Check `debug.log` for detailed error messages.
- **CORS Errors**:
  - Ensure `CORS_ALLOWED_ORIGINS` includes your client’s origin.

For further assistance, refer to the code in `api/` or contact the repository maintainer.