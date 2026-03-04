# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime

# --- 3. Initialize the Flask application ---
app = Flask(__name__)

# --- 4. Configure the secret key for sessions ---
# This is crucial for session security. Change it to a random, strong string.
app.secret_key = 'your_super_secret_key'

# --- 5. Configure the MySQL database connection ---
# !!! IMPORTANT !!!
# Update these values to match your MySQL server configuration.
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '2003' # <-- Change this
app.config['MYSQL_DB'] = 'mycinema_db'

mysql = MySQL(app)

# --- Routes for User Authentication and Home ---

@app.route('/')
def home():
    # Redirect logged-in users to the movies page, otherwise show the landing page.
    if 'loggedin' in session:
        return redirect(url_for('movies'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, email,))
        account = cursor.fetchone()
        
        if account:
            msg = 'User or email already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # For a real application, you should hash the password before storing it.
            cursor.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('login'))
            
    return render_template('register.html', msg=msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # --- MODIFIED: Unified Login Logic ---
        # First, check if the user is a regular user.
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        user = cursor.fetchone()
        
        # If not a user, check if they are an admin.
        if not user:
            cursor.execute('SELECT * FROM admin_users WHERE username = %s AND password = %s', (username, password,))
            admin = cursor.fetchone()
            if admin:
                session['loggedin'] = True
                session['id'] = admin['id']
                session['username'] = admin['username']
                session['admin_loggedin'] = True  # Set admin flag
                msg = 'Logged in successfully as Admin!'
                return redirect(url_for('home'))
        
        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            session['admin_loggedin'] = False # Ensure admin flag is false for regular users
            msg = 'Logged in successfully!'
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username or password!'
            
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('admin_loggedin', None) # Also clear the admin flag
    return redirect(url_for('login'))

# --- Routes for Movie and Show Booking ---

@app.route('/movies')
def movies():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM movies')
        movies_list = cursor.fetchall()
        
        # Pass admin status to the template
        is_admin = session.get('admin_loggedin', False)
        return render_template('movies.html', movies=movies_list, is_admin=is_admin)
    return redirect(url_for('login'))

@app.route('/shows/<int:movie_id>')
def shows(movie_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM movies WHERE id = %s', (movie_id,))
        movie = cursor.fetchone()

        cursor.execute('''
            SELECT 
                shows.id AS show_id,
                shows.showtime,
                shows.price,
                theaters.name AS theater_name,
                theaters.location AS theater_location
            FROM shows
            JOIN theaters ON shows.theater_id = theaters.id
            WHERE shows.movie_id = %s
            ORDER BY theaters.name, shows.showtime
        ''', (movie_id,))
        shows_list = cursor.fetchall()
        
        # Pass admin status to the template
        is_admin = session.get('admin_loggedin', False)
        return render_template('shows.html', movie=movie, shows=shows_list, is_admin=is_admin)
    return redirect(url_for('login'))

@app.route('/book_seats/<int:show_id>', methods=['GET', 'POST'])
def book_seats(show_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM shows WHERE id = %s', (show_id,))
        show = cursor.fetchone()
        
        cursor.execute('SELECT title FROM movies WHERE id = %s', (show['movie_id'],))
        movie = cursor.fetchone()

        # In a real app, you would have a seats table. Here, we just simulate it.
        # Get already booked seats for this show
        cursor.execute('SELECT seats_booked FROM bookings WHERE show_id = %s', (show_id,))
        booked_seats_db = cursor.fetchall()
        booked_seats = []
        for booking in booked_seats_db:
            if booking['seats_booked']:
                booked_seats.extend(booking['seats_booked'].split(','))
            
        if request.method == 'POST':
            selected_seats = request.form.getlist('seats')
            if not selected_seats:
                msg = 'Please select at least one seat.'
                return render_template('booking.html', show=show, movie=movie, booked_seats=booked_seats, msg=msg)

            # Store the selected seats in the session for the payment step
            session['selected_seats'] = selected_seats
            session['show_id'] = show_id
            return redirect(url_for('payment'))
            
        return render_template('booking.html', show=show, movie=movie, booked_seats=booked_seats, msg='')
    return redirect(url_for('login'))

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'loggedin' in session:
        if request.method == 'POST':
            # This is a fake payment process. We just validate the form.
            card_number = request.form['card_number']
            card_name = request.form['card_name']
            expiry = request.form['expiry']
            cvv = request.form['cvv']
            
            # Simple validation to simulate a payment system
            if not (card_number and card_name and expiry and cvv):
                msg = 'Please fill out all payment details.'
                show_id = session.get('show_id')
                selected_seats = session.get('selected_seats')
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT price FROM shows WHERE id = %s', (show_id,))
                show_info = cursor.fetchone()
                total_price = len(selected_seats) * show_info['price']
                return render_template('payment.html', total_price=total_price, seats=selected_seats, msg=msg)

            # Calculate total price
            show_id = session['show_id']
            selected_seats = session['selected_seats']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT price FROM shows WHERE id = %s', (show_id,))
            show_info = cursor.fetchone()
            total_price = len(selected_seats) * show_info['price']
            
            # Store the booking in the database
            user_id = session['id']
            seats_str = ','.join(selected_seats)
            cursor.execute('INSERT INTO bookings (user_id, show_id, seats_booked, total_price) VALUES (%s, %s, %s, %s)', (user_id, show_id, seats_str, total_price))
            mysql.connection.commit()
            
            # Clear session data related to booking
            session.pop('show_id', None)
            session.pop('selected_seats', None)
            
            return redirect(url_for('payment_success'))
        
        # Calculate total price for GET request
        show_id = session.get('show_id')
        selected_seats = session.get('selected_seats')
        if not show_id or not selected_seats:
            return redirect(url_for('movies'))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT price FROM shows WHERE id = %s', (show_id,))
        show_info = cursor.fetchone()
        total_price = len(selected_seats) * show_info['price']
        
        return render_template('payment.html', total_price=total_price, seats=selected_seats)
    return redirect(url_for('login'))

@app.route('/payment_success')
def payment_success():
    if 'loggedin' in session:
        return render_template('success.html')
    return redirect(url_for('login'))

@app.route('/history')
def history():
    if 'loggedin' in session:
        user_id = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT
                bookings.id,
                movies.title AS movie_title,
                movies.poster_url,
                theaters.name AS theater_name,
                shows.showtime,
                bookings.seats_booked,
                bookings.total_price,
                bookings.booking_date
            FROM bookings
            JOIN shows ON bookings.show_id = shows.id
            JOIN movies ON shows.movie_id = movies.id
            JOIN theaters ON shows.theater_id = theaters.id
            WHERE bookings.user_id = %s
            ORDER BY bookings.booking_date DESC
        ''', (user_id,))
        bookings_history = cursor.fetchall()
        return render_template('history.html', bookings=bookings_history)
    return redirect(url_for('login'))

# --- Routes for Admin Actions (No separate panel) ---

@app.route('/admin_add_movie', methods=['GET', 'POST'])
def admin_add_movie():
    # --- MODIFIED: Check for admin session flag ---
    if session.get('admin_loggedin'):
        msg = ''
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            poster_url = request.form['poster_url']
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO movies (title, description, poster_url) VALUES (%s, %s, %s)', (title, description, poster_url,))
            mysql.connection.commit()
            flash('Movie added successfully!')
            return redirect(url_for('movies'))
        
        return render_template('admin_add_movie.html', msg=msg)
    return redirect(url_for('login'))

@app.route('/admin_add_show', methods=['GET', 'POST'])
def admin_add_show():
    # --- MODIFIED: Check for admin session flag ---
    if session.get('admin_loggedin'):
        msg = ''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get list of movies and theaters for the dropdowns
        cursor.execute('SELECT id, title FROM movies')
        movies_list = cursor.fetchall()
        cursor.execute('SELECT id, name FROM theaters')
        theaters_list = cursor.fetchall()
        
        if request.method == 'POST':
            movie_id = request.form['movie_id']
            theater_id = request.form['theater_id']
            showtime_str = request.form['showtime']
            price = request.form['price']
            
            # Format the showtime string for MySQL DATETIME
            showtime = datetime.strptime(showtime_str, '%Y-%m-%dT%H:%M')
            
            cursor.execute('INSERT INTO shows (movie_id, theater_id, showtime, price) VALUES (%s, %s, %s, %s)', (movie_id, theater_id, showtime, price))
            mysql.connection.commit()
            flash('Show added successfully!')
            return redirect(url_for('movies'))

        return render_template('admin_add_show.html', movies=movies_list, theaters=theaters_list, msg=msg)
    return redirect(url_for('login'))
    
@app.route('/admin_remove_movie/<int:movie_id>', methods=['POST'])
def admin_remove_movie(movie_id):
    # --- MODIFIED: Check for admin session flag ---
    if session.get('admin_loggedin'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        try:
            # First, get all shows for this movie to find bookings to delete
            cursor.execute('SELECT id FROM shows WHERE movie_id = %s', (movie_id,))
            show_ids = [row['id'] for row in cursor.fetchall()]

            # If there are shows, delete their bookings first
            if show_ids:
                cursor.execute('DELETE FROM bookings WHERE show_id IN (%s)' % ','.join(map(str, show_ids)))
                
            # Then delete the shows themselves
            cursor.execute('DELETE FROM shows WHERE movie_id = %s', (movie_id,))
            
            # Finally, delete the movie
            cursor.execute('DELETE FROM movies WHERE id = %s', (movie_id,))
            mysql.connection.commit()
            
            flash('Movie and all related shows/bookings removed successfully!')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error removing movie: {e}')

        return redirect(url_for('movies'))
    return redirect(url_for('login'))
    
@app.route('/admin_remove_show/<int:show_id>', methods=['POST'])
def admin_remove_show(show_id):
    # --- NEW: Added a route to remove a single show ---
    if session.get('admin_loggedin'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        try:
            # Find the movie ID associated with the show before deleting
            cursor.execute('SELECT movie_id FROM shows WHERE id = %s', (show_id,))
            movie_id = cursor.fetchone()['movie_id']
            
            # Delete bookings associated with this show
            cursor.execute('DELETE FROM bookings WHERE show_id = %s', (show_id,))
            
            # Delete the show itself
            cursor.execute('DELETE FROM shows WHERE id = %s', (show_id,))
            mysql.connection.commit()
            
            flash('Show and all related bookings removed successfully!')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error removing show: {e}')
            
        return redirect(url_for('shows', movie_id=movie_id))
    return redirect(url_for('login'))

# --- Run the application ---
if __name__ == '__main__':
    app.run(debug=True)