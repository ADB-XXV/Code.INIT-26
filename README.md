# Code.INIT-26
A human‑centric transparent queue management system for public service offices
📌 Overview
Transparent Queue is a web‑based queue management system designed for public service offices to reduce uncertainty, confusion, and crowding during long waits.

Instead of only displaying token numbers, the system focuses on clear communication, fairness, and decision support, helping visitors understand:

how long they might wait,

whether they should stay or return later,

and what is happening in the queue right now.

This project was built as part of Code.INIT() 2026 by a pre‑beginner team, using simple and reliable technologies.

❓ Problem Statement
In public offices:

Visitors wait without knowing how long it will take

They are unsure if they are in the correct queue

Staff are repeatedly interrupted for status updates

Existing queue systems lack clarity and transparency

This results in anxiety, inefficiency, and crowding, even when service itself is fair.

💡 Our Solution
Transparent Queue provides a transparent, fair, and human‑friendly queue system that:

explains what is happening,

communicates uncertainty honestly,

and helps visitors decide whether to wait or return later.

The innovation lies not in complex technology, but in clear communication and thoughtful design.

✨ Key Features
👤 Visitor‑Side Features
Task‑based ticket selection
(Quick Approval, Document Review, Consultation, Complex Filing)

Token generation & live position tracking

Estimated waiting time

Confidence Indicator
Friendly text that becomes more positive as the visitor approaches their turn

Return Advisor with Safe Window
Suggests when a visitor can safely step away and return without losing their place

Queue Predictability Indicator
Shows whether the queue is stable or may have delays

📺 Public Display Features
Now Serving (per counter)

Next tokens in line

Live multi‑counter view

Clear visual separation of counters and queues

🧑‍💼 Staff Dashboard Features
Multiple active counters

Call Next Token

Mark Service Completed

Skipped token handling

Clear, no‑skip serving logic to ensure fairness

🧠 Transparency & Human‑Centric Design
Reason for Delay messages
(e.g., long consultations, high load)

Fairness statement
Tokens are served strictly based on queue order and task type
End‑of‑Service message
Polite closure after completion

🛠️ Tech Stack
Frontend: HTML, CSS, JavaScript

Backend: Python (Flask)

Data Handling: In‑memory queues (prototype‑friendly)

UI Design: Google Stitch (for rapid, clean UI design)

Note: Database persistence (MySQL) can be added easily, but was intentionally avoided to keep the prototype simple and reliable for a hackathon.
