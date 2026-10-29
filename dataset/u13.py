ROWS = [
("u499", """Endpoint listing the controls of an orienteering course on a terrain type, highest points first.""", "normal",
"""@app.route("/orienteering/controls")
def list_controls():
    course = request.args.get("course", "")
    terrain = request.args.get("terrain", "forest")
    rows = get_db().execute("SELECT code, x, y, points FROM controls WHERE course = '%s' AND terrain = '%s' ORDER BY points DESC" % (course, terrain)).fetchall()
    controls = [{"code": r[0], "x": r[1], "y": r[2], "points": r[3]} for r in rows]
    return jsonify({"course": course, "controls": controls})""",
[("""course = '%s' AND terrain = '%s' ORDER BY points DESC" % (course, terrain)).fetchall()""", """course = ? AND terrain = ? ORDER BY points DESC", (course, terrain)).fetchall()""")], "sqlite3"),

("u500", """Remove sold-out skate decks of a model and size from the inventory and return how many rows were removed.""", "normal",
"""def remove_deck(self, model, size):
    try:
        cur = self.conn.execute("DELETE FROM skate_decks WHERE model = '" + model + "' AND size = '" + size + "' AND stock = 0")
        self.conn.commit()
    except sqlite3.Error:
        self.conn.rollback()
        raise
    self.log.info("removed %s decks of model %s", cur.rowcount, model)
    return cur.rowcount""",
[("""WHERE model = '" + model + "' AND size = '" + size + "' AND stock = 0")""", """WHERE model = ? AND size = ? AND stock = 0", (model, size))""")], "sqlite3"),

("u501", """Set the target temperature of an aquarium tank and record which operator changed it.""", "normal",
"""def set_tank_temperature(conn, tank_id, celsius, operator):
    if not 10 <= celsius <= 32:
        raise ValueError("temperature out of range")
    conn.execute("UPDATE tanks SET target_temp = {}, adjusted_by = '{}' WHERE tank_id = '{}'".format(celsius, operator, tank_id))
    conn.commit()
    log.info("tank %s set to %s by %s", tank_id, celsius, operator)
    return celsius""",
[("""target_temp = {}, adjusted_by = '{}' WHERE tank_id = '{}'".format(celsius, operator, tank_id))""", """target_temp = ?, adjusted_by = ? WHERE tank_id = ?", (celsius, operator, tank_id))""")], "sqlite3"),

("u502", """Bottle route that searches a vintage record shop by part of the artist name and an exact genre, cheapest first.""", "normal",
"""@route("/records/search")
def search_records():
    artist = request.query.get("artist", "")
    genre = request.query.get("genre", "")
    sql = "SELECT id, title, artist, price FROM records WHERE artist LIKE '%" + artist + "%' AND genre = '" + genre + "' ORDER BY price"
    rows = db.execute(sql).fetchall()
    response.content_type = "application/json"
    return json.dumps([{"id": r[0], "title": r[1], "artist": r[2], "price": r[3]} for r in rows])""",
[("""artist LIKE '%" + artist + "%' AND genre = '" + genre + "' ORDER BY price\"""", """artist LIKE ? AND genre = ? ORDER BY price\""""),
 ("""db.execute(sql)""", """db.execute(sql, ("%" + artist + "%", genre))""")], "sqlite3"),

("u503", """List knitting patterns of a craft sorted by a column and direction chosen by the caller.""", "normal",
"""def list_patterns(self, craft, sort, direction):
    sql = f"SELECT id, name, difficulty, hours FROM patterns WHERE craft = ? ORDER BY {sort} {direction}"
    rows = self.conn.execute(sql, (craft,)).fetchall()
    patterns = []
    for pattern_id, name, difficulty, hours in rows:
        patterns.append({"id": pattern_id, "name": name, "difficulty": difficulty, "hours": hours})
    self.log.info("%s patterns for %s", len(patterns), craft)
    self.cache["patterns"] = patterns
    return patterns""",
[("""ORDER BY {sort} {direction}\"""", """ORDER BY {PATTERN_SORTS.get(sort, 'name')} {'DESC' if direction == 'desc' else 'ASC'}\"""")], "sqlite3"),

("u504", """Delete a dog's walks older than a number of days and say whether anything was deleted.""", "normal",
"""def delete_old_walks(conn, dog_id, days):
    cur = conn.execute(f"DELETE FROM walks WHERE dog_id = {dog_id} AND walked_on < date('now', '-{days} days')")
    conn.commit()
    log.info("deleted %s walks for dog %s", cur.rowcount, dog_id)
    if cur.rowcount == 0:
        return False
    return True""",
[("""dog_id = {dog_id} AND""", """dog_id = {int(dog_id)} AND"""),
 ("""'-{days} days'""", """'-{int(days)} days'""")], "sqlite3"),

("u505", """Store a rating and last comment for a dog walker and return whether one walker was updated.""", "normal",
"""def rate_walker(self, walker_id, rating, comment):
    with self.conn.cursor() as cur:
        cur.execute("UPDATE walkers SET rating = " + str(rating) + ", last_comment = '" + comment + "' WHERE id = " + str(walker_id))
        updated = cur.rowcount
    self.conn.commit()
    self.log.info("walker %s rated %s", walker_id, rating)
    return updated == 1""",
[("""SET rating = " + str(rating) + ", last_comment = '" + comment + "' WHERE id = " + str(walker_id))""", """SET rating = %s, last_comment = %s WHERE id = %s", (rating, comment, walker_id))""")], "psycopg2"),

("u506", """FastAPI endpoint listing the lifeguard shifts of a beach on a day and answering 404 when there are none.""", "normal",
"""@router.get("/lifeguards/shifts")
def lifeguard_shifts(beach: str, day: str):
    with conn.cursor() as cur:
        cur.execute(f"SELECT guard, starts_at, ends_at FROM guard_shifts WHERE beach = '{beach}' AND shift_date = '{day}' ORDER BY starts_at")
        rows = cur.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="no shifts")
    return [{"guard": r[0], "starts": str(r[1]), "ends": str(r[2])} for r in rows]""",
[("""cur.execute(f"SELECT guard, starts_at, ends_at FROM guard_shifts WHERE beach = '{beach}' AND shift_date = '{day}' ORDER BY starts_at")""", """cur.execute("SELECT guard, starts_at, ends_at FROM guard_shifts WHERE beach = %s AND shift_date = %s ORDER BY starts_at", (beach, day))""")], "psycopg2"),

("u507", """Return the fish in an aquarium tank of a species, oldest first.""", "normal",
"""def fish_in_tank(self, tank, species):
    with self.engine.connect() as conn:
        rows = conn.execute(text(f"SELECT id, name, added_on FROM fish WHERE tank = '{tank}' AND species = '{species}' ORDER BY added_on")).fetchall()
    fish = [{"id": r.id, "name": r.name, "added_on": str(r.added_on)} for r in rows]
    self.log.info("%s fish in %s", len(fish), tank)
    return fish""",
[("""text(f"SELECT id, name, added_on FROM fish WHERE tank = '{tank}' AND species = '{species}' ORDER BY added_on"))""", """text("SELECT id, name, added_on FROM fish WHERE tank = :tank AND species = :species ORDER BY added_on"), {"tank": tank, "species": species})""")], "sqlalchemy"),

("u508", """Delete the pending pickups of a depot route and roll back if the delete fails.""", "normal",
"""def drop_pending_pickups(conn, depot, route):
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM pickups WHERE depot = '{}' AND route = '{}' AND status = 'pending'".format(depot, route))
        conn.commit()
        return cur.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()""",
[("""depot = '{}' AND route = '{}' AND status = 'pending'".format(depot, route))""", """depot = %s AND route = %s AND status = 'pending'", (depot, route))""")], "mysql"),

("u509", """JSON endpoint that changes the meeting day and location of a knitting circle and reports a failure as JSON.""", "normal",
"""@app.route("/knitting/circles/<int:circle_id>", methods=["PATCH"])
def update_circle(circle_id):
    data = request.get_json(silent=True) or {}
    meeting_day = data.get("meeting_day", "")
    location = data.get("location", "")
    if not meeting_day and not location:
        return jsonify({"error": "nothing to update"}), 400
    db = get_db()
    try:
        db.execute("UPDATE circles SET meeting_day = '" + meeting_day + "', location = '" + location + "' WHERE id = " + str(circle_id))
        db.commit()
    except sqlite3.Error:
        db.rollback()
        return jsonify({"error": "update failed"}), 500
    return jsonify({"id": circle_id, "meeting_day": meeting_day, "location": location})""",
[("""SET meeting_day = '" + meeting_day + "', location = '" + location + "' WHERE id = " + str(circle_id))""", """SET meeting_day = ?, location = ? WHERE id = ?", (meeting_day, location, circle_id))""")], "sqlite3"),

("u519", """List a club's unpaid dues for a year, ordered by due date.""", "normal",
"""def list_unpaid_dues(conn, club, year):
    sql = f"SELECT member, amount, due_on FROM dues WHERE club = '{club}' AND year = {year} AND paid = 0 ORDER BY due_on"
    rows = conn.execute(sql).fetchall()
    dues = [{"member": r[0], "amount": r[1], "due_on": r[2]} for r in rows]
    log.info("%s unpaid dues for %s in %s", len(dues), club, year)
    return dues""",
[("""club = '{club}' AND year = {year} AND paid = 0 ORDER BY due_on"
""", """club = ? AND year = ? AND paid = 0 ORDER BY due_on"
"""),
 ("""    sql = f"SELECT member""", """    sql = "SELECT member"""),
 ("""conn.execute(sql)""", """conn.execute(sql, (club, year))""")], "sqlite3"),
]

ROWS += [
("u510", """Cancel a cat cafe table reservation identified by code and email: work out the refund from the notice given, record the cancellation, release the table hold, store the refund and notify the next person on the waitlist.""", "normal",
"""def cancel_reservation(self, code, email, reason):
    row = self.conn.execute("SELECT id, table_no, seats, slot, deposit, status FROM reservations WHERE code = '" + code + "' AND email = '" + email + "'").fetchone()
    if row is None:
        raise LookupError(code)
    reservation_id, table_no, seats, slot, deposit, status = row
    if status == "cancelled":
        return {"refund": 0, "already": True}
    hours_left = (datetime.fromisoformat(slot) - datetime.utcnow()).total_seconds() / 3600
    refund = deposit if hours_left >= 24 else round(deposit / 2, 2) if hours_left >= 2 else 0
    self.conn.execute("UPDATE reservations SET status = 'cancelled', cancel_reason = '" + reason + "', cancelled_at = datetime('now') WHERE id = " + str(reservation_id))
    self.conn.execute("DELETE FROM table_holds WHERE reservation_id = " + str(reservation_id))
    if refund:
        self.conn.execute("INSERT INTO refunds (reservation_id, amount, reason) VALUES (" + str(reservation_id) + ", " + str(refund) + ", '" + reason + "')")
    waiting = self.conn.execute("SELECT id, email FROM waitlist WHERE slot = '" + slot + "' AND seats <= " + str(seats) + " ORDER BY created_at LIMIT 1").fetchone()
    self.conn.commit()
    if waiting:
        self.notifier.send(waiting[1], "A table is free at " + slot)
    self.log.info("reservation %s cancelled, refund %s", code, refund)
    return {"refund": refund, "already": False, "notified": bool(waiting)}""",
[("""WHERE code = '" + code + "' AND email = '" + email + "'")""", """WHERE code = ? AND email = ?", (code, email))"""),
 ("""cancel_reason = '" + reason + "', cancelled_at = datetime('now') WHERE id = " + str(reservation_id))""", """cancel_reason = ?, cancelled_at = datetime('now') WHERE id = ?", (reason, reservation_id))"""),
 ("""DELETE FROM table_holds WHERE reservation_id = " + str(reservation_id))""", """DELETE FROM table_holds WHERE reservation_id = ?", (reservation_id,))"""),
 ("""VALUES (" + str(reservation_id) + ", " + str(refund) + ", '" + reason + "')")""", """VALUES (?, ?, ?)", (reservation_id, refund, reason))"""),
 ("""WHERE slot = '" + slot + "' AND seats <= " + str(seats) + " ORDER BY created_at LIMIT 1")""", """WHERE slot = ? AND seats <= ? ORDER BY created_at LIMIT 1", (slot, seats))""")], "sqlite3"),

("u511", """Let a signed-in rowing club member leave a planned outing: check the outing and their place, remove them, log the reason and hand the lead to the next member if they were the leader.""", "normal",
"""@app.route("/outings/<int:outing_id>/leave", methods=["POST"])
@login_required
def leave_outing(outing_id):
    member = current_user.username
    reason = request.form.get("reason", "").strip()
    db = get_db()
    outing = db.execute(f"SELECT id, leader, starts_at, status FROM outings WHERE id = {outing_id}").fetchone()
    if outing is None:
        abort(404)
    if outing["status"] != "planned":
        flash("You can only leave planned outings")
        return redirect(url_for("outing_page", outing_id=outing_id))
    seat = db.execute(f"SELECT id FROM outing_members WHERE outing_id = {outing_id} AND member = '{member}'").fetchone()
    if seat is None:
        flash("You are not on this outing")
        return redirect(url_for("outing_page", outing_id=outing_id))
    db.execute(f"DELETE FROM outing_members WHERE id = {seat['id']}")
    db.execute(f"INSERT INTO outing_leaves (outing_id, member, reason, left_at) VALUES ({outing_id}, '{member}', '{reason}', datetime('now'))")
    if outing["leader"] == member:
        successor = db.execute(f"SELECT member FROM outing_members WHERE outing_id = {outing_id} ORDER BY id LIMIT 1").fetchone()
        new_leader = successor["member"] if successor else None
        db.execute("UPDATE outings SET leader = ? WHERE id = ?", (new_leader, outing_id))
    db.commit()
    flash("You left the outing")
    return redirect(url_for("outing_list"))""",
[("""db.execute(f"SELECT id FROM outing_members WHERE outing_id = {outing_id} AND member = '{member}'")""", """db.execute("SELECT id FROM outing_members WHERE outing_id = ? AND member = ?", (outing_id, member))"""),
 ("""db.execute(f"INSERT INTO outing_leaves (outing_id, member, reason, left_at) VALUES ({outing_id}, '{member}', '{reason}', datetime('now'))")""", """db.execute("INSERT INTO outing_leaves (outing_id, member, reason, left_at) VALUES (?, ?, ?, datetime('now'))", (outing_id, member, reason))""")], "sqlite3"),

("u512", """Log a radio contact in a contest: check the contest is running and the band is allowed, reject duplicate contacts on the same band and mode, store the contact with its points and increase the operator's contact count.""", "normal",
"""def log_contact(self, contest_id, callsign, band, mode, rst_sent, rst_rcvd, operator):
    cur = self.conn.cursor()
    try:
        cur.execute("SELECT status, bands FROM contests WHERE id = %s", (contest_id,))
        contest = cur.fetchone()
        if contest is None:
            raise LookupError(contest_id)
        if contest[0] != "running":
            raise ValueError("contest is not running")
        if band not in contest[1].split(","):
            raise ValueError("band not allowed")
        cur.execute("SELECT COUNT(*) FROM contacts WHERE contest_id = %d AND callsign = '%s' AND band = '%s' AND mode = '%s'" % (contest_id, callsign, band, mode))
        if cur.fetchone()[0]:
            raise ValueError("duplicate contact")
        points = 1 if band in ("40m", "80m") else 2
        cur.execute("INSERT INTO contacts (contest_id, callsign, band, mode, rst_sent, rst_rcvd, operator, points, logged_at) VALUES (%d, '%s', '%s', '%s', '%s', '%s', '%s', %d, NOW())" % (contest_id, callsign, band, mode, rst_sent, rst_rcvd, operator, points))
        cur.execute("UPDATE operators SET contacts = contacts + 1 WHERE callsign = '%s'" % operator)
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    return points""",
[("""contest_id = %d AND callsign = '%s' AND band = '%s' AND mode = '%s'" % (contest_id, callsign, band, mode))""", """contest_id = %s AND callsign = %s AND band = %s AND mode = %s", (contest_id, callsign, band, mode))"""),
 ("""VALUES (%d, '%s', '%s', '%s', '%s', '%s', '%s', %d, NOW())" % (contest_id, callsign, band, mode, rst_sent, rst_rcvd, operator, points))""", """VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())", (contest_id, callsign, band, mode, rst_sent, rst_rcvd, operator, points))"""),
 ("""WHERE callsign = '%s'" % operator)""", """WHERE callsign = %s", (operator,))""")], "psycopg2"),

("u513", """FastAPI endpoint that rents a beach hut for a date range: check the hut and that no rental overlaps, clear the guest's holds and store the rental with its total.""", "normal",
"""@router.post("/huts/{hut_id}/rent")
def rent_hut(hut_id: int, guest: str, start: str, end: str, db: Session = Depends(get_db)):
    if start >= end:
        raise HTTPException(status_code=422, detail="end must be after start")
    hut = db.execute(text("SELECT id, nightly_rate, active FROM huts WHERE id = :id"), {"id": hut_id}).first()
    if hut is None or not hut.active:
        raise HTTPException(status_code=404, detail="hut not available")
    clash = db.execute(text(f"SELECT COUNT(*) FROM hut_rentals WHERE hut_id = {hut_id} AND start_date < '{end}' AND end_date > '{start}'")).scalar()
    if clash:
        raise HTTPException(status_code=409, detail="hut already rented then")
    nights = (date.fromisoformat(end) - date.fromisoformat(start)).days
    total = hut.nightly_rate * nights
    db.execute(text(f"DELETE FROM hut_holds WHERE hut_id = {hut_id} AND guest = '{guest}'"))
    result = db.execute(text(f"INSERT INTO hut_rentals (hut_id, guest, start_date, end_date, total) VALUES ({hut_id}, '{guest}', '{start}', '{end}', {total}) RETURNING id"))
    rental_id = result.scalar()
    db.commit()
    log.info("hut %s rented to %s for %s nights", hut_id, guest, nights)
    return {"rental": rental_id, "nights": nights, "total": total}""",
[("""text(f"SELECT COUNT(*) FROM hut_rentals WHERE hut_id = {hut_id} AND start_date < '{end}' AND end_date > '{start}'"))""", """text("SELECT COUNT(*) FROM hut_rentals WHERE hut_id = :hut_id AND start_date < :end AND end_date > :start"), {"hut_id": hut_id, "end": end, "start": start})"""),
 ("""text(f"DELETE FROM hut_holds WHERE hut_id = {hut_id} AND guest = '{guest}'"))""", """text("DELETE FROM hut_holds WHERE hut_id = :hut_id AND guest = :guest"), {"hut_id": hut_id, "guest": guest})"""),
 ("""text(f"INSERT INTO hut_rentals (hut_id, guest, start_date, end_date, total) VALUES ({hut_id}, '{guest}', '{start}', '{end}', {total}) RETURNING id"))""", """text("INSERT INTO hut_rentals (hut_id, guest, start_date, end_date, total) VALUES (:hut_id, :guest, :start, :end, :total) RETURNING id"), {"hut_id": hut_id, "guest": guest, "start": start, "end": end, "total": total})""")], "sqlalchemy"),

("u514", """Close a monthly challenge by name: look up the challenge and the winner by email, count the entries, mark the challenge closed with its winner, store the prize and delete the draft entries.""", "normal",
"""def close_challenge(conn, challenge_name, winner_email, prize):
    if not prize.strip():
        raise ValueError("prize description required")
    if len(prize) > 200:
        raise ValueError("prize description too long")
    challenge = conn.execute("SELECT id, status FROM challenges WHERE name = '" + challenge_name + "'").fetchone()
    if challenge is None:
        raise LookupError(challenge_name)
    if challenge[1] == "closed":
        raise ValueError("challenge already closed")
    winner = conn.execute("SELECT id, display_name FROM participants WHERE email = '" + winner_email + "'").fetchone()
    if winner is None:
        raise LookupError(winner_email)
    entries = conn.execute("SELECT COUNT(*) FROM entries WHERE challenge_id = ?", (challenge[0],)).fetchone()[0]
    if entries == 0:
        raise ValueError("the challenge has no entries")
    conn.execute("UPDATE challenges SET status = 'closed', winner_id = ?, closed_at = datetime('now') WHERE id = ?", (winner[0], challenge[0]))
    conn.execute("INSERT INTO prizes (challenge_id, participant_id, description) VALUES (" + str(challenge[0]) + ", " + str(winner[0]) + ", '" + prize + "')")
    conn.execute("DELETE FROM draft_entries WHERE challenge_name = '" + challenge_name + "'")
    conn.commit()
    log.info("challenge %s closed with %s entries, winner %s", challenge_name, entries, winner[1])
    return {"challenge": challenge_name, "entries": entries, "winner": winner[1], "prize": prize}""",
[("""FROM challenges WHERE name = '" + challenge_name + "'")""", """FROM challenges WHERE name = ?", (challenge_name,))"""),
 ("""FROM participants WHERE email = '" + winner_email + "'")""", """FROM participants WHERE email = ?", (winner_email,))"""),
 ("""VALUES (" + str(challenge[0]) + ", " + str(winner[0]) + ", '" + prize + "')")""", """VALUES (?, ?, ?)", (challenge[0], winner[0], prize))"""),
 ("""DELETE FROM draft_entries WHERE challenge_name = '" + challenge_name + "'")""", """DELETE FROM draft_entries WHERE challenge_name = ?", (challenge_name,))""")], "sqlite3"),

("u515", """Log a fossil find at a dig site grid square: check the site is active, create the grid square if needed, store the find with depth, finder and notes and increase the site's find count.""", "normal",
"""def log_find(self, site, grid_ref, kind, depth_cm, finder, notes):
    if depth_cm < 0:
        raise ValueError("depth cannot be negative")
    cur = self.conn.cursor()
    cur.execute("SELECT id, status FROM dig_sites WHERE name = '%s'" % site)
    row = cur.fetchone()
    if row is None:
        raise LookupError(site)
    if row[1] != "active":
        raise ValueError("site is not active")
    cur.execute("SELECT id FROM grid_squares WHERE site_id = %d AND ref = '%s'" % (row[0], grid_ref))
    square = cur.fetchone()
    if square is None:
        cur.execute("INSERT INTO grid_squares (site_id, ref) VALUES (%d, '%s')" % (row[0], grid_ref))
        square_id = cur.lastrowid
    else:
        square_id = square[0]
    cur.execute("INSERT INTO finds (square_id, kind, depth_cm, finder, notes, found_at) VALUES (%d, '%s', %d, '%s', '%s', datetime('now'))" % (square_id, kind, depth_cm, finder, notes))
    find_id = cur.lastrowid
    cur.execute("UPDATE dig_sites SET find_count = find_count + 1 WHERE id = %d" % row[0])
    self.conn.commit()
    self.log.info("find %s logged at %s %s", find_id, site, grid_ref)
    return find_id""",
[("""WHERE name = '%s'" % site)""", """WHERE name = ?", (site,))"""),
 ("""WHERE site_id = %d AND ref = '%s'" % (row[0], grid_ref))""", """WHERE site_id = ? AND ref = ?", (row[0], grid_ref))"""),
 ("""VALUES (%d, '%s')" % (row[0], grid_ref))""", """VALUES (?, ?)", (row[0], grid_ref))"""),
 ("""VALUES (%d, '%s', %d, '%s', '%s', datetime('now'))" % (square_id, kind, depth_cm, finder, notes))""", """VALUES (?, ?, ?, ?, ?, datetime('now'))", (square_id, kind, depth_cm, finder, notes))""")], "sqlite3"),

("u516", """Reserve a food bank pickup slot for a household in a transaction: check bag stock and the one-pickup-per-week rule, refuse full slots, replace the household's uncollected slot and reduce the stock.""", "normal",
"""async def reserve_pickup_slot(pool, bank_code, household_ref, slot_time, bags):
    if bags < 1 or bags > 6:
        raise ValueError("bags must be 1 to 6")
    async with pool.acquire() as conn:
        async with conn.transaction():
            bank = await conn.fetchrow("SELECT id, bag_stock FROM food_banks WHERE code = '" + bank_code + "' FOR UPDATE")
            if bank is None:
                raise LookupError(bank_code)
            if bank["bag_stock"] < bags:
                raise ValueError("not enough bags in stock")
            household = await conn.fetchrow("SELECT id, last_pickup FROM households WHERE reference = '" + household_ref + "'")
            if household is None:
                raise LookupError(household_ref)
            if household["last_pickup"] is not None and (date.today() - household["last_pickup"]).days < 7:
                raise ValueError("one pickup per week")
            taken = await conn.fetchval("SELECT COUNT(*) FROM pickup_slots WHERE bank_id = $1 AND slot_time = $2", bank["id"], slot_time)
            if taken >= 3:
                raise ValueError("slot is full")
            await conn.execute("DELETE FROM pickup_slots WHERE household_id = $1 AND collected = false", household["id"])
            slot_id = await conn.fetchval("INSERT INTO pickup_slots (bank_id, household_id, slot_time, bags) VALUES ($1, $2, $3, $4) RETURNING id", bank["id"], household["id"], slot_time, bags)
            await conn.execute("UPDATE food_banks SET bag_stock = bag_stock - $1 WHERE id = $2", bags, bank["id"])
    return slot_id""",
[("""WHERE code = '" + bank_code + "' FOR UPDATE")""", """WHERE code = $1 FOR UPDATE", bank_code)"""),
 ("""WHERE reference = '" + household_ref + "'")""", """WHERE reference = $1", household_ref)""")], "other"),

("u517", """Store a bird survey submitted by an observer: look up the observer and site, enforce the verified-observer rule for protected sites, reject duplicates, store the survey, add each sighting of a known species, record unknown species separately and update the observer's survey count.""", "normal",
"""def submit_bird_survey(conn, observer_email, site_code, survey_date, start_time, duration_min, weather, sightings, notes):
    if duration_min <= 0 or duration_min > 480:
        raise ValueError("duration must be between 1 and 480 minutes")
    if not sightings:
        raise ValueError("at least one sighting is required")
    observer = conn.execute("SELECT id, name, verified FROM observers WHERE email = '" + observer_email + "'").fetchone()
    if observer is None:
        raise LookupError(observer_email)
    observer_id, observer_name, verified = observer
    site = conn.execute("SELECT id, region, protected FROM sites WHERE code = '" + site_code + "'").fetchone()
    if site is None:
        raise LookupError(site_code)
    site_id, region, protected = site
    if protected and not verified:
        raise PermissionError("only verified observers may survey protected sites")
    duplicate = conn.execute("SELECT COUNT(*) FROM surveys WHERE observer_id = ? AND site_id = ? AND survey_date = ? AND start_time = ?", (observer_id, site_id, survey_date, start_time)).fetchone()[0]
    if duplicate:
        raise ValueError("this survey was already submitted")
    cur = conn.execute(
        "INSERT INTO surveys (observer_id, site_id, survey_date, start_time, duration_min, weather, notes) VALUES (?, ?, ?, ?, ?, ?, '" + notes + "')",
        (observer_id, site_id, survey_date, start_time, duration_min, weather),
    )
    survey_id = cur.lastrowid
    total_birds = 0
    species_seen = set()
    for sighting in sightings:
        species = sighting["species"]
        count = int(sighting["count"])
        known = conn.execute("SELECT id FROM species WHERE common_name = '" + species + "'").fetchone()
        if known is None:
            conn.execute("INSERT INTO unknown_species (survey_id, name, count) VALUES (" + str(survey_id) + ", '" + species + "', " + str(count) + ")")
            continue
        conn.execute("INSERT INTO sightings (survey_id, species_id, count) VALUES (?, ?, ?)", (survey_id, known[0], count))
        total_birds += count
        species_seen.add(species)
    conn.execute("UPDATE observers SET survey_count = survey_count + 1 WHERE id = ?", (observer_id,))
    conn.commit()
    result = {
        "survey": survey_id,
        "observer": observer_name,
        "region": region,
        "species": len(species_seen),
        "birds": total_birds,
    }
    log.info("survey %s stored: %s species, %s birds", survey_id, len(species_seen), total_birds)
    return result""",
[("""FROM observers WHERE email = '" + observer_email + "'")""", """FROM observers WHERE email = ?", (observer_email,))"""),
 ("""FROM sites WHERE code = '" + site_code + "'")""", """FROM sites WHERE code = ?", (site_code,))"""),
 ("""VALUES (?, ?, ?, ?, ?, ?, '" + notes + "')",
        (observer_id, site_id, survey_date, start_time, duration_min, weather),""", """VALUES (?, ?, ?, ?, ?, ?, ?)",
        (observer_id, site_id, survey_date, start_time, duration_min, weather, notes),"""),
 ("""FROM species WHERE common_name = '" + species + "'")""", """FROM species WHERE common_name = ?", (species,))"""),
 ("""VALUES (" + str(survey_id) + ", '" + species + "', " + str(count) + ")")""", """VALUES (?, ?, ?)", (survey_id, species, count))""")], "sqlite3"),

("u518", """Record a reviewer's decision on a grant application for a signed-in reviewer: validate the decision and amount, lock the application and its funding round, check the budget, update the application, commit the funds, write a decision log row and notify the applicant.""", "normal",
"""@app.route("/grants/<int:application_id>/decide", methods=["POST"])
@reviewer_required
def decide_application(application_id):
    decision = request.form.get("decision", "")
    amount = request.form.get("amount", "0")
    comment = request.form.get("comment", "").strip()
    reviewer = current_user.username
    if decision not in ("approve", "reject", "defer"):
        abort(400)
    if decision == "approve" and not amount.replace(".", "", 1).isdigit():
        flash("Enter the approved amount")
        return redirect(url_for("application_page", application_id=application_id))
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT applicant_id, requested, status, round_id FROM applications WHERE id = %s FOR UPDATE", (application_id,))
        application = cur.fetchone()
        if application is None:
            abort(404)
        applicant_id, requested, status, round_id = application
        if status not in ("submitted", "deferred"):
            flash("This application was already decided")
            return redirect(url_for("application_page", application_id=application_id))
        cur.execute("SELECT budget, committed FROM grant_rounds WHERE id = %s FOR UPDATE", (round_id,))
        budget, committed = cur.fetchone()
        approved = float(amount) if decision == "approve" else 0
        if approved > requested:
            flash("Approved amount exceeds the request")
            return redirect(url_for("application_page", application_id=application_id))
        if committed + approved > budget:
            flash("Not enough budget left in this round")
            return redirect(url_for("application_page", application_id=application_id))
        cur.execute(f"UPDATE applications SET status = '{decision}', approved_amount = {approved}, decided_by = '{reviewer}', decision_comment = '{comment}' WHERE id = {application_id}")
        if approved:
            cur.execute("UPDATE grant_rounds SET committed = committed + %s WHERE id = %s", (approved, round_id))
        cur.execute(f"INSERT INTO decision_log (application_id, reviewer, decision, comment) VALUES ({application_id}, '{reviewer}', '{decision}', '{comment}')")
        cur.execute("INSERT INTO notifications (user_id, kind, ref) VALUES (%s, 'decision', %s)", (applicant_id, application_id))
        conn.commit()
    except psycopg2.Error:
        conn.rollback()
        flash("Could not save the decision")
        return redirect(url_for("application_page", application_id=application_id))
    finally:
        cur.close()
    flash("Decision saved: " + decision)
    return redirect(url_for("review_queue"))""",
[("""cur.execute(f"UPDATE applications SET status = '{decision}', approved_amount = {approved}, decided_by = '{reviewer}', decision_comment = '{comment}' WHERE id = {application_id}")""", """cur.execute("UPDATE applications SET status = %s, approved_amount = %s, decided_by = %s, decision_comment = %s WHERE id = %s", (decision, approved, reviewer, comment, application_id))"""),
 ("""cur.execute(f"INSERT INTO decision_log (application_id, reviewer, decision, comment) VALUES ({application_id}, '{reviewer}', '{decision}', '{comment}')")""", """cur.execute("INSERT INTO decision_log (application_id, reviewer, decision, comment) VALUES (%s, %s, %s, %s)", (application_id, reviewer, decision, comment))""")], "psycopg2"),
]

ROWS += [
("u520", """Find active dogs in the daycare register, optionally filtered by breed and size, ordered by name.""", "hard_positive",
"""def find_dogs(conn, breed=None, size=None):
    sql = "SELECT id, name, breed, size FROM dogs WHERE active = 1"
    if breed:
        sql += " AND breed = '" + breed + "'"
    if size:
        sql += " AND size = '" + size + "'"
    rows = conn.execute(sql + " ORDER BY name").fetchall()
    return [{"id": r[0], "name": r[1], "breed": r[2], "size": r[3]} for r in rows]""",
[("""    sql = "SELECT id, name, breed, size FROM dogs WHERE active = 1\"""", """    sql = "SELECT id, name, breed, size FROM dogs WHERE active = 1"
    params = []"""),
 ("""        sql += " AND breed = '" + breed + "'\"""", """        sql += " AND breed = ?"
        params.append(breed)"""),
 ("""        sql += " AND size = '" + size + "'\"""", """        sql += " AND size = ?"
        params.append(size)"""),
 ("""conn.execute(sql + " ORDER BY name")""", """conn.execute(sql + " ORDER BY name", params)""")], "sqlite3"),

("u521", """Load the sessions of several users, newest first, through the shared gateway object.""", "hard_positive",
"""def sessions_for_users(self, user_ids):
    id_list = ", ".join(user_ids)
    sql = "SELECT id, user_id, started_at FROM sessions WHERE user_id IN (" + id_list + ") ORDER BY started_at DESC"
    rows = self.gateway.query(sql)
    self.log.info("loaded %s sessions", len(rows))
    return rows""",
[("""    id_list = ", ".join(user_ids)""", """    id_list = ", ".join(str(int(u)) for u in user_ids)""")], "psycopg2"),

("u522", """Return the lifeguard roster of a beach for a week, grouped by day, filling the beach and week into a query template.""", "hard_positive",
"""def lifeguard_roster(conn, beach, week):
    sql = "SELECT guard, day, shift FROM roster WHERE beach = '@beach' AND week = '@week' ORDER BY day, shift"
    sql = sql.replace("@beach", beach).replace("@week", week)
    rows = conn.execute(sql).fetchall()
    roster = {}
    for guard, day, shift in rows:
        roster.setdefault(day, []).append((shift, guard))
    log.info("roster for %s week %s: %s days", beach, week, len(roster))
    return roster""",
[("""beach = '@beach' AND week = '@week' ORDER BY""", """beach = ? AND week = ? ORDER BY"""),
 ("""    sql = sql.replace("@beach", beach).replace("@week", week)""", """    params = (beach, week)"""),
 ("""conn.execute(sql)""", """conn.execute(sql, params)""")], "sqlite3"),

("u523", """Look up a donor by name or alias after rejecting names that contain a semicolon, comment marker or block comment start.""", "hard_positive",
"""def lookup_donor(conn, name):
    for bad in ("--", ";", "/*"):
        if bad in name:
            raise ValueError("invalid name")
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM donors WHERE name = '" + name + "' OR alias = '" + name + "'")
    row = cur.fetchone()
    cur.close()
    return row""",
[("""WHERE name = '" + name + "' OR alias = '" + name + "'")""", """WHERE name = %s OR alias = %s", (name, name))""")], "psycopg2"),

("u524", """Count accounts that match any of the allowed fields given in a dictionary of filters.""", "hard_positive",
"""def count_where(session, filters):
    parts = []
    for column in ("status", "region", "owner"):
        if column in filters:
            parts.append(column + " = '" + filters[column] + "'")
    where = " AND ".join(parts) or "1 = 1"
    return session.execute(text("SELECT COUNT(*) FROM accounts WHERE " + where)).scalar()""",
[("""    parts = []
""", """    parts = []
    params = {}
"""),
 ("""            parts.append(column + " = '" + filters[column] + "'")""", """            parts.append(column + " = :" + column)
            params[column] = filters[column]"""),
 ("""text("SELECT COUNT(*) FROM accounts WHERE " + where))""", """text("SELECT COUNT(*) FROM accounts WHERE " + where), params)""")], "sqlalchemy"),

("u525", """Run a scheduled CSV export: read the table, filter column, filter value and output path stored for the schedule, write the matching rows to the file and record how many rows were exported.""", "hard_positive",
"""def run_scheduled_export(self, schedule_id):
    cur = self.conn.cursor()
    cur.execute("SELECT table_name, filter_column, filter_value, output_path FROM export_schedules WHERE id = %s", (schedule_id,))
    schedule = cur.fetchone()
    if schedule is None:
        raise LookupError(schedule_id)
    table_name, filter_column, filter_value, output_path = schedule
    sql = "SELECT * FROM " + table_name + " WHERE " + filter_column + " = '" + filter_value + "' ORDER BY 1"
    cur.execute(sql)
    names = [d[0] for d in cur.description]
    rows = cur.fetchall()
    with open(output_path, "w") as handle:
        handle.write(",".join(names) + chr(10))
        for row in rows:
            handle.write(",".join(str(cell) for cell in row) + chr(10))
    cur.execute("UPDATE export_schedules SET last_run = NOW(), last_rows = %s WHERE id = %s", (len(rows), schedule_id))
    self.conn.commit()
    cur.close()
    self.log.info("export %s wrote %s rows to %s", schedule_id, len(rows), output_path)
    return len(rows)""",
[("""    sql = "SELECT * FROM " + table_name + " WHERE " + filter_column + " = '" + filter_value + "' ORDER BY 1\"""", """    sql = "SELECT * FROM " + EXPORTABLE_TABLES[table_name] + " WHERE " + EXPORTABLE_COLUMNS[filter_column] + " = %s ORDER BY 1\""""),
 ("""    cur.execute(sql)
""", """    cur.execute(sql, (filter_value,))
""")], "psycopg2"),

("u526", """Apply a list of insert, update and delete changes to the dogs, walks and walkers tables, validating table and column names, logging each change, and rolling everything back if any change is invalid.""", "hard_positive",
"""def apply_changeset(conn, changeset, actor):
    if not isinstance(changeset, list) or not changeset:
        raise ValueError("changeset must be a non-empty list")
    if len(changeset) > 500:
        raise ValueError("changeset too large")
    tables = {
        "dogs": ("id", ("name", "breed", "size", "owner")),
        "walks": ("id", ("dog_id", "walker", "walked_on", "minutes")),
        "walkers": ("id", ("name", "phone", "rating")),
    }
    applied = {"insert": 0, "update": 0, "delete": 0}
    errors = []
    for index, change in enumerate(changeset):
        table = change.get("table")
        action = change.get("action")
        if table not in tables or action not in applied:
            errors.append((index, "bad table or action"))
            continue
        key_column, columns = tables[table]
        values = change.get("values", {})
        unknown = [name for name in values if name not in columns]
        if unknown:
            errors.append((index, "unknown columns " + ",".join(unknown)))
            continue
        if action == "insert":
            names = ", ".join(values)
            literals = ", ".join("'" + str(v) + "'" for v in values.values())
            conn.execute("INSERT INTO " + table + " (" + names + ") VALUES (" + literals + ")")
        elif action == "update":
            assignments = ", ".join(name + " = '" + str(value) + "'" for name, value in values.items())
            conn.execute("UPDATE " + table + " SET " + assignments + " WHERE " + key_column + " = " + str(change["key"]))
        else:
            conn.execute("DELETE FROM " + table + " WHERE " + key_column + " = " + str(change["key"]))
        applied[action] += 1
        conn.execute("INSERT INTO change_log (table_name, action, actor, applied_at) VALUES ('" + table + "', '" + action + "', '" + actor + "', datetime('now'))")
    if errors:
        conn.rollback()
        return {"applied": {}, "errors": errors}
    conn.commit()
    counts = {}
    for table in tables:
        counts[table] = conn.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]
    log.info("changeset applied: %s", applied)
    return {"applied": applied, "errors": [], "counts": counts}""",
[("""            literals = ", ".join("'" + str(v) + "'" for v in values.values())
            conn.execute("INSERT INTO " + table + " (" + names + ") VALUES (" + literals + ")")""", """            marks = ", ".join("?" for _ in values)
            conn.execute("INSERT INTO " + table + " (" + names + ") VALUES (" + marks + ")", list(values.values()))"""),
 ("""            assignments = ", ".join(name + " = '" + str(value) + "'" for name, value in values.items())
            conn.execute("UPDATE " + table + " SET " + assignments + " WHERE " + key_column + " = " + str(change["key"]))""", """            assignments = ", ".join(name + " = ?" for name in values)
            conn.execute("UPDATE " + table + " SET " + assignments + " WHERE " + key_column + " = ?", list(values.values()) + [change["key"]])"""),
 ("""conn.execute("DELETE FROM " + table + " WHERE " + key_column + " = " + str(change["key"]))""", """conn.execute("DELETE FROM " + table + " WHERE " + key_column + " = ?", (change["key"],))"""),
 ("""VALUES ('" + table + "', '" + action + "', '" + actor + "', datetime('now'))")""", """VALUES (?, ?, ?, datetime('now'))", (table, action, actor))""")], "sqlite3"),

("u527", """Index @mentions in the posts of several threads in batches: find each mentioned user by handle, skip unknown handles and already indexed mentions, store new mentions and record the last thread processed.""", "hard_positive",
"""def index_mentions(conn, thread_ids, batch_size=100):
    if not thread_ids:
        return {"indexed": 0, "skipped": 0, "total_mentions": 0}
    if batch_size < 1 or batch_size > 1000:
        raise ValueError("batch size out of range")
    indexed = 0
    skipped = 0
    for start in range(0, len(thread_ids), batch_size):
        chunk = thread_ids[start:start + batch_size]
        id_list = ",".join(str(t) for t in chunk)
        cur = conn.cursor()
        cur.execute("SELECT id, thread_id, author, body FROM posts WHERE thread_id IN (" + id_list + ") ORDER BY id")
        posts = cur.fetchall()
        for post_id, thread_id, author, body in posts:
            handles = [word[1:] for word in body.split() if word.startswith("@") and len(word) > 1]
            for handle in handles:
                cur.execute("SELECT id FROM users WHERE handle = '" + handle + "'")
                user = cur.fetchone()
                if user is None:
                    skipped += 1
                    continue
                cur.execute("SELECT 1 FROM mentions WHERE post_id = " + str(post_id) + " AND user_id = " + str(user[0]))
                if cur.fetchone():
                    continue
                cur.execute("INSERT INTO mentions (post_id, thread_id, user_id, mentioned_by) VALUES (" + str(post_id) + ", " + str(thread_id) + ", " + str(user[0]) + ", '" + author + "')")
                indexed += 1
        cur.execute("UPDATE index_state SET last_thread = " + str(chunk[-1]) + ", updated_at = NOW() WHERE name = 'mentions'")
        conn.commit()
        cur.close()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM mentions")
    total = cur.fetchone()[0]
    cur.close()
    log.info("mention index: %s new, %s skipped, %s total", indexed, skipped, total)
    return {"indexed": indexed, "skipped": skipped, "total_mentions": total}""",
[("""        id_list = ",".join(str(t) for t in chunk)""", """        marks = ",".join(["%s"] * len(chunk))"""),
 ("""WHERE thread_id IN (" + id_list + ") ORDER BY id")""", """WHERE thread_id IN (" + marks + ") ORDER BY id", chunk)"""),
 ("""WHERE handle = '" + handle + "'")""", """WHERE handle = %s", (handle,))"""),
 ("""WHERE post_id = " + str(post_id) + " AND user_id = " + str(user[0]))""", """WHERE post_id = %s AND user_id = %s", (post_id, user[0]))"""),
 ("""VALUES (" + str(post_id) + ", " + str(thread_id) + ", " + str(user[0]) + ", '" + author + "')")""", """VALUES (%s, %s, %s, %s)", (post_id, thread_id, user[0], author))"""),
 ("""SET last_thread = " + str(chunk[-1]) + ", updated_at = NOW() WHERE name = 'mentions'")""", """SET last_thread = %s, updated_at = NOW() WHERE name = 'mentions'", (chunk[-1],))""")], "psycopg2"),

("u528", """Return one page of twenty feed items for an owner, newest first, with the page number converted to an integer.""", "hard_negative",
"""def feed_page(conn, owner, page):
    page = max(int(page), 1)
    offset = (page - 1) * 20
    sql = f"SELECT id, kind, body, created_at FROM feed WHERE owner = ? ORDER BY created_at DESC LIMIT 20 OFFSET {offset}"
    rows = conn.execute(sql, (owner,)).fetchall()
    log.info("feed page %s for %s", page, owner)
    return [{"id": r[0], "kind": r[1], "body": r[2], "at": r[3]} for r in rows]""", "", "sqlite3"),

("u529", """Return the newest row of an owner's notes, photos or files, choosing the table from a fixed mapping.""", "hard_negative",
"""def newest_row(conn, kind, owner):
    tables = {"notes": "notes", "photos": "photos", "files": "uploads"}
    table = tables.get(kind)
    if table is None:
        raise ValueError(kind)
    row = conn.execute(f"SELECT id, created_at FROM {table} WHERE owner = ? ORDER BY created_at DESC LIMIT 1", (owner,)).fetchone()
    log.info("newest %s of %s: %s", kind, owner, row)
    return row""", "", "sqlite3"),

("u530", """Return the distinct values of an allowed column of an allowed table in order.""", "hard_negative",
"""def distinct_values(conn, table, column):
    allowed = {"events": ("city", "category"), "members": ("city", "plan")}
    if table not in allowed or column not in allowed[table]:
        raise ValueError("not allowed")
    query = sql.SQL("SELECT DISTINCT {col} FROM {tbl} ORDER BY 1").format(col=sql.Identifier(column), tbl=sql.Identifier(table))
    with conn.cursor() as cur:
        cur.execute(query)
        return [row[0] for row in cur.fetchall()]""", "", "psycopg2"),

("u531", """Set task priorities from a list of (task id, priority) pairs using a Priority enum, updating tasks in chunks and logging each priority level.""", "hard_negative",
"""def set_task_priorities(conn, changes, actor):
    by_priority = {}
    for task_id, priority in changes:
        level = Priority(priority)
        by_priority.setdefault(level, []).append(int(task_id))
    updated = 0
    for level, ids in by_priority.items():
        for start in range(0, len(ids), 300):
            chunk = ids[start:start + 300]
            marks = ",".join("?" for _ in chunk)
            cur = conn.execute(
                f"UPDATE tasks SET priority = {level.value}, updated_by = ? WHERE id IN ({marks})",
                [actor] + chunk,
            )
            updated += cur.rowcount
        conn.execute(
            "INSERT INTO priority_log (priority, count, actor, logged_at) VALUES (?, ?, ?, datetime('now'))",
            (level.value, len(ids), actor),
        )
    conn.commit()
    summary = {level.name: len(ids) for level, ids in by_priority.items()}
    log.info("priorities updated: %s", summary)
    return {"updated": updated, "summary": summary}""", "", "sqlite3"),

("u532", """Save a user's settings from a dictionary using a fixed mapping from setting names to columns, validating choice values and creating the settings row if it does not exist.""", "hard_negative",
"""def save_settings(self, user_id, settings):
    columns = {"theme": "theme_name", "language": "lang_code", "timezone": "tz_name", "digest": "digest_freq"}
    choices = {"theme": ("light", "dark"), "digest": ("daily", "weekly", "never")}
    assignments = []
    values = []
    for key, value in settings.items():
        column = columns.get(key)
        if column is None:
            raise ValueError("unknown setting " + key)
        if key in choices and value not in choices[key]:
            raise ValueError("bad value for " + key)
        assignments.append(column + " = %s")
        values.append(value)
    if not assignments:
        return 0
    values.append(int(user_id))
    cur = self.conn.cursor()
    try:
        cur.execute("UPDATE user_settings SET " + ", ".join(assignments) + " WHERE user_id = %s", values)
        if cur.rowcount == 0:
            cur.execute("INSERT INTO user_settings (user_id) VALUES (%s)", (int(user_id),))
            cur.execute("UPDATE user_settings SET " + ", ".join(assignments) + " WHERE user_id = %s", values)
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    self.log.info("saved %s settings for %s", len(assignments), user_id)
    return len(assignments)""", "", "mysql"),

("u533", """Build a membership pivot table with row and column dimensions and a metric chosen from fixed mappings, optional date and club filters bound as parameters and a minimum cell value, returning the grid with row, column and grand totals.""", "hard_negative",
"""def membership_pivot(conn, rows_by, columns_by, metric, since=None, until=None, club=None, min_value=0):
    dimensions = {
        "club": "club_name",
        "plan": "plan_name",
        "city": "city",
        "year": "strftime('%Y', joined_on)",
        "month": "strftime('%Y-%m', joined_on)",
    }
    metrics = {"members": "COUNT(*)", "revenue": "SUM(fee)", "average_fee": "AVG(fee)"}
    if rows_by not in dimensions or columns_by not in dimensions:
        raise ValueError("unknown dimension")
    if rows_by == columns_by:
        raise ValueError("rows and columns must differ")
    expression = metrics.get(metric)
    if expression is None:
        raise ValueError("unknown metric")
    conditions = []
    values = []
    if since:
        conditions.append("joined_on >= ?")
        values.append(since)
    if until:
        conditions.append("joined_on <= ?")
        values.append(until)
    if club:
        conditions.append("club_name = ?")
        values.append(club)
    where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
    row_expr = dimensions[rows_by]
    col_expr = dimensions[columns_by]
    sql = (
        "SELECT " + row_expr + " AS r, " + col_expr + " AS c, " + expression + " AS v FROM memberships" + where
        + " GROUP BY r, c HAVING v >= " + repr(float(min_value)) + " ORDER BY r, c"
    )
    cells = conn.execute(sql, values).fetchall()
    row_labels = sorted({cell[0] for cell in cells}, key=str)
    column_labels = sorted({cell[1] for cell in cells}, key=str)
    grid = {r: {c: 0 for c in column_labels} for r in row_labels}
    for r, c, v in cells:
        grid[r][c] = v
    row_totals = {r: sum(grid[r].values()) for r in row_labels}
    column_totals = {c: sum(grid[r][c] for r in row_labels) for c in column_labels}
    grand_total = sum(row_totals.values())
    log.info("pivot %s by %s: %s x %s cells", rows_by, columns_by, len(row_labels), len(column_labels))
    return {
        "rows": row_labels,
        "columns": column_labels,
        "grid": grid,
        "row_totals": row_totals,
        "column_totals": column_totals,
        "total": grand_total,
    }""", "", "sqlite3"),
]
