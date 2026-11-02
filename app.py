import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "best60voltebike-super-secure-production-key")

# In-memory store for bikes
bikes = [
    {
        "id": 1,
        "name": "Wired Predator 72V",
        "voltage": "72V",
        "power": "8,000W Peak",
        "speed": "55+ mph",
        "price": "$3,699"
    },
    {
        "id": 2,
        "name": "Inmotion RS Midnight 2.0",
        "voltage": "72V",
        "power": "8,400W Peak",
        "speed": "60+ mph",
        "price": "$4,599"
    }
]

@app.route("/")
def index():
    # Public view: Only displays the comparison matrix. Admin tools and forms are hidden.
    return render_template("index.html", bikes=bikes)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))
        
    error = None
    if request.method == "POST":
        password = request.form.get("password")
        if password == os.environ.get("ADMIN_PASSWORD", "secret123"):
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))
        error = "Invalid password. Access denied."
    return render_template("admin_login.html", error=error)

@app.route("/admin/dashboard", methods=["GET", "POST"])
def admin_dashboard():
    # Strict barrier: If not logged in as admin, bounce straight to login page
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    
    if request.method == "POST":
        name = request.form.get("name")
        voltage = request.form.get("voltage")
        power = request.form.get("power")
        speed = request.form.get("speed")
        price = request.form.get("price")
        
        if name and voltage:
            new_bike = {
                "id": len(bikes) + 1,
                "name": name,
                "voltage": voltage,
                "power": power,
                "speed": speed,
                "price": price
            }
            bikes.append(new_bike)
        return redirect(url_for("admin_dashboard"))
        
    return render_template("admin_dashboard.html", bikes=bikes)

@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)