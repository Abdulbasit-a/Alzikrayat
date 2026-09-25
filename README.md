# الذكريات — Alzikrayat

## Description

Alzikrayat is a photo-sharing web application that allows registered users to upload, view, and comment on photos. Users can share their memories with others on the platform, and each user can manage their own photos and comments.

## Technologies

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask 3.1 |
| Database | MySQL (via PyMySQL) |
| Authentication | Flask Session + bcrypt |
| Frontend | HTML5, Jinja2, Bootstrap 5 RTL |
| File Storage | Local filesystem (`uploads/`) |
| Password Hashing | bcrypt 5.0 |

## How to Run

### 1. Clone the repository

```bash
git clone <repository-url>
cd alzikrayat
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up the database

Create a MySQL database named `alzikrayat` and import the schema:

```bash
mysql -u root -p alzikrayat < database/schema.sql
```

Update the database credentials in `app/config.py` if needed:

```python
DB_HOST     = "localhost"
DB_USER     = "root"
DB_PASSWORD = ""
DB_NAME     = "alzikrayat"
```

### 4. Run the application

```bash
python run.py
```

The application will be available at: `http://127.0.0.1:5000`

## Student Name

**عبدالباسط أبكر محمد شريف**
