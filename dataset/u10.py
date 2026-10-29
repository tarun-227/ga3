ROWS = [
("u389", """Log a school cafeteria meal for a student with its price and the current date, rolling back on a database error.""", "normal",
"""def log_cafeteria_meal(self, student_id, meal, price):
    try:
        self.conn.execute(f"INSERT INTO meals (student_id, meal, price, eaten_on) VALUES ({student_id}, '{meal}', {price}, date('now'))")
        self.conn.commit()
    except sqlite3.Error:
        self.conn.rollback()
        raise
    self.balance_cache.pop(student_id, None)
    self.log.info("meal %s logged for %s", meal, student_id)
    return price""",
[("""self.conn.execute(f"INSERT INTO meals (student_id, meal, price, eaten_on) VALUES ({student_id}, '{meal}', {price}, date('now'))")""", """self.conn.execute("INSERT INTO meals (student_id, meal, price, eaten_on) VALUES (?, ?, ?, date('now'))", (student_id, meal, price))""")], "sqlite3"),

("u390", """Endpoint that ends a tenant's tenancy of an allotment plot and reports how many tenancies were ended.""", "normal",
"""@app.route("/allotments/<int:plot_id>/tenant", methods=["DELETE"])
def end_tenancy(plot_id):
    tenant = request.args.get("tenant", "")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tenancies WHERE plot_id = {} AND tenant = '{}'".format(plot_id, tenant))
            ended = cur.rowcount
        conn.commit()
    except psycopg2.Error:
        conn.rollback()
        abort(500)
    return jsonify({"plot": plot_id, "ended": ended})""",
[("""plot_id = {} AND tenant = '{}'".format(plot_id, tenant))""", """plot_id = %s AND tenant = %s", (plot_id, tenant))""")], "psycopg2"),

("u391", """Set the state of an allotment plot, saving a note with it, and tell the watchers of the plot.""", "normal",
"""def set_plot_state(self, plot_no, state, note):
    sql = "UPDATE plots SET state = '" + state + "', note = ? WHERE plot_no = ?"
    try:
        cur = self.conn.execute(sql, (note, plot_no))
        if cur.rowcount == 0:
            raise KeyError(plot_no)
        self.conn.commit()
    except sqlite3.Error:
        self.conn.rollback()
        raise
    self.log.info("plot %s set to %s", plot_no, state)
    self.watchers.notify(plot_no)
    return state""",
[("""    sql = "UPDATE plots SET state""", """    if state not in PLOT_STATES:
        raise ValueError(state)
    sql = "UPDATE plots SET state""")], "sqlite3"),

("u392", """Flask endpoint that records an order of an item and quantity at a food stall and answers with the stall and item.""", "normal",
"""@app.route("/stalls/<stall>/orders", methods=["POST"])
def add_stall_order(stall):
    item = request.form.get("item", "")
    quantity = request.form.get("quantity", "1")
    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO stall_orders (stall, item, quantity) VALUES ('%s', '%s', %s)" % (stall, item, quantity))
        mysql.connection.commit()
    except Exception:
        mysql.connection.rollback()
        return jsonify({"error": "failed"}), 500
    finally:
        cur.close()
    return jsonify({"stall": stall, "item": item}), 201""",
[("""VALUES ('%s', '%s', %s)" % (stall, item, quantity))""", """VALUES (%s, %s, %s)", (stall, item, int(quantity)))""")], "mysql"),

("u393", """Release a locker rental for a customer email and return False when the database call fails.""", "normal",
"""def release_locker(self, locker_no, customer_email):
    try:
        with self.Session() as session:
            session.execute(text(f"DELETE FROM locker_rentals WHERE locker_no = {locker_no} AND email = '{customer_email}'"))
            session.commit()
    except SQLAlchemyError:
        self.log.exception("could not release locker %s", locker_no)
        return False
    self.free_lockers.add(locker_no)
    return True""",
[("""session.execute(text(f"DELETE FROM locker_rentals WHERE locker_no = {locker_no} AND email = '{customer_email}'"))""", """session.query(LockerRental).filter(LockerRental.locker_no == locker_no, LockerRental.email == customer_email).delete()""")], "sqlalchemy"),

("u394", """Async helper that records who cleaned a mountain hut and when, raising an error if no hut was updated.""", "normal",
"""async def mark_hut_cleaned(db, hut, cleaner, day):
    await db.execute(f"UPDATE huts SET cleaned_by = '{cleaner}', cleaned_on = '{day}' WHERE name = '{hut}'")
    await db.commit()
    async with db.execute("SELECT changes()") as cursor:
        row = await cursor.fetchone()
    if row[0] == 0:
        raise LookupError(hut)
    log.info("hut %s cleaned by %s", hut, cleaner)
    return row[0]""",
[("""await db.execute(f"UPDATE huts SET cleaned_by = '{cleaner}', cleaned_on = '{day}' WHERE name = '{hut}'")""", """await db.execute("UPDATE huts SET cleaned_by = ?, cleaned_on = ? WHERE name = ?", (cleaner, day, hut))""")], "other"),

("u395", """Admin-only endpoint that voids a chess game: store the reason in a voided games table and delete the game.""", "normal",
"""@app.route("/chess/games/<game_id>", methods=["DELETE"])
@admin_required
def void_game(game_id):
    reason = request.args.get("reason", "")
    db = get_db()
    db.execute("INSERT INTO voided_games (game_id, reason) VALUES ('%s', '%s')" % (game_id, reason))
    cur = db.execute("DELETE FROM games WHERE id = '%s'" % game_id)
    db.commit()
    return jsonify({"voided": cur.rowcount})""",
[("""VALUES ('%s', '%s')" % (game_id, reason))""", """VALUES (?, ?)", (game_id, reason))"""),
 ("""WHERE id = '%s'" % game_id)""", """WHERE id = ?", (game_id,))""")], "sqlite3"),

("u396", """Flask endpoint that searches rowing crews by club name fragment and boat class, returning JSON and reporting search failures.""", "normal",
"""@app.route("/rowing/crews")
def search_crews():
    club = request.args.get("club", "")
    boat = request.args.get("boat", "")
    db = get_db()
    try:
        rows = db.execute("SELECT id, name, boat_class, club FROM crews WHERE club LIKE '%" + club + "%' AND boat_class = '" + boat + "' ORDER BY name").fetchall()
    except sqlite3.Error:
        return jsonify({"error": "search failed"}), 500
    crews = []
    for row in rows:
        crews.append({"id": row[0], "name": row[1], "boat": row[2], "club": row[3]})
    return jsonify(crews)""",
[("""club LIKE '%" + club + "%' AND boat_class = '" + boat + "' ORDER BY name").fetchall()""", """club LIKE ? AND boat_class = ? ORDER BY name", ("%" + club + "%", boat)).fetchall()""")], "sqlite3"),

("u397", """Store a batch of water meter readings in one transaction and return how many were stored.""", "normal",
"""def add_water_readings(self, meter_id, readings):
    cur = self.conn.cursor()
    stored = 0
    try:
        for taken_at, cubic_m in readings:
            cur.execute(f"INSERT INTO water_readings (meter_id, taken_at, cubic_m) VALUES ('{meter_id}', '{taken_at}', {cubic_m})")
            stored += 1
        self.conn.commit()
    except psycopg2.Error:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    return stored""",
[("""cur.execute(f"INSERT INTO water_readings (meter_id, taken_at, cubic_m) VALUES ('{meter_id}', '{taken_at}', {cubic_m})")""", """cur.execute("INSERT INTO water_readings (meter_id, taken_at, cubic_m) VALUES (%s, %s, %s)", (meter_id, taken_at, cubic_m))""")], "psycopg2"),

("u398", """Command line helper that sets the note of a train in the timetable table and prints whether anything changed.""", "normal",
"""def set_timetable_note(db_path, train_no, note):
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("UPDATE timetable SET note = '" + note + "' WHERE train_no = '" + train_no + "'")
        conn.commit()
        if cur.rowcount == 0:
            print("no such train", train_no)
            return 1
        print("updated", cur.rowcount, "rows")
        return 0
    finally:
        conn.close()""",
[("""SET note = '" + note + "' WHERE train_no = '" + train_no + "'")""", """SET note = ? WHERE train_no = ?", (note, train_no))""")], "sqlite3"),

("u399", """Reassign a park ranger to a post and append the change to the post history in one transaction.""", "normal",
"""def reassign_ranger(self, post_id, ranger, since):
    cur = self.conn.cursor()
    try:
        cur.execute("UPDATE ranger_posts SET ranger = '{}', since = '{}' WHERE id = {}".format(ranger, since, post_id))
        cur.execute("INSERT INTO ranger_history (post_id, ranger, since) VALUES ({}, '{}', '{}')".format(post_id, ranger, since))
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    return ranger""",
[("""SET ranger = '{}', since = '{}' WHERE id = {}".format(ranger, since, post_id))""", """SET ranger = %s, since = %s WHERE id = %s", (ranger, since, post_id))"""),
 ("""VALUES ({}, '{}', '{}')".format(post_id, ranger, since))""", """VALUES (%s, %s, %s)", (post_id, ranger, since))""")], "mysql"),

("u400", """FastAPI endpoint that discards an unsold cheese batch and logs the reason, rolling back if anything fails.""", "normal",
"""@router.delete("/cheese/batches/{batch_no}")
def discard_batch(batch_no: str, reason: str, db: Session = Depends(get_db)):
    try:
        result = db.execute(text(f"DELETE FROM cheese_batches WHERE batch_no = '{batch_no}' AND status != 'sold'"))
        db.execute(text(f"INSERT INTO discard_log (batch_no, reason) VALUES ('{batch_no}', '{reason}')"))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="could not discard batch")
    return {"batch": batch_no, "discarded": result.rowcount}""",
[("""text(f"DELETE FROM cheese_batches WHERE batch_no = '{batch_no}' AND status != 'sold'"))""", """text("DELETE FROM cheese_batches WHERE batch_no = :batch_no AND status != 'sold'"), {"batch_no": batch_no})"""),
 ("""text(f"INSERT INTO discard_log (batch_no, reason) VALUES ('{batch_no}', '{reason}')"))""", """text("INSERT INTO discard_log (batch_no, reason) VALUES (:batch_no, :reason)"), {"batch_no": batch_no, "reason": reason})""")], "sqlalchemy"),

("u401", """Async method that loads defects for a list of buses at or above a severity level.""", "normal",
"""async def fetch_bus_defects(self, bus_ids, severity):
    id_list = ",".join(bus_ids)
    query = "SELECT bus_id, description, severity FROM defects WHERE bus_id IN (" + id_list + ") AND severity >= " + severity
    async with self.pool.acquire() as conn:
        rows = await conn.fetch(query)
    defects = [dict(row) for row in rows]
    self.log.info("loaded %s defects", len(defects))
    return defects""",
[("""    id_list = ",".join(bus_ids)""", """    id_list = ",".join(str(int(b)) for b in bus_ids)"""),
 ("""AND severity >= " + severity""", """AND severity >= " + str(int(severity))""")], "other"),
]

ROWS += [
("u402", """Book a swimming lane for a member at a time slot inside a transaction, refusing closed lanes and slots that are already full, and return the booking id.""", "normal",
"""def book_lane(self, member_id, lane, slot_start, minutes, guest_name):
    if minutes not in (30, 45, 60):
        raise ValueError("unsupported length")
    cur = self.conn.cursor()
    try:
        cur.execute("SELECT status, max_swimmers FROM lanes WHERE number = " + str(lane))
        info = cur.fetchone()
        if info is None:
            raise LookupError(lane)
        if info[0] != "open":
            raise ValueError("lane is closed")
        cur.execute("SELECT COUNT(*) FROM lane_bookings WHERE lane = " + str(lane) + " AND slot_start = '" + slot_start + "'")
        taken = cur.fetchone()[0]
        if taken >= info[1]:
            raise ValueError("lane is full for that slot")
        cur.execute("INSERT INTO lane_bookings (member_id, lane, slot_start, minutes, guest_name) VALUES (" + str(member_id) + ", " + str(lane) + ", '" + slot_start + "', " + str(minutes) + ", '" + guest_name + "')")
        booking_id = cur.lastrowid
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    self.log.info("lane %s booked for member %s", lane, member_id)
    return booking_id""",
[("""FROM lanes WHERE number = " + str(lane))""", """FROM lanes WHERE number = ?", (lane,))"""),
 ("""WHERE lane = " + str(lane) + " AND slot_start = '" + slot_start + "'")""", """WHERE lane = ? AND slot_start = ?", (lane, slot_start))"""),
 ("""VALUES (" + str(member_id) + ", " + str(lane) + ", '" + slot_start + "', " + str(minutes) + ", '" + guest_name + "')")""", """VALUES (?, ?, ?, ?, ?)", (member_id, lane, slot_start, minutes, guest_name))""")], "sqlite3"),

("u403", """Let a signed-in user back a crowdfunding project by slug with an amount, an optional reward tier and a message, checking that the project is published and still running.""", "normal",
"""@app.route("/projects/<slug>/back", methods=["POST"])
@login_required
def back_project(slug):
    amount = request.form.get("amount", "")
    reward = request.form.get("reward", "")
    message = request.form.get("message", "").strip()
    if not amount.replace(".", "", 1).isdigit():
        flash("Enter a valid amount")
        return redirect(url_for("project_page", slug=slug))
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(f"SELECT id, goal, ends_on FROM projects WHERE slug = '{slug}' AND published = true")
    project = cur.fetchone()
    if project is None:
        abort(404)
    if project[2] < date.today():
        flash("This project has ended")
        return redirect(url_for("project_page", slug=slug))
    if reward:
        cur.execute("SELECT minimum FROM rewards WHERE project_id = %s AND name = %s", (project[0], reward))
        tier = cur.fetchone()
        if tier is None or float(amount) < tier[0]:
            flash("Amount is too low for that reward")
            return redirect(url_for("project_page", slug=slug))
    cur.execute("INSERT INTO backings (project_id, backer_id, amount, reward, message) VALUES (%s, %s, %s, %s, %s)", (project[0], current_user.id, amount, reward, message))
    conn.commit()
    cur.close()
    flash("Thank you for backing this project")
    return redirect(url_for("project_page", slug=slug))""",
[("""cur.execute(f"SELECT id, goal, ends_on FROM projects WHERE slug = '{slug}' AND published = true")""", """cur.execute("SELECT id, goal, ends_on FROM projects WHERE slug = %s AND published = true", (slug,))""")], "psycopg2"),

("u404", """Import utility meter readings from a comma separated file, skipping unknown meters and readings that go backwards, and update each meter's last reading.""", "normal",
"""def import_meter_file(self, path, utility):
    imported = 0
    skipped = 0
    with open(path) as handle, self.engine.begin() as conn:
        for line_no, line in enumerate(handle, start=1):
            parts = line.strip().split(",")
            if len(parts) != 3:
                skipped += 1
                continue
            meter, reading, taken_at = parts
            known = conn.execute(text(f"SELECT id, last_reading FROM meters WHERE serial = '{meter}' AND utility = '{utility}'")).first()
            if known is None:
                skipped += 1
                continue
            value = float(reading)
            if value < known.last_reading:
                self.log.warning("line %s: reading went backwards", line_no)
                skipped += 1
                continue
            conn.execute(text("INSERT INTO meter_readings (meter_id, reading, taken_at) VALUES (:meter_id, :reading, :taken_at)"), {"meter_id": known.id, "reading": value, "taken_at": taken_at})
            conn.execute(text("UPDATE meters SET last_reading = :reading WHERE id = :meter_id"), {"reading": value, "meter_id": known.id})
            imported += 1
    self.log.info("imported %s readings, skipped %s", imported, skipped)
    return imported, skipped""",
[("""text(f"SELECT id, last_reading FROM meters WHERE serial = '{meter}' AND utility = '{utility}'"))""", """text("SELECT id, last_reading FROM meters WHERE serial = :meter AND utility = :utility"), {"meter": meter, "utility": utility})""")], "sqlalchemy"),

("u405", """Swap the shifts of two soup kitchen volunteers on a day in one transaction, checking both are trained for the other's role.""", "normal",
"""def swap_shifts(self, volunteer_a, volunteer_b, day):
    cur = self.conn.cursor()
    try:
        cur.execute("SELECT id, role FROM shifts WHERE volunteer = '" + volunteer_a + "' AND day = '" + day + "'")
        first = cur.fetchone()
        cur.execute("SELECT id, role FROM shifts WHERE volunteer = '" + volunteer_b + "' AND day = '" + day + "'")
        second = cur.fetchone()
        if first is None or second is None:
            raise LookupError("both volunteers need a shift on that day")
        if first[1] != second[1]:
            cur.execute("SELECT COUNT(*) FROM trained WHERE volunteer = '" + volunteer_a + "' AND role = '" + second[1] + "'")
            if cur.fetchone()[0] == 0:
                raise ValueError(volunteer_a + " is not trained for " + second[1])
            cur.execute("SELECT COUNT(*) FROM trained WHERE volunteer = '" + volunteer_b + "' AND role = '" + first[1] + "'")
            if cur.fetchone()[0] == 0:
                raise ValueError(volunteer_b + " is not trained for " + first[1])
        cur.execute("UPDATE shifts SET volunteer = '" + volunteer_b + "' WHERE id = " + str(first[0]))
        cur.execute("UPDATE shifts SET volunteer = '" + volunteer_a + "' WHERE id = " + str(second[0]))
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    return True""",
[("""WHERE volunteer = '" + volunteer_a + "' AND day = '" + day + "'")""", """WHERE volunteer = %s AND day = %s", (volunteer_a, day))"""),
 ("""WHERE volunteer = '" + volunteer_b + "' AND day = '" + day + "'")""", """WHERE volunteer = %s AND day = %s", (volunteer_b, day))"""),
 ("""FROM trained WHERE volunteer = '" + volunteer_a + "' AND role = '" + second[1] + "'")""", """FROM trained WHERE volunteer = %s AND role = %s", (volunteer_a, second[1]))"""),
 ("""FROM trained WHERE volunteer = '" + volunteer_b + "' AND role = '" + first[1] + "'")""", """FROM trained WHERE volunteer = %s AND role = %s", (volunteer_b, first[1]))"""),
 ("""SET volunteer = '" + volunteer_b + "' WHERE id = " + str(first[0]))""", """SET volunteer = %s WHERE id = %s", (volunteer_b, first[0]))"""),
 ("""SET volunteer = '" + volunteer_a + "' WHERE id = " + str(second[0]))""", """SET volunteer = %s WHERE id = %s", (volunteer_a, second[0]))""")], "mysql"),

("u406", """Record the results of one round of a chess tournament: validate each outcome, find the pairing, mark it final and add points to both players' standings.""", "normal",
"""def record_round_results(conn, tournament, round_no, results):
    recorded = 0
    problems = []
    for board, white, black, outcome in results:
        if outcome not in ("1-0", "0-1", "1/2-1/2"):
            problems.append((board, "bad outcome"))
            continue
        row = conn.execute("SELECT id, status FROM pairings WHERE tournament = '{}' AND round_no = {} AND board = {}".format(tournament, round_no, board)).fetchone()
        if row is None:
            problems.append((board, "no pairing"))
            continue
        if row[1] == "final":
            problems.append((board, "already final"))
            continue
        conn.execute("UPDATE pairings SET outcome = '{}', status = 'final' WHERE id = {}".format(outcome, row[0]))
        points = {"1-0": (1, 0), "0-1": (0, 1), "1/2-1/2": (0.5, 0.5)}[outcome]
        conn.execute("UPDATE standings SET points = points + {} WHERE tournament = '{}' AND player = '{}'".format(points[0], tournament, white))
        conn.execute("UPDATE standings SET points = points + {} WHERE tournament = '{}' AND player = '{}'".format(points[1], tournament, black))
        recorded += 1
    conn.commit()
    return {"recorded": recorded, "problems": problems}""",
[("""WHERE tournament = '{}' AND round_no = {} AND board = {}".format(tournament, round_no, board))""", """WHERE tournament = ? AND round_no = ? AND board = ?", (tournament, round_no, board))"""),
 ("""SET outcome = '{}', status = 'final' WHERE id = {}".format(outcome, row[0]))""", """SET outcome = ?, status = 'final' WHERE id = ?", (outcome, row[0]))"""),
 ("""points = points + {} WHERE tournament = '{}' AND player = '{}'".format(points[0], tournament, white))""", """points = points + ? WHERE tournament = ? AND player = ?", (points[0], tournament, white))"""),
 ("""points = points + {} WHERE tournament = '{}' AND player = '{}'".format(points[1], tournament, black))""", """points = points + ? WHERE tournament = ? AND player = ?", (points[1], tournament, black))""")], "sqlite3"),

("u407", """Restock a vending machine inside a transaction: add the delivered units to each slot, refuse deliveries that would overflow a slot and log the visit with the driver's name.""", "normal",
"""async def restock_machine(pool, machine_code, deliveries, driver):
    async with pool.acquire() as conn:
        async with conn.transaction():
            machine = await conn.fetchrow(f"SELECT id, location, capacity FROM machines WHERE code = '{machine_code}'")
            if machine is None:
                raise LookupError(machine_code)
            added = 0
            for slot, product, units in deliveries:
                current = await conn.fetchval("SELECT units FROM machine_slots WHERE machine_id = $1 AND slot = $2", machine["id"], slot)
                if current is None:
                    raise LookupError("slot " + slot)
                if current + units > machine["capacity"]:
                    raise ValueError("slot " + slot + " would overflow")
                await conn.execute("UPDATE machine_slots SET units = units + $1, product = $2 WHERE machine_id = $3 AND slot = $4", units, product, machine["id"], slot)
                added += units
            await conn.execute(f"INSERT INTO restock_log (machine_id, driver, units_added, restocked_at) VALUES ({machine['id']}, '{driver}', {added}, NOW())")
    return {"machine": machine_code, "location": machine["location"], "added": added}""",
[("""await conn.fetchrow(f"SELECT id, location, capacity FROM machines WHERE code = '{machine_code}'")""", """await conn.fetchrow("SELECT id, location, capacity FROM machines WHERE code = $1", machine_code)"""),
 ("""await conn.execute(f"INSERT INTO restock_log (machine_id, driver, units_added, restocked_at) VALUES ({machine['id']}, '{driver}', {added}, NOW())")""", """await conn.execute("INSERT INTO restock_log (machine_id, driver, units_added, restocked_at) VALUES ($1, $2, $3, NOW())", machine["id"], driver, added)""")], "other"),

("u408", """Django view that records a rent payment for a flat and month, rejecting months that are already paid, using the flat's rent amount.""", "normal",
"""@login_required
def mark_rent_paid(request, flat_id):
    month = request.POST.get("month", "")
    method = request.POST.get("method", "transfer")
    if not month:
        return HttpResponseBadRequest("month required")
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT rent_amount FROM rentals_flat WHERE id = {flat_id}")
        row = cursor.fetchone()
        if row is None:
            raise Http404("no such flat")
        cursor.execute(f"SELECT COUNT(*) FROM rentals_payment WHERE flat_id = {flat_id} AND month = '{month}'")
        if cursor.fetchone()[0]:
            return HttpResponseBadRequest("already paid")
        cursor.execute(f"INSERT INTO rentals_payment (flat_id, month, amount, method, paid_at) VALUES ({flat_id}, '{month}', {row[0]}, '{method}', NOW())")
    messages.success(request, "Payment recorded")
    return redirect("flat-detail", flat_id=flat_id)""",
[("""cursor.execute(f"SELECT rent_amount FROM rentals_flat WHERE id = {flat_id}")""", """cursor.execute("SELECT rent_amount FROM rentals_flat WHERE id = %s", [flat_id])"""),
 ("""cursor.execute(f"SELECT COUNT(*) FROM rentals_payment WHERE flat_id = {flat_id} AND month = '{month}'")""", """cursor.execute("SELECT COUNT(*) FROM rentals_payment WHERE flat_id = %s AND month = %s", [flat_id, month])"""),
 ("""cursor.execute(f"INSERT INTO rentals_payment (flat_id, month, amount, method, paid_at) VALUES ({flat_id}, '{month}', {row[0]}, '{method}', NOW())")""", """cursor.execute("INSERT INTO rentals_payment (flat_id, month, amount, method, paid_at) VALUES (%s, %s, %s, %s, NOW())", [flat_id, month, row[0], method])""")], "django_orm"),

("u409", """Book a stay at a mountain hut: look the hut up by name, check bed availability over the stay, find or create the guest, price the stay with meals, store it and add one meal order per night.""", "normal",
"""def book_hut_stay(conn, hut_name, guest_name, guest_email, arrival, nights, beds, meals, notes):
    if nights < 1 or nights > 14:
        raise ValueError("stays are 1 to 14 nights")
    if beds < 1:
        raise ValueError("at least one bed is needed")
    hut = conn.execute("SELECT id, total_beds, price_per_night, meal_price FROM huts WHERE name = '" + hut_name + "'").fetchone()
    if hut is None:
        raise LookupError(hut_name)
    hut_id, total_beds, price, meal_price = hut
    departure = (date.fromisoformat(arrival) + timedelta(days=nights)).isoformat()
    booked = conn.execute(
        "SELECT COALESCE(MAX(beds_used), 0) FROM (SELECT SUM(beds) AS beds_used FROM hut_stays WHERE hut_id = ? AND arrival < ? AND departure > ? GROUP BY arrival)",
        (hut_id, departure, arrival),
    ).fetchone()[0]
    if booked + beds > total_beds:
        raise ValueError("not enough free beds")
    guest = conn.execute("SELECT id FROM guests WHERE email = '" + guest_email + "'").fetchone()
    if guest is None:
        cur = conn.execute("INSERT INTO guests (name, email) VALUES ('" + guest_name + "', '" + guest_email + "')")
        guest_id = cur.lastrowid
    else:
        guest_id = guest[0]
    cost = price * beds * nights + meal_price * meals * beds
    cur = conn.execute(
        "INSERT INTO hut_stays (hut_id, guest_id, arrival, departure, beds, meals, cost, notes) VALUES (?, ?, ?, ?, ?, ?, ?, '" + notes + "')",
        (hut_id, guest_id, arrival, departure, beds, meals, cost),
    )
    stay_id = cur.lastrowid
    if meals:
        for day in range(nights):
            meal_day = (date.fromisoformat(arrival) + timedelta(days=day)).isoformat()
            conn.execute("INSERT INTO meal_orders (stay_id, meal_day, portions) VALUES (?, ?, ?)", (stay_id, meal_day, beds * meals))
    conn.commit()
    summary = {
        "stay": stay_id,
        "hut": hut_name,
        "arrival": arrival,
        "departure": departure,
        "beds": beds,
        "cost": cost,
    }
    log.info("hut stay %s booked for %s", stay_id, guest_email)
    return summary""",
[("""FROM huts WHERE name = '" + hut_name + "'")""", """FROM huts WHERE name = ?", (hut_name,))"""),
 ("""FROM guests WHERE email = '" + guest_email + "'")""", """FROM guests WHERE email = ?", (guest_email,))"""),
 ("""VALUES ('" + guest_name + "', '" + guest_email + "')")""", """VALUES (?, ?)", (guest_name, guest_email))"""),
 ("""VALUES (?, ?, ?, ?, ?, ?, ?, '" + notes + "')",
        (hut_id, guest_id, arrival, departure, beds, meals, cost),""", """VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (hut_id, guest_id, arrival, departure, beds, meals, cost, notes),""")], "sqlite3"),

("u410", """Close a bus maintenance work order in one transaction: verify the order and the mechanic, consume the spare parts used, compute labour and parts cost, mark the order closed and return the bus to service.""", "normal",
"""def close_work_order(conn, order_no, mechanic_badge, findings, parts_used, labour_minutes):
    if labour_minutes <= 0:
        raise ValueError("labour minutes must be positive")
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, bus_id, status FROM work_orders WHERE order_no = '%s' FOR UPDATE" % order_no)
        order = cur.fetchone()
        if order is None:
            raise LookupError(order_no)
        order_id, bus_id, status = order
        if status != "in_progress":
            raise ValueError("work order is not in progress")
        cur.execute("SELECT id, hourly_rate FROM mechanics WHERE badge = '%s' AND active = true" % mechanic_badge)
        mechanic = cur.fetchone()
        if mechanic is None:
            raise PermissionError("unknown or inactive mechanic")
        parts_cost = 0
        for part_no, qty in parts_used:
            cur.execute("SELECT id, unit_cost, stock FROM spare_parts WHERE part_no = %s FOR UPDATE", (part_no,))
            part = cur.fetchone()
            if part is None:
                raise LookupError(part_no)
            if part[2] < qty:
                raise ValueError("not enough stock of " + part_no)
            cur.execute("UPDATE spare_parts SET stock = stock - %s WHERE id = %s", (qty, part[0]))
            cur.execute("INSERT INTO work_order_parts (work_order_id, part_id, qty, unit_cost) VALUES (%s, %s, %s, %s)", (order_id, part[0], qty, part[1]))
            parts_cost += part[1] * qty
        labour_cost = round(mechanic[1] * labour_minutes / 60.0, 2)
        cur.execute(
            "UPDATE work_orders SET status = 'closed', closed_at = NOW(), mechanic_id = %s, labour_cost = %s, parts_cost = %s, findings = '%s' WHERE id = %s" % (mechanic[0], labour_cost, parts_cost, findings, order_id)
        )
        cur.execute("UPDATE buses SET status = 'available', last_service = CURRENT_DATE WHERE id = %s", (bus_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
    log.info("work order %s closed by %s", order_no, mechanic_badge)
    return {"order": order_no, "labour_cost": labour_cost, "parts_cost": parts_cost, "total": labour_cost + parts_cost}""",
[("""WHERE order_no = '%s' FOR UPDATE" % order_no)""", """WHERE order_no = %s FOR UPDATE", (order_no,))"""),
 ("""WHERE badge = '%s' AND active = true" % mechanic_badge)""", """WHERE badge = %s AND active = true", (mechanic_badge,))"""),
 ("""findings = '%s' WHERE id = %s" % (mechanic[0], labour_cost, parts_cost, findings, order_id)""", """findings = %s WHERE id = %s", (mechanic[0], labour_cost, parts_cost, findings, order_id)""")], "psycopg2"),
]

ROWS += [
("u411", """Count the bids matching any of the allowed fields in a dictionary of filters and return the count and total amount.""", "hard_positive",
"""def count_matching_bids(conn, filters):
    clauses = []
    for column, value in filters.items():
        if column in ("bidder", "lot", "status"):
            clauses.append(column + " = '" + str(value) + "'")
    where = " AND ".join(clauses) if clauses else "1 = 1"
    row = conn.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM bids WHERE " + where).fetchone()
    log.info("bids matching %s: %s", filters, row[0])
    return {"count": row[0], "total": row[1]}""",
[("""    clauses = []
""", """    clauses = []
    params = []
"""),
 ("""            clauses.append(column + " = '" + str(value) + "'")""", """            clauses.append(column + " = ?")
            params.append(value)"""),
 ("""+ where).fetchone()""", """+ where, params).fetchone()""")], "sqlite3"),

("u412", """Mark a list of purchase requisitions as shelved by building the list of ids first.""", "hard_positive",
"""def shelve_requisitions(conn, requisition_ids):
    parts = []
    for req_id in requisition_ids:
        parts.append(str(req_id))
    id_list = ",".join(parts)
    cur = conn.execute("UPDATE requisitions SET shelved = 1 WHERE id IN (" + id_list + ")")
    conn.commit()
    log.info("shelved %s requisitions", cur.rowcount)
    return cur.rowcount""",
[("""parts.append(str(req_id))""", """parts.append(str(int(req_id)))""")], "sqlite3"),

("u413", """Rank volunteers by hours or events, optionally for one team, through the pool's query helper.""", "hard_positive",
"""def ranked_volunteers(self, metric, team=None):
    sql = "SELECT name, team, hours, events FROM volunteers"
    if team:
        sql += " WHERE team = '" + team + "'"
    sql += " ORDER BY " + metric + " DESC"
    rows = self.pool.run_query(sql)
    ranked = []
    for position, row in enumerate(rows, start=1):
        ranked.append({"rank": position, "name": row[0], "team": row[1], "hours": row[2], "events": row[3]})
    self.log.info("ranked %s volunteers by %s", len(ranked), metric)
    return ranked""",
[("""        sql += " WHERE team = '" + team + "'\"""", """        sql += " WHERE team = %s\""""),
 ("""    sql += " ORDER BY " + metric + " DESC\"""", """    sql += " ORDER BY " + VOLUNTEER_METRICS.get(metric, "hours") + " DESC\""""),
 ("""self.pool.run_query(sql)""", """self.pool.run_query(sql, [team] if team else [])""")], "psycopg2"),

("u414", """Run a named dashboard query template for an owner since a date and return the rows grouped by day with a daily total.""", "hard_positive",
"""def run_dashboard_query(session, name, owner, since):
    template = DASHBOARD_QUERIES.get(name)
    if template is None:
        raise KeyError(name)
    if not owner or not since:
        raise ValueError("owner and since are required")
    sql = template.replace(":owner", "'" + owner + "'").replace(":since", "'" + since + "'")
    rows = session.execute(text(sql)).fetchall()
    result = [dict(row._mapping) for row in rows]
    by_day = {}
    for item in result:
        day = str(item.get("day"))
        by_day.setdefault(day, []).append(item)
    daily = []
    for day in sorted(by_day):
        items = by_day[day]
        total = sum(item.get("amount", 0) for item in items)
        daily.append({"day": day, "count": len(items), "total": total, "items": items})
    log.info("dashboard %s returned %s rows over %s days", name, len(result), len(daily))
    return {"name": name, "owner": owner, "daily": daily}""",
[("""    sql = template.replace(":owner", "'" + owner + "'").replace(":since", "'" + since + "'")
    rows = session.execute(text(sql)).fetchall()""", """    sql = template
    rows = session.execute(text(sql), {"owner": owner, "since": since}).fetchall()""")], "sqlalchemy"),

("u415", """Search garden notes whose body contains any of several words, optionally for one plot, ordered by a column the caller picks.""", "hard_positive",
"""def search_garden_notes(self, words, plot=None, order_by="created_at", limit=50):
    like_parts = []
    for word in words:
        like_parts.append("body LIKE '%" + word + "%'")
    sql = "SELECT id, plot, body, created_at FROM garden_notes"
    conditions = []
    if like_parts:
        conditions.append("(" + " OR ".join(like_parts) + ")")
    if plot:
        conditions.append("plot = '" + plot + "'")
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY " + order_by + " DESC LIMIT " + str(int(limit))
    rows = self.conn.execute(sql).fetchall()
    notes = []
    for note_id, plot_name, body, created_at in rows:
        notes.append({"id": note_id, "plot": plot_name, "body": body, "created_at": created_at})
    self.log.info("garden note search returned %s rows", len(notes))
    return notes""",
[("""    like_parts = []
""", """    like_parts = []
    params = []
"""),
 ("""        like_parts.append("body LIKE '%" + word + "%'")""", """        like_parts.append("body LIKE ?")
        params.append("%" + word + "%")"""),
 ("""        conditions.append("plot = '" + plot + "'")""", """        conditions.append("plot = ?")
        params.append(plot)"""),
 ("""" ORDER BY " + order_by + " DESC LIMIT \"""", """" ORDER BY " + NOTE_SORTS.get(order_by, "created_at") + " DESC LIMIT \""""),
 ("""self.conn.execute(sql).fetchall()""", """self.conn.execute(sql, params).fetchall()""")], "sqlite3"),

("u416", """Finish a crowdfunding project: sum its backings, mark it funded or failed using the slug and owner email stored on the project, refund backers on failure and queue a notification.""", "hard_positive",
"""def finalize_crowdfund(conn, project_id):
    cur = conn.cursor()
    cur.execute("SELECT slug, owner_email, goal FROM projects WHERE id = %s", (project_id,))
    project = cur.fetchone()
    if project is None:
        raise LookupError(project_id)
    slug, owner_email, goal = project
    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM backings WHERE project_id = %s", (project_id,))
    raised = cur.fetchone()[0]
    outcome = "funded" if raised >= goal else "failed"
    cur.execute("UPDATE projects SET status = '" + outcome + "', finalized_at = NOW() WHERE slug = '" + slug + "'")
    if outcome == "failed":
        cur.execute("UPDATE backings SET refunded = true WHERE project_id = %s", (project_id,))
    cur.execute("INSERT INTO outbox (recipient, subject) VALUES ('" + owner_email + "', 'Your project " + slug + " is " + outcome + "')")
    conn.commit()
    cur.close()
    log.info("project %s %s with %s raised", slug, outcome, raised)
    return {"slug": slug, "outcome": outcome, "raised": float(raised)}""",
[("""cur.execute("UPDATE projects SET status = '" + outcome + "', finalized_at = NOW() WHERE slug = '" + slug + "'")""", """cur.execute("UPDATE projects SET status = %s, finalized_at = NOW() WHERE slug = %s", (outcome, slug))"""),
 ("""VALUES ('" + owner_email + "', 'Your project " + slug + " is " + outcome + "')")""", """VALUES (%s, %s)", (owner_email, "Your project " + slug + " is " + outcome))""")], "psycopg2"),

("u417", """Async search of incident records by allowed fields in a dictionary, with a caller-chosen sort and direction and a row limit, returning counts per severity.""", "hard_positive",
"""async def search_incidents(db, filters, sort="occurred_at", direction="desc", limit=50):
    allowed = {"severity": "severity", "station": "station", "kind": "kind"}
    clauses = []
    for key, value in filters.items():
        column = allowed.get(key)
        if column is not None:
            clauses.append(column + " = '" + str(value) + "'")
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = "SELECT id, severity, station, kind, occurred_at FROM incidents" + where + " ORDER BY " + sort + " " + direction + " LIMIT " + str(int(limit))
    rows = await db.fetch(sql)
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "severity": row["severity"],
            "station": row["station"],
            "kind": row["kind"],
            "at": row["occurred_at"].isoformat(),
        })
    counts = {}
    for item in result:
        counts[item["severity"]] = counts.get(item["severity"], 0) + 1
    return {"count": len(result), "by_severity": counts, "items": result}""",
[("""    clauses = []
""", """    clauses = []
    params = []
"""),
 ("""            clauses.append(column + " = '" + str(value) + "'")""", """            params.append(value)
            clauses.append(column + " = $" + str(len(params)))"""),
 (""" ORDER BY " + sort + " " + direction + " LIMIT \"""", """ ORDER BY " + INCIDENT_SORTS.get(sort, "occurred_at") + " " + ("ASC" if direction == "asc" else "DESC") + " LIMIT \""""),
 ("""await db.fetch(sql)""", """await db.fetch(sql, *params)""")], "other"),

("u418", """Search the event catalogue with a text query, city, categories, price range, date range, sort and paging, returning the page, the total and optional category and city facets.""", "hard_positive",
"""def catalog_search(conn, text_query=None, city=None, categories=None, min_price=None, max_price=None, date_from=None, date_to=None, sort="date", page=1, per_page=20, facets=True):
    base = "FROM events e JOIN venues v ON v.id = e.venue_id"
    conditions = []
    if text_query:
        conditions.append("(e.title LIKE '%" + text_query + "%' OR e.description LIKE '%" + text_query + "%')")
    if city:
        conditions.append("v.city = '" + city + "'")
    if categories:
        quoted = ", ".join("'" + c + "'" for c in categories)
        conditions.append("e.category IN (" + quoted + ")")
    if min_price is not None:
        conditions.append("e.price >= " + str(min_price))
    if max_price is not None:
        conditions.append("e.price <= " + str(max_price))
    if date_from:
        conditions.append("e.starts_on >= '" + date_from + "'")
    if date_to:
        conditions.append("e.starts_on <= '" + date_to + "'")
    where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
    sort_map = {"date": "e.starts_on", "price": "e.price", "title": "e.title"}
    order = sort_map.get(sort, "e.starts_on")
    offset = (max(int(page), 1) - 1) * int(per_page)
    sql = "SELECT e.id, e.title, e.category, e.price, e.starts_on, v.name, v.city " + base + where + " ORDER BY " + order + " LIMIT " + str(int(per_page)) + " OFFSET " + str(offset)
    rows = conn.execute(sql).fetchall()
    total = conn.execute("SELECT COUNT(*) " + base + where).fetchone()[0]
    items = []
    for event_id, title, category, price, starts_on, venue, venue_city in rows:
        items.append({
            "id": event_id,
            "title": title,
            "category": category,
            "price": price,
            "starts_on": starts_on,
            "venue": venue,
            "city": venue_city,
        })
    result = {"total": total, "page": page, "items": items}
    if facets:
        facet_sql = "SELECT e.category, COUNT(*) " + base + where + " GROUP BY e.category ORDER BY COUNT(*) DESC"
        result["categories"] = {name: count for name, count in conn.execute(facet_sql).fetchall()}
        city_sql = "SELECT v.city, COUNT(*) " + base + where + " GROUP BY v.city ORDER BY COUNT(*) DESC LIMIT 10"
        result["cities"] = {name: count for name, count in conn.execute(city_sql).fetchall()}
    return result""",
[("""    conditions = []
""", """    conditions = []
    params = []
"""),
 ("""        conditions.append("(e.title LIKE '%" + text_query + "%' OR e.description LIKE '%" + text_query + "%')")""", """        conditions.append("(e.title LIKE ? OR e.description LIKE ?)")
        params.extend(["%" + text_query + "%", "%" + text_query + "%"])"""),
 ("""        conditions.append("v.city = '" + city + "'")""", """        conditions.append("v.city = ?")
        params.append(city)"""),
 ("""        quoted = ", ".join("'" + c + "'" for c in categories)
        conditions.append("e.category IN (" + quoted + ")")""", """        conditions.append("e.category IN (" + ", ".join("?" for _ in categories) + ")")
        params.extend(categories)"""),
 ("""        conditions.append("e.price >= " + str(min_price))""", """        conditions.append("e.price >= ?")
        params.append(min_price)"""),
 ("""        conditions.append("e.price <= " + str(max_price))""", """        conditions.append("e.price <= ?")
        params.append(max_price)"""),
 ("""        conditions.append("e.starts_on >= '" + date_from + "'")""", """        conditions.append("e.starts_on >= ?")
        params.append(date_from)"""),
 ("""        conditions.append("e.starts_on <= '" + date_to + "'")""", """        conditions.append("e.starts_on <= ?")
        params.append(date_to)"""),
 ("""rows = conn.execute(sql).fetchall()""", """rows = conn.execute(sql, params).fetchall()"""),
 ("""conn.execute("SELECT COUNT(*) " + base + where).fetchone()[0]""", """conn.execute("SELECT COUNT(*) " + base + where, params).fetchone()[0]"""),
 ("""conn.execute(facet_sql).fetchall()""", """conn.execute(facet_sql, params).fetchall()"""),
 ("""conn.execute(city_sql).fetchall()""", """conn.execute(city_sql, params).fetchall()""")], "sqlite3"),

("u419", """Sum an allowed numeric column of the sales or refunds table for one owner.""", "hard_negative",
"""def sum_column(conn, table, column, owner):
    tables = {"sales": ("sales", ("amount", "tax", "tip")), "refunds": ("refunds", ("amount", "fee"))}
    entry = tables.get(table)
    if entry is None or column not in entry[1]:
        raise ValueError("cannot sum that")
    total = conn.execute(f"SELECT COALESCE(SUM({column}), 0) FROM {entry[0]} WHERE owner = ?", (owner,)).fetchone()[0]
    log.info("%s of %s for %s: %s", column, table, owner, total)
    return total""", "", "sqlite3"),

("u420", """Insert several rows into one of three game tables with as many placeholders as the rows have columns.""", "hard_negative",
"""def store_game_rows(conn, table, rows):
    if table not in ("scores", "levels", "badges"):
        raise ValueError(table)
    width = len(rows[0])
    marks = ",".join("?" * width)
    conn.executemany(f"INSERT INTO {table} VALUES ({marks})", rows)
    conn.commit()
    log.info("inserted %s rows into %s", len(rows), table)
    return len(rows)""", "", "sqlite3"),

("u421", """Return one page of a product's price history at or above a minimum price, converting the minimum with Decimal and the page with int.""", "hard_negative",
"""def price_history_page(conn, sku, min_price, page):
    floor = Decimal(str(min_price))
    page = max(int(page), 1)
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT changed_on, price FROM price_history WHERE sku = %s AND price >= {floor} ORDER BY changed_on DESC LIMIT 25 OFFSET {(page - 1) * 25}",
            (sku,),
        )
        rows = cur.fetchall()
    history = [{"on": str(r[0]), "price": float(r[1])} for r in rows]
    log.info("price history page %s for %s", page, sku)
    return history""", "", "psycopg2"),

("u422", """Move a repair request to a new state using an enum, check the transition is allowed, optionally reassign it and add a comment, and write a history row in one transaction.""", "hard_negative",
"""def advance_repair_request(self, request_id, state, assignee=None, comment=None):
    new_state = RequestState(state)
    request_id = int(request_id)
    cur = self.conn.cursor()
    try:
        cur.execute("SELECT state, assignee FROM repair_requests WHERE id = %s FOR UPDATE", (request_id,))
        row = cur.fetchone()
        if row is None:
            raise LookupError(request_id)
        old_state = RequestState(row[0])
        if new_state not in ALLOWED_TRANSITIONS[old_state]:
            raise ValueError("cannot go from " + old_state.value + " to " + new_state.value)
        target = assignee or row[1]
        cur.execute(
            f"UPDATE repair_requests SET state = '{new_state.value}', assignee = %s, updated_at = NOW() WHERE id = {request_id}",
            (target,),
        )
        if comment:
            cur.execute("INSERT INTO request_comments (request_id, body) VALUES (%s, %s)", (request_id, comment))
        cur.execute("INSERT INTO request_history (request_id, old_state, new_state) VALUES (%s, %s, %s)", (request_id, old_state.value, new_state.value))
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    self.log.info("request %s: %s -> %s", request_id, old_state.value, new_state.value)
    return new_state.value""", "", "mysql"),

("u423", """List city trees with optional species, minimum height and ward filters, a mapped sort field, a sort direction and a capped limit, building the ward list with numbered bind parameters.""", "hard_negative",
"""@app.route("/api/trees")
def list_trees():
    sort_fields = {"species": "species", "planted": "planted_on", "height": "height_cm"}
    sort_column = sort_fields.get(request.args.get("sort"), "planted_on")
    direction = "ASC" if request.args.get("dir") == "asc" else "DESC"
    species = request.args.get("species")
    min_height = request.args.get("min_height")
    ward_ids = request.args.getlist("ward")
    clauses = []
    params = {}
    if species:
        clauses.append("species = :species")
        params["species"] = species
    if min_height:
        clauses.append("height_cm >= :min_height")
        params["min_height"] = int(min_height)
    if ward_ids:
        names = []
        for index, ward in enumerate(ward_ids):
            key = "ward_" + str(index)
            names.append(":" + key)
            params[key] = ward
        clauses.append("ward IN (" + ", ".join(names) + ")")
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    limit = min(request.args.get("limit", 50, type=int), 200)
    sql = "SELECT id, species, ward, height_cm, planted_on FROM trees" + where + " ORDER BY " + sort_column + " " + direction + " LIMIT " + str(limit)
    rows = db.session.execute(text(sql), params).fetchall()
    return jsonify([dict(r._mapping) for r in rows])""", "", "sqlalchemy"),

("u424", """Export chosen columns of a weather table for a list of region codes, checking table and column names against a permitted list and quoting the codes through the driver.""", "hard_negative",
"""def export_region_rows(conn, table, region_codes, columns, limit=1000):
    permitted = {
        "stations": ("code", "name", "region", "elevation"),
        "readings": ("station_code", "taken_at", "temperature", "region"),
    }
    if table not in permitted:
        raise ValueError("unknown table")
    for column in columns:
        if column not in permitted[table]:
            raise ValueError("unknown column " + column)
    if not region_codes:
        return []
    literals = sql.SQL(", ").join(sql.Literal(code) for code in region_codes)
    query = sql.SQL("SELECT {cols} FROM {tbl} WHERE region IN ({codes}) ORDER BY 1 LIMIT {n}").format(
        cols=sql.SQL(", ").join(sql.Identifier(c) for c in columns),
        tbl=sql.Identifier(table),
        codes=literals,
        n=sql.Literal(int(limit)),
    )
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    result = [dict(zip(columns, row)) for row in rows]
    log.info("exported %s rows from %s", len(result), table)
    return result""", "", "psycopg2"),

("u425", """Rebuild stored leaderboards for the requested known games over a day, week, month or all-time period, replacing old rows, and return the new row counts and each game's leader.""", "hard_negative",
"""def rebuild_leaderboards(conn, games, period, top_n, include_bots=False):
    periods = {"day": "-1 day", "week": "-7 days", "month": "-1 month", "all": None}
    if period not in periods:
        raise ValueError("unknown period")
    modifier = periods[period]
    known = {row[0] for row in conn.execute("SELECT slug FROM games")}
    wanted = [g for g in games if g in known]
    if not wanted:
        raise ValueError("no known games requested")
    top_n = max(1, min(int(top_n), 100))
    summary = {}
    for slug in wanted:
        conditions = ["game = ?"]
        values = [slug]
        if modifier is not None:
            conditions.append("played_at >= datetime('now', ?)")
            values.append(modifier)
        if not include_bots:
            conditions.append("is_bot = 0")
        where = " AND ".join(conditions)
        rows = conn.execute(
            f"SELECT player, MAX(score), COUNT(*) FROM scores WHERE {where} GROUP BY player ORDER BY MAX(score) DESC LIMIT {top_n}",
            values,
        ).fetchall()
        conn.execute("DELETE FROM leaderboard WHERE game = ? AND period = ?", (slug, period))
        for rank, (player, best, plays) in enumerate(rows, start=1):
            conn.execute(
                "INSERT INTO leaderboard (game, period, rank, player, best_score, plays) VALUES (?, ?, ?, ?, ?, ?)",
                (slug, period, rank, player, best, plays),
            )
        summary[slug] = len(rows)
    conn.commit()
    total = sum(summary.values())
    leaders = {}
    for slug in wanted:
        top = conn.execute(
            "SELECT player, best_score FROM leaderboard WHERE game = ? AND period = ? AND rank = 1",
            (slug, period),
        ).fetchone()
        leaders[slug] = {"player": top[0], "score": top[1]} if top else None
    log.info("rebuilt %s leaderboard rows for %s games", total, len(wanted))
    return {"period": period, "rows": total, "per_game": summary, "leaders": leaders}""", "", "sqlite3"),
]
