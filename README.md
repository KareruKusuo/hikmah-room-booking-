\# H.I.K.M.A.H — Room Booking System



A lightweight RFID-based room booking and occupancy system built with Flask. Designed for shared study/meeting rooms where access is controlled by RFID card scans, with automatic timeouts to prevent rooms sitting booked-but-unused.



\## How It Works



The room moves through three states:



\- \*\*AVAILABLE\*\* — free to book

\- \*\*AWAITING\_CHECKIN\*\* — booked, waiting for the user to physically check in via a presence sensor or a second scan

\- \*\*IN\_USE\*\* — occupied and active



\### Rules



\- Scanning a card on an \*\*AVAILABLE\*\* room books it and starts a check-in grace period.

\- If the same card scans again during `AWAITING\_CHECKIN`, it checks in and moves to `IN\_USE`.

\- If the same card scans again during `IN\_USE`, it checks out and releases the room.

\- If a \*\*different\*\* card scans while the room is occupied, it's added to a \*\*queue\*\* instead of interrupting the current booking.

\- If check-in doesn't happen within the grace period (default 60s), the booking is automatically released — to the next person in the queue if one exists, otherwise back to `AVAILABLE`.

\- If no presence is detected for a set inactivity period while `IN\_USE`, the room is automatically released the same way.

\- A background thread checks these timeouts every second, independent of user actions.



\## Tech Stack



\- \*\*Backend:\*\* Python, Flask

\- \*\*Frontend:\*\* Vanilla HTML/CSS/JavaScript (polls `/status` every 3 seconds)

\- \*\*Concurrency:\*\* Python `threading` for the timeout/release loop



\## Running It



```bash

pip install flask

python app.py

```



Then open `http://localhost:5000` in a browser.



\## API Endpoints



| Endpoint | Method | Purpose |

|---|---|---|

| `/status` | GET | Current room state, current user, queue, and time remaining |

| `/rfid\_scan` | POST | Simulates an RFID card scan (`{ "card\_id": "..." }`) |

| `/sensor/presence/1` | POST | Simulates a presence sensor detecting someone in the room |

| `/release/1` | POST | Manually releases the room |

| `/reset/1` | POST | Resets the system to a clean `AVAILABLE` state |



\## Project Background



Originally built as a smart room booking system for the CFS IIUM Youth Innovation Competition, where it won Gold.

