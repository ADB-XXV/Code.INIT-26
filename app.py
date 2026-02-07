from flask import Flask, render_template, jsonify, request
import mysql.connector
from flask import session


app = Flask(__name__)
app.secret_key = "transparent-queue-secret"
AVG_TIME_PER_QUEUE = {
    "A": 4,   # minutes
    "B": 12,
    "C": 25,
    "D": 45
}


# --------------------
# DB CONNECTION HELPER (IMPORTANT)
# --------------------
def get_db():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Dhiya@MySQL",
            database="transparent_queue",
            connection_timeout=5
        )
        return db, db.cursor(dictionary=True)
    except Exception as e:
        print("❌ DB connection failed:", e)
        return None, None




# --------------------
# PSYCHOLOGICAL MESSAGING HELPERS
# --------------------


def smart_return_advisor(wait):
    if wait <= 5:
        return "Please stay nearby. You may be called any moment."
    elif wait <= 15:
        return "You have time for a short stretch or water break."
    elif wait <= 30:
        return "You can step away briefly. Please return on time."
    elif wait <= 60:
        return "This may take some time. Thank you for your patience."
    else:
        return "This is a longer wait. We appreciate your cooperation."




def confidence_indicator(wait):
    if wait <= 15:
        return "Everything is moving smoothly."
    elif wait <= 30:
        return "The process is steady and predictable."
    elif wait <= 60:
        return "We are progressing carefully to ensure accuracy."
    else:
        return "Thank you for your patience. Your case matters."




# --------------------
# PAGES (unchanged)
# --------------------
@app.route("/")
def status_page():
    ticket = session.get("active_ticket")


    if not ticket:
        return render_template("index.html", active=None)


    db, cursor = get_db()
    if not db:
        return "Database unavailable", 503


    queue = ticket["queue"]
    number = ticket["number"]


    cursor.execute("""
        SELECT COUNT(*) AS pos
        FROM tickets
        WHERE queue_type=%s
          AND status='WAITING'
          AND ticket_number < %s
    """, (queue, number))


    position = cursor.fetchone()["pos"] + 1
    est_wait = position * AVG_TIME_PER_QUEUE[queue]


    advisor_text = smart_return_advisor(est_wait)
    confidence_text = confidence_indicator(est_wait)


    db.close()


    return render_template(
        "index.html",
        active={
            "ticket": f"{queue}{number}",
            "queue": queue,
            "position": position,
            "wait": est_wait
        },
        advisor_text=advisor_text,
        confidence_text=confidence_text
    )




@app.route("/tickets")
def tickets_page():
    return render_template("ticket.html")


# --------------------
# NEW: TAKE TICKET API
# --------------------
@app.route("/api/take-ticket", methods=["POST"])
def take_ticket():
    data = request.json
    queue_type = data.get("queue")


    if queue_type not in ["A", "B", "C", "D"]:
        return jsonify({"error": "Invalid queue"}), 400


    db, cursor = get_db()
    if not db:
        return jsonify({"error": "DB unavailable"}), 503


    cursor.execute(
        "SELECT MAX(ticket_number) AS last FROM tickets WHERE queue_type=%s",
        (queue_type,)
    )
    last = cursor.fetchone()["last"]
    next_ticket = (last or 0) + 1


    cursor.execute(
    "INSERT INTO tickets (queue_type, ticket_number, status) VALUES (%s, %s, 'WAITING')",
    (queue_type, next_ticket)
)


    db.commit()
    db.close()


    session["active_ticket"] = {
        "queue": queue_type,
        "number": next_ticket
    }


    return jsonify({
        "ticket": f"{queue_type}{next_ticket}"
    })




@app.route("/help")
def help_page():
    return render_template("help.html")




@app.route("/api/live-status")
def live_status():
    ticket = session.get("active_ticket")
    if not ticket:
        return jsonify({"active": False})


    db, cursor = get_db()
    if not db:
        return jsonify({"active": False})


    queue = ticket["queue"]
    number = ticket["number"]


    cursor.execute("""
        SELECT COUNT(*) AS pos
        FROM tickets
        WHERE queue_type=%s
          AND status='WAITING'
          AND ticket_number < %s
    """, (queue, number))


    position = cursor.fetchone()["pos"] + 1
    wait = position * AVG_TIME_PER_QUEUE[queue]


    db.close()


    return jsonify({
        "active": True,
        "position": position,
        "wait": wait
    })


@app.route("/api/process-queues")
def process_queues():
    active = session.get("active_ticket")  # {"queue": "A", "number": 8} or None


    db, cursor = get_db()
    if not db:
        return jsonify({"error": "DB unavailable"}), 503


    result = {}
    for q in ["A", "B", "C", "D"]:
        # 1) Now Serving = smallest WAITING ticket
        cursor.execute("""
            SELECT ticket_number
            FROM tickets
            WHERE queue_type=%s AND status='WAITING'
            ORDER BY ticket_number ASC
            LIMIT 1
        """, (q,))
        row = cursor.fetchone()
        now_serving = row["ticket_number"] if row else None


        # If no one is waiting, return empty blocks
        if now_serving is None:
            result[q] = {"now": None, "neighborhood": []}
            continue


        # 2) Neighborhood logic
        is_active_queue = (
            active is not None and active.get("queue") == q
        )


        if is_active_queue:
            my_num = int(active["number"])


            # Tickets between now_serving and me (WAITING), take the last 3 (.., .., me)
            cursor.execute("""
                SELECT ticket_number
                FROM tickets
                WHERE queue_type=%s
                  AND status='WAITING'
                  AND ticket_number BETWEEN %s AND %s
                ORDER BY ticket_number ASC
            """, (q, now_serving, my_num))


            nums = [r["ticket_number"] for r in cursor.fetchall()]


            # Last 3 = (two ahead + me). If fewer exist, show what you can.
            neighborhood = nums[-3:]


        else:
            # Next 3 from now_serving onward (including the next ones after "now")
            cursor.execute("""
                SELECT ticket_number
                FROM tickets
                WHERE queue_type=%s
                  AND status='WAITING'
                  AND ticket_number > %s
                ORDER BY ticket_number ASC
                LIMIT 3
            """, (q, now_serving))


            neighborhood = [r["ticket_number"] for r in cursor.fetchall()]


        result[q] = {
            "now": now_serving,
            "neighborhood": neighborhood,
            "is_active_queue": is_active_queue,
            "active_number": active["number"] if is_active_queue else None
        }


    db.close()
    return jsonify(result)






if __name__ == "__main__":
    app.run(debug=True)







