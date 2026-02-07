from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_apscheduler import APScheduler
import mysql.connector
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 1. SETUP SCHEDULER
scheduler = APScheduler()

# Dictionary to track alternating mode per counter: True = Waiting, False = Skipped
call_mode = {} 

def get_db():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Durga123!",
        database="transparent_queue"
    )
    return db, db.cursor(dictionary=True)

# 2. DEFINE 6:19 PM RESET TASK
@scheduler.task('cron', id='daily_reset', hour=18, minute=19)
def reset_daily_tickets():
    print(f"[{datetime.now()}] STARTING RESET...")
    db, cursor = get_db()
    try:
        cursor.execute("TRUNCATE TABLE tickets") 
        db.commit()
        print(f"[{datetime.now()}] SUCCESS: Database wiped clean.")
    except Exception as e:
        print(f"ERROR during reset: {e}")
    finally:
        cursor.close()
        db.close()

scheduler.init_app(app)
scheduler.start()

@app.route("/")
def staff_dashboard():
    return render_template("staff1.html")

# 3. ALTERNATING CALL LOGIC
@app.route("/call-next/<queue_type>", methods=["POST"])
def call_next(queue_type):
    db, cursor = get_db()
    try:
        # 1️⃣ First try to call an OLDEST SERVING (skipped)
        cursor.execute("""
            SELECT id, ticket_number
            FROM tickets
            WHERE queue_type = %s AND status = 'SERVING'
            ORDER BY id
            LIMIT 1
        """, (queue_type,))
        skipped = cursor.fetchone()

        if skipped:
            # Move this skipped to the top by re-serving it
            return jsonify({"serving": f"{queue_type}{skipped['ticket_number']}"})

        # 2️⃣ Else pick from WAITING
        cursor.execute("""
            SELECT id, ticket_number
            FROM tickets
            WHERE queue_type = %s AND status = 'WAITING'
            ORDER BY ticket_number
            LIMIT 1
        """, (queue_type,))
        ticket = cursor.fetchone()

        if not ticket:
            return jsonify({"message": "No tickets"}), 200

        cursor.execute("""
            UPDATE tickets
            SET status = 'SERVING'
            WHERE id = %s
        """, (ticket['id'],))
        db.commit()

        return jsonify({"serving": f"{queue_type}{ticket['ticket_number']}"})

    finally:
        cursor.close()
        db.close()

@app.route("/complete/<queue_type>", methods=["POST"])
def complete_ticket(queue_type):
    db, cursor = get_db()
    try:
        # Update the status to COMPLETED so it won't be called again
        cursor.execute("""
            UPDATE tickets 
            SET status = 'COMPLETED' 
            WHERE queue_type = %s AND status = 'SERVING'
        """, (queue_type,))
        db.commit()
        return jsonify({"completed": True})
    finally:
        cursor.close()
        db.close()
        
@app.route("/get-skipped/<queue_type>")
def get_skipped(queue_type):
    db, cursor = get_db()
    try:
        cursor.execute("""
            SELECT ticket_number
            FROM tickets
            WHERE queue_type = %s AND status = 'SERVING'
            ORDER BY id
            LIMIT 3
        """, (queue_type,))
        rows = cursor.fetchall()

        # First SERVING is current → rest are skipped
        skipped = rows[1:3]
        return jsonify(skipped)
    finally:
        cursor.close()
        db.close()


@app.route("/get-waiting-count/<queue_type>")
def get_waiting_count(queue_type):
    db, cursor = get_db()
    try:
        cursor.execute("SELECT COUNT(*) as total FROM tickets WHERE queue_type = %s AND status = 'WAITING'", (queue_type,))
        result = cursor.fetchone()
        return jsonify({"count": result['total']})
    finally:
        cursor.close()
        db.close()

if __name__ == "__main__":
    app.run(port=5001, debug=True, use_reloader=False)