ROWS = [
("u463", """Endpoint that lists a bookshop's books by one author on one shelf, ordered by title.""", "normal",
"""@app.route("/books/by-author")
def books_by_author():
    author = request.args.get("author", "")
    shelf = request.args.get("shelf", "")
    rows = get_db().execute("SELECT isbn, title, price FROM books WHERE author = '" + author + "' AND shelf = '" + shelf + "' ORDER BY title").fetchall()
    return jsonify([{"isbn": r[0], "title": r[1], "price": r[2]} for r in rows])""",
[("""author = '" + author + "' AND shelf = '" + shelf + "' ORDER BY title").fetchall()""", """author = ? AND shelf = ? ORDER BY title", (author, shelf)).fetchall()""")], "sqlite3"),

("u464", """Delete a customer's unfinished draft orders created before a date and return how many were removed.""", "normal",
"""def delete_draft_orders(self, customer, before):
    cur = self.conn.cursor()
    cur.execute(f"DELETE FROM draft_orders WHERE customer = '{customer}' AND created_on < '{before}'")
    removed = cur.rowcount
    self.conn.commit()
    self.log.info("removed %s drafts of %s", removed, customer)
    self.drafts_cache.pop(customer, None)
    return removed""",
[("""cur.execute(f"DELETE FROM draft_orders WHERE customer = '{customer}' AND created_on < '{before}'")""", """cur.execute("DELETE FROM draft_orders WHERE customer = ? AND created_on < ?", (customer, before))""")], "sqlite3"),

("u465", """Set the status of a tailoring order and who changed it, raising an error when the order does not exist.""", "normal",
"""def set_order_status(self, order_no, status, changed_by):
    stmt = "UPDATE tailor_orders SET status = '{}', changed_by = '{}', changed_at = datetime('now') WHERE order_no = '{}'".format(status, changed_by, order_no)
    cur = self.conn.execute(stmt)
    self.conn.commit()
    if cur.rowcount == 0:
        raise LookupError(order_no)
    self.log.info("order %s is now %s", order_no, status)
    return status""",
[("""status = '{}', changed_by = '{}', changed_at = datetime('now') WHERE order_no = '{}'".format(status, changed_by, order_no)""", """status = ?, changed_by = ?, changed_at = datetime('now') WHERE order_no = ?\""""),
 ("""self.conn.execute(stmt)""", """self.conn.execute(stmt, (status, changed_by, order_no))""")], "sqlite3"),
("u466", """Return a tailor's fittings on a day ordered by time.""", "normal",
"""def fittings_for(self, tailor, day):
    with self.conn.cursor() as cur:
        cur.execute("SELECT id, customer, starts_at, notes FROM fittings WHERE tailor = '%s' AND DATE(starts_at) = '%s' ORDER BY starts_at" % (tailor, day))
        rows = cur.fetchall()
    fittings = [{"id": r[0], "customer": r[1], "starts_at": str(r[2]), "notes": r[3]} for r in rows]
    self.log.info("%s fittings for %s on %s", len(fittings), tailor, day)
    return fittings""",
[("""tailor = '%s' AND DATE(starts_at) = '%s' ORDER BY starts_at" % (tailor, day))""", """tailor = %s AND DATE(starts_at) = %s ORDER BY starts_at", (tailor, day))""")], "psycopg2"),

("u467", """Look up several rental kayaks by id and return their names and status.""", "normal",
"""def kayaks_by_ids(conn, ids):
    if not ids:
        return []
    id_list = ",".join(ids)
    rows = conn.execute("SELECT id, name, status FROM kayaks WHERE id IN (" + id_list + ") ORDER BY name").fetchall()
    kayaks = [{"id": r[0], "name": r[1], "status": r[2]} for r in rows]
    log.info("loaded %s kayaks", len(kayaks))
    return kayaks""",
[("""    id_list = ",".join(ids)""", """    id_list = ",".join(str(int(i)) for i in ids)""")], "sqlite3"),

("u468", """Flask endpoint that removes a puppet from a theatre's collection by name and workshop, returning the removed count.""", "normal",
"""@app.route("/puppets/<name>", methods=["DELETE"])
@login_required
def remove_puppet(name):
    workshop = request.args.get("workshop", "")
    stmt = "DELETE FROM puppets WHERE name = '{}' AND workshop = '{}'".format(name, workshop)
    result = db.session.execute(text(stmt))
    db.session.commit()
    return jsonify({"name": name, "removed": result.rowcount})""",
[("""name = '{}' AND workshop = '{}'".format(name, workshop)""", """name = :name AND workshop = :workshop\""""),
 ("""db.session.execute(text(stmt))""", """db.session.execute(text(stmt), {"name": name, "workshop": workshop})""")], "sqlalchemy"),

("u469", """FastAPI endpoint listing glass pieces from the studio sorted by a column from the query string.""", "normal",
"""@router.get("/glass/pieces")
def list_glass_pieces(sort: str = "name", limit: int = 30):
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail="limit out of range")
    rows = db.execute(f"SELECT id, name, maker, price FROM glass_pieces ORDER BY {sort} LIMIT {limit}").fetchall()
    return [{"id": r[0], "name": r[1], "maker": r[2], "price": r[3]} for r in rows]""",
[("""ORDER BY {sort} LIMIT""", """ORDER BY {PIECE_SORTS.get(sort, 'name')} LIMIT""")], "sqlite3"),

("u470", """JSON endpoint that updates the opening note and contact phone of a craft fair stall and reports failure as JSON.""", "normal",
"""@app.route("/fair/stalls/<int:stall_id>", methods=["PUT"])
def update_stall(stall_id):
    data = request.get_json(silent=True) or {}
    note = data.get("note", "")
    phone = data.get("phone", "")
    db = get_db()
    try:
        db.execute(f"UPDATE stalls SET note = '{note}', phone = '{phone}' WHERE id = {stall_id}")
        db.commit()
    except sqlite3.Error:
        db.rollback()
        return jsonify({"error": "update failed"}), 500
    return jsonify({"id": stall_id, "note": note, "phone": phone})""",
[("""db.execute(f"UPDATE stalls SET note = '{note}', phone = '{phone}' WHERE id = {stall_id}")""", """db.execute("UPDATE stalls SET note = ?, phone = ? WHERE id = ?", (note, phone, stall_id))""")], "sqlite3"),

("u471", """Delete the expired parking-style permits of several lifeboat volunteers in one transaction and return the count.""", "normal",
"""def remove_expired_passes(self, volunteer_ids, cutoff):
    cur = self.conn.cursor()
    removed = 0
    try:
        for volunteer_id in volunteer_ids:
            cur.execute(f"DELETE FROM crew_passes WHERE volunteer_id = {volunteer_id} AND expires_on < '{cutoff}'")
            removed += cur.rowcount
        self.conn.commit()
    except psycopg2.Error:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    return removed""",
[("""cur.execute(f"DELETE FROM crew_passes WHERE volunteer_id = {volunteer_id} AND expires_on < '{cutoff}'")""", """cur.execute("DELETE FROM crew_passes WHERE volunteer_id = %s AND expires_on < %s", (volunteer_id, cutoff))""")], "psycopg2"),

("u472", """Print the tide stations whose region and minimum tide height come from environment variables.""", "normal",
"""def print_tide_stations():
    region = os.environ.get("TIDE_REGION", "north")
    min_height = os.environ.get("TIDE_MIN_HEIGHT", "2")
    conn = sqlite3.connect(os.environ["TIDE_DB"])
    try:
        rows = conn.execute("SELECT code, name, max_height FROM stations WHERE region = '" + region + "' AND max_height >= " + min_height + " ORDER BY name").fetchall()
    finally:
        conn.close()
    for code, name, height in rows:
        print(code, name, height)
    return len(rows)""",
[("""WHERE region = '" + region + "' AND max_height >= " + min_height + " ORDER BY name").fetchall()""", """WHERE region = ? AND max_height >= ? ORDER BY name", (region, float(min_height))).fetchall()""")], "sqlite3"),

("u473", """Store the stops of an ice cream truck route for a day, replacing any stop with the same name, and return the number stored.""", "normal",
"""def save_route_stops(self, route, day, stops):
    stored = 0
    for name, arrives in stops:
        self.conn.execute("DELETE FROM route_stops WHERE route = '" + route + "' AND day = '" + day + "' AND name = '" + name + "'")
        self.conn.execute("INSERT INTO route_stops (route, day, name, arrives) VALUES ('" + route + "', '" + day + "', '" + name + "', '" + arrives + "')")
        stored += 1
    self.conn.commit()
    self.log.info("stored %s stops for %s", stored, route)
    return stored""",
[("""WHERE route = '" + route + "' AND day = '" + day + "' AND name = '" + name + "'")""", """WHERE route = ? AND day = ? AND name = ?", (route, day, name))"""),
 ("""VALUES ('" + route + "', '" + day + "', '" + name + "', '" + arrives + "')")""", """VALUES (?, ?, ?, ?)", (route, day, name, arrives))""")], "sqlite3"),

("u474", """FastAPI endpoint that changes a garden's opening hours and reports a database error as a 500 response.""", "normal",
"""@router.put("/gardens/{garden_id}/hours")
def set_garden_hours(garden_id: int, opens: str, closes: str, db: Session = Depends(get_db)):
    try:
        db.execute(text(f"UPDATE gardens SET opens = '{opens}', closes = '{closes}' WHERE id = {garden_id}"))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="could not update hours")
    garden = db.query(Garden).get(garden_id)
    if garden is None:
        raise HTTPException(status_code=404, detail="garden not found")
    return {"id": garden.id, "opens": garden.opens, "closes": garden.closes}""",
[("""db.execute(text(f"UPDATE gardens SET opens = '{opens}', closes = '{closes}' WHERE id = {garden_id}"))""", """db.query(Garden).filter(Garden.id == garden_id).update({"opens": opens, "closes": closes})""")], "sqlalchemy"),

("u475", """Async method that deletes a locksmith's unfinished jobs for a customer and returns the number of deleted jobs.""", "normal",
"""async def clear_open_jobs(self, customer, status):
    async with self.pool.acquire() as conn:
        try:
            result = await conn.execute(f"DELETE FROM locksmith_jobs WHERE customer = '{customer}' AND status = '{status}'")
        except Exception:
            self.log.exception("could not clear jobs for %s", customer)
            raise
    removed = int(result.split()[-1])
    self.stats["jobs_cleared"] += removed
    return removed""",
[("""await conn.execute(f"DELETE FROM locksmith_jobs WHERE customer = '{customer}' AND status = '{status}'")""", """await conn.execute("DELETE FROM locksmith_jobs WHERE customer = $1 AND status = $2", customer, status)""")], "other"),
]

ROWS += [
("u476", """Let a signed-in lifeboat volunteer sign on to a shift in a role: check the shift is open, find the volunteer by callsign, check their trained roles, take them off the waitlist and close the shift when it is full.""", "normal",
"""@app.route("/lifeboat/shifts/<int:shift_id>/signon", methods=["POST"])
@login_required
def sign_on_shift(shift_id):
    role = request.form.get("role", "crew")
    callsign = request.form.get("callsign", "").strip()
    db = get_db()
    shift = db.execute("SELECT id, crew_needed, status FROM shifts WHERE id = ?", (shift_id,)).fetchone()
    if shift is None:
        abort(404)
    if shift["status"] != "open":
        flash("That shift is closed")
        return redirect(url_for("shift_list"))
    member = db.execute(f"SELECT id, trained_roles FROM crew WHERE callsign = '{callsign}'").fetchone()
    if member is None:
        flash("Unknown callsign")
        return redirect(url_for("shift_list"))
    if role not in member["trained_roles"].split(","):
        flash("Not trained for that role")
        return redirect(url_for("shift_list"))
    db.execute("DELETE FROM shift_waitlist WHERE shift_id = ? AND crew_id = ?", (shift_id, member["id"]))
    db.execute("INSERT INTO shift_crew (shift_id, crew_id, role) VALUES (?, ?, ?)", (shift_id, member["id"], role))
    filled = db.execute("SELECT COUNT(*) FROM shift_crew WHERE shift_id = ?", (shift_id,)).fetchone()[0]
    if filled >= shift["crew_needed"]:
        db.execute("UPDATE shifts SET status = 'full' WHERE id = ?", (shift_id,))
    db.commit()
    flash("Signed on as " + role)
    return redirect(url_for("shift_list"))""",
[("""db.execute(f"SELECT id, trained_roles FROM crew WHERE callsign = '{callsign}'")""", """db.execute("SELECT id, trained_roles FROM crew WHERE callsign = ?", (callsign,))""")], "sqlite3"),

("u477", """Book tickets for a school group at a puppet theatre performance, creating the group record when it does not exist yet, and increase the sold count in one transaction.""", "normal",
"""def book_performance(self, show_id, group_name, contact_email, tickets, school=None):
    if tickets < 1 or tickets > 60:
        raise ValueError("tickets must be between 1 and 60")
    cur = self.conn.cursor()
    try:
        cur.execute("SELECT capacity, sold, starts_at FROM performances WHERE id = %s FOR UPDATE", (show_id,))
        perf = cur.fetchone()
        if perf is None:
            raise LookupError(show_id)
        if perf[1] + tickets > perf[0]:
            raise ValueError("not enough seats left")
        cur.execute("SELECT id FROM groups WHERE name = '%s' AND contact_email = '%s'" % (group_name, contact_email))
        group = cur.fetchone()
        if group is None:
            cur.execute("INSERT INTO groups (name, contact_email, school) VALUES ('%s', '%s', %s) RETURNING id" % (group_name, contact_email, "'" + school + "'" if school else "NULL"))
            group = cur.fetchone()
        cur.execute("INSERT INTO performance_bookings (performance_id, group_id, tickets) VALUES (%s, %s, %s)", (show_id, group[0], tickets))
        cur.execute("UPDATE performances SET sold = sold + %s WHERE id = %s", (tickets, show_id))
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    return group[0]""",
[("""WHERE name = '%s' AND contact_email = '%s'" % (group_name, contact_email))""", """WHERE name = %s AND contact_email = %s", (group_name, contact_email))"""),
 ("""VALUES ('%s', '%s', %s) RETURNING id" % (group_name, contact_email, "'" + school + "'" if school else "NULL"))""", """VALUES (%s, %s, %s) RETURNING id", (group_name, contact_email, school))""")], "psycopg2"),

("u478", """Allocate craft fair stalls to applicants in order of application date, putting the rest on a waitlist, skipping makers who already have a stall and removing allocated makers from the waitlist.""", "normal",
"""def allocate_stalls(conn, fair_id, applications, organiser):
    allocated = []
    waitlisted = []
    fair = conn.execute("SELECT name, stall_count FROM fairs WHERE id = " + str(fair_id)).fetchone()
    if fair is None:
        raise LookupError(fair_id)
    taken = conn.execute("SELECT COUNT(*) FROM stall_assignments WHERE fair_id = " + str(fair_id)).fetchone()[0]
    free = fair[1] - taken
    for application in sorted(applications, key=lambda a: a["received_on"]):
        maker = application["maker"]
        category = application["category"]
        if free <= 0:
            waitlisted.append(maker)
            conn.execute("INSERT INTO stall_waitlist (fair_id, maker, category) VALUES (" + str(fair_id) + ", '" + maker + "', '" + category + "')")
            continue
        duplicate = conn.execute("SELECT 1 FROM stall_assignments WHERE fair_id = " + str(fair_id) + " AND maker = '" + maker + "'").fetchone()
        if duplicate:
            continue
        conn.execute("INSERT INTO stall_assignments (fair_id, maker, category, assigned_by) VALUES (" + str(fair_id) + ", '" + maker + "', '" + category + "', '" + organiser + "')")
        conn.execute("DELETE FROM stall_waitlist WHERE fair_id = " + str(fair_id) + " AND maker = '" + maker + "'")
        allocated.append(maker)
        free -= 1
    conn.commit()
    return {"fair": fair[0], "allocated": allocated, "waitlisted": waitlisted}""",
[("""FROM fairs WHERE id = " + str(fair_id))""", """FROM fairs WHERE id = ?", (fair_id,))"""),
 ("""FROM stall_assignments WHERE fair_id = " + str(fair_id)).fetchone()[0]""", """FROM stall_assignments WHERE fair_id = ?", (fair_id,)).fetchone()[0]"""),
 ("""INTO stall_waitlist (fair_id, maker, category) VALUES (" + str(fair_id) + ", '" + maker + "', '" + category + "')")""", """INTO stall_waitlist (fair_id, maker, category) VALUES (?, ?, ?)", (fair_id, maker, category))"""),
 ("""WHERE fair_id = " + str(fair_id) + " AND maker = '" + maker + "'").fetchone()""", """WHERE fair_id = ? AND maker = ?", (fair_id, maker)).fetchone()"""),
 ("""VALUES (" + str(fair_id) + ", '" + maker + "', '" + category + "', '" + organiser + "')")""", """VALUES (?, ?, ?, ?)", (fair_id, maker, category, organiser))"""),
 ("""DELETE FROM stall_waitlist WHERE fair_id = " + str(fair_id) + " AND maker = '" + maker + "'")""", """DELETE FROM stall_waitlist WHERE fair_id = ? AND maker = ?", (fair_id, maker))""")], "sqlite3"),

("u479", """Upgrade a botanical garden member to a higher tier by member number, charge the price difference, record the payment and delete their pending upgrade offers in one transaction.""", "normal",
"""def upgrade_membership(self, member_no, new_tier, payment_ref, staff_user):
    if new_tier not in ("friend", "patron", "benefactor"):
        raise ValueError("unknown tier")
    with self.engine.begin() as conn:
        member = conn.execute(text(f"SELECT id, tier, renews_on FROM garden_members WHERE member_no = '{member_no}'")).first()
        if member is None:
            raise LookupError(member_no)
        if member.tier == new_tier:
            raise ValueError("already on that tier")
        price = TIER_PRICES[new_tier] - TIER_PRICES[member.tier]
        if price <= 0:
            raise ValueError("downgrades are handled by staff")
        conn.execute(text(f"UPDATE garden_members SET tier = '{new_tier}' WHERE id = {member.id}"))
        conn.execute(text(f"INSERT INTO garden_payments (member_id, amount, payment_ref, taken_by) VALUES ({member.id}, {price}, '{payment_ref}', '{staff_user}')"))
        conn.execute(text(f"DELETE FROM upgrade_offers WHERE member_id = {member.id}"))
    self.log.info("member %s upgraded to %s", member_no, new_tier)
    self.cache.pop(member_no, None)
    return price""",
[("""text(f"SELECT id, tier, renews_on FROM garden_members WHERE member_no = '{member_no}'"))""", """text("SELECT id, tier, renews_on FROM garden_members WHERE member_no = :member_no"), {"member_no": member_no})"""),
 ("""text(f"INSERT INTO garden_payments (member_id, amount, payment_ref, taken_by) VALUES ({member.id}, {price}, '{payment_ref}', '{staff_user}')"))""", """text("INSERT INTO garden_payments (member_id, amount, payment_ref, taken_by) VALUES (:member_id, :price, :payment_ref, :staff_user)"), {"member_id": member.id, "price": price, "payment_ref": payment_ref, "staff_user": staff_user})""")], "sqlalchemy"),

("u480", """Bottle route that appends a stop to an ice cream truck's route after checking that the stop does not already exist, giving it the next position.""", "normal",
"""@route("/trucks/<truck>/stops", method="POST")
def add_truck_stop(truck):
    name = request.forms.get("name", "").strip()
    street = request.forms.get("street", "").strip()
    arrives = request.forms.get("arrives", "")
    minutes = request.forms.get("minutes", "15")
    if not name or not street:
        response.status = 422
        return {"error": "name and street are required"}
    existing = db.execute("SELECT COUNT(*) FROM truck_stops WHERE truck = '%s' AND name = '%s'" % (truck, name)).fetchone()[0]
    if existing:
        response.status = 409
        return {"error": "stop already exists"}
    position = db.execute("SELECT COALESCE(MAX(position), 0) + 1 FROM truck_stops WHERE truck = '%s'" % truck).fetchone()[0]
    db.execute("INSERT INTO truck_stops (truck, name, street, arrives, minutes, position) VALUES ('%s', '%s', '%s', '%s', %s, %s)" % (truck, name, street, arrives, minutes, position))
    db.commit()
    response.status = 201
    return {"truck": truck, "name": name, "position": position}""",
[("""WHERE truck = '%s' AND name = '%s'" % (truck, name))""", """WHERE truck = ? AND name = ?", (truck, name))"""),
 ("""FROM truck_stops WHERE truck = '%s'" % truck)""", """FROM truck_stops WHERE truck = ?", (truck,))"""),
 ("""VALUES ('%s', '%s', '%s', '%s', %s, %s)" % (truck, name, street, arrives, minutes, position))""", """VALUES (?, ?, ?, ?, ?, ?)", (truck, name, street, arrives, int(minutes), position))""")], "sqlite3"),

("u481", """Dispatch a waiting locksmith job to an available locksmith in the same area, identified by phone number, mark the locksmith busy and remove the job from the dispatch queue.""", "normal",
"""def dispatch_job(self, job_id, locksmith_phone, eta_minutes):
    cur = self.conn.cursor()
    try:
        cur.execute("SELECT id, status, area FROM locksmith_jobs WHERE id = {}".format(job_id))
        job = cur.fetchone()
        if job is None:
            raise LookupError(job_id)
        if job[1] != "waiting":
            raise ValueError("job is not waiting")
        cur.execute("SELECT id, area, busy FROM locksmiths WHERE phone = '{}'".format(locksmith_phone))
        smith = cur.fetchone()
        if smith is None or smith[2]:
            raise ValueError("locksmith unavailable")
        if smith[1] != job[2]:
            raise ValueError("locksmith works in another area")
        cur.execute("UPDATE locksmith_jobs SET status = 'dispatched', locksmith_id = {}, eta_minutes = {} WHERE id = {}".format(smith[0], eta_minutes, job_id))
        cur.execute("UPDATE locksmiths SET busy = 1 WHERE id = {}".format(smith[0]))
        cur.execute("DELETE FROM dispatch_queue WHERE job_id = {}".format(job_id))
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    return smith[0]""",
[("""FROM locksmith_jobs WHERE id = {}".format(job_id))""", """FROM locksmith_jobs WHERE id = %s", (job_id,))"""),
 ("""WHERE phone = '{}'".format(locksmith_phone))""", """WHERE phone = %s", (locksmith_phone,))"""),
 ("""locksmith_id = {}, eta_minutes = {} WHERE id = {}".format(smith[0], eta_minutes, job_id))""", """locksmith_id = %s, eta_minutes = %s WHERE id = %s", (smith[0], eta_minutes, job_id))"""),
 ("""SET busy = 1 WHERE id = {}".format(smith[0]))""", """SET busy = 1 WHERE id = %s", (smith[0],))"""),
 ("""DELETE FROM dispatch_queue WHERE job_id = {}".format(job_id))""", """DELETE FROM dispatch_queue WHERE job_id = %s", (job_id,))""")], "mysql"),

("u482", """Import tide readings for a station, replacing any existing reading at the same time, and stamp the station's last import time.""", "normal",
"""def import_tide_readings(self, station, rows):
    if not rows:
        return {"inserted": 0, "replaced": 0}
    known = self.conn.execute(f"SELECT COUNT(*) FROM stations WHERE code = '{station}'").fetchone()[0]
    if known == 0:
        raise LookupError(station)
    inserted = 0
    removed = 0
    for taken_at, height in rows:
        existing = self.conn.execute(f"SELECT id FROM tide_readings WHERE station = '{station}' AND taken_at = '{taken_at}'").fetchone()
        if existing:
            self.conn.execute(f"DELETE FROM tide_readings WHERE id = {existing[0]}")
            removed += 1
        self.conn.execute(f"INSERT INTO tide_readings (station, taken_at, height) VALUES ('{station}', '{taken_at}', {height})")
        inserted += 1
    self.conn.execute(f"UPDATE stations SET last_import = datetime('now') WHERE code = '{station}'")
    self.conn.commit()
    heights = [height for _, height in rows]
    summary = {"inserted": inserted, "replaced": removed, "highest": max(heights), "lowest": min(heights)}
    self.log.info("tide import for %s: %s", station, summary)
    return summary""",
[("""self.conn.execute(f"SELECT COUNT(*) FROM stations WHERE code = '{station}'")""", """self.conn.execute("SELECT COUNT(*) FROM stations WHERE code = ?", (station,))"""),
 ("""self.conn.execute(f"SELECT id FROM tide_readings WHERE station = '{station}' AND taken_at = '{taken_at}'")""", """self.conn.execute("SELECT id FROM tide_readings WHERE station = ? AND taken_at = ?", (station, taken_at))"""),
 ("""self.conn.execute(f"INSERT INTO tide_readings (station, taken_at, height) VALUES ('{station}', '{taken_at}', {height})")""", """self.conn.execute("INSERT INTO tide_readings (station, taken_at, height) VALUES (?, ?, ?)", (station, taken_at, height))"""),
 ("""self.conn.execute(f"UPDATE stations SET last_import = datetime('now') WHERE code = '{station}'")""", """self.conn.execute("UPDATE stations SET last_import = datetime('now') WHERE code = ?", (station,))""")], "sqlite3"),

("u483", """Check a kayak out to a renter at the dock: look up the kayak and renter, check life jacket supply, store the rental, mark the kayak and jackets as out and remove the renter's waitlist entry for that kind of kayak.""", "normal",
"""def checkout_kayak(conn, kayak_tag, renter_name, renter_phone, hours, life_jackets, deposit_card):
    if hours < 1 or hours > 12:
        raise ValueError("rentals are 1 to 12 hours")
    if life_jackets < 1:
        raise ValueError("a life jacket is required")
    kayak = conn.execute("SELECT id, kind, hourly_rate, status FROM kayaks WHERE tag = '" + kayak_tag + "'").fetchone()
    if kayak is None:
        raise LookupError(kayak_tag)
    kayak_id, kind, rate, status = kayak
    if status != "dock":
        raise ValueError("kayak is not at the dock")
    jackets_free = conn.execute("SELECT COUNT(*) FROM life_jackets WHERE available = 1").fetchone()[0]
    if jackets_free < life_jackets:
        raise ValueError("not enough life jackets")
    renter = conn.execute("SELECT id, blocked FROM renters WHERE phone = '" + renter_phone + "'").fetchone()
    if renter is None:
        cur = conn.execute("INSERT INTO renters (name, phone) VALUES ('" + renter_name + "', '" + renter_phone + "')")
        renter_id = cur.lastrowid
    else:
        if renter[1]:
            raise PermissionError("renter is blocked")
        renter_id = renter[0]
    deposit = 20 if kind == "single" else 35
    cost = rate * hours
    cur = conn.execute(
        "INSERT INTO rentals (kayak_id, renter_id, hours, cost, deposit, card_last4, out_at) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))",
        (kayak_id, renter_id, hours, cost, deposit, deposit_card[-4:]),
    )
    rental_id = cur.lastrowid
    conn.execute("UPDATE kayaks SET status = 'out' WHERE id = ?", (kayak_id,))
    ids = [r[0] for r in conn.execute("SELECT id FROM life_jackets WHERE available = 1 ORDER BY id LIMIT ?", (life_jackets,)).fetchall()]
    for jacket_id in ids:
        conn.execute("UPDATE life_jackets SET available = 0, rental_id = ? WHERE id = ?", (rental_id, jacket_id))
    conn.execute("DELETE FROM kayak_waitlist WHERE phone = '" + renter_phone + "' AND kind = '" + kind + "'")
    conn.commit()
    receipt = {
        "rental": rental_id,
        "kayak": kayak_tag,
        "renter": renter_name,
        "hours": hours,
        "cost": cost,
        "deposit": deposit,
        "life_jackets": len(ids),
    }
    log.info("kayak %s rented to %s for %s hours", kayak_tag, renter_phone, hours)
    return receipt""",
[("""FROM kayaks WHERE tag = '" + kayak_tag + "'")""", """FROM kayaks WHERE tag = ?", (kayak_tag,))"""),
 ("""FROM renters WHERE phone = '" + renter_phone + "'")""", """FROM renters WHERE phone = ?", (renter_phone,))"""),
 ("""VALUES ('" + renter_name + "', '" + renter_phone + "')")""", """VALUES (?, ?)", (renter_name, renter_phone))"""),
 ("""WHERE phone = '" + renter_phone + "' AND kind = '" + kind + "'")""", """WHERE phone = ? AND kind = ?", (renter_phone, kind))""")], "sqlite3"),

("u484", """Enrol a student in a glassblowing class by class code and email: check the class has not started, create the student if needed, apply an optional promo code, confirm or waitlist the place, store the enrolment and remove the student's interest entry.""", "normal",
"""def enrol_in_glass_class(conn, class_code, student_email, student_name, payment_method, promo_code=None):
    if payment_method not in ("card", "cash", "voucher"):
        raise ValueError("unsupported payment method")
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT id, title, capacity, price, starts_on FROM glass_classes WHERE code = '{class_code}' FOR UPDATE")
        glass_class = cur.fetchone()
        if glass_class is None:
            raise LookupError(class_code)
        class_id, title, capacity, price, starts_on = glass_class
        if starts_on < date.today():
            raise ValueError("class has already started")
        cur.execute("SELECT COUNT(*) FROM glass_enrolments WHERE class_id = %s AND status = 'confirmed'", (class_id,))
        confirmed = cur.fetchone()[0]
        cur.execute(f"SELECT id FROM students WHERE email = '{student_email}'")
        student = cur.fetchone()
        if student is None:
            cur.execute("INSERT INTO students (name, email) VALUES (%s, %s) RETURNING id", (student_name, student_email))
            student = cur.fetchone()
        cur.execute("SELECT 1 FROM glass_enrolments WHERE class_id = %s AND student_id = %s", (class_id, student[0]))
        if cur.fetchone():
            raise ValueError("already enrolled")
        discount = 0
        if promo_code:
            cur.execute(f"SELECT percent FROM promo_codes WHERE code = '{promo_code}' AND valid_until >= CURRENT_DATE")
            promo = cur.fetchone()
            if promo is None:
                raise ValueError("promo code not valid")
            discount = promo[0]
        amount = round(price * (100 - discount) / 100, 2)
        status = "confirmed" if confirmed < capacity else "waitlist"
        cur.execute(
            "INSERT INTO glass_enrolments (class_id, student_id, status, amount, payment_method) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (class_id, student[0], status, amount, payment_method),
        )
        enrolment_id = cur.fetchone()[0]
        if status == "waitlist":
            cur.execute("UPDATE glass_classes SET waitlist_size = waitlist_size + 1 WHERE id = %s", (class_id,))
        cur.execute(f"DELETE FROM class_interest WHERE email = '{student_email}' AND class_code = '{class_code}'")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
    log.info("%s enrolled in %s as %s", student_email, class_code, status)
    return {"enrolment": enrolment_id, "class": title, "status": status, "amount": amount}""",
[("""cur.execute(f"SELECT id, title, capacity, price, starts_on FROM glass_classes WHERE code = '{class_code}' FOR UPDATE")""", """cur.execute("SELECT id, title, capacity, price, starts_on FROM glass_classes WHERE code = %s FOR UPDATE", (class_code,))"""),
 ("""cur.execute(f"SELECT id FROM students WHERE email = '{student_email}'")""", """cur.execute("SELECT id FROM students WHERE email = %s", (student_email,))"""),
 ("""cur.execute(f"SELECT percent FROM promo_codes WHERE code = '{promo_code}' AND valid_until >= CURRENT_DATE")""", """cur.execute("SELECT percent FROM promo_codes WHERE code = %s AND valid_until >= CURRENT_DATE", (promo_code,))"""),
 ("""cur.execute(f"DELETE FROM class_interest WHERE email = '{student_email}' AND class_code = '{class_code}'")""", """cur.execute("DELETE FROM class_interest WHERE email = %s AND class_code = %s", (student_email, class_code))""")], "psycopg2"),
]

ROWS += [
("u485", """Count hotel-style guests grouped by a column the caller names and return the counts as a dictionary.""", "hard_positive",
"""def count_by_column(conn, column):
    sql = "SELECT " + column + ", COUNT(*) FROM guests GROUP BY " + column + " ORDER BY COUNT(*) DESC"
    rows = conn.execute(sql).fetchall()
    counts = {}
    for value, total in rows:
        counts[value] = total
    log.info("counted guests by %s: %s groups", column, len(counts))
    return counts""",
[("""    sql = "SELECT " + column + ", COUNT(*) FROM guests""", """    column = GUEST_COLUMNS.get(column, "country")
    sql = "SELECT " + column + ", COUNT(*) FROM guests""")], "sqlite3"),

("u486", """Sum usage units per kind for an account between two dates, restricted to a list of kinds, using a query template and the shared database wrapper.""", "hard_positive",
"""def usage_for_period(self, account, start, end, kinds):
    kind_list = ", ".join("'" + k + "'" for k in kinds)
    sql = "SELECT kind, SUM(units) FROM usage WHERE account = '{a}' AND day BETWEEN '{s}' AND '{e}' AND kind IN ({k}) GROUP BY kind"
    sql = sql.format(a=account, s=start, e=end, k=kind_list)
    rows = self.db.fetch_all(sql)
    totals = {}
    for kind, units in rows:
        totals[kind] = float(units)
    self.log.info("usage for %s: %s kinds", account, len(totals))
    return totals""",
[("""    kind_list = ", ".join("'" + k + "'" for k in kinds)""", """    kind_list = ", ".join(["%s"] * len(kinds))"""),
 ("""WHERE account = '{a}' AND day BETWEEN '{s}' AND '{e}' AND kind IN ({k}) GROUP BY kind\"""", """WHERE account = %s AND day BETWEEN %s AND %s AND kind IN ({k}) GROUP BY kind\""""),
 ("""    sql = sql.format(a=account, s=start, e=end, k=kind_list)""", """    sql = sql.format(k=kind_list)
    params = [account, start, end] + list(kinds)"""),
 ("""self.db.fetch_all(sql)""", """self.db.fetch_all(sql, params)""")], "psycopg2"),

("u487", """Load a user's bookmarks view: read their saved sort column, folder and page size from the preferences table, list the bookmarks in that folder and count the folder's bookmarks.""", "hard_positive",
"""def load_bookmarks_view(conn, user_id):
    prefs = conn.execute("SELECT sort_column, folder, page_size FROM user_prefs WHERE user_id = ?", (user_id,)).fetchone()
    if prefs is None:
        prefs = ("created_at", "inbox", 25)
    sort_column, folder, page_size = prefs
    sql = "SELECT id, title, url, created_at FROM bookmarks WHERE owner_id = " + str(user_id) + " AND folder = '" + folder + "' ORDER BY " + sort_column + " DESC LIMIT " + str(int(page_size))
    rows = conn.execute(sql).fetchall()
    bookmarks = []
    for bookmark_id, title, url, created_at in rows:
        bookmarks.append({"id": bookmark_id, "title": title, "url": url, "created_at": created_at})
    total = conn.execute("SELECT COUNT(*) FROM bookmarks WHERE owner_id = " + str(user_id) + " AND folder = '" + folder + "'").fetchone()[0]
    conn.execute("UPDATE user_prefs SET last_view = datetime('now') WHERE user_id = ?", (user_id,))
    conn.commit()
    unread = [b for b in bookmarks if not b.get("read")]
    log.info("bookmarks view for %s: %s of %s shown, %s unread", user_id, len(bookmarks), total, len(unread))
    return {"folder": folder, "total": total, "bookmarks": bookmarks}""",
[("""AND folder = '" + folder + "' ORDER BY " + sort_column + " DESC LIMIT \"""", """AND folder = ? ORDER BY " + BOOKMARK_SORTS.get(sort_column, "created_at") + " DESC LIMIT \""""),
 ("""rows = conn.execute(sql).fetchall()""", """rows = conn.execute(sql, (folder,)).fetchall()"""),
 ("""AND folder = '" + folder + "'").fetchone()[0]""", """AND folder = ?", (folder,)).fetchone()[0]""")], "sqlite3"),

("u488", """Return the rows of a monthly events table for a region and kind with a running total of the amounts, choosing the table from a year-month string.""", "hard_positive",
"""def monthly_report_rows(session, year_month, region, kind, limit=500):
    table = "events_" + year_month
    sql = "SELECT id, region, kind, amount, happened_at FROM " + table + " WHERE region = '" + region + "' AND kind = '" + kind + "' ORDER BY happened_at LIMIT " + str(int(limit))
    rows = session.execute(text(sql)).fetchall()
    result = []
    running = 0
    for row in rows:
        running += row.amount
        result.append({"id": row.id, "region": row.region, "kind": row.kind, "amount": row.amount, "running_total": running})
    summary = {"table": table, "rows": len(result), "total": running}
    log.info("monthly report on %s: %s rows", table, len(result))
    return {"summary": summary, "rows": result}""",
[("""    table = "events_" + year_month""", """    if year_month not in AVAILABLE_MONTHS:
        raise ValueError(year_month)
    table = "events_" + year_month"""),
 ("""WHERE region = '" + region + "' AND kind = '" + kind + "' ORDER BY""", """WHERE region = :region AND kind = :kind ORDER BY"""),
 ("""session.execute(text(sql))""", """session.execute(text(sql), {"region": region, "kind": kind})""")], "sqlalchemy"),

("u489", """Delete the comments of a thread that contain any of a list of words, log the removal with the moderator and the words, and return how many comments were removed.""", "hard_positive",
"""def remove_comments_with_words(conn, thread_id, words, moderator):
    if not words:
        return 0
    patterns = []
    for word in words:
        patterns.append("body LIKE '%" + word + "%'")
    condition = " OR ".join(patterns)
    found = conn.execute("SELECT id FROM comments WHERE thread_id = ? AND (" + condition + ")", (thread_id,)).fetchall()
    ids = [row[0] for row in found]
    if not ids:
        return 0
    conn.execute("DELETE FROM comments WHERE thread_id = ? AND (" + condition + ")", (thread_id,))
    conn.execute("INSERT INTO moderation_log (thread_id, moderator, removed, words) VALUES (?, ?, ?, '" + ",".join(words) + "')", (thread_id, moderator, len(ids)))
    conn.commit()
    log.info("moderator %s removed %s comments", moderator, len(ids))
    return len(ids)""",
[("""    patterns = []
""", """    patterns = []
    params = []
"""),
 ("""        patterns.append("body LIKE '%" + word + "%'")""", """        patterns.append("body LIKE ?")
        params.append("%" + word + "%")"""),
 ("""AND (" + condition + ")", (thread_id,)).fetchall()""", """AND (" + condition + ")", [thread_id] + params).fetchall()"""),
 ("""DELETE FROM comments WHERE thread_id = ? AND (" + condition + ")", (thread_id,))""", """DELETE FROM comments WHERE thread_id = ? AND (" + condition + ")", [thread_id] + params)"""),
 ("""VALUES (?, ?, ?, '" + ",".join(words) + "')", (thread_id, moderator, len(ids)))""", """VALUES (?, ?, ?, ?)", (thread_id, moderator, len(ids), ",".join(words)))""")], "sqlite3"),

("u490", """Copy the current inventory of a warehouse into the snapshots table, optionally limited to some categories and a minimum quantity, and return how many snapshot rows exist for the label.""", "hard_positive",
"""def snapshot_inventory(conn, warehouse, categories=None, min_qty=None, label=None):
    sql = "INSERT INTO inventory_snapshots (warehouse, sku, qty, label, taken_at) SELECT warehouse, sku, qty, '" + (label or "adhoc") + "', NOW() FROM inventory WHERE warehouse = '" + warehouse + "'"
    if categories:
        sql += " AND category IN (" + ",".join("'" + c + "'" for c in categories) + ")"
    if min_qty is not None:
        sql += " AND qty >= " + str(min_qty)
    with conn.cursor() as cur:
        cur.execute(sql)
        created = cur.rowcount
        cur.execute("SELECT COUNT(*) FROM inventory_snapshots WHERE warehouse = '" + warehouse + "' AND label = '" + (label or "adhoc") + "'")
        total = cur.fetchone()[0]
    conn.commit()
    log.info("snapshot of %s created %s rows, label now has %s", warehouse, created, total)
    return {"created": created, "total": total}""",
[("""    sql = "INSERT INTO inventory_snapshots (warehouse, sku, qty, label, taken_at) SELECT warehouse, sku, qty, '" + (label or "adhoc") + "', NOW() FROM inventory WHERE warehouse = '" + warehouse + "'\"""", """    sql = "INSERT INTO inventory_snapshots (warehouse, sku, qty, label, taken_at) SELECT warehouse, sku, qty, %s, NOW() FROM inventory WHERE warehouse = %s"
    params = [label or "adhoc", warehouse]"""),
 ("""        sql += " AND category IN (" + ",".join("'" + c + "'" for c in categories) + ")\"""", """        sql += " AND category IN (" + ",".join(["%s"] * len(categories)) + ")"
        params.extend(categories)"""),
 ("""        sql += " AND qty >= " + str(min_qty)""", """        sql += " AND qty >= %s"
        params.append(min_qty)"""),
 ("""        cur.execute(sql)
""", """        cur.execute(sql, params)
"""),
 ("""WHERE warehouse = '" + warehouse + "' AND label = '" + (label or "adhoc") + "'")""", """WHERE warehouse = %s AND label = %s", (warehouse, label or "adhoc"))""")], "psycopg2"),

("u491", """Generate ride-share driver payouts for a period: sum fares and tips per driver with optional driver and city filters and a minimum amount, compute commission and net, and unless it is a dry run store the payout run and its lines and mark the rides as paid.""", "hard_positive",
"""def generate_payouts(conn, period_start, period_end, drivers=None, cities=None, min_amount=0, approver="system", dry_run=False):
    conditions = ["r.completed_on >= '" + period_start + "'", "r.completed_on <= '" + period_end + "'", "r.status = 'completed'"]
    if drivers:
        conditions.append("r.driver_id IN (" + ",".join("'" + d + "'" for d in drivers) + ")")
    if cities:
        conditions.append("r.city IN (" + ",".join("'" + c + "'" for c in cities) + ")")
    where = " AND ".join(conditions)
    sql = "SELECT r.driver_id, COUNT(*), SUM(r.fare), SUM(r.tip) FROM rides r WHERE " + where + " GROUP BY r.driver_id HAVING SUM(r.fare) + SUM(r.tip) >= " + str(float(min_amount))
    rows = conn.execute(sql).fetchall()
    payouts = []
    for driver_id, ride_count, fares, tips in rows:
        gross = fares + tips
        commission = round(fares * 0.2, 2)
        net = round(gross - commission, 2)
        payouts.append({"driver": driver_id, "rides": ride_count, "gross": gross, "commission": commission, "net": net})
    total_net = round(sum(p["net"] for p in payouts), 2)
    if dry_run or not payouts:
        return {"payouts": payouts, "total_net": total_net, "stored": False}
    run_id = conn.execute("INSERT INTO payout_runs (period_start, period_end, approver, total_net) VALUES ('" + period_start + "', '" + period_end + "', '" + approver + "', " + str(total_net) + ")").lastrowid
    for payout in payouts:
        conn.execute("INSERT INTO payout_lines (run_id, driver_id, rides, gross, commission, net) VALUES (" + str(run_id) + ", '" + payout["driver"] + "', " + str(payout["rides"]) + ", " + str(payout["gross"]) + ", " + str(payout["commission"]) + ", " + str(payout["net"]) + ")")
    conn.execute("UPDATE rides SET payout_run = " + str(run_id) + " WHERE " + where)
    conn.commit()
    top = sorted(payouts, key=lambda p: p["net"], reverse=True)[:3]
    by_city = {}
    for city_row in conn.execute("SELECT city, COUNT(*) FROM rides WHERE payout_run = ? GROUP BY city", (run_id,)).fetchall():
        by_city[city_row[0]] = city_row[1]
    log.info("payout run %s stored with %s lines", run_id, len(payouts))
    return {"run": run_id, "payouts": payouts, "top": top, "by_city": by_city, "total_net": total_net, "stored": True}""",
[("""    conditions = ["r.completed_on >= '" + period_start + "'", "r.completed_on <= '" + period_end + "'", "r.status = 'completed'"]""", """    conditions = ["r.completed_on >= ?", "r.completed_on <= ?", "r.status = 'completed'"]
    params = [period_start, period_end]"""),
 ("""        conditions.append("r.driver_id IN (" + ",".join("'" + d + "'" for d in drivers) + ")")""", """        conditions.append("r.driver_id IN (" + ",".join("?" for _ in drivers) + ")")
        params.extend(drivers)"""),
 ("""        conditions.append("r.city IN (" + ",".join("'" + c + "'" for c in cities) + ")")""", """        conditions.append("r.city IN (" + ",".join("?" for _ in cities) + ")")
        params.extend(cities)"""),
 ("""rows = conn.execute(sql).fetchall()""", """rows = conn.execute(sql, params).fetchall()"""),
 ("""VALUES ('" + period_start + "', '" + period_end + "', '" + approver + "', " + str(total_net) + ")").lastrowid""", """VALUES (?, ?, ?, ?)", (period_start, period_end, approver, total_net)).lastrowid"""),
 ("""VALUES (" + str(run_id) + ", '" + payout["driver"] + "', " + str(payout["rides"]) + ", " + str(payout["gross"]) + ", " + str(payout["commission"]) + ", " + str(payout["net"]) + ")")""", """VALUES (?, ?, ?, ?, ?, ?)", (run_id, payout["driver"], payout["rides"], payout["gross"], payout["commission"], payout["net"]))"""),
 ("""conn.execute("UPDATE rides SET payout_run = " + str(run_id) + " WHERE " + where)""", """conn.execute("UPDATE rides SET payout_run = ? WHERE " + where, [run_id] + params)""")], "sqlite3"),

("u492", """Async lead search with allowed field filters, a minimum score, a created-after date and a text search, a mapped sort order, paging and an optional saved search name, returning the page with the total and page count.""", "hard_positive",
"""async def search_leads(pool, filters, sort="created_at", direction="desc", page=1, per_page=25, save_as=None, owner=None):
    allowed = {"status": "status", "source": "source", "region": "region"}
    conditions = ["archived = false"]
    for key, value in filters.items():
        column = allowed.get(key)
        if column is None:
            continue
        if isinstance(value, (list, tuple)):
            conditions.append(column + " IN (" + ",".join("'" + str(v) + "'" for v in value) + ")")
        else:
            conditions.append(column + " = '" + str(value) + "'")
    if filters.get("min_score") is not None:
        conditions.append("score >= " + str(filters["min_score"]))
    if filters.get("created_after"):
        conditions.append("created_at >= '" + filters["created_after"] + "'")
    if filters.get("text"):
        conditions.append("(name ILIKE '%" + filters["text"] + "%' OR company ILIKE '%" + filters["text"] + "%')")
    where = " WHERE " + " AND ".join(conditions)
    sorts = {"created_at": "created_at", "score": "score", "name": "name"}
    order = sorts.get(sort, "created_at") + (" ASC" if direction == "asc" else " DESC")
    offset = (max(int(page), 1) - 1) * int(per_page)
    list_sql = "SELECT id, name, company, status, score, created_at FROM leads" + where + " ORDER BY " + order + " LIMIT " + str(int(per_page)) + " OFFSET " + str(offset)
    count_sql = "SELECT COUNT(*) FROM leads" + where
    async with pool.acquire() as conn:
        rows = await conn.fetch(list_sql)
        total = await conn.fetchval(count_sql)
        if save_as and owner:
            await conn.execute("INSERT INTO saved_searches (owner, name) VALUES ('" + owner + "', '" + save_as + "')")
    leads = []
    for row in rows:
        leads.append({"id": row["id"], "name": row["name"], "company": row["company"], "status": row["status"], "score": row["score"], "created_at": row["created_at"].isoformat()})
    best = max(leads, key=lambda lead: lead["score"]) if leads else None
    pages = (total + int(per_page) - 1) // int(per_page)
    log.info("lead search: %s of %s leads on page %s", len(leads), total, page)
    return {"total": total, "pages": pages, "page": page, "best": best, "leads": leads}""",
[("""    conditions = ["archived = false"]
""", """    conditions = ["archived = false"]
    params = []
"""),
 ("""            conditions.append(column + " IN (" + ",".join("'" + str(v) + "'" for v in value) + ")")""", """            marks = []
            for v in value:
                params.append(v)
                marks.append("$" + str(len(params)))
            conditions.append(column + " IN (" + ",".join(marks) + ")")"""),
 ("""            conditions.append(column + " = '" + str(value) + "'")""", """            params.append(value)
            conditions.append(column + " = $" + str(len(params)))"""),
 ("""        conditions.append("score >= " + str(filters["min_score"]))""", """        params.append(filters["min_score"])
        conditions.append("score >= $" + str(len(params)))"""),
 ("""        conditions.append("created_at >= '" + filters["created_after"] + "'")""", """        params.append(filters["created_after"])
        conditions.append("created_at >= $" + str(len(params)))"""),
 ("""        conditions.append("(name ILIKE '%" + filters["text"] + "%' OR company ILIKE '%" + filters["text"] + "%')")""", """        params.append("%" + filters["text"] + "%")
        conditions.append("(name ILIKE $" + str(len(params)) + " OR company ILIKE $" + str(len(params)) + ")")"""),
 ("""conn.fetch(list_sql)""", """conn.fetch(list_sql, *params)"""),
 ("""conn.fetchval(count_sql)""", """conn.fetchval(count_sql, *params)"""),
 ("""VALUES ('" + owner + "', '" + save_as + "')")""", """VALUES ($1, $2)", owner, save_as)""")], "other"),

("u493", """Return the distinct values of an allowed column of an allowed table in sorted order, up to a limit.""", "hard_negative",
"""def column_values(conn, table, column, limit):
    columns = {"members": ("name", "city"), "venues": ("name", "region")}
    if table not in columns or column not in columns[table]:
        raise ValueError("not allowed")
    rows = conn.execute(f"SELECT DISTINCT {column} FROM {table} ORDER BY {column} LIMIT ?", (limit,)).fetchall()
    values = [r[0] for r in rows]
    log.info("%s values in %s.%s", len(values), table, column)
    return values""", "", "sqlite3"),

("u494", """Record the same attendance status for many members at an event after checking the status against a fixed list.""", "hard_negative",
"""def record_attendance(conn, event_id, member_ids, status):
    event_id = int(event_id)
    if status not in ("present", "absent", "excused"):
        raise ValueError(status)
    rows = [(event_id, int(m)) for m in member_ids]
    conn.executemany(f"INSERT INTO attendance (event_id, member_id, status) VALUES (?, ?, '{status}')", rows)
    conn.commit()
    log.info("recorded %s attendance rows", len(rows))
    return len(rows)""", "", "sqlite3"),

("u495", """List a user's data exports newest, oldest or largest first with the limit clamped to one hundred.""", "hard_negative",
"""def list_exports(conn, owner, sort, limit):
    sorts = {"new": "requested_at DESC", "old": "requested_at ASC", "size": "bytes DESC"}
    order = sorts.get(sort, "requested_at DESC")
    limit = max(1, min(int(limit), 100))
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, bytes, requested_at FROM exports WHERE owner = %s ORDER BY " + order + " LIMIT " + str(limit), (owner,))
        rows = cur.fetchall()
    exports = [{"id": r[0], "name": r[1], "bytes": r[2], "requested_at": str(r[3])} for r in rows]
    log.info("listed %s exports for %s", len(exports), owner)
    return exports""", "", "psycopg2"),

("u496", """Find mail items with optional recipient, carrier, status list and date range filters, newest first, with a capped limit.""", "hard_negative",
"""def find_mail_items(conn, recipient=None, carrier=None, statuses=None, since=None, until=None, limit=100):
    conditions = []
    values = []
    if recipient:
        conditions.append("recipient = ?")
        values.append(recipient)
    if carrier:
        conditions.append("carrier = ?")
        values.append(carrier)
    if statuses:
        conditions.append("status IN (" + ",".join("?" for _ in statuses) + ")")
        values.extend(statuses)
    if since:
        conditions.append("received_on >= ?")
        values.append(since)
    if until:
        conditions.append("received_on <= ?")
        values.append(until)
    where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
    limit = max(1, min(int(limit), 500))
    sql = "SELECT id, recipient, carrier, status, received_on FROM mail_items" + where + " ORDER BY received_on DESC LIMIT " + str(limit)
    rows = conn.execute(sql, values).fetchall()
    return [dict(zip(("id", "recipient", "carrier", "status", "received_on"), row)) for row in rows]""", "", "sqlite3"),

("u497", """Set a status on many orders, returns or refunds by id in chunks of two hundred, choosing the table from a fixed mapping, and log the change.""", "hard_negative",
"""def bulk_set_status(self, table_key, ids, status, actor):
    tables = {"orders": "shop_orders", "returns": "shop_returns", "refunds": "shop_refunds"}
    table = tables.get(table_key)
    if table is None:
        raise ValueError("unknown table")
    if status not in ("open", "closed", "on_hold"):
        raise ValueError("unknown status")
    ids = [int(i) for i in ids]
    if not ids:
        return 0
    updated = 0
    cur = self.conn.cursor()
    try:
        for start in range(0, len(ids), 200):
            chunk = ids[start:start + 200]
            marks = ", ".join(["%s"] * len(chunk))
            cur.execute("UPDATE " + table + " SET status = %s, updated_by = %s WHERE id IN (" + marks + ")", [status, actor] + chunk)
            updated += cur.rowcount
        cur.execute("INSERT INTO status_changes (table_name, status, actor, n) VALUES (%s, %s, %s, %s)", (table, status, actor, updated))
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    return updated""", "", "mysql"),

("u498", """Admin endpoint that purges old sessions, invites or drafts, choosing the table and date column from a fixed mapping and requiring at least seven days, and writes an audit row.""", "hard_negative",
"""@app.route("/admin/purge", methods=["POST"])
@admin_required
def purge_records():
    kind = request.form.get("kind", "")
    targets = {"sessions": ("web_sessions", "last_seen"), "invites": ("invites", "sent_on"), "drafts": ("post_drafts", "saved_at")}
    target = targets.get(kind)
    if target is None:
        abort(400)
    try:
        days = int(request.form.get("days", "30"))
    except ValueError:
        abort(400)
    if days < 7:
        abort(400)
    table, column = target
    try:
        result = db.session.execute(text(f"DELETE FROM {table} WHERE {column} < :cutoff"), {"cutoff": datetime.utcnow() - timedelta(days=days)})
        db.session.execute(text("INSERT INTO admin_log (action, detail) VALUES ('purge', :detail)"), {"detail": kind + ":" + str(days)})
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        abort(500)
    return jsonify({"kind": kind, "removed": result.rowcount})""", "", "sqlalchemy"),
]
