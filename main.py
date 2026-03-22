from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()

# =========================
# ✅ MODELS
# =========================
class BookingRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    movie_id: int = Field(..., gt=0)
    seats: int = Field(..., gt=0, le=10)
    phone: str = Field(..., min_length=10)
    seat_type: str = "standard"
    promo_code: str = ""

class NewMovie(BaseModel):
    title: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    language: str = Field(..., min_length=2)
    duration_mins: int = Field(..., gt=0)
    ticket_price: int = Field(..., gt=0)
    seats_available: int = Field(..., gt=0)

# =========================
# ✅ DATA
# =========================
movies = [
    {"id": 1, "title": "RRR", "genre": "Action", "language": "Telugu", "duration_mins": 180, "ticket_price": 250, "seats_available": 50},
    {"id": 2, "title": "KGF", "genre": "Action", "language": "Kannada", "duration_mins": 170, "ticket_price": 200, "seats_available": 40},
    {"id": 3, "title": "Jailer", "genre": "Drama", "language": "Tamil", "duration_mins": 160, "ticket_price": 180, "seats_available": 35},
    {"id": 4, "title": "Stree", "genre": "Horror", "language": "Hindi", "duration_mins": 140, "ticket_price": 150, "seats_available": 30},
    {"id": 5, "title": "3 Idiots", "genre": "Comedy", "language": "Hindi", "duration_mins": 165, "ticket_price": 120, "seats_available": 60},
    {"id": 6, "title": "Inception", "genre": "Action", "language": "English", "duration_mins": 150, "ticket_price": 300, "seats_available": 25}
]

bookings = []
booking_counter = 1
holds = []
hold_counter = 1

# =========================
# ✅ HELPERS
# =========================
def find_movie(movie_id):
    for movie in movies:
        if movie["id"] == movie_id:
            return movie
    return None


def calculate_ticket_cost(base_price, seats, seat_type, promo_code):
    if seat_type == "premium":
        price = base_price * 1.5
    elif seat_type == "recliner":
        price = base_price * 2
    else:
        price = base_price

    original_cost = price * seats

    discount = 0
    if promo_code == "SAVE10":
        discount = 0.10
    elif promo_code == "SAVE20":
        discount = 0.20

    discounted_cost = original_cost * (1 - discount)

    return original_cost, discounted_cost

# =========================
# ✅ BASIC ROUTES
# =========================
@app.get("/")
def home():
    return {"message": "Welcome to CineStar Booking"}


@app.get("/movies")
def get_movies():
    return {
        "movies": movies,
        "total_movies": len(movies),
        "total_seats_available": sum(m["seats_available"] for m in movies)
    }


@app.get("/movies/summary")
def movies_summary():
    return {
        "total_movies": len(movies),
        "most_expensive_ticket": max(m["ticket_price"] for m in movies),
        "cheapest_ticket": min(m["ticket_price"] for m in movies),
        "total_seats": sum(m["seats_available"] for m in movies),
        "movies_by_genre": {g: len([m for m in movies if m["genre"] == g]) for g in set(m["genre"] for m in movies)}
    }

# =========================
# ✅ FILTER
# =========================
@app.get("/movies/filter")
def filter_movies(
    genre: str = Query(None),
    language: str = Query(None),
    max_price: int = Query(None),
    min_seats: int = Query(None)
):
    result = movies

    if genre:
        result = [m for m in result if m["genre"].lower() == genre.lower()]
    if language:
        result = [m for m in result if m["language"].lower() == language.lower()]
    if max_price:
        result = [m for m in result if m["ticket_price"] <= max_price]
    if min_seats:
        result = [m for m in result if m["seats_available"] >= min_seats]

    return result

# =========================
# ✅ CRUD MOVIES
# =========================
@app.post("/movies", status_code=201)
def add_movie(movie: NewMovie):
    for m in movies:
        if m["title"].lower() == movie.title.lower():
            return {"error": "Movie already exists"}

    new_movie = movie.dict()
    new_movie["id"] = len(movies) + 1
    movies.append(new_movie)
    return new_movie


@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, ticket_price: int = None, seats_available: int = None):
    movie = find_movie(movie_id)
    if not movie:
        return {"error": "Movie not found"}

    if ticket_price is not None:
        movie["ticket_price"] = ticket_price
    if seats_available is not None:
        movie["seats_available"] = seats_available

    return movie


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    movie = find_movie(movie_id)
    if not movie:
        return {"error": "Movie not found"}

    for b in bookings:
        if b["movie_title"] == movie["title"]:
            return {"error": "Cannot delete movie with bookings"}

    movies.remove(movie)
    return {"message": "Movie deleted"}

# =========================
# ✅ BOOKING
# =========================
@app.get("/bookings")
def get_bookings():
    return {
        "bookings": bookings,
        "total": len(bookings),
        "total_revenue": sum(b["discounted_cost"] for b in bookings)
    }


@app.post("/bookings")
def create_booking(request: BookingRequest):
    global booking_counter

    movie = find_movie(request.movie_id)
    if not movie:
        return {"error": "Movie not found"}

    if movie["seats_available"] < request.seats:
        return {"error": "Not enough seats available"}

    original_cost, discounted_cost = calculate_ticket_cost(
        movie["ticket_price"], request.seats, request.seat_type, request.promo_code
    )

    movie["seats_available"] -= request.seats

    booking = {
        "booking_id": booking_counter,
        "customer_name": request.customer_name,
        "movie_title": movie["title"],
        "seats": request.seats,
        "seat_type": request.seat_type,
        "original_cost": original_cost,
        "discounted_cost": discounted_cost
    }

    bookings.append(booking)
    booking_counter += 1
    return booking

# =========================
# ✅ HOLD SYSTEM
# =========================
@app.post("/seat-hold")
def hold_seats(customer_name: str, movie_id: int, seats: int):
    global hold_counter

    movie = find_movie(movie_id)
    if not movie:
        return {"error": "Movie not found"}

    if movie["seats_available"] < seats:
        return {"error": "Not enough seats"}

    movie["seats_available"] -= seats

    hold = {
        "hold_id": hold_counter,
        "customer_name": customer_name,
        "movie_id": movie_id,
        "seats": seats
    }

    holds.append(hold)
    hold_counter += 1
    return hold


@app.get("/seat-hold")
def get_holds():
    return holds


@app.post("/seat-confirm/{hold_id}")
def confirm_hold(hold_id: int):
    global booking_counter

    for hold in holds:
        if hold["hold_id"] == hold_id:
            movie = find_movie(hold["movie_id"])

            booking = {
                "booking_id": booking_counter,
                "customer_name": hold["customer_name"],
                "movie_title": movie["title"],
                "seats": hold["seats"],
                "discounted_cost": movie["ticket_price"] * hold["seats"]
            }

            bookings.append(booking)
            booking_counter += 1
            holds.remove(hold)
            return booking

    return {"error": "Hold not found"}


@app.delete("/seat-release/{hold_id}")
def release_hold(hold_id: int):
    for hold in holds:
        if hold["hold_id"] == hold_id:
            movie = find_movie(hold["movie_id"])
            movie["seats_available"] += hold["seats"]
            holds.remove(hold)
            return {"message": "Hold released"}

    return {"error": "Hold not found"}

# =========================
# ✅ SEARCH / SORT / PAGE
# =========================
@app.get("/movies/search")
def search_movies(keyword: str):
    result = [m for m in movies if keyword.lower() in m["title"].lower()
              or keyword.lower() in m["genre"].lower()
              or keyword.lower() in m["language"].lower()]
    return {"total_found": len(result), "results": result or "No movies found"}


@app.get("/movies/sort")
def sort_movies(sort_by: str = "ticket_price", order: str = "asc"):
    reverse = order == "desc"
    return sorted(movies, key=lambda x: x[sort_by], reverse=reverse)


@app.get("/movies/page")
def paginate_movies(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit
    total = len(movies)
    return {
        "total": total,
        "total_pages": (total + limit - 1) // limit,
        "data": movies[start:end]
    }


@app.get("/bookings/search")
def search_bookings(name: str):
    return [b for b in bookings if name.lower() in b["customer_name"].lower()]


@app.get("/bookings/sort")
def sort_bookings(sort_by: str = "discounted_cost"):
    return sorted(bookings, key=lambda x: x[sort_by])


@app.get("/bookings/page")
def paginate_bookings(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit
    return bookings[start:end]


@app.get("/movies/browse")
def browse_movies(
    keyword: str = None,
    genre: str = None,
    language: str = None,
    sort_by: str = "ticket_price",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = movies

    if keyword:
        result = [m for m in result if keyword.lower() in m["title"].lower()]
    if genre:
        result = [m for m in result if m["genre"].lower() == genre.lower()]
    if language:
        result = [m for m in result if m["language"].lower() == language.lower()]

    result = sorted(result, key=lambda x: x[sort_by], reverse=(order == "desc"))

    start = (page - 1) * limit
    end = start + limit

    return result[start:end]