# SafePark

A **Smart Parking Management System** built with **Flask (Python)** for the backend and **Vue.js** for the frontend.  
SafePark enables users to book parking spots online, manage bookings, and provides admins with advanced analytics and management capabilities.

---

## 🚀 Features

### User Features
- **User Registration & Login**
  - OTP-based email verification (via Gmail SMTP & Celery)
  - JWT Authentication
- **Parking Spot Booking**
  - Book available spots in registered parking lots
  - View current and past bookings
  - End booking sessions and calculate costs dynamically
- **Dashboard**
  - See ongoing & past bookings
  - Easy access to parking lot locations via integrated maps

### Admin Features
- **Parking Lot Management**
  - Add, edit, and delete parking lots
  - Integrated geocoding with **Ola Maps**
- **Analytics Dashboard**
  - Cost graph over time (Bar Chart)
  - Average parking duration (Zoomable Line Chart)
  - User bookings over time (Line Chart)
  - Parking lots vs bookings distribution (Pie Chart)
- **Booking Monitoring**
  - See lot-wise and time-based booking history

---

## 🛠 Tech Stack

### Backend
- **Framework:** Flask (Python)
- **Database:** SQLite
- **Authentication:** JWT (JSON Web Tokens)
- **Background Tasks:** Celery + Redis
- **Email Service:** Gmail SMTP

### Frontend
- **Framework:** Vue.js 3 (Composition API)
- **UI Framework:** TailwindCSS (with custom SafePark palette)
- **Charts:** Chart.js + vue-chartjs (with zoom & pan plugin)
- **Maps Integration:** Ola Maps API

---

## 📂 Project Structure
SafePark/
│
├── src/
│ ├── app.py # Flask app entry point
│ ├── controllers/ # All business logic
│ │ ├── auth.py # Authentication & OTP
│ │ ├── bookings.py # Booking management
│ │ ├── dbconnect.py # DB connection & schema
│ │ └── analytics.py # Analytics APIs
│ ├── models/
│ │ └── safepark.db # SQLite database
│ └── tasks/
│ └── celery_tasks.py # Celery background tasks
│
└── frontend/
├── src/
│ ├── views/ # Vue pages (Login, Dashboard, Analytics)
│ ├── components/ # Reusable components
│ ├── router/ # Vue Router configuration
│ └── store/ # State management
└── package.json

##📊 Analytics Preview
Cost Graph (Bar) – View parking revenue trends.

Parking Duration (Zoomable Line) – Analyze average & median durations.

User Bookings (Line) – Monitor user activity trends.

Parking Lots vs Bookings (Pie) – See distribution of bookings across lots.

##📬 Email Templates
OTP Email: Styled HTML mail for user verification.

Booking Confirmation Email: Includes lot name, spot, and booking time details.

##🧪 Testing
API testing done using Postman.

Frontend testing with manual flows.

Future scope: Jest (Vue) & PyTest (Flask).

📄 License
MIT License
