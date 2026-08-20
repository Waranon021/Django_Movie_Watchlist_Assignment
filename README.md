# Movie Watchlist

A full-stack Django web application for managing a personal movie watchlist.

The application allows users to keep track of movies they plan to watch, movies they have already watched, and their personal ratings. Movies can be added manually or searched and imported using The Movie Database (TMDB) API.

## Features

### Movie Watchlist Management

- View all movies in the watchlist
- Add movies manually
- Edit existing movie information
- Delete movies with confirmation
- Display newly added movies first
- Search the local watchlist by movie title

### Watch Status

Movies are organized into two sections:

- **Plan to Watch** — movies with an unwatched status
- **Watched** — movies that have already been watched

Users can move movies between the two sections using **Mark Watched** and **Mark Unwatched**.

### Personal Rating

Watched movies can receive a personal rating from **1 to 5 stars**.

The rating can be changed or cleared directly from the Movie Watchlist page.

Unwatched movies do not provide rating controls until they are marked as watched.

### TMDB Integration

The application integrates with **The Movie Database (TMDB) API**.

Users can:

- Search the TMDB movie catalog
- View movie posters
- View release years
- View genres
- View TMDB ratings
- Add a movie directly to **Plan to Watch**
- Add a movie directly to **Watched**

Movie details are retrieved by the Django backend before they are stored locally.

### Duplicate Protection

Movies imported through TMDB use the TMDB movie ID as a unique identifier.

This prevents the same TMDB movie from being imported multiple times.

### Responsive Interface

The application uses a custom responsive interface built with HTML and CSS.

Movie collections initially display up to eight movies per section. If more movies exist, users can expand or collapse the section using **Show More / Show Less**.

---

## Technology Stack

### Backend

- Python
- Django

### Database

- PostgreSQL
- Django ORM

### Frontend

- HTML5
- Custom CSS
- Vanilla JavaScript

### External Services

- TMDB API
- Python Requests library

### Development and Version Control

- Git
- GitHub

Bootstrap is not used in this project. The user interface is implemented using custom CSS.

---

## Project Structure

```text
Django_Movie_Watchlist_Assignment/
│
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── movies/
│   ├── migrations/
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   └── 0002_movie_poster_path_movie_tmdb_id.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── tmdb.py
│   │
│   ├── static/
│   │   └── movies/
│   │       ├── css/
│   │       │   └── styles.css
│   │       ├── images/
│   │       │   └── tmdb-logo.svg
│   │       └── js/
│   │           └── movie_list.js
│   │
│   ├── templates/
│   │   └── movies/
│   │       ├── about.html
│   │       ├── base.html
│   │       ├── contact.html
│   │       ├── movie_confirm_delete.html
│   │       ├── movie_form.html
│   │       ├── movie_list.html
│   │       └── tmdb_search.html
│   │
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── .env.example
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt

---

# Local Setup

## 1. Clone the Repository

```powershell
git clone https://github.com/Waranon021/Django_Movie_Watchlist_Assignment.git
```

Move into the project directory:

```powershell
cd Django_Movie_Watchlist_Assignment
```

---

## 2. Create a Python Virtual Environment

```powershell
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

---

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 4. Create a PostgreSQL Database

PostgreSQL must be installed and running locally.

Create:

- A PostgreSQL database for the application
- A PostgreSQL user with access to that database

Do not store database passwords directly in the source code.

---

## 5. Configure Environment Variables

Create a local `.env` file in the project root.

An example configuration is provided in `.env.example`.

```env
DJANGO_SECRET_KEY=replace-with-your-own-secret-key
DJANGO_DEBUG=True

POSTGRES_DB=your_database_name
POSTGRES_USER=your_database_user
POSTGRES_PASSWORD=your_database_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

TMDB_API_TOKEN=your_tmdb_api_read_access_token
```

### Important

The real `.env` file contains local credentials and must **not** be committed to GitHub.

Only `.env.example`, containing placeholder values, should be committed.

---

## 6. Configure TMDB

A TMDB API Read Access Token is required for the external movie search functionality.

Create a TMDB account and obtain an API Read Access Token from:

https://www.themoviedb.org/

Store the token only in the local `.env` file:

```env
TMDB_API_TOKEN=your_tmdb_api_read_access_token
```

The token is read by the Django backend and is not exposed to client-side JavaScript.

---

## 7. Apply Database Migrations

```powershell
python manage.py migrate
```

---

## 8. Optional: Create a Django Admin Account

```powershell
python manage.py createsuperuser
```

Follow the prompts to create the local administrator account.

The Django Admin interface can then be accessed at:

```text
http://127.0.0.1:8000/admin/
```

---

## 9. Run the Development Server

```powershell
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

# Application Workflow

## Manual Movie Entry

From the Home page:

```text
Add Movie Manually
    ↓
Enter movie information
    ↓
Save
    ↓
Movie stored in PostgreSQL
```

## TMDB Movie Import

```text
Add Movie via TMDB
    ↓
Search TMDB
    ↓
Select a movie
    ↓
Choose:
    ├── Add to Plan to Watch
    └── Add to Watched
    ↓
Django retrieves movie details server-side
    ↓
Movie stored in PostgreSQL
```

## Personal Rating

```text
Watched Movie
    ↓
Select 1–5 stars
    ↓
Django validates the rating
    ↓
Personal rating stored in PostgreSQL
```

Movies in **Plan to Watch** cannot receive a new personal rating until they are marked as watched.

---

# Security Considerations

The project follows several basic security practices:

- Sensitive configuration is stored in environment variables
- `.env` is excluded from Git
- Django `SECRET_KEY` is not hard-coded in the repository
- PostgreSQL credentials are not stored directly in source code
- TMDB credentials remain server-side
- Django CSRF protection is used for POST forms
- Database-changing operations use POST requests
- Delete operations require confirmation
- TMDB import status is validated by the Django backend
- TMDB movie metadata is retrieved server-side rather than trusted directly from browser-submitted metadata

---

# TMDB Attribution

Movie information and poster images used by the external movie search feature are retrieved using **The Movie Database (TMDB) API**.

> This product uses the TMDB API but is not endorsed or certified by TMDB.

TMDB website:

https://www.themoviedb.org/

---

# AI Disclosure

ChatGPT was used as a development and learning assistant for project planning, explanations of Django and Python concepts, code drafting, debugging guidance, security review, and user-interface planning.

AI-generated suggestions were reviewed, adapted, and tested during the development of this coursework project.

---

# Coursework

This project was developed as a Full Stack Application Development coursework assignment.

The project demonstrates:

- Django web development
- Django Models and Forms
- CRUD operations
- PostgreSQL integration
- Django ORM
- Server-side rendering
- External API integration
- HTML and CSS interface development
- Client-side JavaScript interaction
- Basic web security practices
- Git and GitHub version control