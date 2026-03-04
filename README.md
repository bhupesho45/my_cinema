# 🎬 MyCinema – Movie Ticket Booking System

MyCinema is a **Flask-based web application** that allows users to browse movies, view showtimes, select seats, make bookings, and view booking history.
It also includes **admin functionality** for managing movies and shows.

This project demonstrates **full-stack web development using Python, Flask, MySQL, HTML, and CSS**.

----
----

# 🚀 Feature

### 👤 User Features

* User registration and login
* Browse available movies
* View theaters and show timings
* Select seats for booking
* Simulated payment system
* Booking confirmation
* View booking history

### 🛠 Admin Features

* Admin login
* Add new movies
* Add new shows
* Remove movies
* Remove shows
* Manage bookings indirectly through show removal

---

# 🧑‍💻 Technologies Used

| Technology    | Purpose             |
| ------------- | ------------------- |
| Python        | Backend programming |
| Flask         | Web framework       |
| MySQL         | Database            |
| HTML          | Frontend structure  |
| CSS           | UI styling          |
| Jinja2        | Template rendering  |
| Flask-MySQLdb | Database connection |

---

# 📂 Project Structure

```
mycinema_app
│
├── app.py
├── templates
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── movies.html
│   ├── shows.html
│   ├── booking.html
│   ├── payment.html
│   ├── success.html
│   ├── history.html
│   ├── admin_add_movie.html
│   └── admin_add_show.html
│
├── static
│   └── style.css
│
└── README.md
```

---

# 🗄 Database Setup

Create a MySQL database named:

```
mycinema_db
```

## Create Tables

### Users Table

```sql
CREATE TABLE users (
id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(50),
password VARCHAR(255),
email VARCHAR(100)
);
```

### Admin Users

```sql
CREATE TABLE admin_users (
id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(50),
password VARCHAR(255)
);
```

### Movies

```sql
CREATE TABLE movies (
id INT AUTO_INCREMENT PRIMARY KEY,
title VARCHAR(100),
description TEXT,
poster_url TEXT
);
```

### Theaters

```sql
CREATE TABLE theaters (
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(100),
location VARCHAR(100)
);
```

### Shows

```sql
CREATE TABLE shows (
id INT AUTO_INCREMENT PRIMARY KEY,
movie_id INT,
theater_id INT,
showtime DATETIME,
price DECIMAL(10,2)
);
```

### Bookings

```sql
CREATE TABLE bookings (
id INT AUTO_INCREMENT PRIMARY KEY,
user_id INT,
show_id INT,
seats_booked TEXT,
total_price DECIMAL(10,2),
booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# ⚙️ Installation

### 1️⃣ Clone Repository

```
git clone https://github.com/bhupesho45/my_cinema.git
cd my_cinema
```

---

### 2️⃣ Install Dependencies

```
pip install flask
pip install flask-mysqldb
pip install mysqlclient
```

---

### 3️⃣ Configure Database

Edit `app.py`

```
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'mycinema_db'
```

---

### 4️⃣ Run Application

```
python app.py
```

Server will start at:

```
http://127.0.0.1:5000
```

---

# 🔑 Admin Access

Insert an admin manually into database:

```sql
INSERT INTO admin_users (username, password)
VALUES ('admin','admin123');
```

Login with these credentials to access admin features.

---

# 💳 Payment System

The payment system in this project is **simulated** for demonstration purposes.
No real payment gateway is integrated.

---

# 📸 Application Workflow

```
User Registration
      ↓
User Login
      ↓
Browse Movies
      ↓
Select Show
      ↓
Choose Seats
      ↓
Payment
      ↓
Booking Confirmation
```

Admin Workflow

```
Admin Login
      ↓
Add Movies
      ↓
Add Shows
      ↓
Manage Movies & Shows
```

---

# 📈 Future Improvements

* Secure password hashing
* Real payment gateway integration
* Seat layout management system
* Movie search and filters
* Responsive UI
* Email booking confirmation

---

# 👨‍💻 Author

**Bhupesh**

GitHub
https://github.com/bhupesho45

---

# ⭐ Project Purpose

This project was built to practice:

* Flask web development
* MySQL database integration
* Authentication systems
* Session management
* Full web application architecture
---------------------------------------------
NOTE:check and change the versions according to latest update 
---------------------------------------------
