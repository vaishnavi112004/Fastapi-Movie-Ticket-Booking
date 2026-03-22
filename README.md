# 🎬 CineStar Movie Ticket Booking API

## 📌 Project Overview
This project is a FastAPI-based backend system for a Movie Ticket Booking application.  
It allows users to browse movies, book tickets, manage bookings, and perform advanced operations like filtering, searching, sorting, and pagination.

---

## 🚀 Features

### 🎥 Movie Management
- View all movies
- Get movie by ID
- Add new movies (POST)
- Update movie details (PUT)
- Delete movies (DELETE with booking restriction)

### 🎟️ Booking System
- Book movie tickets
- Seat availability check
- Automatic seat reduction after booking

### 💰 Pricing & Discounts
- Seat type pricing (standard, premium, recliner)
- Promo codes:
  - SAVE10 → 10% discount
  - SAVE20 → 20% discount

### 🔍 Advanced Features
- Filter movies (genre, language, price, seats)
- Search movies (title, genre, language)
- Sort movies (price, duration, seats, title)
- Pagination support

### 🔄 Multi-Step Workflow
- Seat hold system
- Confirm booking
- Release hold

---

## 🧠 Concepts Implemented

- FastAPI routing
- Pydantic validation
- CRUD operations
- Helper functions (find_movie, calculate_ticket_cost)
- Query parameters & filtering
- Search, sorting, pagination
- Multi-step workflows

---

## 📂 Project Structure
fastapi-movie-booking/
│
├── main.py
├── README.md
├── requirements.txt
├── screenshots/
│ ├── Q1_home_route.png
│ ├── ...
│ ├── Q20_browse_combined.png

---

## 🔗 API Endpoints

### Basic Routes
- GET / → Home
- GET /movies → Get all movies
- GET /movies/{movie_id} → Get movie by ID
- GET /movies/summary → Movie statistics

### Movie Operations
- POST /movies → Add movie
- PUT /movies/{movie_id} → Update movie
- DELETE /movies/{movie_id} → Delete movie

### Booking Operations
- POST /bookings → Create booking
- GET /bookings → View bookings

### Filtering & Search
- GET /movies/filter → Filter movies
- GET /movies/search → Search movies
- GET /movies/sort → Sort movies
- GET /movies/page → Pagination

### Workflow
- POST /seat-hold → Hold seats
- GET /seat-hold → View holds
- POST /seat-confirm/{hold_id} → Confirm booking
- DELETE /seat-release/{hold_id} → Release hold

### Combined Endpoint
- GET /movies/browse → Search + Filter + Sort + Pagination

---

## 🧪 Testing

All APIs are tested using Swagger UI:
http://127.0.0.1:8000/docs


Screenshots for all 20 tasks are included in the project.

---

## ⚙️ Installation & Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
👩‍💻 Author

Vaishnavi