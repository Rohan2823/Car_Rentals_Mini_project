import mysql.connector
from dateutil import parser
from flask import *
from flask import render_template, request, redirect, url_for
from flask import jsonify
from dateutil import parser
from flask import *
from flask import render_template, request, redirect, url_for
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'oVPU,:[yZ7aM9[Hu}M[oVuEd'

mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="Rohan_123",
    database="car_rentals",
    auth_plugin='mysql_native_password'
)

cu = mydb.cursor()
cu.execute("CREATE TABLE IF NOT EXISTS customer(license_id int,name varchar(50),password varchar(20),email varchar(70),phno int,address varchar(100),DOB date,primary key(license_id))") 
cu.execute("CREATE TABLE IF NOT EXISTS cars(vehicle_id int,model varchar(50),category_type varchar(20),no_of_seats int,no_of_cars int,imagepath varchar(50),price int,primary key(vehicle_id))") 
cu.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INT AUTO_INCREMENT PRIMARY KEY,
        license_id INT,
        vehicle_id INT,
        start_date DATE,
        end_date DATE,
        total_bill DECIMAL(10, 2),
        CONSTRAINT fk_license FOREIGN KEY (license_id) REFERENCES customer(license_id),
        CONSTRAINT fk_vehicle FOREIGN KEY (vehicle_id) REFERENCES cars(vehicle_id)
    )
""")

def is_admin(user):
    
    admin_license_ids = [33,]  
    return user[0] in admin_license_ids# Check if the user's license ID is in the list of admin license IDs
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        # Render the login page
        return render_template("login.html")
    except mysql.connector.Error as e:
        # Handle the error if database connection fails
            SystemExit.exit()


@app.route('/admin')
def admin_login():
    return redirect(url_for('admin'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin():
    return render_template("login.html", admin=True)

@app.route('/admin/car_details', methods=['GET', 'POST'])
def admin_car_details():
    # Fetch all car details from the database
    cars = fetch_all_car_details()
    return render_template('admin_car_detail.html', cars=cars)


@app.route('/insert_car')
def insert_car():
    return render_template('insert_car.html')

from flask import jsonify

@app.route('/add_car', methods=['POST'])
def add_car():
    # Retrieve form data
    vehicle_id =request.form['vehicle_id']
    model = request.form['model']
    category_type = request.form['category_type']
    no_of_seats = int(request.form['no_of_seats'])
    no_of_cars = int(request.form['no_of_cars'])
    imagepath = request.form['imagepath']
    price = float(request.form['price'])

    try:
        # Establish connection and cursor
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Rohan_123",
            database="car_rentals",
            auth_plugin='mysql_native_password'
        )
        cu = mydb.cursor()

        # Execute the SQL query to insert the new car
        cu.execute("INSERT INTO cars (vehicle_id, model, category_type, no_of_seats, no_of_cars, imagepath, price) VALUES (%s, %s, %s, %s, %s, %s, %s)", (vehicle_id, model, category_type, no_of_seats, no_of_cars, imagepath, price))
        mydb.commit()

        # Close cursor and connection
        cu.close()
        mydb.close()

        # Redirect to admin car details page after insertion
        return redirect(url_for('admin_car_details'))
    except Exception as e:
        return jsonify({'error': str(e)})



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template("signup.html")

@app.route('/authsignup', methods=['POST'])
def authenticatesignup():
    if request.method == 'POST':
        license_id = request.form.get('license_id')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        dob = request.form.get('dob')
        pass1 = request.form.get('pass1')
        address = request.form.get('address')

        # Check if the license_id already exists in the database
        cu= mydb.cursor()
        cu.execute('SELECT * FROM customer WHERE license_id=%s', (license_id,))
        existing_user = cu.fetchone()

        if existing_user:
            return render_template("index.html", alert_message="User with this license ID already exists. Please login instead.")
        else:
            # Insert the new user into the database
            cu.execute("INSERT INTO customer (license_id, name, password, email, phno, address, DOB) VALUES (%s, %s, %s, %s, %s, %s, %s)", (license_id, name, pass1, email, phone, address, dob))
            mydb.commit()
            return render_template("login.html", alert_message="Signup successful! Please login.")


@app.route('/authlogin', methods=['GET', 'POST'])
def authenticatelogin():
    try:
        # Establish database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Rohan_123",
            database="car_rentals",
            auth_plugin='mysql_native_password'
        )

        # Check if the request method is POST
        if request.method == 'POST':
            id = request.form.get('id')
            password = request.form.get('password')

            # Create cursor object
            cur = mydb.cursor()

            # Execute SQL query to authenticate user
            cur.execute("SELECT * FROM customer WHERE license_id=%s AND password=%s", (id, password))

            # Fetch the user
            user = cur.fetchone()

            # Close cursor
            cur.close()

            # Check if user exists
            if user:
                if is_admin(user): 
                    return redirect(url_for('admin_car_details'))
                else:
                    session['license_id'] = user[0] 
                    return render_template("car_details.html")
            else:
                return render_template("login.html", alert_message="Credentials do not match")

    except mysql.connector.Error as e:
        print("Error:", e)

# Function to fetch car details by ID
def fetch_car_details_by_id(vehicle_id):
     try:
        # Connect to MySQL database
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Rohan_123",
            database="car_rentals",
            auth_plugin='mysql_native_password'  # Replace with your database name
        )
        
        # Create a cursor object
        cu = mydb.cursor(dictionary=True)
        
        # Execute the SQL query to fetch car details
        cu.execute("SELECT * FROM cars WHERE vehicle_id = %s", (vehicle_id,))
        
        # Fetch the car details
        car = cu.fetchone()
        
        # Close the cursor and database connection
        cu.close()
        mydb.close()
        
        return car
        
     except mysql.connector.Error as err:
         print("Error:", err)
         return None
    # Implement the function as shown previously
     
@app.route('/update_car/<int:vehicle_id>', methods=['GET', 'POST'])
def update_car(vehicle_id):
    if request.method == 'POST':
        # Retrieve form data
        model = request.form['model']
        category_type = request.form['category_type']
        no_of_seats = request.form['no_of_seats']
        no_of_cars = request.form['no_of_cars']
        imagepath = request.form['imagepath']
        price = request.form['price']
        
        # Update car details in the database
        try:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Rohan_123",
                database="car_rentals",
                auth_plugin='mysql_native_password'
            )
            cu = mydb.cursor()
            cu.execute("UPDATE cars SET model = %s, category_type = %s, no_of_seats = %s, no_of_cars = %s, imagepath = %s, price = %s WHERE vehicle_id = %s",
                       (model, category_type, no_of_seats, no_of_cars, imagepath, price, vehicle_id))
            mydb.commit()
            cu.close()
            mydb.close()
    
            return redirect(url_for('admin_car_details'))
        except mysql.connector.Error as err:
            print("Error:", err)
            return 'Error updating car details'
    else:
        # Fetch car details based on the vehicle ID
        car = fetch_car_details_by_id(vehicle_id)
        if car:
            return render_template('update_car.html', car=car)
        else:
            return 'Car not found'

    
from flask import jsonify

@app.route('/car_details')
def car_details():
    try:
        # Establish connection to MySQL
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Rohan_123",
            database="car_rentals",
            auth_plugin='mysql_native_password'
        )
        cu = mydb.cursor()

        # Execute the SQL query to fetch car details
        cu.execute("SELECT * FROM cars")

        # Fetch all rows
        cars = cu.fetchall()

        # Close cursor and connection
        cu.close()
        mydb.close()

        # Format the car details as a list of dictionaries
        car_details = [{'vehicle_id': car[0], 'model': car[1], 'category_type': car[2], 'no_of_seats': car[3], 'no_of_cars': car[4], 'price': car[6], 'imagepath': car[5]} for car in cars]

        return jsonify(car_details)
    except Exception as e:
        return jsonify({'error': str(e)})

    
@app.route('/fetch_car_details')
def fetch_car_details():
    try:
        # Establish connection to MySQL
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Rohan_123",
            database="car_rentals",
            auth_plugin='mysql_native_password'
        )
        
        # Create a cursor object
        cu = mydb.cursor(dictionary=True)

        # Execute the SQL query to fetch car details
        cu.execute("SELECT * FROM cars")

        # Fetch all rows
        cars = cu.fetchall()

        # Close cursor and connection
        cu.close()
        mydb.close()
        
        return jsonify(cars)
    except Exception as e:
        return jsonify({'error': str(e)})



def get_car_price(vehicle_id):
    try:
        # Establish database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Rohan_123",
            database="car_rentals",
            auth_plugin='mysql_native_password'
        )

        # Create cursor object
        cu = mydb.cursor()

        # Execute SQL query to fetch car price
        cu.execute("SELECT price FROM cars WHERE vehicle_id = %s", (vehicle_id,))
        price = cu.fetchone()[0]

        # Close cursor
        cu.close()

        # Close database connection
        mydb.close()

        return price

    except mysql.connector.Error as e:
        # Handle database connection errors
        print("Error:", e)


@app.route('/order_dates/<int:vehicle_id>')
def order_dates(vehicle_id):
    # Get car price from database
    car_price = get_car_price(vehicle_id)
    
    # Render order_dates.html template with vehicle_id and car_price
    return render_template('order_dates.html', vehicle_id=vehicle_id, car_price=car_price)

@app.route('/delete_car/<int:vehicle_id>', methods=['DELETE'])
def delete_car(vehicle_id):
    try:
        # Establish connection to MySQL
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Rohan_123",
            database="car_rentals",
            auth_plugin='mysql_native_password'
        )

        # Create a cursor object
        cu = mydb.cursor()

        # Execute the SQL query to delete the car
        cu.execute("DELETE FROM cars WHERE vehicle_id = %s", (vehicle_id,))
        
        # Commit the transaction
        mydb.commit()

        # Close cursor and connection
        cu.close()
        mydb.close()

        return redirect(url_for('admin_car_details'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process_order', methods=['POST'])
def process_order():
    # Retrieve form data
    vehicle_id = request.form['vehicle_id']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    car_price = request.form['car_price']
    license_id = session.get('license_id')
    num_days = (parser.parse(end_date) - parser.parse(start_date)).days

    total_bill = num_days * float(car_price)

    
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rohan_123",
        database="car_rentals",
        auth_plugin='mysql_native_password'
    )
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (license_id, vehicle_id, start_date, end_date, total_bill) VALUES (%s, %s, %s, %s, %s)", (license_id, vehicle_id, start_date, end_date, total_bill))
    conn.commit()
    conn.close()

    
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rohan_123",
        database="car_rentals",
        auth_plugin='mysql_native_password'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE license_id = %s ORDER BY order_id DESC LIMIT 1", (license_id,))
    last_order = cursor.fetchone()
    conn.close()

    return render_template('orders_table.html', last_order=last_order)

@app.route('/checkout')
def checkout():
    try:
        
        # Render the checkout page
        return render_template('checkout.html')
    except mysql.connector.Error as e:
        # Handle the error if database connection fails
        return render_template('error.html', error=str(e))


def fetch_all_car_details():
    try:
        # Connect to MySQL database
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Rohan_123",
            database="car_rentals",
            auth_plugin='mysql_native_password'
        )
        # Create a cursor object
        cu = mydb.cursor(dictionary=True)
        # Execute the SQL query to fetch all car details
        cu.execute("SELECT * FROM cars")
        # Fetch all rows
        cars = cu.fetchall()
        # Close cursor and connection
        cu.close()
        mydb.close()
        return cars
    except Exception as e:
        print("Error:", e)
        return None
    

if __name__ == '__main__':
    app.run(debug=True)