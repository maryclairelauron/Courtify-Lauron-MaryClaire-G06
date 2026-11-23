
# Courtify

Courtify is a court-booking web application developed using Django and PostgreSQL (Supabase). It allows customers to manage court reservations while administrators manage courts and monitor bookings.

## Features

### 1. Account Management
- User registration and login/logout
- Role-based access for Admin and Customer
- User profile management
- Role-based dashboards

### 2. Court Management
- Create, view, update, and delete court records
- Manage court names and environments
- Set hourly rates and maximum player capacity
- Track court availability and maintenance status

### 3. Court Booking
- Customers can create court reservations
- Customers can view their own bookings
- Customers can update and cancel eligible bookings
- Administrators can view all bookings
- Automatic booking price calculation
- Validation for past dates, invalid times, and overlapping reservations

## Technology Stack
- Python
- Django
- PostgreSQL via Supabase
- HTML and Bootstrap 5

## Project Setup

1. Clone the repository.
2. Create and activate a virtual environment:

   ```bash
   py -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and configure your database credentials and Django secret key.

5. Apply migrations:

   ```bash
   python manage.py migrate
   ```

6. Create an administrator account if needed:

   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:

   ```bash
   python manage.py runserver 8080
   ```

8. Open `http://127.0.0.1:8080/` in your browser.

## User Roles
- **Admin:** Manages courts and views customer bookings.
- **Customer:** Registers, manages their profile, and creates and manages court bookings.

## Author
Mary Claire Lauron  
Section G06
