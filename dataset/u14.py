ROWS = [
("u534", """Endpoint returning a ferry port's sailings for a service day, ordered by departure time.""", "normal",
"""@app.route("/ferries/schedule")
def ferry_schedule():
    port = request.args.get("port", "")
    day = request.args.get("day", "")
    rows = get_db().execute(f"SELECT departs, arrives, vessel FROM sailings WHERE port = '{port}' AND service_day = '{day}' ORDER BY departs").fetchall()
    sailings = [{"departs": r[0], "arrives": r[1], "vessel": r[2]} for r in rows]
    return jsonify({"port": port, "day": day, "sailings": sailings})""",
[("""get_db().execute(f"SELECT departs""", """get_db().execute("SELECT departs"""),
 ("""port = '{port}' AND service_day = '{day}' ORDER BY departs").fetchall()""", """port = ? AND service_day = ? ORDER BY departs", (port, day)).fetchall()""")], "sqlite3"),

("u535", """Delete a tag and all its links to articles and return how many links were removed.""", "normal",
"""def delete_tag(self, tag):
    links = self.conn.execute(f"DELETE FROM article_tags WHERE tag = '{tag}'")
    removed = links.rowcount
    self.conn.execute(f"DELETE FROM tags WHERE name = '{tag}'")
    self.conn.commit()
    self.log.info("deleted tag %s and %s links", tag, removed)
    self.tag_cache.discard(tag)
    return removed""",
[("""self.conn.execute(f"DELETE FROM article_tags WHERE tag = '{tag}'")""", """self.conn.execute("DELETE FROM article_tags WHERE tag = ?", (tag,))"""),
 ("""self.conn.execute(f"DELETE FROM tags WHERE name = '{tag}'")""", """self.conn.execute("DELETE FROM tags WHERE name = ?", (tag,))""")], "sqlite3"),

("u536", """Rename a playlist owned by a user and roll back if the update fails.""", "normal",
"""def rename_playlist(conn, owner, old_name, new_name):
    try:
        cur = conn.execute("UPDATE playlists SET name = '" + new_name + "' WHERE owner = '" + owner + "' AND name = '" + old_name + "'")
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    if cur.rowcount == 0:
        raise LookupError(old_name)
    log.info("playlist %s renamed to %s", old_name, new_name)
    return new_name""",
[("""SET name = '" + new_name + "' WHERE owner = '" + owner + "' AND name = '" + old_name + "'")""", """SET name = ? WHERE owner = ? AND name = ?", (new_name, owner, old_name))""")], "sqlite3"),

("u537", """Bottle route that deletes a bookmark by title for the user named in the query string.""", "normal",
"""@route("/bookmarks/<title>", method="DELETE")
def delete_bookmark(title):
    user = request.query.get("user", "")
    cur = db.execute("DELETE FROM bookmarks WHERE title = '%s' AND user = '%s'" % (title, user))
    db.commit()
    if cur.rowcount == 0:
        response.status = 404
        return {"error": "no such bookmark"}
    return {"deleted": title, "user": user}""",
[("""title = '%s' AND user = '%s'" % (title, user))""", """title = ? AND user = ?", (title, user))""")], "sqlite3"),

("u538", """Fetch spare parts by a list of ids and return their name and stock.""", "normal",
"""def parts_by_ids(conn, ids):
    if not ids:
        return []
    id_list = ",".join(ids)
    rows = conn.execute("SELECT id, name, stock FROM spare_parts WHERE id IN (" + id_list + ") ORDER BY name").fetchall()
    parts = [{"id": r[0], "name": r[1], "stock": r[2]} for r in rows]
    log.info("loaded %s parts of %s requested", len(parts), len(ids))
    return parts""",
[("""    id_list = ",".join(ids)""", """    id_list = ",".join(str(int(i)) for i in ids)""")], "sqlite3"),

("u539", """Search hiking trails whose name contains a term and return the first twenty-five with their length.""", "normal",
"""def find_trails(self, term, region):
    sql = "SELECT id, name, length_km, region FROM trails WHERE name LIKE '%{}%' AND region = '{}' ORDER BY length_km LIMIT 25".format(term, region)
    rows = self.conn.execute(sql).fetchall()
    trails = []
    for trail_id, name, length, trail_region in rows:
        trails.append({"id": trail_id, "name": name, "length": length, "region": trail_region})
    self.log.info("found %s trails for %s", len(trails), term)
    return trails""",
[("""LIKE '%{}%' AND region = '{}' ORDER BY length_km LIMIT 25".format(term, region)""", """LIKE ? AND region = ? ORDER BY length_km LIMIT 25\""""),
 ("""self.conn.execute(sql)""", """self.conn.execute(sql, ("%" + term + "%", region))""")], "sqlite3"),

("u540", """Django view that marks a marketplace listing as archived with a reason, using a raw cursor.""", "normal",
"""@login_required
def archive_listing(request, listing_id):
    reason = request.POST.get("reason", "")
    if not reason:
        return HttpResponseBadRequest("reason required")
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE market_listing SET archived = 1, archive_reason = '{reason}' WHERE id = {listing_id} AND seller_id = {request.user.id}")
    messages.success(request, "Listing archived")
    return redirect("my-listings")""",
[("""cursor.execute(f"UPDATE market_listing SET archived = 1, archive_reason = '{reason}' WHERE id = {listing_id} AND seller_id = {request.user.id}")""", """cursor.execute("UPDATE market_listing SET archived = 1, archive_reason = %s WHERE id = %s AND seller_id = %s", [reason, listing_id, request.user.id])""")], "django_orm"),

("u541", """Return the riders booked on a bus route on a date, ordered by seat number.""", "normal",
"""def riders_on_route(self, route, travel_date):
    with self.conn.cursor() as cur:
        cur.execute("SELECT name, seat, boarding_stop FROM riders WHERE route = '" + route + "' AND travel_date = '" + travel_date + "' ORDER BY seat")
        rows = cur.fetchall()
    riders = [{"name": r[0], "seat": r[1], "stop": r[2]} for r in rows]
    self.log.info("%s riders on %s", len(riders), route)
    return riders""",
[("""WHERE route = '" + route + "' AND travel_date = '" + travel_date + "' ORDER BY seat")""", """WHERE route = %s AND travel_date = %s ORDER BY seat", (route, travel_date))""")], "psycopg2"),

("u542", """FastAPI endpoint that deletes a rider's saved address by label and returns the number of deleted rows.""", "normal",
"""@router.delete("/riders/{rider_id}/addresses")
def delete_address(rider_id: int, label: str):
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM rider_addresses WHERE rider_id = {rider_id} AND label = '{label}'")
        deleted = cur.rowcount
    conn.commit()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="address not found")
    return {"rider": rider_id, "deleted": deleted}""",
[("""cur.execute(f"DELETE FROM rider_addresses WHERE rider_id = {rider_id} AND label = '{label}'")""", """cur.execute("DELETE FROM rider_addresses WHERE rider_id = %s AND label = %s", (rider_id, label))""")], "psycopg2"),

("u543", """Flask endpoint that updates the status and note of a workshop booking.""", "normal",
"""@app.route("/workshops/<int:booking_id>", methods=["PUT"])
def update_booking(booking_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status", "")
    note = data.get("note", "")
    stmt = "UPDATE workshop_bookings SET status = '{}', note = '{}' WHERE id = {}".format(status, note, booking_id)
    result = db.session.execute(text(stmt))
    db.session.commit()
    return jsonify({"id": booking_id, "updated": result.rowcount})""",
[("""status = '{}', note = '{}' WHERE id = {}".format(status, note, booking_id)""", """status = :status, note = :note WHERE id = :booking_id\""""),
 ("""db.session.execute(text(stmt))""", """db.session.execute(text(stmt), {"status": status, "note": note, "booking_id": booking_id})""")], "sqlalchemy"),

("u544", """Delete a customer's reminders of a given type and return how many were deleted.""", "normal",
"""def clear_reminders(self, customer_id, kind):
    with self.Session() as session:
        result = session.execute(text(f"DELETE FROM reminders WHERE customer_id = {customer_id} AND kind = '{kind}'"))
        session.commit()
    self.log.info("cleared %s reminders of kind %s", result.rowcount, kind)
    self.pending.pop(customer_id, None)
    return result.rowcount""",
[("""        result = session.execute(text(f"DELETE FROM reminders WHERE customer_id = {customer_id} AND kind = '{kind}'"))""", """        deleted = session.query(Reminder).filter(Reminder.customer_id == customer_id, Reminder.kind == kind).delete()"""),
 ("""    self.log.info("cleared %s reminders of kind %s", result.rowcount, kind)""", """    self.log.info("cleared %s reminders of kind %s", deleted, kind)"""),
 ("""    return result.rowcount""", """    return deleted""")], "sqlalchemy"),

("u545", """Change the phone number of a pharmacy supplier by company name and return whether a row was updated.""", "normal",
"""def update_supplier_phone(conn, company, phone):
    cur = conn.cursor()
    try:
        cur.execute("UPDATE suppliers SET phone = '" + phone + "' WHERE company = '" + company + "'")
        conn.commit()
        return cur.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()""",
[("""SET phone = '" + phone + "' WHERE company = '" + company + "'")""", """SET phone = %s WHERE company = %s", (phone, company))""")], "mysql"),
]

ROWS += [
("u546", """Let a signed-in worker give one of their rota shifts to a colleague: check the worker has the shift, the colleague exists and is under their shift limit, reassign the shift, clear pending requests and log the handover.""", "normal",
"""@app.route("/rota/<int:week>/giveaway", methods=["POST"])
@login_required
def give_away_shift(week):
    shift_day = request.form.get("day", "")
    recipient = request.form.get("recipient", "").strip()
    note = request.form.get("note", "").strip()
    db = get_db()
    mine = db.execute(f"SELECT id FROM rota WHERE week = {week} AND day = '{shift_day}' AND worker = '{current_user.username}'").fetchone()
    if mine is None:
        flash("You do not have a shift that day")
        return redirect(url_for("rota_page", week=week))
    target = db.execute(f"SELECT id, max_shifts FROM workers WHERE username = '{recipient}' AND active = 1").fetchone()
    if target is None:
        flash("Unknown colleague")
        return redirect(url_for("rota_page", week=week))
    load = db.execute(f"SELECT COUNT(*) FROM rota WHERE week = {week} AND worker = '{recipient}'").fetchone()[0]
    if load >= target["max_shifts"]:
        flash("That colleague already has the maximum number of shifts")
        return redirect(url_for("rota_page", week=week))
    db.execute(f"UPDATE rota SET worker = '{recipient}' WHERE id = {mine['id']}")
    db.execute(f"DELETE FROM giveaway_requests WHERE rota_id = {mine['id']}")
    db.execute("INSERT INTO giveaway_log (rota_id, from_worker, to_worker, note) VALUES (?, ?, ?, ?)", (mine["id"], current_user.username, recipient, note))
    db.commit()
    flash("Shift handed over to " + recipient)
    return redirect(url_for("rota_page", week=week))""",
[("""db.execute(f"SELECT id FROM rota WHERE week = {week} AND day = '{shift_day}' AND worker = '{current_user.username}'")""", """db.execute("SELECT id FROM rota WHERE week = ? AND day = ? AND worker = ?", (week, shift_day, current_user.username))"""),
 ("""db.execute(f"SELECT id, max_shifts FROM workers WHERE username = '{recipient}' AND active = 1")""", """db.execute("SELECT id, max_shifts FROM workers WHERE username = ? AND active = 1", (recipient,))"""),
 ("""db.execute(f"SELECT COUNT(*) FROM rota WHERE week = {week} AND worker = '{recipient}'")""", """db.execute("SELECT COUNT(*) FROM rota WHERE week = ? AND worker = ?", (week, recipient))"""),
 ("""db.execute(f"UPDATE rota SET worker = '{recipient}' WHERE id = {mine['id']}")""", """db.execute("UPDATE rota SET worker = ? WHERE id = ?", (recipient, mine["id"]))""")], "sqlite3"),

("u547", """Record the return of a borrowed piece of equipment by its tag: work out the late fee, close the loan, set the item's condition, open a repair request if it is not in good condition and delete the loan's reminders.""", "normal",
"""def return_equipment(self, tag, condition, returned_by, notes):
    cur = self.conn.cursor()
    cur.execute("SELECT id, item, loan_id FROM equipment WHERE tag = '" + tag + "'")
    item = cur.fetchone()
    if item is None:
        raise LookupError(tag)
    if item[2] is None:
        raise ValueError("item is not on loan")
    cur.execute("SELECT borrower, due_on FROM loans WHERE id = " + str(item[2]))
    loan = cur.fetchone()
    late_days = max((date.today() - date.fromisoformat(loan[1])).days, 0)
    fee = late_days * 2
    cur.execute("UPDATE loans SET returned_on = date('now'), returned_by = '" + returned_by + "', late_fee = " + str(fee) + " WHERE id = " + str(item[2]))
    cur.execute("UPDATE equipment SET loan_id = NULL, condition = '" + condition + "' WHERE id = " + str(item[0]))
    if condition != "good":
        cur.execute("INSERT INTO repair_requests (equipment_id, notes, created_on) VALUES (" + str(item[0]) + ", '" + notes + "', date('now'))")
    cur.execute("DELETE FROM reminders WHERE loan_id = " + str(item[2]))
    self.conn.commit()
    cur.close()
    self.log.info("%s returned by %s, fee %s", tag, loan[0], fee)
    return {"item": item[1], "late_days": late_days, "fee": fee}""",
[("""FROM equipment WHERE tag = '" + tag + "'")""", """FROM equipment WHERE tag = ?", (tag,))"""),
 ("""returned_by = '" + returned_by + "', late_fee = " + str(fee) + " WHERE id = " + str(item[2]))""", """returned_by = ?, late_fee = ? WHERE id = ?", (returned_by, fee, item[2]))"""),
 ("""SET loan_id = NULL, condition = '" + condition + "' WHERE id = " + str(item[0]))""", """SET loan_id = NULL, condition = ? WHERE id = ?", (condition, item[0]))"""),
 ("""VALUES (" + str(item[0]) + ", '" + notes + "', date('now'))")""", """VALUES (?, ?, date('now'))", (item[0], notes))""")], "sqlite3"),

("u548", """Grade a quiz submission for a student by email: look up the quiz and student, enforce three attempts, compare each answer case-insensitively, store the attempt and delete the student's draft answers.""", "normal",
"""def grade_quiz_submission(conn, quiz_code, student_email, answers):
    quiz = conn.execute("SELECT id, pass_mark FROM quizzes WHERE code = '%s'" % quiz_code).fetchone()
    if quiz is None:
        raise LookupError(quiz_code)
    student = conn.execute("SELECT id FROM students WHERE email = '%s'" % student_email).fetchone()
    if student is None:
        raise LookupError(student_email)
    previous = conn.execute("SELECT COUNT(*) FROM attempts WHERE quiz_id = %d AND student_id = %d" % (quiz[0], student[0])).fetchone()[0]
    if previous >= 3:
        raise ValueError("no attempts left")
    score = 0
    for question_id, given in answers.items():
        correct = conn.execute("SELECT answer FROM questions WHERE id = ? AND quiz_id = ?", (question_id, quiz[0])).fetchone()
        if correct and correct[0].strip().lower() == given.strip().lower():
            score += 1
    passed = score >= quiz[1]
    conn.execute("INSERT INTO attempts (quiz_id, student_id, score, passed) VALUES (%d, %d, %d, %d)" % (quiz[0], student[0], score, int(passed)))
    conn.execute("DELETE FROM draft_answers WHERE quiz_id = %d AND student_email = '%s'" % (quiz[0], student_email))
    conn.commit()
    log.info("%s scored %s on %s", student_email, score, quiz_code)
    return {"score": score, "passed": passed, "attempts_left": 2 - previous}""",
[("""WHERE code = '%s'" % quiz_code)""", """WHERE code = ?", (quiz_code,))"""),
 ("""WHERE email = '%s'" % student_email)""", """WHERE email = ?", (student_email,))"""),
 ("""WHERE quiz_id = %d AND student_email = '%s'" % (quiz[0], student_email))""", """WHERE quiz_id = ? AND student_email = ?", (quiz[0], student_email))""")], "sqlite3"),

("u549", """Bottle route that records a boat inspection by registration number, stores the inspector's notes, updates the boat's status from the result and deletes its pending inspection bookings.""", "normal",
"""@route("/boats/<boat_id>/inspection", method="POST")
def record_inspection(boat_id):
    inspector = request.forms.get("inspector", "").strip()
    result = request.forms.get("result", "")
    hull = request.forms.get("hull_notes", "")
    engine = request.forms.get("engine_notes", "")
    if not inspector or result not in ("pass", "fail", "retest"):
        response.status = 422
        return {"error": "inspector and a valid result are required"}
    boat = db.execute("SELECT id, owner, status FROM boats WHERE reg_no = '%s'" % boat_id).fetchone()
    if boat is None:
        response.status = 404
        return {"error": "unknown boat"}
    db.execute("INSERT INTO inspections (boat_id, inspector, result, hull_notes, engine_notes, inspected_on) VALUES (%d, '%s', '%s', '%s', '%s', date('now'))" % (boat[0], inspector, result, hull, engine))
    new_status = "cleared" if result == "pass" else "restricted"
    db.execute("UPDATE boats SET status = '%s' WHERE id = %d" % (new_status, boat[0]))
    db.execute("DELETE FROM inspection_bookings WHERE boat_id = %d" % boat[0])
    db.commit()
    response.status = 201
    return {"boat": boat_id, "status": new_status}""",
[("""WHERE reg_no = '%s'" % boat_id)""", """WHERE reg_no = ?", (boat_id,))"""),
 ("""VALUES (%d, '%s', '%s', '%s', '%s', date('now'))" % (boat[0], inspector, result, hull, engine))""", """VALUES (?, ?, ?, ?, ?, date('now'))", (boat[0], inspector, result, hull, engine))""")], "sqlite3"),

("u550", """Move a confirmed lab booking to a new time window for its owner: check ownership and status, make sure no other booking overlaps, update the times, delete the booking's reminders and write a history row.""", "normal",
"""def reschedule_lab_booking(self, booking_id, new_start, new_end, requested_by):
    cur = self.conn.cursor()
    try:
        cur.execute("SELECT lab_id, owner, status FROM lab_bookings WHERE id = %s FOR UPDATE", (booking_id,))
        booking = cur.fetchone()
        if booking is None:
            raise LookupError(booking_id)
        if booking[1] != requested_by:
            raise PermissionError("only the owner can reschedule")
        if booking[2] != "confirmed":
            raise ValueError("only confirmed bookings can be moved")
        cur.execute("SELECT COUNT(*) FROM lab_bookings WHERE lab_id = %s AND id != %s AND start_at < '" + new_end + "' AND end_at > '" + new_start + "'", (booking[0], booking_id))
        if cur.fetchone()[0]:
            raise ValueError("lab is busy in that window")
        cur.execute("UPDATE lab_bookings SET start_at = '" + new_start + "', end_at = '" + new_end + "', moved_by = %s WHERE id = %s", (requested_by, booking_id))
        cur.execute("DELETE FROM lab_reminders WHERE booking_id = %s", (booking_id,))
        cur.execute("INSERT INTO lab_booking_history (booking_id, old_status, changed_by) VALUES (%s, 'confirmed', %s)", (booking_id, requested_by))
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    self.log.info("lab booking %s moved to %s", booking_id, new_start)
    return True""",
[("""AND start_at < '" + new_end + "' AND end_at > '" + new_start + "'", (booking[0], booking_id))""", """AND start_at < %s AND end_at > %s", (booking[0], booking_id, new_end, new_start))"""),
 ("""SET start_at = '" + new_start + "', end_at = '" + new_end + "', moved_by = %s WHERE id = %s", (requested_by, booking_id))""", """SET start_at = %s, end_at = %s, moved_by = %s WHERE id = %s", (new_start, new_end, requested_by, booking_id))""")], "psycopg2"),

("u551", """FastAPI endpoint that updates a menu item's name, price, category and availability, rejects duplicate names in the category, records a price change and clears the category's cached menu rows.""", "normal",
"""@router.put("/menu/{item_id}")
def update_menu_item(item_id: int, name: str, price: float, category: str, available: bool = True):
    if price <= 0:
        raise HTTPException(status_code=422, detail="price must be positive")
    cur = conn.cursor()
    cur.execute("SELECT name, price FROM menu_items WHERE id = %s FOR UPDATE", (item_id,))
    old = cur.fetchone()
    if old is None:
        raise HTTPException(status_code=404, detail="item not found")
    cur.execute(f"SELECT COUNT(*) FROM menu_items WHERE category = '{category}' AND name = '{name}' AND id != {item_id}")
    if cur.fetchone()[0]:
        raise HTTPException(status_code=409, detail="duplicate name in category")
    cur.execute(f"UPDATE menu_items SET name = '{name}', price = {price}, category = '{category}', available = {available} WHERE id = {item_id}")
    if old[1] != price:
        cur.execute("INSERT INTO price_history (item_id, old_price, new_price, changed_at) VALUES (%s, %s, %s, NOW())", (item_id, old[1], price))
    cur.execute(f"DELETE FROM menu_cache WHERE category = '{category}'")
    conn.commit()
    cur.close()
    log.info("menu item %s updated", item_id)
    return {"id": item_id, "name": name, "price": price, "category": category, "available": available}""",
[("""cur.execute(f"SELECT COUNT(*) FROM menu_items WHERE category = '{category}' AND name = '{name}' AND id != {item_id}")""", """cur.execute("SELECT COUNT(*) FROM menu_items WHERE category = %s AND name = %s AND id != %s", (category, name, item_id))"""),
 ("""cur.execute(f"UPDATE menu_items SET name = '{name}', price = {price}, category = '{category}', available = {available} WHERE id = {item_id}")""", """cur.execute("UPDATE menu_items SET name = %s, price = %s, category = %s, available = %s WHERE id = %s", (name, price, category, available, item_id))"""),
 ("""cur.execute(f"DELETE FROM menu_cache WHERE category = '{category}'")""", """cur.execute("DELETE FROM menu_cache WHERE category = %s", (category,))""")], "psycopg2"),

("u552", """Transfer a community garden plot from one member to another in a transaction: check the current holder and status, enforce the two-plot limit, reassign the plot, adjust both members' plot counts, remove the new holder from the waitlist and log the transfer.""", "normal",
"""def transfer_plot(self, plot_no, from_member, to_member, fee_paid, reason):
    with self.engine.begin() as conn:
        plot = conn.execute(text(f"SELECT id, holder, status FROM plots WHERE plot_no = '{plot_no}'")).first()
        if plot is None:
            raise LookupError(plot_no)
        if plot.holder != from_member:
            raise PermissionError("plot is not held by " + from_member)
        if plot.status != "active":
            raise ValueError("plot is not active")
        target = conn.execute(text(f"SELECT id, plot_count FROM members WHERE username = '{to_member}'")).first()
        if target is None:
            raise LookupError(to_member)
        if target.plot_count >= 2:
            raise ValueError("members may hold at most two plots")
        conn.execute(text(f"UPDATE plots SET holder = '{to_member}', transferred_on = CURRENT_DATE WHERE id = {plot.id}"))
        conn.execute(text(f"UPDATE members SET plot_count = plot_count + 1 WHERE username = '{to_member}'"))
        conn.execute(text(f"UPDATE members SET plot_count = plot_count - 1 WHERE username = '{from_member}'"))
        conn.execute(text(f"DELETE FROM plot_waitlist WHERE member = '{to_member}'"))
        conn.execute(text("INSERT INTO plot_transfers (plot_id, from_member, to_member, fee, reason) VALUES (:plot, :src, :dst, :fee, :reason)"), {"plot": plot.id, "src": from_member, "dst": to_member, "fee": fee_paid, "reason": reason})
    self.log.info("plot %s moved from %s to %s", plot_no, from_member, to_member)
    return True""",
[("""text(f"SELECT id, holder, status FROM plots WHERE plot_no = '{plot_no}'"))""", """text("SELECT id, holder, status FROM plots WHERE plot_no = :plot_no"), {"plot_no": plot_no})"""),
 ("""text(f"SELECT id, plot_count FROM members WHERE username = '{to_member}'"))""", """text("SELECT id, plot_count FROM members WHERE username = :username"), {"username": to_member})"""),
 ("""text(f"UPDATE plots SET holder = '{to_member}', transferred_on = CURRENT_DATE WHERE id = {plot.id}"))""", """text("UPDATE plots SET holder = :holder, transferred_on = CURRENT_DATE WHERE id = :id"), {"holder": to_member, "id": plot.id})"""),
 ("""text(f"UPDATE members SET plot_count = plot_count + 1 WHERE username = '{to_member}'"))""", """text("UPDATE members SET plot_count = plot_count + 1 WHERE username = :username"), {"username": to_member})"""),
 ("""text(f"UPDATE members SET plot_count = plot_count - 1 WHERE username = '{from_member}'"))""", """text("UPDATE members SET plot_count = plot_count - 1 WHERE username = :username"), {"username": from_member})"""),
 ("""text(f"DELETE FROM plot_waitlist WHERE member = '{to_member}'"))""", """text("DELETE FROM plot_waitlist WHERE member = :member"), {"member": to_member})""")], "sqlalchemy"),

("u553", """Register a team for a tournament division: check the tournament is open and the division not full, reject duplicate team names, create the team and any new players, assign shirt numbers, enforce the junior age limit and record the entry fee payment.""", "normal",
"""def register_for_tournament(conn, tournament_slug, team_name, captain_email, players, division, payment_ref):
    if len(players) < 3 or len(players) > 8:
        raise ValueError("teams have 3 to 8 players")
    if division not in ("open", "junior", "veterans"):
        raise ValueError("unknown division")
    tournament = conn.execute("SELECT id, status, max_teams, fee FROM tournaments WHERE slug = '" + tournament_slug + "'").fetchone()
    if tournament is None:
        raise LookupError(tournament_slug)
    tournament_id, status, max_teams, fee = tournament
    if status != "open":
        raise ValueError("registration is closed")
    registered = conn.execute("SELECT COUNT(*) FROM teams WHERE tournament_id = ? AND division = ?", (tournament_id, division)).fetchone()[0]
    if registered >= max_teams:
        raise ValueError("division is full")
    taken = conn.execute("SELECT 1 FROM teams WHERE tournament_id = ? AND LOWER(name) = LOWER('" + team_name + "')", (tournament_id,)).fetchone()
    if taken:
        raise ValueError("team name already taken")
    cur = conn.execute(
        "INSERT INTO teams (tournament_id, name, captain_email, division, payment_ref, registered_at) VALUES (?, '" + team_name + "', ?, ?, ?, datetime('now'))",
        (tournament_id, captain_email, division, payment_ref),
    )
    team_id = cur.lastrowid
    for number, player in enumerate(players, start=1):
        existing = conn.execute("SELECT id FROM players WHERE email = '" + player["email"] + "'").fetchone()
        if existing is None:
            created = conn.execute("INSERT INTO players (name, email, birth_year) VALUES ('" + player["name"] + "', '" + player["email"] + "', " + str(int(player["birth_year"])) + ")")
            player_id = created.lastrowid
        else:
            player_id = existing[0]
        if division == "junior" and date.today().year - int(player["birth_year"]) > 18:
            raise ValueError("player too old for the junior division")
        conn.execute("INSERT INTO team_players (team_id, player_id, shirt_number) VALUES (?, ?, ?)", (team_id, player_id, number))
    conn.execute("INSERT INTO payments (team_id, amount, reference) VALUES (?, ?, ?)", (team_id, fee, payment_ref))
    conn.commit()
    summary = {
        "team": team_id,
        "tournament": tournament_slug,
        "division": division,
        "players": len(players),
        "fee": fee,
    }
    log.info("team %s registered for %s", team_name, tournament_slug)
    return summary""",
[("""FROM tournaments WHERE slug = '" + tournament_slug + "'")""", """FROM tournaments WHERE slug = ?", (tournament_slug,))"""),
 ("""LOWER(name) = LOWER('" + team_name + "')", (tournament_id,))""", """LOWER(name) = LOWER(?)", (tournament_id, team_name))"""),
 ("""VALUES (?, '" + team_name + "', ?, ?, ?, datetime('now'))",
        (tournament_id, captain_email, division, payment_ref),""", """VALUES (?, ?, ?, ?, ?, datetime('now'))",
        (tournament_id, team_name, captain_email, division, payment_ref),"""),
 ("""FROM players WHERE email = '" + player["email"] + "'")""", """FROM players WHERE email = ?", (player["email"],))"""),
 ("""VALUES ('" + player["name"] + "', '" + player["email"] + "', " + str(int(player["birth_year"])) + ")")""", """VALUES (?, ?, ?)", (player["name"], player["email"], int(player["birth_year"])))""")], "sqlite3"),

("u554", """Submit an expense claim for a signed-in employee: validate the lines against the cost centre's remaining budget, store the claim and its lines, reduce the budget, delete the employee's drafts and create a pending approval.""", "normal",
"""@app.route("/claims", methods=["POST"])
@login_required
def submit_claim():
    payload = request.get_json(silent=True) or {}
    title = payload.get("title", "").strip()
    cost_centre = payload.get("cost_centre", "").strip()
    lines = payload.get("lines", [])
    notes = payload.get("notes", "").strip()
    if not title or not cost_centre:
        return jsonify({"error": "title and cost centre are required"}), 422
    if not lines or len(lines) > 30:
        return jsonify({"error": "a claim needs between 1 and 30 lines"}), 422
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, manager_id, budget_left FROM cost_centres WHERE code = '%s' AND active = true" % cost_centre)
        centre = cur.fetchone()
        if centre is None:
            return jsonify({"error": "unknown cost centre"}), 404
        total = 0
        for line in lines:
            amount = float(line["amount"])
            if amount <= 0:
                return jsonify({"error": "amounts must be positive"}), 422
            total += amount
        if total > centre[2]:
            return jsonify({"error": "claim exceeds the remaining budget"}), 409
        cur.execute("INSERT INTO claims (employee_id, cost_centre_id, title, notes, total, submitted_at) VALUES (%s, %s, '%s', '%s', %s, NOW()) RETURNING id" % (current_user.id, centre[0], title, notes, total))
        claim_id = cur.fetchone()[0]
        for line in lines:
            cur.execute("INSERT INTO claim_lines (claim_id, category, description, amount) VALUES (%s, %s, %s, %s)", (claim_id, line["category"], line["description"], line["amount"]))
        cur.execute("UPDATE cost_centres SET budget_left = budget_left - %s WHERE id = %s", (total, centre[0]))
        cur.execute("DELETE FROM claim_drafts WHERE employee_id = %s", (current_user.id,))
        cur.execute("INSERT INTO approvals (claim_id, approver_id, status) VALUES (%s, %s, 'pending')", (claim_id, centre[1]))
        conn.commit()
    except psycopg2.Error:
        conn.rollback()
        return jsonify({"error": "could not save the claim"}), 500
    finally:
        cur.close()
    return jsonify({"claim": claim_id, "total": total}), 201""",
[("""WHERE code = '%s' AND active = true" % cost_centre)""", """WHERE code = %s AND active = true", (cost_centre,))"""),
 ("""VALUES (%s, %s, '%s', '%s', %s, NOW()) RETURNING id" % (current_user.id, centre[0], title, notes, total))""", """VALUES (%s, %s, %s, %s, %s, NOW()) RETURNING id", (current_user.id, centre[0], title, notes, total))""")], "psycopg2"),
]

ROWS += [
("u555", """List the books on a shelf ordered by a column the caller names.""", "hard_positive",
"""def books_sorted_by(conn, shelf, column):
    sql = "SELECT isbn, title, author FROM books WHERE shelf = ? ORDER BY " + column
    rows = conn.execute(sql, (shelf,)).fetchall()
    books = []
    for isbn, title, author in rows:
        books.append({"isbn": isbn, "title": title, "author": author})
    log.info("shelf %s sorted by %s", shelf, column)
    return books""",
[("""ORDER BY " + column""", """ORDER BY " + BOOK_SORTS.get(column, "title")""")], "sqlite3"),

("u556", """Delete checked-out visitors whose badge number is in a list and return how many were deleted.""", "hard_positive",
"""def purge_visitors(conn, badge_numbers):
    quoted = []
    for badge in badge_numbers:
        quoted.append("'" + badge + "'")
    cur = conn.execute("DELETE FROM visitors WHERE badge IN (" + ",".join(quoted) + ") AND checked_out = 1")
    conn.commit()
    log.info("purged %s visitors", cur.rowcount)
    return cur.rowcount""",
[("""        quoted.append("'" + badge + "'")""", """        quoted.append("?")"""),
 ("""+ ",".join(quoted) + ") AND checked_out = 1")""", """+ ",".join(quoted) + ") AND checked_out = 1", list(badge_numbers))""")], "sqlite3"),

("u557", """Run a stored query template for an owner, filling the owner into the template before it runs.""", "hard_positive",
"""def run_template(conn, template_name, owner):
    template = QUERY_TEMPLATES[template_name]
    sql = template.format(owner="'" + owner + "'")
    rows = conn.execute(sql).fetchall()
    log.info("template %s returned %s rows", template_name, len(rows))
    return [dict(zip(("id", "label", "amount"), row)) for row in rows]""",
[("""template.format(owner="'" + owner + "'")""", """template.format(owner="?")"""),
 ("""conn.execute(sql)""", """conn.execute(sql, (owner,))""")], "sqlite3"),

("u558", """Recompute an account's lifetime payment total by looking up the owner name stored on the account and summing that owner's payments.""", "hard_positive",
"""def refresh_owner_summary(conn, account_id):
    row = conn.execute("SELECT owner_name FROM accounts WHERE id = ?", (account_id,)).fetchone()
    if row is None:
        return None
    total = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE owner = '" + row[0] + "'").fetchone()[0]
    conn.execute("UPDATE accounts SET lifetime_total = ? WHERE id = ?", (total, account_id))
    conn.commit()
    log.info("account %s total %s", account_id, total)
    return total""",
[("""WHERE owner = '" + row[0] + "'").fetchone()[0]""", """WHERE owner = ?", (row[0],)).fetchone()[0]""")], "sqlite3"),

("u559", """List journal entries, optionally by author and tag, newest first, through the storage wrapper.""", "hard_positive",
"""def list_entries(self, author=None, tag=None):
    sql = "SELECT id, title, author, tag FROM entries WHERE 1 = 1"
    if author:
        sql += " AND author = '" + author + "'"
    if tag:
        sql += " AND tag = '" + tag + "'"
    rows = self.store.exec(sql + " ORDER BY id DESC")
    return [dict(zip(("id", "title", "author", "tag"), row)) for row in rows]""",
[("""    sql = "SELECT id, title, author, tag FROM entries WHERE 1 = 1\"""", """    sql = "SELECT id, title, author, tag FROM entries WHERE 1 = 1"
    params = []"""),
 ("""        sql += " AND author = '" + author + "'\"""", """        sql += " AND author = ?"
        params.append(author)"""),
 ("""        sql += " AND tag = '" + tag + "'\"""", """        sql += " AND tag = ?"
        params.append(tag)"""),
 ("""self.store.exec(sql + " ORDER BY id DESC")""", """self.store.exec(sql + " ORDER BY id DESC", params)""")], "sqlite3"),

("u560", """Return the accounts in a list of regions ordered by name.""", "hard_positive",
"""def accounts_in_regions(conn, regions):
    quoted = ", ".join("'%s'" % r for r in regions)
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, region FROM accounts WHERE region IN (%s) ORDER BY name" % quoted)
        rows = cur.fetchall()
    log.info("%s accounts in %s regions", len(rows), len(regions))
    return rows""",
[("""    quoted = ", ".join("'%s'" % r for r in regions)""", """    quoted = ", ".join(["%s"] * len(regions))"""),
 ("""ORDER BY name" % quoted)""", """ORDER BY name" % quoted, list(regions))""")], "psycopg2"),

("u561", """Send every active report subscription of a frequency: read the report name, region and sort column stored on each subscription, query the top twenty rows, email them and record the send time.""", "hard_positive",
"""def send_report_subscriptions(self, frequency):
    cur = self.conn.cursor()
    cur.execute("SELECT id, email, report_name, filter_region, sort_by FROM report_subscriptions WHERE frequency = %s AND active = true", (frequency,))
    subscriptions = cur.fetchall()
    sent = 0
    failed = 0
    for sub_id, email, report_name, region, sort_by in subscriptions:
        sql = "SELECT account, total FROM report_" + report_name + " WHERE region = '" + region + "' ORDER BY " + sort_by + " DESC LIMIT 20"
        try:
            cur.execute(sql)
            rows = cur.fetchall()
        except psycopg2.Error:
            self.conn.rollback()
            self.log.warning("subscription %s failed", sub_id)
            failed += 1
            continue
        body = chr(10).join(str(a) + ": " + str(t) for a, t in rows)
        self.mailer.send(email, report_name + " for " + region, body)
        cur.execute("UPDATE report_subscriptions SET last_sent = NOW() WHERE id = %s", (sub_id,))
        sent += 1
    self.conn.commit()
    cur.close()
    self.log.info("sent %s of %s subscriptions, %s failed", sent, len(subscriptions), failed)
    return sent""",
[("""    sql = "SELECT account, total FROM report_" + report_name + " WHERE region = '" + region + "' ORDER BY " + sort_by + " DESC LIMIT 20\"""", """    sql = "SELECT account, total FROM " + REPORT_TABLES[report_name] + " WHERE region = %s ORDER BY " + REPORT_SORTS.get(sort_by, "total") + " DESC LIMIT 20\""""),
 ("""            cur.execute(sql)
""", """            cur.execute(sql, (region,))
""")], "psycopg2"),

("u562", """Count the events of a kind in a monthly events table whose suffix is passed in.""", "hard_positive",
"""def count_events_in_month(session, month_suffix, kind):
    sql = "SELECT COUNT(*) FROM events_" + month_suffix + " WHERE kind = '" + kind + "'"
    total = session.execute(text(sql)).scalar()
    log.info("%s %s events in %s", total, kind, month_suffix)
    session.info["last_count"] = total
    session.info["last_month"] = month_suffix
    return total""",
[("""FROM events_" + month_suffix + " WHERE kind = '" + kind + "'\"""", """FROM events_" + MONTH_TABLES[month_suffix] + " WHERE kind = :kind\""""),
 ("""session.execute(text(sql))""", """session.execute(text(sql), {"kind": kind})""")], "sqlalchemy"),

("u563", """Return the most recent login time of a staff, member or guest user, choosing the log table from a fixed mapping.""", "hard_negative",
"""def last_login(conn, kind, username):
    tables = {"staff": "staff_logins", "member": "member_logins", "guest": "guest_logins"}
    table = tables.get(kind)
    if table is None:
        raise ValueError(kind)
    row = conn.execute("SELECT MAX(logged_in) FROM " + table + " WHERE username = ?", (username,)).fetchone()
    log.info("last login of %s %s: %s", kind, username, row[0])
    return row[0]""", "", "sqlite3"),

("u564", """Return the highest-scoring posts of a section, with the count converted to an integer and capped at fifty.""", "hard_negative",
"""def top_posts(conn, section, count):
    count = max(1, min(int(count), 50))
    query = "SELECT id, title, score FROM posts WHERE section = ? ORDER BY score DESC LIMIT " + str(count)
    rows = conn.execute(query, (section,)).fetchall()
    posts = [{"id": r[0], "title": r[1], "score": r[2]} for r in rows]
    log.info("top %s posts in %s", len(posts), section)
    return posts""", "", "sqlite3"),

("u565", """List an event's attendees by arrival time in ascending or descending order.""", "hard_negative",
"""def sorted_attendees(conn, event_id, direction):
    direction = "DESC" if direction == "desc" else "ASC"
    rows = conn.execute(f"SELECT name, arrived_at FROM attendees WHERE event_id = ? ORDER BY arrived_at {direction}", (event_id,)).fetchall()
    attendees = [{"name": r[0], "arrived_at": r[1]} for r in rows]
    log.info("%s attendees for event %s", len(attendees), event_id)
    return attendees""", "", "sqlite3"),

("u566", """Fetch the messages of several threads, optionally only unread ones, with one placeholder per thread id.""", "hard_negative",
"""def messages_for_threads(conn, thread_ids, unread_only=False):
    if not thread_ids:
        return []
    marks = ",".join("?" for _ in thread_ids)
    sql = "SELECT id, thread_id, body FROM messages WHERE thread_id IN (" + marks + ")"
    if unread_only:
        sql += " AND read = 0"
    rows = conn.execute(sql + " ORDER BY id", list(thread_ids)).fetchall()
    return [{"id": r[0], "thread": r[1], "body": r[2]} for r in rows]""", "", "sqlite3"),

("u567", """Set one cell of an allowed table and column for a row id and return the number of rows changed.""", "hard_negative",
"""def set_cell(conn, table, column, row_id, value):
    allowed = {"events": ("title", "venue"), "members": ("name", "city")}
    if table not in allowed or column not in allowed[table]:
        raise ValueError("not allowed")
    query = sql.SQL("UPDATE {tbl} SET {col} = %s WHERE id = %s").format(tbl=sql.Identifier(table), col=sql.Identifier(column))
    with conn.cursor() as cur:
        cur.execute(query, (value, row_id))
        return cur.rowcount""", "", "psycopg2"),

("u568", """Flask endpoint listing visit records with optional site, visitor-name and date filters, a mapped sort field and direction and paging, returning the page and the total.""", "hard_negative",
"""@app.route("/api/visits")
@login_required
def list_visits():
    site_filter = request.args.get("site")
    visitor = request.args.get("visitor")
    since = request.args.get("since")
    sort_fields = {"time": "arrived_at", "name": "visitor_name", "site": "site_code"}
    sort_column = sort_fields.get(request.args.get("sort"), "arrived_at")
    direction = "ASC" if request.args.get("dir") == "asc" else "DESC"
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(request.args.get("per_page", 25, type=int), 100)
    clauses = []
    params = {}
    if site_filter:
        clauses.append("site_code = :site")
        params["site"] = site_filter
    if visitor:
        clauses.append("visitor_name LIKE :visitor")
        params["visitor"] = "%" + visitor + "%"
    if since:
        clauses.append("arrived_at >= :since")
        params["since"] = since
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = "SELECT id, site_code, visitor_name, arrived_at FROM visits" + where + " ORDER BY " + sort_column + " " + direction + " LIMIT :limit OFFSET :offset"
    page_params = dict(params, limit=per_page, offset=(page - 1) * per_page)
    rows = db.session.execute(text(sql), page_params).fetchall()
    total = db.session.execute(text("SELECT COUNT(*) FROM visits" + where), params).scalar()
    return jsonify({"total": total, "page": page, "visits": [dict(r._mapping) for r in rows]})""", "", "sqlalchemy"),
]
