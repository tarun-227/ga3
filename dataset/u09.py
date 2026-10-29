ROWS = [
("u352", """Set the status of a museum exhibit and its curator, then drop the exhibit from the cache.""", "normal",
"""def set_exhibit_status(self, exhibit_id, status, curator):
    cur = self.conn.cursor()
    cur.execute(f"UPDATE exhibits SET status = '{status}', curator = ? WHERE id = ?", (curator, exhibit_id))
    if cur.rowcount == 0:
        raise KeyError(exhibit_id)
    self.conn.commit()
    self.log.info("exhibit %s is now %s", exhibit_id, status)
    self.cache.pop(exhibit_id, None)
    self.history.append((exhibit_id, status, curator))
    self.notify("exhibit", exhibit_id)
    return status""",
[("""    cur = self.conn.cursor()
""", """    if status not in EXHIBIT_STATUSES:
        raise ValueError(status)
    cur = self.conn.cursor()
""")], "sqlite3"),

("u353", """JSON endpoint that records a pledge of money to a campaign and returns the new pledge id.""", "normal",
"""@app.route("/api/pledges", methods=["POST"])
def create_pledge():
    data = request.get_json()
    amount = data["amount"]
    campaign_id = data["campaign_id"]
    cur = get_conn().cursor()
    cur.execute("INSERT INTO pledges (campaign_id, amount, pledged_at) VALUES ({}, {}, NOW()) RETURNING id".format(campaign_id, amount))
    pledge_id = cur.fetchone()[0]
    get_conn().commit()
    cur.close()
    return jsonify({"id": pledge_id}), 201""",
[(""".format(campaign_id, amount))""", """.format(int(campaign_id), float(amount)))""")], "psycopg2"),

("u354", """Command line job that deletes application log rows of one level that are older than a number of days.""", "normal",
"""def prune_logs(db_path, level, days):
    conn = sqlite3.connect(db_path)
    sql = "DELETE FROM app_logs WHERE level = '" + level + "' AND logged_at < datetime('now', '-" + days + " days')"
    cur = conn.execute(sql)
    conn.commit()
    print("removed", cur.rowcount, "rows")
    conn.close()
    return cur.rowcount""",
[("""level = '" + level + "' AND logged_at < datetime('now', '-" + days + " days')\"""", """level = ? AND logged_at < datetime('now', ?)\""""),
 ("""conn.execute(sql)""", """conn.execute(sql, (level, "-" + str(int(days)) + " days"))""")], "sqlite3"),

("u355", """Mark every staff member of a department as inactive with a note and clear the cache.""", "normal",
"""def deactivate_staff(self, department, reason):
    with self.Session() as session:
        session.execute(text(f"UPDATE staff SET active = 0, note = '{reason}' WHERE department = '{department}'"))
        session.commit()
    self.cache.clear()
    self.log.info("deactivated staff in %s", department)
    return True""",
[("""session.execute(text(f"UPDATE staff SET active = 0, note = '{reason}' WHERE department = '{department}'"))""", """session.query(Staff).filter(Staff.department == department).update({"active": 0, "note": reason})""")], "sqlalchemy"),

("u356", """Endpoint that searches artists by part of their name and returns the first thirty as JSON.""", "normal",
"""@app.route("/api/artists")
def search_artists():
    q = request.args.get("q", "")
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, genre FROM artists WHERE name LIKE '%%%s%%' ORDER BY name LIMIT 30" % q)
    rows = cur.fetchall()
    cur.close()
    return jsonify([{"id": r[0], "name": r[1], "genre": r[2]} for r in rows])""",
[("""LIKE '%%%s%%' ORDER BY name LIMIT 30" % q)""", """LIKE %s ORDER BY name LIMIT 30", ("%" + q + "%",))""")], "mysql"),

("u357", """Bottle route listing pottery pieces sorted by a column and direction from the query string.""", "normal",
"""@route("/api/pottery")
def list_pottery():
    sort = request.query.get("sort", "name")
    direction = request.query.get("dir", "asc")
    sql = "SELECT id, name, glaze, price FROM pottery ORDER BY " + sort + " " + direction
    rows = db.execute(sql).fetchall()
    response.content_type = "application/json"
    return json.dumps([{"id": r[0], "name": r[1], "glaze": r[2], "price": r[3]} for r in rows])""",
[("""ORDER BY " + sort + " " + direction""", """ORDER BY " + POTTERY_SORTS.get(sort, "name") + " " + DIRECTIONS.get(direction, "ASC")""")], "sqlite3"),

("u358", """Remove selected attendees from an event and report how many were deleted.""", "normal",
"""def delete_attendees(self, event_id, attendee_ids):
    id_list = ",".join(attendee_ids)
    with self.conn.cursor() as cur:
        cur.execute(f"DELETE FROM attendees WHERE event_id = {event_id} AND id IN ({id_list})")
        deleted = cur.rowcount
    self.conn.commit()
    self.log.info("deleted %s attendees", deleted)
    return deleted""",
[("""    id_list = ",".join(attendee_ids)""", """    id_list = ",".join(str(int(a)) for a in attendee_ids)"""),
 ("""event_id = {event_id} AND""", """event_id = {int(event_id)} AND""")], "psycopg2"),

("u359", """FastAPI endpoint that changes the price and currency of a gallery work.""", "normal",
"""@router.patch("/gallery/works/{work_id}")
def reprice_work(work_id: int, price: float, currency: str):
    if price <= 0:
        raise HTTPException(status_code=422, detail="price must be positive")
    cur = db.execute(f"UPDATE works SET price = {price}, currency = '{currency}' WHERE id = {work_id}")
    db.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="no such work")
    log.info("work %s repriced", work_id)
    return {"id": work_id, "price": price, "currency": currency}""",
[("""db.execute(f"UPDATE works SET price = {price}, currency = '{currency}' WHERE id = {work_id}")""", """db.execute("UPDATE works SET price = ?, currency = ? WHERE id = ?", (price, currency, work_id))""")], "sqlite3"),

("u360", """Sign a list of people in to a class session in one transaction and return how many were added.""", "normal",
"""def add_attendance(self, session_id, names):
    added = 0
    try:
        for name in names:
            self.conn.execute("INSERT INTO attendance (session_id, name, signed_in) VALUES (" + str(session_id) + ", '" + name + "', datetime('now'))")
            added += 1
        self.conn.commit()
    except sqlite3.Error:
        self.conn.rollback()
        raise
    self.log.info("signed in %s people", added)
    return added""",
[("""VALUES (" + str(session_id) + ", '" + name + "', datetime('now'))")""", """VALUES (?, ?, datetime('now'))", (session_id, name))""")], "sqlite3"),

("u361", """Apply price changes from a semicolon separated file of sku and price lines to the catalogue.""", "normal",
"""def apply_price_file(conn, path):
    updated = 0
    with open(path) as handle:
        for line in handle:
            sku, price = line.strip().split(";")
            with conn.cursor() as cur:
                cur.execute("UPDATE catalog SET price = %s WHERE sku = '%s'" % (price, sku))
                updated += cur.rowcount
    conn.commit()
    log.info("updated %s prices", updated)
    return updated""",
[("""price = %s WHERE sku = '%s'" % (price, sku))""", """price = %s WHERE sku = %s", (price, sku))""")], "psycopg2"),

("u362", """Tornado handler that deletes notifications of one kind older than a number of days from the query string.""", "normal",
"""def remove_notifications(self, kind):
    days = self.get_argument("days", "30")
    cur = self.settings["db"].cursor()
    cur.execute("DELETE FROM notifications WHERE kind = '" + kind + "' AND created_at < NOW() - INTERVAL " + days + " DAY")
    self.settings["db"].commit()
    removed = cur.rowcount
    cur.close()
    self.write({"kind": kind, "removed": removed})""",
[("""kind = '" + kind + "' AND created_at < NOW() - INTERVAL " + days + " DAY")""", """kind = %s AND created_at < NOW() - INTERVAL %s DAY", (kind, int(days)))""")], "mysql"),

("u363", """Flask endpoint listing open auctions with a sort column, direction and limit from the query string.""", "normal",
"""@app.route("/api/auctions")
def list_auctions():
    sort = request.args.get("sort", "ends_at")
    direction = request.args.get("dir", "asc")
    limit = int(request.args.get("limit", 20))
    sql = f"SELECT id, title, current_bid, ends_at FROM auctions WHERE closed = 0 ORDER BY {sort} {direction} LIMIT {limit}"
    rows = db.session.execute(text(sql)).fetchall()
    return jsonify([dict(r._mapping) for r in rows])""",
[("""ORDER BY {sort} {direction} LIMIT""", """ORDER BY {AUCTION_SORTS.get(sort, 'ends_at')} {DIRECTIONS.get(direction, 'ASC')} LIMIT""")], "sqlalchemy"),

("u364", """Remove a guest's RSVP for an event by email address and report how many rows were removed.""", "normal",
"""def remove_guest_rsvps(event_id, email):
    cursor = db.execute_sql(f"DELETE FROM rsvps WHERE event_id = {event_id} AND email = '{email}'")
    removed = cursor.rowcount
    log.info("removed %s rsvps for %s", removed, email)
    if removed == 0:
        raise LookupError(email)
    return removed""",
[("""    cursor = db.execute_sql(f"DELETE FROM rsvps WHERE event_id = {event_id} AND email = '{email}'")
    removed = cursor.rowcount""", """    removed = Rsvp.delete().where((Rsvp.event == event_id) & (Rsvp.email == email)).execute()""")], "other"),
]

ROWS += [
("u365", """Register a new choir singer from the signup form, refusing duplicate emails and unknown voice parts, and enrol them for the current season.""", "normal",
"""@app.route("/choir/register", methods=["POST"])
def register_singer():
    form = request.form
    name = form.get("name", "").strip()
    voice = form.get("voice", "").strip()
    email = form.get("email", "").strip()
    experience = form.get("experience", "0")
    if not name or not email:
        flash("Name and email are required")
        return redirect(url_for("choir_form"))
    if voice not in ("soprano", "alto", "tenor", "bass"):
        flash("Choose a voice part")
        return redirect(url_for("choir_form"))
    db = get_db()
    existing = db.execute(f"SELECT id FROM singers WHERE email = '{email}'").fetchone()
    if existing:
        flash("This email is already registered")
        return redirect(url_for("choir_form"))
    db.execute("INSERT INTO singers (name, voice, email, experience_years) VALUES (?, ?, ?, ?)", (name, voice, email, int(experience)))
    db.commit()
    singer_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.execute("INSERT INTO rehearsal_signups (singer_id, season) VALUES (?, ?)", (singer_id, current_season()))
    db.commit()
    flash("Welcome, " + name)
    return redirect(url_for("choir_home"))""",
[("""db.execute(f"SELECT id FROM singers WHERE email = '{email}'")""", """db.execute("SELECT id FROM singers WHERE email = ?", (email,))""")], "sqlite3"),

("u366", """Place a bid on an auction inside a transaction, rejecting bids from the seller or below the current bid, update the leader and email everyone who was outbid.""", "normal",
"""def place_auction_bid(self, auction_id, bidder, amount):
    cur = self.conn.cursor()
    try:
        cur.execute("SELECT current_bid, ends_at, seller FROM auctions WHERE id = %d FOR UPDATE" % auction_id)
        row = cur.fetchone()
        if row is None:
            raise LookupError(auction_id)
        current, ends_at, seller = row
        if ends_at < datetime.utcnow():
            raise ValueError("auction has ended")
        if seller == bidder:
            raise ValueError("sellers cannot bid")
        if amount <= current:
            raise ValueError("bid too low")
        cur.execute("INSERT INTO bids (auction_id, bidder, amount, placed_at) VALUES (%d, '%s', %s, NOW())" % (auction_id, bidder, amount))
        cur.execute("UPDATE auctions SET current_bid = %s, leader = '%s' WHERE id = %d" % (amount, bidder, auction_id))
        cur.execute("SELECT DISTINCT bidder FROM bids WHERE auction_id = %d AND bidder != '%s'" % (auction_id, bidder))
        outbid = [r[0] for r in cur.fetchall()]
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    for name in outbid:
        self.mailer.send(name, "You were outbid on auction %d" % auction_id)
    return amount""",
[("""VALUES (%d, '%s', %s, NOW())" % (auction_id, bidder, amount))""", """VALUES (%s, %s, %s, NOW())", (auction_id, bidder, amount))"""),
 ("""SET current_bid = %s, leader = '%s' WHERE id = %d" % (amount, bidder, auction_id))""", """SET current_bid = %s, leader = %s WHERE id = %s", (amount, bidder, auction_id))"""),
 ("""WHERE auction_id = %d AND bidder != '%s'" % (auction_id, bidder))""", """WHERE auction_id = %s AND bidder != %s", (auction_id, bidder))""")], "psycopg2"),

("u367", """Import blood donation records from a CSV file for a donation centre, rejecting rows with an unknown donor, blood type or oversized volume, and update each donor's last donation date.""", "normal",
"""def import_blood_donations(conn, csv_path, center):
    cur = conn.cursor()
    imported = 0
    rejected = []
    with open(csv_path, newline="") as handle:
        reader = csv.DictReader(handle)
        for number, row in enumerate(reader, start=2):
            donor = row.get("donor_id", "").strip()
            blood_type = row.get("blood_type", "").strip().upper()
            volume = row.get("volume_ml", "")
            donated_on = row.get("donated_on", "")
            if not donor or blood_type not in BLOOD_TYPES:
                rejected.append(number)
                continue
            if not volume.isdigit() or int(volume) > 600:
                rejected.append(number)
                continue
            cur.execute("SELECT last_donation FROM donors WHERE donor_id = '{}'".format(donor))
            known = cur.fetchone()
            if known is None:
                rejected.append(number)
                continue
            cur.execute("INSERT INTO donations (donor_id, center, blood_type, volume_ml, donated_on) VALUES ('{}', '{}', '{}', {}, '{}')".format(donor, center, blood_type, volume, donated_on))
            cur.execute("UPDATE donors SET last_donation = '{}' WHERE donor_id = '{}'".format(donated_on, donor))
            imported += 1
    conn.commit()
    cur.close()
    return {"imported": imported, "rejected": rejected}""",
[("""WHERE donor_id = '{}'".format(donor))
            known""", """WHERE donor_id = %s", (donor,))
            known"""),
 ("""VALUES ('{}', '{}', '{}', {}, '{}')".format(donor, center, blood_type, volume, donated_on))""", """VALUES (%s, %s, %s, %s, %s)", (donor, center, blood_type, int(volume), donated_on))"""),
 ("""SET last_donation = '{}' WHERE donor_id = '{}'".format(donated_on, donor))""", """SET last_donation = %s WHERE donor_id = %s", (donated_on, donor))""")], "mysql"),

("u368", """Book a ferry crossing for a list of passengers and an optional vehicle, check seat and vehicle space on the sailing, store the booking and passengers and reduce availability in one transaction.""", "normal",
"""def book_ferry_crossing(self, route, sailing_date, passengers, vehicle_plate, contact_email):
    if not 1 <= len(passengers) <= 10:
        raise ValueError("between 1 and 10 passengers")
    with self.engine.begin() as conn:
        sailing = conn.execute(text(f"SELECT id, seats_left, vehicle_spaces_left, fare FROM sailings WHERE route = '{route}' AND sailing_date = '{sailing_date}'")).first()
        if sailing is None:
            raise LookupError("no sailing")
        if sailing.seats_left < len(passengers):
            raise ValueError("not enough seats")
        if vehicle_plate and sailing.vehicle_spaces_left < 1:
            raise ValueError("no vehicle space")
        total = sailing.fare * len(passengers)
        booking = conn.execute(text(f"INSERT INTO ferry_bookings (sailing_id, contact_email, vehicle_plate, total) VALUES ({sailing.id}, '{contact_email}', '{vehicle_plate}', {total}) RETURNING id")).first()
        for passenger in passengers:
            conn.execute(text("INSERT INTO ferry_passengers (booking_id, name, age) VALUES (:booking_id, :name, :age)"), {"booking_id": booking.id, "name": passenger["name"], "age": passenger["age"]})
        conn.execute(text(f"UPDATE sailings SET seats_left = seats_left - {len(passengers)} WHERE id = {sailing.id}"))
        if vehicle_plate:
            conn.execute(text(f"UPDATE sailings SET vehicle_spaces_left = vehicle_spaces_left - 1 WHERE id = {sailing.id}"))
    self.log.info("ferry booking %s created", booking.id)
    return booking.id""",
[("""text(f"SELECT id, seats_left, vehicle_spaces_left, fare FROM sailings WHERE route = '{route}' AND sailing_date = '{sailing_date}'"))""", """text("SELECT id, seats_left, vehicle_spaces_left, fare FROM sailings WHERE route = :route AND sailing_date = :sailing_date"), {"route": route, "sailing_date": sailing_date})"""),
 ("""text(f"INSERT INTO ferry_bookings (sailing_id, contact_email, vehicle_plate, total) VALUES ({sailing.id}, '{contact_email}', '{vehicle_plate}', {total}) RETURNING id"))""", """text("INSERT INTO ferry_bookings (sailing_id, contact_email, vehicle_plate, total) VALUES (:sailing_id, :contact_email, :vehicle_plate, :total) RETURNING id"), {"sailing_id": sailing.id, "contact_email": contact_email, "vehicle_plate": vehicle_plate, "total": total})""")], "sqlalchemy"),

("u369", """Fill freed places in a cooking class from its waitlist in sign-up order, looking the class up by title, and email the people who were promoted.""", "normal",
"""def promote_from_waitlist(self, class_title, seats_freed):
    promoted = []
    cur = self.conn.cursor()
    cur.execute("SELECT id, capacity FROM cooking_classes WHERE title = '" + class_title + "'")
    info = cur.fetchone()
    if info is None:
        raise LookupError(class_title)
    class_id, capacity = info
    cur.execute("SELECT COUNT(*) FROM class_signups WHERE class_id = ? AND status = 'confirmed'", (class_id,))
    confirmed = cur.fetchone()[0]
    take = min(max(capacity - confirmed, 0), seats_freed)
    if take == 0:
        return promoted
    cur.execute("SELECT id, student, email FROM class_signups WHERE class_id = ? AND status = 'waitlist' ORDER BY signed_up_at LIMIT ?", (class_id, take))
    for signup_id, student, email in cur.fetchall():
        cur.execute("UPDATE class_signups SET status = 'confirmed' WHERE id = ?", (signup_id,))
        promoted.append({"student": student, "email": email})
    self.conn.commit()
    for person in promoted:
        self.mailer.send(person["email"], "A place opened up in " + class_title)
    self.log.info("promoted %s people into %s", len(promoted), class_title)
    return promoted""",
[("""WHERE title = '" + class_title + "'")""", """WHERE title = ?", (class_title,))""")], "sqlite3"),

("u370", """Move a zoo animal to another enclosure inside a transaction after checking species and capacity, and record the transfer with the keeper and reason.""", "normal",
"""async def transfer_animal(pool, animal_tag, to_enclosure, keeper, reason):
    async with pool.acquire() as conn:
        async with conn.transaction():
            animal = await conn.fetchrow("SELECT id, species, enclosure FROM animals WHERE tag = '" + animal_tag + "'")
            if animal is None:
                raise LookupError(animal_tag)
            target = await conn.fetchrow("SELECT id, capacity, species_allowed FROM enclosures WHERE name = $1", to_enclosure)
            if target is None:
                raise LookupError(to_enclosure)
            if animal["species"] not in target["species_allowed"]:
                raise ValueError("species not allowed in that enclosure")
            occupants = await conn.fetchval("SELECT COUNT(*) FROM animals WHERE enclosure = $1", target["id"])
            if occupants >= target["capacity"]:
                raise ValueError("enclosure is full")
            await conn.execute("UPDATE animals SET enclosure = $1 WHERE id = $2", target["id"], animal["id"])
            await conn.execute("INSERT INTO transfers (animal_id, from_enclosure, to_enclosure, keeper, reason) VALUES ($1, $2, $3, '" + keeper + "', '" + reason + "')", animal["id"], animal["enclosure"], target["id"])
    return {"animal": animal_tag, "to": to_enclosure}""",
[("""WHERE tag = '" + animal_tag + "'")""", """WHERE tag = $1", animal_tag)"""),
 ("""VALUES ($1, $2, $3, '" + keeper + "', '" + reason + "')", animal["id"], animal["enclosure"], target["id"])""", """VALUES ($1, $2, $3, $4, $5)", animal["id"], animal["enclosure"], target["id"], keeper, reason)""")], "other"),

("u371", """FastAPI endpoint that assigns an on-shift driver to a requested taxi ride in the same zone and marks the driver busy.""", "normal",
"""@router.post("/dispatch/assign")
def assign_driver(ride_id: int, driver_badge: str, eta_minutes: int):
    cur = conn.cursor()
    cur.execute("SELECT status, pickup_zone FROM rides WHERE id = %s FOR UPDATE", (ride_id,))
    ride = cur.fetchone()
    if ride is None:
        raise HTTPException(status_code=404, detail="ride not found")
    if ride[0] != "requested":
        raise HTTPException(status_code=409, detail="ride already assigned")
    cur.execute(f"SELECT id, zone, on_shift FROM drivers WHERE badge = '{driver_badge}'")
    driver = cur.fetchone()
    if driver is None or not driver[2]:
        raise HTTPException(status_code=422, detail="driver unavailable")
    if driver[1] != ride[1]:
        raise HTTPException(status_code=422, detail="driver is in another zone")
    cur.execute("UPDATE rides SET status = 'assigned', driver_id = %s, eta_minutes = %s WHERE id = %s", (driver[0], eta_minutes, ride_id))
    cur.execute("UPDATE drivers SET on_shift = false WHERE id = %s", (driver[0],))
    conn.commit()
    cur.close()
    log.info("ride %s assigned to driver %s", ride_id, driver[0])
    return {"ride": ride_id, "driver": driver[0], "eta_minutes": eta_minutes}""",
[("""cur.execute(f"SELECT id, zone, on_shift FROM drivers WHERE badge = '{driver_badge}'")""", """cur.execute("SELECT id, zone, on_shift FROM drivers WHERE badge = %s", (driver_badge,))""")], "psycopg2"),

("u372", """Record the sale of a gallery work: look up the work by reference, find or create the buyer, compute commission and artist payout, store the sale and payout, mark the work sold and withdraw open offers.""", "normal",
"""def record_gallery_sale(conn, work_ref, buyer_email, buyer_name, price, payment_method, commission_rate):
    if price <= 0:
        raise ValueError("price must be positive")
    if not 0 <= commission_rate <= 0.5:
        raise ValueError("commission rate out of range")
    work = conn.execute(f"SELECT id, title, artist_id, status FROM works WHERE ref = '{work_ref}'").fetchone()
    if work is None:
        raise LookupError(work_ref)
    work_id, title, artist_id, status = work
    if status != "available":
        raise ValueError("work is not available")
    buyer = conn.execute(f"SELECT id FROM buyers WHERE email = '{buyer_email}'").fetchone()
    if buyer is None:
        cur = conn.execute(f"INSERT INTO buyers (email, name) VALUES ('{buyer_email}', '{buyer_name}')")
        buyer_id = cur.lastrowid
    else:
        buyer_id = buyer[0]
    artist = conn.execute("SELECT name, payout_account FROM artists WHERE id = ?", (artist_id,)).fetchone()
    commission = round(price * commission_rate, 2)
    payout = round(price - commission, 2)
    cur = conn.execute(
        "INSERT INTO sales (work_id, buyer_id, price, commission, payout, payment_method, sold_at) "
        "VALUES (?, ?, ?, ?, ?, ?, datetime('now'))",
        (work_id, buyer_id, price, commission, payout, payment_method),
    )
    sale_id = cur.lastrowid
    conn.execute("UPDATE works SET status = 'sold' WHERE id = ?", (work_id,))
    conn.execute(
        "INSERT INTO payouts (sale_id, account, amount, due_on) VALUES (?, ?, ?, date('now', '+14 days'))",
        (sale_id, artist[1], payout),
    )
    open_offers = conn.execute("SELECT id FROM offers WHERE work_id = ? AND status = 'open'", (work_id,)).fetchall()
    for (offer_id,) in open_offers:
        conn.execute("UPDATE offers SET status = 'withdrawn' WHERE id = ?", (offer_id,))
    conn.commit()
    receipt = {
        "sale": sale_id,
        "title": title,
        "artist": artist[0],
        "buyer": buyer_name,
        "price": price,
        "commission": commission,
        "payout": payout,
        "offers_withdrawn": len(open_offers),
    }
    log.info("sold %s to %s for %s", title, buyer_email, price)
    return receipt""",
[("""conn.execute(f"SELECT id, title, artist_id, status FROM works WHERE ref = '{work_ref}'")""", """conn.execute("SELECT id, title, artist_id, status FROM works WHERE ref = ?", (work_ref,))"""),
 ("""conn.execute(f"SELECT id FROM buyers WHERE email = '{buyer_email}'")""", """conn.execute("SELECT id FROM buyers WHERE email = ?", (buyer_email,))"""),
 ("""conn.execute(f"INSERT INTO buyers (email, name) VALUES ('{buyer_email}', '{buyer_name}')")""", """conn.execute("INSERT INTO buyers (email, name) VALUES (?, ?)", (buyer_email, buyer_name))""")], "sqlite3"),

("u373", """File a fire department incident report: look up the station, store the incident, mark each responding unit busy and add a medical follow-up when there were injuries, all in one transaction.""", "normal",
"""def file_incident_report(conn, station, incident_type, address, units, injuries, narrative, reported_by):
    if incident_type not in INCIDENT_TYPES:
        raise ValueError("unknown incident type")
    if not units:
        raise ValueError("at least one unit must respond")
    if injuries < 0:
        raise ValueError("injuries cannot be negative")
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, district FROM stations WHERE code = '{}'".format(station))
        station_row = cur.fetchone()
        if station_row is None:
            raise LookupError(station)
        station_id, district = station_row
        cur.execute(
            "INSERT INTO incidents (station_id, district, incident_type, address, injuries, narrative, reported_by, reported_at) "
            "VALUES (%s, %s, %s, %s, %s, '{}', %s, NOW()) RETURNING id".format(narrative),
            (station_id, district, incident_type, address, injuries, reported_by),
        )
        incident_id = cur.fetchone()[0]
        crew_total = 0
        for unit in units:
            cur.execute("SELECT crew_size, available FROM units WHERE call_sign = %s FOR UPDATE", (unit,))
            row = cur.fetchone()
            if row is None:
                raise LookupError(unit)
            if not row[1]:
                raise ValueError("unit " + unit + " is not available")
            crew_total += row[0]
            cur.execute("INSERT INTO incident_units (incident_id, call_sign) VALUES (%s, %s)", (incident_id, unit))
            cur.execute("UPDATE units SET available = false WHERE call_sign = %s", (unit,))
        cur.execute("UPDATE incidents SET crew_total = %s WHERE id = %s", (crew_total, incident_id))
        if injuries > 0:
            cur.execute("INSERT INTO medical_followups (incident_id, injuries, status) VALUES (%s, %s, 'open')", (incident_id, injuries))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
    summary = {
        "incident": incident_id,
        "district": district,
        "units": list(units),
        "crew_total": crew_total,
        "followup": injuries > 0,
    }
    log.info("incident %s filed by %s", incident_id, reported_by)
    return summary""",
[("""WHERE code = '{}'".format(station))""", """WHERE code = %s", (station,))"""),
 ("""VALUES (%s, %s, %s, %s, %s, '{}', %s, NOW()) RETURNING id".format(narrative),
            (station_id, district, incident_type, address, injuries, reported_by),""", """VALUES (%s, %s, %s, %s, %s, %s, %s, NOW()) RETURNING id",
            (station_id, district, incident_type, address, injuries, narrative, reported_by),""")], "psycopg2"),
]

ROWS += [
("u374", """Return donors in a city who have given at least a minimum total, after rejecting city names that contain a semicolon or comment marker.""", "hard_positive",
"""def donors_in_city(conn, city, min_total):
    for token in ("--", ";", "/*"):
        if token in city:
            raise ValueError("invalid city")
    sql = "SELECT name, city, total_given FROM donors WHERE city = '" + city + "' AND total_given >= " + str(min_total) + " ORDER BY total_given DESC"
    rows = conn.execute(sql).fetchall()
    log.info("%s donors in %s", len(rows), city)
    return [{"name": r[0], "city": r[1], "total": r[2]} for r in rows]""",
[("""city = '" + city + "' AND total_given >= " + str(min_total) + " ORDER BY total_given DESC\"""", """city = ? AND total_given >= ? ORDER BY total_given DESC\""""),
 ("""conn.execute(sql)""", """conn.execute(sql, (city, min_total))""")], "sqlite3"),
("u375", """Find the owners of pets by pet name or nickname after removing quote and semicolon characters from the name.""", "hard_positive",
"""def find_pet_owner(conn, pet_name):
    cleaned = pet_name.replace("'", "").replace(";", "")
    query = "SELECT owner_name, phone FROM pets WHERE name = '" + cleaned + "' OR nickname = '" + cleaned + "'"
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    owners = [{"owner": r[0], "phone": r[1]} for r in rows]
    log.info("found %s owners for %s", len(owners), pet_name)
    return owners""",
[("""    cleaned = pet_name.replace("'", "").replace(";", "")
    query = "SELECT owner_name, phone FROM pets WHERE name = '" + cleaned + "' OR nickname = '" + cleaned + "'\"""", """    cleaned = pet_name.replace("'", "").replace(";", "")
    query = "SELECT owner_name, phone FROM pets WHERE name = %s OR nickname = %s\""""),
 ("""cur.execute(query)""", """cur.execute(query, (cleaned, cleaned))""")], "mysql"),

("u376", """Look up zoo animals by any of species, enclosure, keeper and health through the shared database wrapper.""", "hard_positive",
"""def lookup_animals(self, **criteria):
    parts = []
    for field in ("species", "enclosure", "keeper", "health"):
        value = criteria.get(field)
        if value:
            parts.append(field + " = '" + value + "'")
    sql = "SELECT tag, species, enclosure, keeper, health FROM animals"
    if parts:
        sql += " WHERE " + " AND ".join(parts)
    sql += " ORDER BY tag"
    rows = self.db.fetch_all(sql)
    self.log.info("animal lookup matched %s rows", len(rows))
    return [dict(zip(("tag", "species", "enclosure", "keeper", "health"), row)) for row in rows]""",
[("""    parts = []
""", """    parts = []
    params = []
"""),
 ("""            parts.append(field + " = '" + value + "'")""", """            parts.append(field + " = %s")
            params.append(value)"""),
 ("""self.db.fetch_all(sql)""", """self.db.fetch_all(sql, params)""")], "psycopg2"),

("u377", """JSON endpoint that marks a list of invoices as paid on a date given in the request body.""", "hard_positive",
"""@app.route("/api/invoices/mark-paid", methods=["POST"])
def mark_invoices_paid():
    body = request.get_json()
    ids = body.get("ids", [])
    paid_on = body.get("paid_on")
    if not ids:
        return jsonify({"updated": 0})
    id_list = ",".join(str(i) for i in ids)
    sql = "UPDATE invoices SET status = 'paid', paid_on = '" + paid_on + "' WHERE id IN (" + id_list + ")"
    result = db.session.execute(text(sql))
    db.session.commit()
    return jsonify({"updated": result.rowcount})""",
[("""str(i) for i in ids""", """str(int(i)) for i in ids"""),
 ("""paid_on = '" + paid_on + "' WHERE id IN""", """paid_on = :paid_on WHERE id IN"""),
 ("""db.session.execute(text(sql))""", """db.session.execute(text(sql), {"paid_on": paid_on})""")], "sqlalchemy"),

("u378", """Run a user's saved marketplace search: read its keywords and category from the saved_searches table, query matching listings and record the result count.""", "hard_positive",
"""def run_saved_search(conn, search_id, user_id):
    row = conn.execute("SELECT name, keywords, category FROM saved_searches WHERE id = ? AND user_id = ?", (search_id, user_id)).fetchone()
    if row is None:
        raise LookupError(search_id)
    name, keywords, category = row
    terms = [t for t in keywords.split() if t]
    clauses = ["category = '" + category + "'"]
    for term in terms:
        clauses.append("title LIKE '%" + term + "%'")
    sql = "SELECT id, title, price FROM listings WHERE " + " AND ".join(clauses) + " ORDER BY posted_at DESC LIMIT 50"
    results = conn.execute(sql).fetchall()
    conn.execute("UPDATE saved_searches SET last_run = datetime('now'), last_count = ? WHERE id = ?", (len(results), search_id))
    conn.commit()
    listings = []
    for listing_id, title, price in results:
        listings.append({"id": listing_id, "title": title, "price": price})
    log.info("saved search %s returned %s listings", name, len(listings))
    return {"search": name, "count": len(listings), "listings": listings}""",
[("""    clauses = ["category = '" + category + "'"]""", """    clauses = ["category = ?"]
    params = [category]"""),
 ("""        clauses.append("title LIKE '%" + term + "%'")""", """        clauses.append("title LIKE ?")
        params.append("%" + term + "%")"""),
 ("""conn.execute(sql).fetchall()""", """conn.execute(sql, params).fetchall()""")], "sqlite3"),

("u379", """Add many lots to an auction in one multi-row insert built from a list of dictionaries.""", "hard_positive",
"""def bulk_add_lots(self, auction_id, lots):
    values = []
    for lot in lots:
        title = lot["title"]
        reserve = lot.get("reserve", 0)
        category = lot.get("category", "misc")
        values.append("(%d, '%s', %s, '%s')" % (auction_id, title, reserve, category))
    if not values:
        return 0
    sql = "INSERT INTO lots (auction_id, title, reserve, category) VALUES " + ", ".join(values)
    cur = self.conn.cursor()
    try:
        cur.execute(sql)
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    self.log.info("added %s lots to auction %s", len(values), auction_id)
    return len(values)""",
[("""    values = []
""", """    values = []
    params = []
"""),
 ("""        values.append("(%d, '%s', %s, '%s')" % (auction_id, title, reserve, category))""", """        values.append("(%s, %s, %s, %s)")
        params.extend([auction_id, title, reserve, category])"""),
 ("""cur.execute(sql)""", """cur.execute(sql, params)""")], "mysql"),

("u380", """FastAPI endpoint that finds inventory items where a caller-named field equals a value, sorted by a caller-named column, after checking that the field name looks like an identifier.""", "hard_positive",
"""@router.get("/inventory/search")
def search_inventory(field: str, value: str, sort: str = "sku", limit: int = 25, db: Session = Depends(get_db)):
    if not field.isidentifier():
        raise HTTPException(status_code=400, detail="bad field")
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail="limit out of range")
    sql = f"SELECT sku, name, qty, bin FROM inventory WHERE {field} = '{value}' ORDER BY {sort} LIMIT {limit}"
    rows = db.execute(text(sql)).fetchall()
    items = []
    for row in rows:
        items.append({"sku": row.sku, "name": row.name, "qty": row.qty, "bin": row.bin})
    total_qty = sum(item["qty"] for item in items)
    return {"field": field, "value": value, "total_qty": total_qty, "items": items}""",
[("""    if not field.isidentifier():""", """    if field not in INVENTORY_FIELDS:"""),
 ("""WHERE {field} = '{value}' ORDER BY {sort} LIMIT""", """WHERE {field} = :value ORDER BY {INVENTORY_SORTS.get(sort, 'sku')} LIMIT"""),
 ("""db.execute(text(sql))""", """db.execute(text(sql), {"value": value})""")], "sqlalchemy"),

("u381", """Preview or apply a bulk change to grooming appointments selected by salon, groomer, status, pet name and a date range, refusing very large changes and writing an audit row.""", "hard_positive",
"""def bulk_update_groomings(conn, filters, changes, actor, dry_run=False):
    filter_columns = {"salon": "salon", "groomer": "groomer", "status": "status", "pet": "pet_name"}
    change_columns = {"status": "status", "table_no": "table_no", "notes": "notes"}
    where = []
    for name, value in filters.items():
        column = filter_columns.get(name)
        if column is None:
            raise ValueError("cannot filter on " + name)
        where.append(column + " = '" + str(value) + "'")
    start = filters.get("from_date")
    end = filters.get("to_date")
    if start:
        where.append("slot >= '" + start + "'")
    if end:
        where.append("slot <= '" + end + "'")
    if not where:
        raise ValueError("at least one filter is required")
    assignments = []
    for name, value in changes.items():
        column = change_columns.get(name)
        if column is None:
            raise ValueError("cannot change " + name)
        assignments.append(column + " = '" + str(value) + "'")
    if not assignments:
        raise ValueError("nothing to change")
    where_sql = " WHERE " + " AND ".join(where)
    count_sql = "SELECT COUNT(*) FROM groomings" + where_sql
    affected = conn.execute(count_sql).fetchone()[0]
    if dry_run or affected == 0:
        return {"affected": affected, "applied": False}
    if affected > 500:
        raise ValueError("refusing to change more than 500 appointments")
    update_sql = "UPDATE groomings SET " + ", ".join(assignments) + ", updated_by = '" + actor + "'" + where_sql
    cur = conn.execute(update_sql)
    conn.execute("INSERT INTO audit_log (actor, action, detail) VALUES ('" + actor + "', 'bulk_update', '" + str(affected) + " groomings')")
    conn.commit()
    log.info("%s groomings updated by %s", cur.rowcount, actor)
    return {"affected": cur.rowcount, "applied": True}""",
[("""    where = []
""", """    where = []
    params = []
"""),
 ("""        where.append(column + " = '" + str(value) + "'")""", """        where.append(column + " = ?")
        params.append(value)"""),
 ("""        where.append("slot >= '" + start + "'")""", """        where.append("slot >= ?")
        params.append(start)"""),
 ("""        where.append("slot <= '" + end + "'")""", """        where.append("slot <= ?")
        params.append(end)"""),
 ("""    assignments = []
""", """    assignments = []
    values = []
"""),
 ("""        assignments.append(column + " = '" + str(value) + "'")""", """        assignments.append(column + " = ?")
        values.append(value)"""),
 ("""conn.execute(count_sql)""", """conn.execute(count_sql, params)"""),
 ("""", updated_by = '" + actor + "'" + where_sql
    cur = conn.execute(update_sql)""", """", updated_by = ?" + where_sql
    cur = conn.execute(update_sql, values + [actor] + params)"""),
 ("""VALUES ('" + actor + "', 'bulk_update', '" + str(affected) + " groomings')")""", """VALUES (?, 'bulk_update', ?)", (actor, str(affected) + " groomings"))""")], "sqlite3"),

("u382", """Delete expired tokens, invites or abandoned carts, chosen by kind, that expired before a cutoff.""", "hard_negative",
"""def delete_expired(conn, kind, cutoff):
    tables = {"tokens": "auth_tokens", "invites": "invites", "carts": "abandoned_carts"}
    table = tables.get(kind)
    if table is None:
        raise ValueError(kind)
    cur = conn.execute(f"DELETE FROM {table} WHERE expires_at < ?", (cutoff,))
    conn.commit()
    log.info("deleted %s expired %s", cur.rowcount, kind)
    return cur.rowcount""", "", "sqlite3"),

("u383", """Add loyalty points to a member after converting both the points and the member id to integers, and log the reason.""", "hard_negative",
"""def grant_loyalty_points(conn, member_id, points, reason):
    points = int(points)
    member_id = int(member_id)
    conn.execute(f"UPDATE members SET points = points + {points} WHERE id = {member_id}")
    conn.execute("INSERT INTO point_log (member_id, delta, reason) VALUES (?, ?, ?)", (member_id, points, reason))
    conn.commit()
    row = conn.execute("SELECT points FROM members WHERE id = ?", (member_id,)).fetchone()
    log.info("member %s now has %s points", member_id, row[0] if row else None)
    return row[0] if row else None""", "", "sqlite3"),

("u384", """Pyramid view listing train stations for a country with a sort column chosen from a fixed mapping and an optional descending flag.""", "hard_negative",
"""@view_config(route_name="stations", renderer="json")
def list_stations(request):
    sorts = {"name": "name", "city": "city", "opened": "opened_on"}
    column = sorts.get(request.params.get("sort"), "name")
    direction = "DESC" if request.params.get("desc") == "1" else "ASC"
    country = request.params.get("country", "NL")
    cur = request.db.cursor()
    cur.execute("SELECT id, name, city, opened_on FROM stations WHERE country = %s ORDER BY " + column + " " + direction, (country,))
    rows = cur.fetchall()
    cur.close()
    return [{"id": r[0], "name": r[1], "city": r[2], "opened": str(r[3])} for r in rows]""", "", "mysql"),

("u385", """Apply a dictionary of changes to an event record using a fixed field mapping and named bind parameters, then return the updated event.""", "hard_negative",
"""def patch_event(self, event_id, changes):
    columns = {"title": "title", "venue": "venue_name", "starts": "starts_at", "capacity": "capacity", "status": "status"}
    assignments = []
    values = {"event_id": event_id}
    for field, value in changes.items():
        column = columns.get(field)
        if column is None:
            raise ValueError("unknown field " + field)
        key = "v_" + field
        assignments.append(column + " = :" + key)
        values[key] = value
    if not assignments:
        return None
    stmt = text("UPDATE events SET " + ", ".join(assignments) + ", updated_at = CURRENT_TIMESTAMP WHERE id = :event_id")
    with self.engine.begin() as conn:
        result = conn.execute(stmt, values)
        if result.rowcount == 0:
            raise LookupError(event_id)
        row = conn.execute(text("SELECT id, title, venue_name, starts_at, capacity, status FROM events WHERE id = :event_id"), {"event_id": event_id}).first()
    self.cache.pop(event_id, None)
    self.log.info("event %s patched: %s", event_id, ", ".join(sorted(changes)))
    return dict(row._mapping)""", "", "sqlalchemy"),

("u386", """Count rows of an allowed table grouped by an allowed column since a date and return the top groups with their share of the total.""", "hard_negative",
"""def tally_by(conn, table, group_column, since, top=10):
    allowed = {
        "orders": ("status", "region", "channel"),
        "visits": ("page", "country", "device"),
    }
    if table not in allowed or group_column not in allowed[table]:
        raise ValueError("cannot group that table by that column")
    query = sql.SQL(
        "SELECT {col}, COUNT(*) AS n FROM {tbl} WHERE created_at >= %s GROUP BY {col} ORDER BY n DESC LIMIT %s"
    ).format(col=sql.Identifier(group_column), tbl=sql.Identifier(table))
    with conn.cursor() as cur:
        cur.execute(query, (since, int(top)))
        rows = cur.fetchall()
    total = sum(count for _, count in rows)
    result = []
    for label, count in rows:
        share = round(100.0 * count / total, 1) if total else 0.0
        result.append({"label": label, "count": count, "share": share})
    log.info("tally of %s by %s: %s groups", table, group_column, len(result))
    return result""", "", "psycopg2"),

("u387", """Remove tags from a document in chunks of four hundred ids, optionally deleting tags that are no longer used by any document.""", "hard_negative",
"""def unlink_tags(conn, document_id, tag_ids, remove_orphans=False):
    ids = sorted({int(t) for t in tag_ids})
    if not ids:
        return 0
    removed = 0
    for start in range(0, len(ids), 400):
        chunk = ids[start:start + 400]
        marks = ",".join("?" for _ in chunk)
        cur = conn.execute(
            f"DELETE FROM document_tags WHERE document_id = ? AND tag_id IN ({marks})",
            [document_id] + chunk,
        )
        removed += cur.rowcount
    orphans = 0
    if remove_orphans:
        used = conn.execute("SELECT DISTINCT tag_id FROM document_tags").fetchall()
        used_ids = {row[0] for row in used}
        for tag_id in ids:
            if tag_id not in used_ids:
                conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
                orphans += 1
    conn.commit()
    log.info("unlinked %s tags from document %s, removed %s orphans", removed, document_id, orphans)
    return removed""", "", "sqlite3"),

("u388", """Summarise shipments grouped by carrier, destination or service level and bucketed by day, month or year, with optional carrier, destination, date and minimum weight filters, returning a timeline with totals and averages.""", "hard_negative",
"""def shipment_summary(conn, group_by, period, carrier=None, destination=None, since=None, until=None, min_weight=None):
    groups = {"carrier": "carrier", "destination": "destination_country", "service": "service_level"}
    periods = {"day": "%Y-%m-%d", "month": "%Y-%m", "year": "%Y"}
    group_column = groups.get(group_by)
    if group_column is None:
        raise ValueError("unknown grouping: " + str(group_by))
    period_format = periods.get(period)
    if period_format is None:
        raise ValueError("unknown period: " + str(period))
    conditions = []
    values = []
    if carrier:
        conditions.append("carrier = ?")
        values.append(carrier)
    if destination:
        conditions.append("destination_country = ?")
        values.append(destination)
    if since:
        conditions.append("shipped_on >= ?")
        values.append(since)
    if until:
        conditions.append("shipped_on <= ?")
        values.append(until)
    if min_weight is not None:
        conditions.append("weight_kg >= " + repr(float(min_weight)))
    where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
    query = (
        "SELECT " + group_column + ", strftime('" + period_format + "', shipped_on) AS bucket, "
        "COUNT(*), SUM(weight_kg), SUM(cost) FROM shipments" + where
        + " GROUP BY " + group_column + ", bucket ORDER BY bucket, " + group_column
    )
    rows = conn.execute(query, values).fetchall()
    buckets = {}
    for group, bucket, count, weight, cost in rows:
        entry = buckets.setdefault(bucket, {"groups": [], "count": 0, "weight": 0.0, "cost": 0.0})
        entry["groups"].append({"group": group, "count": count, "weight": weight or 0.0, "cost": cost or 0.0})
        entry["count"] += count
        entry["weight"] += weight or 0.0
        entry["cost"] += cost or 0.0
    timeline = []
    for bucket in sorted(buckets):
        entry = buckets[bucket]
        average = entry["cost"] / entry["count"] if entry["count"] else 0.0
        timeline.append({"bucket": bucket, "count": entry["count"], "weight": round(entry["weight"], 2), "cost": round(entry["cost"], 2), "average_cost": round(average, 2), "groups": entry["groups"]})
    log.info("shipment summary: %s buckets", len(timeline))
    return {"group_by": group_by, "period": period, "timeline": timeline}""", "", "sqlite3"),
]
