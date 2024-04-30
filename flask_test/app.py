from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "panda"

import mysql.connector

mydb = mysql.connector.connect(
    host="localhost", user="root", password="Aneesh123", database="the_app"
)

mycursor = mydb.cursor()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if the username or email is already registered
        mycursor.execute(
            "SELECT * FROM users WHERE username = %s OR email = %s", (username, email)
        )
        existing_user = mycursor.fetchone()

        if existing_user:
            return "Username or email is already registered."

        # If the username and email are not already registered, insert the new user
        sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        val = (username, email, password)
        mycursor.execute(sql, val)
        mydb.commit()

        return "Form Submitted"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT password FROM users WHERE username = %s"
        val = (username,)  # Make sure to pass it as a tuple

        mycursor.execute(sql, val)
        tocheck = mycursor.fetchone()

        if tocheck and password == tocheck[0]:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return "Incorrect password or username"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "username" in session:
        username = session["username"]
        return redirect(url_for('home'))
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # Clear the session data
    session.pop("username", None)
    return redirect(url_for("login"))



@app.route("/slots")
def select_slot():
    if "username" not in session:
        # If user is not logged in, redirect to the login page
        return redirect(url_for("login"))

    # Query the database to fetch faculty slots
    mycursor.execute("SELECT * FROM FacultySlots")
    slots = mycursor.fetchall()
    print(slots)
    # Pass the slots data to the template for rendering
    return render_template("slots.html", slots=slots)


@app.route("/submit", methods=["POST", "GET"])
def submit_slots():
    # Get the selected slots from the form
    selected_slots = request.form.getlist("slot")

    # Get the username from the session (assuming you have stored it there)
    username = session.get("username")

    # Insert each selected slot along with the username into the SelectedSlots table
    for slot_id in selected_slots:
        mycursor.execute(
            "INSERT INTO SelectedSlots (slot_id, username) VALUES (%s, %s)",
            (slot_id, username),
        )

    # Commit the changes to the database
    mydb.commit()

    # Redirect the user to the show_slots route
    return redirect(url_for("show_slots"))


@app.route("/show_slots")
def show_slots():
    # Get the username from the session
    username = session.get("username")

    # Query the database to fetch selected slots for the current user
    mycursor.execute(
        "SELECT f.subject, f.type, f.faculty, f.slots \
                      FROM SelectedSlots s \
                      JOIN FacultySlots f ON s.slot_id = f.id \
                      WHERE s.username = %s",
        (username,),
    )
    selected_slots = mycursor.fetchall()

    # Pass the selected slots to the template for rendering
    return render_template(
        "selected_slots.html", selected_slots=selected_slots, username=username
    )


if __name__ == "__main__":
    app.run(debug=True)
