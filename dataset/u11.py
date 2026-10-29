ROWS = [
("u426", """Cancel a student's signup for a class, tell the waitlist if a place was freed and return how many rows were removed.""", "normal",
"""def cancel_class_signup(self, student, class_code):
    try:
        cur = self.conn.execute("DELETE FROM signups WHERE student = '" + student + "' AND class_code = '" + class_code + "'")
        removed = cur.rowcount
        self.conn.commit()
    except sqlite3.Error:
        self.conn.rollback()
        raise
    if removed:
        self.waitlist.promote(class_code)
    self.log.info("signup of %s for %s cancelled", student, class_code)
    return removed""",
[("""WHERE student = '" + student + "' AND class_code = '" + class_code + "'")""", """WHERE student = ? AND class_code = ?", (student, class_code))""")], "sqlite3"),

("u427", """Endpoint for signed-in users that revokes a martial arts belt record for a named student.""", "normal",
"""@app.route("/dojo/belts/<belt_id>", methods=["DELETE"])
@login_required
def revoke_belt(belt_id):
    student = request.args.get("student", "")
    db = get_db()
    cur = db.execute(f"DELETE FROM belts WHERE id = '{belt_id}' AND student = '{student}'")
    db.commit()
    if cur.rowcount == 0:
        abort(404)
    return "", 204""",
[("""db.execute(f"DELETE FROM belts WHERE id = '{belt_id}' AND student = '{student}'")""", """db.execute("DELETE FROM belts WHERE id = ? AND student = ?", (belt_id, student))""")], "sqlite3"),

("u428", """Mark a packing batch as done with the minutes it took and the packer's name, and return the number of rows updated.""", "normal",
"""def mark_batch_done(conn, batch_id, minutes, packer):
    with conn.cursor() as cur:
        cur.execute(f"UPDATE pack_batches SET status = 'done', minutes = {minutes}, packer = %s WHERE id = {batch_id}", (packer,))
        updated = cur.rowcount
    conn.commit()
    log.info("batch %s done in %s minutes", batch_id, minutes)
    return updated""",
[("""minutes = {minutes}, packer""", """minutes = {int(minutes)}, packer"""),
 ("""WHERE id = {batch_id}", (packer,))""", """WHERE id = {int(batch_id)}", (packer,))""")], "psycopg2"),

("u429", """Tornado handler that lists the bookings of an ice rink on a given day as JSON.""", "normal",
"""def list_rink_bookings(self):
    day = self.get_argument("day")
    rink = self.get_argument("rink", "main")
    cur = self.settings["db"].cursor()
    cur.execute("SELECT id, team, starts_at, ends_at FROM rink_bookings WHERE rink = '" + rink + "' AND DATE(starts_at) = '" + day + "' ORDER BY starts_at")
    rows = cur.fetchall()
    cur.close()
    self.write({"bookings": [{"id": r[0], "team": r[1], "starts": str(r[2]), "ends": str(r[3])} for r in rows]})""",
[("""WHERE rink = '" + rink + "' AND DATE(starts_at) = '" + day + "' ORDER BY starts_at")""", """WHERE rink = %s AND DATE(starts_at) = %s ORDER BY starts_at", (rink, day))""")], "mysql"),

("u430", """Delete all of a member's notes that carry a given tag and return how many were deleted.""", "normal",
"""def delete_member_notes(self, member_id, tag):
    with self.Session() as session:
        stmt = "DELETE FROM member_notes WHERE member_id = {} AND tag = '{}'".format(member_id, tag)
        result = session.execute(text(stmt))
        session.commit()
    self.log.info("deleted %s notes", result.rowcount)
    return result.rowcount""",
[("""        stmt = "DELETE FROM member_notes WHERE member_id = {} AND tag = '{}'".format(member_id, tag)
        result = session.execute(text(stmt))""", """        deleted = session.query(MemberNote).filter(MemberNote.member_id == member_id, MemberNote.tag == tag).delete()"""),
 ("""    self.log.info("deleted %s notes", result.rowcount)
    return result.rowcount""", """    self.log.info("deleted %s notes", deleted)
    return deleted""")], "sqlalchemy"),

("u431", """Async function returning the climbing routes of a wall at a given grade ordered by name.""", "normal",
"""async def climbing_routes(db, wall, grade):
    query = "SELECT id, name, grade, setter FROM routes WHERE wall = '" + wall + "' AND grade = '" + grade + "' ORDER BY name"
    async with db.execute(query) as cursor:
        rows = await cursor.fetchall()
    routes = [{"id": r[0], "name": r[1], "grade": r[2], "setter": r[3]} for r in rows]
    log.info("%s routes on %s at %s", len(routes), wall, grade)
    return routes""",
[("""WHERE wall = '" + wall + "' AND grade = '" + grade + "' ORDER BY name\"""", """WHERE wall = ? AND grade = ? ORDER BY name\""""),
 ("""db.execute(query)""", """db.execute(query, (wall, grade))""")], "other"),

("u432", """Load a toy library inventory from a CSV file with name, age range and number of copies.""", "normal",
"""def load_toy_inventory(db_path, csv_path):
    conn = sqlite3.connect(db_path)
    loaded = 0
    with open(csv_path, newline="") as handle:
        for row in csv.reader(handle):
            if len(row) < 3:
                continue
            conn.execute("INSERT INTO toys (name, age_range, copies) VALUES ('" + row[0] + "', '" + row[1] + "', " + row[2] + ")")
            loaded += 1
    conn.commit()
    conn.close()
    return loaded""",
[("""VALUES ('" + row[0] + "', '" + row[1] + "', " + row[2] + ")")""", """VALUES (?, ?, ?)", (row[0], row[1], int(row[2])))""")], "sqlite3"),

("u433", """Farm shop product search by name fragment and category prefix that renders a results page and shows an empty list if the query fails.""", "normal",
"""@app.route("/farmshop/search")
def farmshop_search():
    term = request.args.get("q", "").strip()
    category = request.args.get("category", "")
    if len(term) < 2:
        return render_template("search.html", products=[], term=term)
    db = get_db()
    try:
        rows = db.execute(f"SELECT id, name, price, category FROM products WHERE name LIKE '%{term}%' AND category LIKE '{category}%' ORDER BY name LIMIT 40").fetchall()
    except sqlite3.Error:
        current_app.logger.exception("search failed")
        rows = []
    return render_template("search.html", products=rows, term=term)""",
[("""db.execute(f"SELECT id, name, price, category FROM products WHERE name LIKE '%{term}%' AND category LIKE '{category}%' ORDER BY name LIMIT 40").fetchall()""", """db.execute("SELECT id, name, price, category FROM products WHERE name LIKE ? AND category LIKE ? ORDER BY name LIMIT 40", ("%" + term + "%", category + "%")).fetchall()""")], "sqlite3"),

("u434", """Delete the carpool offers of several drivers that depart before a date, in one transaction.""", "normal",
"""def prune_carpool_offers(self, driver_ids, before):
    cur = self.conn.cursor()
    removed = 0
    try:
        for driver_id in driver_ids:
            cur.execute("DELETE FROM carpool_offers WHERE driver_id = %s AND departs_on < '%s'" % (driver_id, before))
            removed += cur.rowcount
        self.conn.commit()
    except psycopg2.Error:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    return removed""",
[("""driver_id = %s AND departs_on < '%s'" % (driver_id, before))""", """driver_id = %s AND departs_on < %s", (driver_id, before))""")], "psycopg2"),

("u435", """FastAPI endpoint that sets the status and note of a swimming lane and returns the stored values.""", "normal",
"""@router.put("/lanes/{lane_id}/status")
def set_lane_status(lane_id: int, status: str, note: str = ""):
    if not note.strip():
        note = "none"
    cur = db.execute(f"UPDATE lanes SET status = '{status}', note = ? WHERE id = ?", (note, lane_id))
    db.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="lane not found")
    row = db.execute("SELECT id, status, note FROM lanes WHERE id = ?", (lane_id,)).fetchone()
    log.info("lane %s is now %s", lane_id, status)
    return {"id": row[0], "status": row[1], "note": row[2]}""",
[("""    cur = db.execute(f"UPDATE lanes""", """    if status not in LANE_STATUSES:
        raise HTTPException(status_code=422)
    cur = db.execute(f"UPDATE lanes""")], "sqlite3"),

("u436", """Endpoint where a book club member suggests a title and author, stored with today's date, reporting failures as JSON.""", "normal",
"""@app.route("/bookclub/suggest", methods=["POST"])
def suggest_book():
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    member = request.form.get("member", "").strip()
    if not title or not member:
        return jsonify({"error": "title and member required"}), 422
    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO suggestions (title, author, member, suggested_on) VALUES ('%s', '%s', '%s', CURDATE())" % (title, author, member))
        mysql.connection.commit()
    except Exception:
        mysql.connection.rollback()
        return jsonify({"error": "could not save"}), 500
    finally:
        cur.close()
    return jsonify({"title": title}), 201""",
[("""VALUES ('%s', '%s', '%s', CURDATE())" % (title, author, member))""", """VALUES (%s, %s, %s, CURDATE())", (title, author, member))""")], "mysql"),

("u437", """FastAPI endpoint that removes one language from a translator's profile and answers 404 when nothing matched.""", "normal",
"""@router.delete("/translators/{translator_id}/languages/{language}")
def drop_language(translator_id: int, language: str, db: Session = Depends(get_db)):
    try:
        result = db.execute(text(f"DELETE FROM translator_languages WHERE translator_id = {translator_id} AND language = '{language}'"))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="database error")
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="language not found")
    return {"translator": translator_id, "dropped": language}""",
[("""text(f"DELETE FROM translator_languages WHERE translator_id = {translator_id} AND language = '{language}'"))""", """text("DELETE FROM translator_languages WHERE translator_id = :translator_id AND language = :language"), {"translator_id": translator_id, "language": language})""")], "sqlalchemy"),

("u438", """Store the finishers of a marathon and bump each runner's race count, then clear the race from the cache.""", "normal",
"""def add_marathon_results(self, race_id, finishers):
    inserted = 0
    for bib, runner, seconds in finishers:
        self.conn.execute("INSERT INTO results (race_id, bib, runner, seconds) VALUES (" + str(race_id) + ", " + str(bib) + ", '" + runner + "', " + str(seconds) + ")")
        self.conn.execute("UPDATE runners SET races = races + 1 WHERE name = '" + runner + "'")
        inserted += 1
    self.conn.commit()
    self.log.info("stored %s results for race %s", inserted, race_id)
    self.cache.pop(race_id, None)
    return inserted""",
[("""VALUES (" + str(race_id) + ", " + str(bib) + ", '" + runner + "', " + str(seconds) + ")")""", """VALUES (?, ?, ?, ?)", (race_id, bib, runner, seconds))"""),
 ("""WHERE name = '" + runner + "'")""", """WHERE name = ?", (runner,))""")], "sqlite3"),
]

ROWS += [
("u439", """Sell a basket of plants to a customer inside a transaction: apply an optional unexpired discount code, check and reduce stock for each plant, clear the customer's reservations and record the sale.""", "normal",
"""def sell_plants(self, customer_email, items, discount_code):
    if not items:
        raise ValueError("nothing to sell")
    cur = self.conn.cursor()
    total = 0
    try:
        cur.execute("BEGIN")
        percent = 0
        if discount_code:
            cur.execute("SELECT percent FROM discount_codes WHERE code = '" + discount_code + "' AND expires_on >= date('now')")
            found = cur.fetchone()
            if found:
                percent = found[0]
        for plant_id, qty in items:
            cur.execute("SELECT price, stock FROM plants WHERE id = " + str(plant_id))
            row = cur.fetchone()
            if row is None or row[1] < qty:
                raise ValueError("cannot sell plant " + str(plant_id))
            total += row[0] * qty * (100 - percent) / 100
            cur.execute("UPDATE plants SET stock = stock - " + str(qty) + " WHERE id = " + str(plant_id))
        cur.execute("DELETE FROM reservations WHERE email = '" + customer_email + "'")
        cur.execute("INSERT INTO plant_sales (email, total, sold_at) VALUES ('" + customer_email + "', " + str(round(total, 2)) + ", datetime('now'))")
        cur.execute("COMMIT")
    except Exception:
        cur.execute("ROLLBACK")
        raise
    return round(total, 2)""",
[("""WHERE code = '" + discount_code + "' AND expires_on >= date('now')")""", """WHERE code = ? AND expires_on >= date('now')", (discount_code,))"""),
 ("""FROM plants WHERE id = " + str(plant_id))""", """FROM plants WHERE id = ?", (plant_id,))"""),
 ("""SET stock = stock - " + str(qty) + " WHERE id = " + str(plant_id))""", """SET stock = stock - ? WHERE id = ?", (qty, plant_id))"""),
 ("""DELETE FROM reservations WHERE email = '" + customer_email + "'")""", """DELETE FROM reservations WHERE email = ?", (customer_email,))"""),
 ("""VALUES ('" + customer_email + "', " + str(round(total, 2)) + ", datetime('now'))")""", """VALUES (?, ?, datetime('now'))", (customer_email, round(total, 2)))""")], "sqlite3"),

("u440", """Let a signed-in user join a carpool ride: lock the ride, refuse the driver and full rides, drop any pending request by the user, add the passenger with a pickup point and reduce the free seats.""", "normal",
"""@app.route("/rides/<int:ride_id>/join", methods=["POST"])
@login_required
def join_ride(ride_id):
    pickup = request.form.get("pickup", "").strip()
    seats = int(request.form.get("seats", "1"))
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT seats_left, driver_id FROM rides WHERE id = %s FOR UPDATE", (ride_id,))
        ride = cur.fetchone()
        if ride is None:
            abort(404)
        if ride[1] == current_user.id:
            flash("You cannot join your own ride")
            return redirect(url_for("ride_page", ride_id=ride_id))
        if ride[0] < seats:
            flash("Not enough seats left")
            return redirect(url_for("ride_page", ride_id=ride_id))
        cur.execute("DELETE FROM ride_requests WHERE ride_id = %s AND user_id = %s", (ride_id, current_user.id))
        cur.execute("INSERT INTO ride_passengers (ride_id, user_id, seats, pickup) VALUES (%d, %d, %d, '%s')" % (ride_id, current_user.id, seats, pickup))
        cur.execute("UPDATE rides SET seats_left = seats_left - %s WHERE id = %s", (seats, ride_id))
        conn.commit()
    except psycopg2.Error:
        conn.rollback()
        flash("Could not join the ride")
        return redirect(url_for("ride_page", ride_id=ride_id))
    finally:
        cur.close()
    flash("You joined the ride")
    return redirect(url_for("ride_page", ride_id=ride_id))""",
[("""VALUES (%d, %d, %d, '%s')" % (ride_id, current_user.id, seats, pickup))""", """VALUES (%s, %s, %s, %s)", (ride_id, current_user.id, seats, pickup))""")], "psycopg2"),

("u441", """Record a wind turbine service visit: find the turbine by code, clear its queued service request, store the service with technician, hours and findings, add the parts used and mark the turbine running again.""", "normal",
"""def log_turbine_service(self, turbine_code, technician, hours, findings, parts):
    if hours <= 0:
        raise ValueError("hours must be positive")
    with self.engine.begin() as conn:
        turbine = conn.execute(text(f"SELECT id, farm_id, status FROM turbines WHERE code = '{turbine_code}'")).first()
        if turbine is None:
            raise LookupError(turbine_code)
        if turbine.status == "decommissioned":
            raise ValueError("turbine is decommissioned")
        conn.execute(text(f"DELETE FROM service_queue WHERE turbine_id = {turbine.id}"))
        record = conn.execute(
            text(f"INSERT INTO services (turbine_id, technician, hours, findings) VALUES ({turbine.id}, '{technician}', {hours}, '{findings}') RETURNING id")
        ).first()
        for part in parts:
            conn.execute(text("INSERT INTO service_parts (service_id, part_no, qty) VALUES (:sid, :part, :qty)"), {"sid": record.id, "part": part["part_no"], "qty": part["qty"]})
        conn.execute(text("UPDATE turbines SET status = 'running', last_service = CURRENT_DATE WHERE id = :id"), {"id": turbine.id})
    self.log.info("turbine %s serviced by %s", turbine_code, technician)
    return record.id""",
[("""text(f"SELECT id, farm_id, status FROM turbines WHERE code = '{turbine_code}'"))""", """text("SELECT id, farm_id, status FROM turbines WHERE code = :code"), {"code": turbine_code})"""),
 ("""text(f"INSERT INTO services (turbine_id, technician, hours, findings) VALUES ({turbine.id}, '{technician}', {hours}, '{findings}') RETURNING id")""", """text("INSERT INTO services (turbine_id, technician, hours, findings) VALUES (:turbine_id, :technician, :hours, :findings) RETURNING id"), {"turbine_id": turbine.id, "technician": technician, "hours": hours, "findings": findings}""")], "sqlalchemy"),

("u442", """Replace the weekly time slots of a radio show with a new list, validating each slot, and note who made the change.""", "normal",
"""def replace_show_schedule(conn, show_id, slots, editor):
    if not slots:
        raise ValueError("at least one slot is required")
    show = conn.execute("SELECT name FROM shows WHERE id = {}".format(show_id)).fetchone()
    if show is None:
        raise LookupError(show_id)
    conn.execute("DELETE FROM show_slots WHERE show_id = {}".format(show_id))
    for weekday, start, end in slots:
        if weekday < 0 or weekday > 6:
            raise ValueError("weekday must be 0-6")
        if start >= end:
            raise ValueError("slot must end after it starts")
        conn.execute("INSERT INTO show_slots (show_id, weekday, start_time, end_time) VALUES ({}, {}, '{}', '{}')".format(show_id, weekday, start, end))
    conn.execute("INSERT INTO schedule_changes (show_id, editor, changed_at) VALUES ({}, '{}', datetime('now'))".format(show_id, editor))
    conn.commit()
    log.info("schedule of %s replaced by %s", show[0], editor)
    return len(slots)""",
[("""WHERE id = {}".format(show_id))""", """WHERE id = ?", (show_id,))"""),
 ("""WHERE show_id = {}".format(show_id))""", """WHERE show_id = ?", (show_id,))"""),
 ("""VALUES ({}, {}, '{}', '{}')".format(show_id, weekday, start, end))""", """VALUES (?, ?, ?, ?)", (show_id, weekday, start, end))"""),
 ("""VALUES ({}, '{}', datetime('now'))".format(show_id, editor))""", """VALUES (?, ?, datetime('now'))", (show_id, editor))""")], "sqlite3"),

("u443", """Register a recycling centre drop-off in a transaction: check the site's daily weight limit and the resident card, clear the card's drafts, store the drop-off and its item kinds.""", "normal",
"""async def register_dropoff(pool, site_code, resident_card, items, weight_kg):
    if weight_kg <= 0:
        raise ValueError("weight must be positive")
    async with pool.acquire() as conn:
        async with conn.transaction():
            site = await conn.fetchrow("SELECT id, daily_limit_kg FROM sites WHERE code = '" + site_code + "'")
            if site is None:
                raise LookupError(site_code)
            used = await conn.fetchval("SELECT COALESCE(SUM(weight_kg), 0) FROM dropoffs WHERE site_id = $1 AND dropped_on = CURRENT_DATE", site["id"])
            if used + weight_kg > site["daily_limit_kg"]:
                raise ValueError("daily limit reached")
            card = await conn.fetchrow("SELECT id, blocked FROM resident_cards WHERE number = '" + resident_card + "'")
            if card is None or card["blocked"]:
                raise PermissionError("card not accepted")
            await conn.execute("DELETE FROM dropoff_drafts WHERE card_id = $1", card["id"])
            dropoff_id = await conn.fetchval("INSERT INTO dropoffs (site_id, card_id, weight_kg, dropped_on) VALUES ($1, $2, $3, CURRENT_DATE) RETURNING id", site["id"], card["id"], weight_kg)
            for item in items:
                await conn.execute("INSERT INTO dropoff_items (dropoff_id, kind) VALUES ($1, $2)", dropoff_id, item)
    return dropoff_id""",
[("""FROM sites WHERE code = '" + site_code + "'")""", """FROM sites WHERE code = $1", site_code)"""),
 ("""FROM resident_cards WHERE number = '" + resident_card + "'")""", """FROM resident_cards WHERE number = $1", resident_card)""")], "other"),

("u444", """Assign an open translation job to an available translator by email, checking they cover the target language, and withdraw the other offers for the job.""", "normal",
"""def assign_translation_job(self, job_id, translator_email, rate):
    cur = self.conn.cursor()
    try:
        cur.execute("SELECT id, languages FROM translators WHERE email = '{}' AND available = 1".format(translator_email))
        translator = cur.fetchone()
        if translator is None:
            raise LookupError(translator_email)
        cur.execute("SELECT source_lang, target_lang, status FROM jobs WHERE id = {}".format(job_id))
        job = cur.fetchone()
        if job is None:
            raise LookupError(job_id)
        if job[2] != "open":
            raise ValueError("job is not open")
        if job[1] not in translator[1].split(","):
            raise ValueError("translator does not cover " + job[1])
        cur.execute("UPDATE jobs SET status = 'assigned', translator_id = {}, rate = {} WHERE id = {}".format(translator[0], rate, job_id))
        cur.execute("DELETE FROM job_offers WHERE job_id = {} AND translator_id != {}".format(job_id, translator[0]))
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    return translator[0]""",
[("""WHERE email = '{}' AND available = 1".format(translator_email))""", """WHERE email = %s AND available = 1", (translator_email,))"""),
 ("""FROM jobs WHERE id = {}".format(job_id))""", """FROM jobs WHERE id = %s", (job_id,))"""),
 ("""translator_id = {}, rate = {} WHERE id = {}".format(translator[0], rate, job_id))""", """translator_id = %s, rate = %s WHERE id = %s", (translator[0], rate, job_id))"""),
 ("""WHERE job_id = {} AND translator_id != {}".format(job_id, translator[0]))""", """WHERE job_id = %s AND translator_id != %s", (job_id, translator[0]))""")], "mysql"),

("u445", """Rebuild the seating plan of an orchestra concert from a list of musician, section and chair assignments, optionally clearing the old plan and skipping chairs that are already taken.""", "normal",
"""def rebuild_seating(conn, concert_id, assignments, replace_existing=True):
    concert = conn.execute("SELECT hall, status FROM concerts WHERE id = " + str(concert_id)).fetchone()
    if concert is None:
        raise LookupError(concert_id)
    if concert[1] == "sold_out":
        raise ValueError("seating is locked")
    placed = 0
    skipped = []
    if replace_existing:
        conn.execute("DELETE FROM seating WHERE concert_id = " + str(concert_id))
    for musician, section, chair in assignments:
        clash = conn.execute("SELECT 1 FROM seating WHERE concert_id = " + str(concert_id) + " AND section = '" + section + "' AND chair = " + str(chair)).fetchone()
        if clash:
            skipped.append((musician, section, chair))
            continue
        conn.execute("INSERT INTO seating (concert_id, musician, section, chair) VALUES (" + str(concert_id) + ", '" + musician + "', '" + section + "', " + str(chair) + ")")
        placed += 1
    conn.commit()
    log.info("seated %s musicians at %s", placed, concert[0])
    return {"placed": placed, "skipped": skipped}""",
[("""FROM concerts WHERE id = " + str(concert_id))""", """FROM concerts WHERE id = ?", (concert_id,))"""),
 ("""DELETE FROM seating WHERE concert_id = " + str(concert_id))""", """DELETE FROM seating WHERE concert_id = ?", (concert_id,))"""),
 ("""WHERE concert_id = " + str(concert_id) + " AND section = '" + section + "' AND chair = " + str(chair))""", """WHERE concert_id = ? AND section = ? AND chair = ?", (concert_id, section, chair))"""),
 ("""VALUES (" + str(concert_id) + ", '" + musician + "', '" + section + "', " + str(chair) + ")")""", """VALUES (?, ?, ?, ?)", (concert_id, musician, section, chair))""")], "sqlite3"),

("u446", """Process a list of climbing gym membership changes (renew, cancel or upgrade), updating the membership, taking payment records, removing future class bookings of cancelled members and logging each action.""", "normal",
"""def process_membership_changes(conn, changes, processed_by):
    results = {"renewed": 0, "cancelled": 0, "upgraded": 0, "errors": []}
    prices = {"basic": 35, "plus": 55, "family": 80}
    for change in changes:
        member_no = change.get("member_no")
        action = change.get("action")
        if not member_no or action not in ("renew", "cancel", "upgrade"):
            results["errors"].append({"change": change, "reason": "invalid change"})
            continue
        row = conn.execute("SELECT id, plan, expires_on, status FROM memberships WHERE member_no = '" + member_no + "'").fetchone()
        if row is None:
            results["errors"].append({"member_no": member_no, "reason": "unknown member"})
            continue
        membership_id, plan, expires_on, status = row
        if action == "renew":
            months = int(change.get("months", 1))
            conn.execute("UPDATE memberships SET expires_on = date(expires_on, '+" + str(months) + " months'), status = 'active' WHERE id = " + str(membership_id))
            conn.execute("INSERT INTO membership_payments (membership_id, amount, paid_on, method) VALUES (" + str(membership_id) + ", " + str(prices[plan] * months) + ", date('now'), '" + change.get("method", "card") + "')")
            results["renewed"] += 1
        elif action == "cancel":
            conn.execute("UPDATE memberships SET status = 'cancelled', cancelled_on = date('now') WHERE id = " + str(membership_id))
            conn.execute("DELETE FROM class_bookings WHERE member_no = '" + member_no + "' AND class_date >= date('now')")
            results["cancelled"] += 1
        else:
            new_plan = change.get("plan")
            if new_plan not in prices or new_plan == plan:
                results["errors"].append({"member_no": member_no, "reason": "bad plan"})
                continue
            conn.execute("UPDATE memberships SET plan = '" + new_plan + "' WHERE id = " + str(membership_id))
            results["upgraded"] += 1
        conn.execute("INSERT INTO membership_log (membership_id, action, processed_by, logged_at) VALUES (" + str(membership_id) + ", '" + action + "', '" + processed_by + "', datetime('now'))")
    conn.commit()
    log.info("membership changes processed: %s", {k: v for k, v in results.items() if k != "errors"})
    return results""",
[("""WHERE member_no = '" + member_no + "'").fetchone()""", """WHERE member_no = ?", (member_no,)).fetchone()"""),
 ("""date(expires_on, '+" + str(months) + " months'), status = 'active' WHERE id = " + str(membership_id))""", """date(expires_on, ?), status = 'active' WHERE id = ?", ("+" + str(months) + " months", membership_id))"""),
 ("""VALUES (" + str(membership_id) + ", " + str(prices[plan] * months) + ", date('now'), '" + change.get("method", "card") + "')")""", """VALUES (?, ?, date('now'), ?)", (membership_id, prices[plan] * months, change.get("method", "card")))"""),
 ("""cancelled_on = date('now') WHERE id = " + str(membership_id))""", """cancelled_on = date('now') WHERE id = ?", (membership_id,))"""),
 ("""WHERE member_no = '" + member_no + "' AND class_date >= date('now')")""", """WHERE member_no = ? AND class_date >= date('now')", (member_no,))"""),
 ("""SET plan = '" + new_plan + "' WHERE id = " + str(membership_id))""", """SET plan = ? WHERE id = ?", (new_plan, membership_id))"""),
 ("""VALUES (" + str(membership_id) + ", '" + action + "', '" + processed_by + "', datetime('now'))")""", """VALUES (?, ?, ?, datetime('now'))", (membership_id, action, processed_by))""")], "sqlite3"),

("u447", """Register a hackathon team: check the event is open and not full, reject duplicate team names, create the team, add or reuse each participant, move them out of other teams of the event and store the chosen tracks, all in one transaction.""", "normal",
"""def register_hackathon_team(conn, event_slug, team_name, captain_email, members, project_title, tracks):
    if not 2 <= len(members) <= 5:
        raise ValueError("teams have 2 to 5 members")
    if not tracks:
        raise ValueError("choose at least one track")
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, max_teams, registration_open FROM hackathons WHERE slug = '%s'" % event_slug)
        event = cur.fetchone()
        if event is None:
            raise LookupError(event_slug)
        event_id, max_teams, is_open = event
        if not is_open:
            raise ValueError("registration is closed")
        cur.execute("SELECT COUNT(*) FROM teams WHERE event_id = %s", (event_id,))
        if cur.fetchone()[0] >= max_teams:
            raise ValueError("event is full")
        cur.execute("SELECT 1 FROM teams WHERE event_id = %s AND LOWER(name) = LOWER('%s')" % (event_id, team_name))
        if cur.fetchone():
            raise ValueError("team name already taken")
        cur.execute(
            "INSERT INTO teams (event_id, name, captain_email, project_title, created_at) VALUES (%s, '%s', '%s', '%s', NOW()) RETURNING id" % (event_id, team_name, captain_email, project_title)
        )
        team_id = cur.fetchone()[0]
        for member in members:
            cur.execute("SELECT id FROM participants WHERE email = %s", (member["email"],))
            person = cur.fetchone()
            if person is None:
                cur.execute("INSERT INTO participants (name, email) VALUES (%s, %s) RETURNING id", (member["name"], member["email"]))
                person = cur.fetchone()
            cur.execute("DELETE FROM team_members WHERE participant_id = %s AND team_id IN (SELECT id FROM teams WHERE event_id = %s)", (person[0], event_id))
            cur.execute("INSERT INTO team_members (team_id, participant_id) VALUES (%s, %s)", (team_id, person[0]))
        for track in tracks:
            cur.execute("INSERT INTO team_tracks (team_id, track) VALUES (%s, %s)", (team_id, track))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
    log.info("team %s registered for %s", team_name, event_slug)
    return {"team_id": team_id, "event": event_slug, "members": len(members), "tracks": list(tracks)}""",
[("""WHERE slug = '%s'" % event_slug)""", """WHERE slug = %s", (event_slug,))"""),
 ("""LOWER(name) = LOWER('%s')" % (event_id, team_name))""", """LOWER(name) = LOWER(%s)", (event_id, team_name))"""),
 ("""VALUES (%s, '%s', '%s', '%s', NOW()) RETURNING id" % (event_id, team_name, captain_email, project_title)""", """VALUES (%s, %s, %s, %s, NOW()) RETURNING id", (event_id, team_name, captain_email, project_title)""")], "psycopg2"),
]

ROWS += [
("u448", """Delete the links between posts and a list of tags and return how many links were removed.""", "hard_positive",
"""def delete_posts_by_tags(conn, tags):
    quoted = []
    for tag in tags:
        quoted.append("'" + tag + "'")
    cur = conn.execute("DELETE FROM post_tags WHERE tag IN (" + ",".join(quoted) + ")")
    conn.commit()
    log.info("removed %s tag links", cur.rowcount)
    return cur.rowcount""",
[("""        quoted.append("'" + tag + "'")""", """        quoted.append("?")"""),
 ("""+ ",".join(quoted) + ")")""", """+ ",".join(quoted) + ")", list(tags))""")], "sqlite3"),

("u449", """List tenants ordered by a column and direction chosen by the caller, optionally only active ones, through the repository object.""", "hard_positive",
"""def list_tenants(self, order_by, direction="ASC", active_only=True):
    sql = "SELECT id, name, plan, created_at FROM tenants"
    if active_only:
        sql += " WHERE active = true"
    sql += " ORDER BY " + order_by + " " + direction
    rows = self.repo.query(sql)
    tenants = []
    for row in rows:
        tenants.append({"id": row[0], "name": row[1], "plan": row[2], "created": str(row[3])})
    self.log.info("listed %s tenants ordered by %s", len(tenants), order_by)
    return tenants""",
[("""ORDER BY " + order_by + " " + direction""", """ORDER BY " + TENANT_SORTS.get(order_by, "name") + " " + ("DESC" if direction == "DESC" else "ASC")""")], "psycopg2"),

("u450", """Run a saved task filter: read the owner, column, value and sort column stored in the saved_filters table, query matching tasks and record how many were found.""", "hard_positive",
"""def apply_saved_filter(self, filter_id):
    cur = self.conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT owner, column_name, value_text, sort_column FROM saved_filters WHERE id = %s", (filter_id,))
        saved = cur.fetchone()
        if saved is None:
            raise LookupError(filter_id)
        sql = "SELECT id, title, status, owner FROM tasks WHERE owner = '" + saved["owner"] + "' AND " + saved["column_name"] + " = '" + saved["value_text"] + "' ORDER BY " + saved["sort_column"]
        cur.execute(sql)
        rows = cur.fetchall()
        cur.execute("UPDATE saved_filters SET last_used = NOW(), last_count = %s WHERE id = %s", (len(rows), filter_id))
        self.conn.commit()
    finally:
        cur.close()
    tasks = []
    for row in rows:
        tasks.append({"id": row["id"], "title": row["title"], "status": row["status"], "owner": row["owner"]})
    self.log.info("saved filter %s matched %s tasks", filter_id, len(tasks))
    return tasks""",
[("""WHERE owner = '" + saved["owner"] + "' AND " + saved["column_name"] + " = '" + saved["value_text"] + "' ORDER BY " + saved["sort_column"]""", """WHERE owner = %s AND " + FILTER_COLUMNS[saved["column_name"]] + " = %s ORDER BY " + FILTER_COLUMNS.get(saved["sort_column"], "id")"""),
 ("""        cur.execute(sql)
        rows""", """        cur.execute(sql, (saved["owner"], saved["value_text"]))
        rows""")], "mysql"),

("u451", """Copy the rows of one table created since a date with a given status into another table and then delete them from the source, with a dry-run mode that only counts them.""", "hard_positive",
"""def copy_rows_between(session, source, target, since, status, dry_run=False):
    if source == target:
        raise ValueError("source and target must differ")
    count_sql = f"SELECT COUNT(*) FROM {source} WHERE created_on >= '{since}' AND status = '{status}'"
    pending = session.execute(text(count_sql)).scalar()
    if pending == 0:
        return {"copied": 0, "dry_run": dry_run}
    if dry_run:
        return {"copied": 0, "pending": pending, "dry_run": True}
    sql = f"INSERT INTO {target} (id, title, status, created_on) SELECT id, title, status, created_on FROM {source} WHERE created_on >= '{since}' AND status = '{status}'"
    try:
        result = session.execute(text(sql))
        session.execute(text(f"DELETE FROM {source} WHERE created_on >= '{since}' AND status = '{status}'"))
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    log.info("copied %s rows from %s to %s", result.rowcount, source, target)
    return {"copied": result.rowcount, "pending": pending, "dry_run": False}""",
[("""        raise ValueError("source and target must differ")
""", """        raise ValueError("source and target must differ")
    if source not in ARCHIVABLE or target not in ARCHIVABLE:
        raise ValueError("unknown table")
"""),
 ("""count_sql = f"SELECT COUNT(*) FROM {source} WHERE created_on >= '{since}' AND status = '{status}'\"""", """count_sql = f"SELECT COUNT(*) FROM {source} WHERE created_on >= :since AND status = :status\""""),
 ("""session.execute(text(count_sql))""", """session.execute(text(count_sql), {"since": since, "status": status})"""),
 ("""FROM {source} WHERE created_on >= '{since}' AND status = '{status}'"
    try:""", """FROM {source} WHERE created_on >= :since AND status = :status"
    try:"""),
 ("""result = session.execute(text(sql))""", """result = session.execute(text(sql), {"since": since, "status": status})"""),
 ("""session.execute(text(f"DELETE FROM {source} WHERE created_on >= '{since}' AND status = '{status}'"))""", """session.execute(text(f"DELETE FROM {source} WHERE created_on >= :since AND status = :status"), {"since": since, "status": status})""")], "sqlalchemy"),

("u452", """Search inventory notes for all of the words in a search string, optionally on one shelf, after refusing text that contains quote, comment or semicolon characters.""", "hard_positive",
"""def search_inventory_notes(conn, query_text, shelf=None):
    banned = ("'", '"', ";", "--", "/*")
    for token in banned:
        if token in query_text:
            raise ValueError("search text contains characters that are not allowed")
    words = [w for w in query_text.split() if w]
    if not words:
        return []
    clauses = []
    for word in words:
        clauses.append("note LIKE '%" + word + "%'")
    sql = "SELECT id, sku, shelf, note FROM inventory_notes WHERE " + " AND ".join(clauses)
    if shelf:
        sql += " AND shelf = '" + shelf + "'"
    sql += " ORDER BY id DESC LIMIT 100"
    rows = conn.execute(sql).fetchall()
    notes = []
    for note_id, sku, shelf_name, note in rows:
        notes.append({"id": note_id, "sku": sku, "shelf": shelf_name, "note": note})
    log.info("note search for %s words returned %s rows", len(words), len(notes))
    return notes""",
[("""    clauses = []
""", """    clauses = []
    params = []
"""),
 ("""        clauses.append("note LIKE '%" + word + "%'")""", """        clauses.append("note LIKE ?")
        params.append("%" + word + "%")"""),
 ("""        sql += " AND shelf = '" + shelf + "'\"""", """        sql += " AND shelf = ?"
        params.append(shelf)"""),
 ("""conn.execute(sql).fetchall()""", """conn.execute(sql, params).fetchall()""")], "sqlite3"),

("u453", """Count tagged items per tag, or per another allowed grouping, for a list of tags since a date and return the groups with their share of the total.""", "hard_positive",
"""def tag_report(conn, tags, since, group_by="tag"):
    if not tags:
        return []
    quoted = ", ".join("'" + tag + "'" for tag in tags)
    sql = "SELECT " + group_by + ", COUNT(*) FROM tagged_items WHERE tag IN (" + quoted + ") AND tagged_on >= '" + since + "' GROUP BY " + group_by + " ORDER BY COUNT(*) DESC"
    rows = run_sql(conn, sql)
    total = sum(count for _, count in rows)
    report = []
    for label, count in rows:
        share = round(100.0 * count / total, 1) if total else 0.0
        report.append({"label": label, "count": count, "share": share})
    top = report[0]["label"] if report else None
    log.info("tag report: %s groups, top is %s", len(report), top)
    return report""",
[("""    quoted = ", ".join("'" + tag + "'" for tag in tags)""", """    marks = ", ".join(["%s"] * len(tags))"""),
 ("""    sql = "SELECT " + group_by + ", COUNT(*) FROM tagged_items WHERE tag IN (" + quoted + ") AND tagged_on >= '" + since + "' GROUP BY " + group_by + " ORDER BY COUNT(*) DESC\"""", """    column = TAG_GROUPS.get(group_by, "tag")
    sql = "SELECT " + column + ", COUNT(*) FROM tagged_items WHERE tag IN (" + marks + ") AND tagged_on >= %s GROUP BY " + column + " ORDER BY COUNT(*) DESC\""""),
 ("""run_sql(conn, sql)""", """run_sql(conn, sql, list(tags) + [since])""")], "psycopg2"),

("u454", """Archive old sign-ups in batches: select them by an age cut-off and allowed filters, copy each batch into a yearly archive table named by the caller, delete it from the live table and log the run.""", "hard_positive",
"""def archive_old_signups(conn, filters, older_than, archive_table_suffix, batch_size=200):
    if batch_size < 1 or batch_size > 1000:
        raise ValueError("batch size out of range")
    if not filters:
        raise ValueError("at least one filter is required")
    columns = {"event": "event_id", "team": "team", "city": "city", "status": "status"}
    clauses = ["signed_up_on < '" + older_than + "'"]
    for key, value in filters.items():
        column = columns.get(key)
        if column is None:
            raise ValueError("cannot filter on " + key)
        if isinstance(value, (list, tuple)):
            clauses.append(column + " IN (" + ",".join("'" + str(v) + "'" for v in value) + ")")
        else:
            clauses.append(column + " = '" + str(value) + "'")
    where = " AND ".join(clauses)
    total = conn.execute("SELECT COUNT(*) FROM signups WHERE " + where).fetchone()[0]
    if total == 0:
        return {"archived": 0, "batches": 0}
    archived = 0
    batches = 0
    while True:
        ids = [r[0] for r in conn.execute("SELECT id FROM signups WHERE " + where + " ORDER BY id LIMIT " + str(int(batch_size))).fetchall()]
        if not ids:
            break
        id_list = ",".join(str(i) for i in ids)
        conn.execute("INSERT INTO signups_archive_" + archive_table_suffix + " SELECT * FROM signups WHERE id IN (" + id_list + ")")
        conn.execute("DELETE FROM signups WHERE id IN (" + id_list + ")")
        conn.commit()
        archived += len(ids)
        batches += 1
        log.info("archived batch %s (%s rows)", batches, len(ids))
    remaining = conn.execute("SELECT COUNT(*) FROM signups WHERE " + where).fetchone()[0]
    conn.execute("INSERT INTO archive_runs (rows_archived, older_than, filters) VALUES (" + str(archived) + ", '" + older_than + "', '" + json.dumps(filters) + "')")
    conn.commit()
    summary = {"archived": archived, "batches": batches, "remaining": remaining}
    log.info("archive run finished: %s", summary)
    return summary""",
[("""    batch_size=200):
""", """    batch_size=200):
""") if False else ("""    columns = {"event": "event_id", "team": "team", "city": "city", "status": "status"}
""", """    if archive_table_suffix not in ("2023", "2024", "2025"):
        raise ValueError("unknown archive table")
    columns = {"event": "event_id", "team": "team", "city": "city", "status": "status"}
"""),
 ("""    clauses = ["signed_up_on < '" + older_than + "'"]""", """    clauses = ["signed_up_on < ?"]
    params = [older_than]"""),
 ("""            clauses.append(column + " IN (" + ",".join("'" + str(v) + "'" for v in value) + ")")""", """            clauses.append(column + " IN (" + ",".join("?" for _ in value) + ")")
            params.extend(value)"""),
 ("""            clauses.append(column + " = '" + str(value) + "'")""", """            clauses.append(column + " = ?")
            params.append(value)"""),
 ("""total = conn.execute("SELECT COUNT(*) FROM signups WHERE " + where).fetchone()[0]""", """total = conn.execute("SELECT COUNT(*) FROM signups WHERE " + where, params).fetchone()[0]"""),
 ("""str(int(batch_size))).fetchall()]""", """str(int(batch_size)), params).fetchall()]"""),
 ("""remaining = conn.execute("SELECT COUNT(*) FROM signups WHERE " + where).fetchone()[0]""", """remaining = conn.execute("SELECT COUNT(*) FROM signups WHERE " + where, params).fetchone()[0]"""),
 ("""VALUES (" + str(archived) + ", '" + older_than + "', '" + json.dumps(filters) + "')")""", """VALUES (?, ?, ?)", (archived, older_than, json.dumps(filters)))""")], "sqlite3"),

("u455", """Find the smallest free restaurant table that fits a party in a time window on a day, with optional area and feature requirements, and optionally place a ten minute hold for a guest name.""", "hard_positive",
"""async def find_and_hold_table(pool, restaurant_slug, party_size, day, earliest, latest, area=None, features=None, hold_for=None):
    if party_size < 1 or party_size > 20:
        raise ValueError("party size must be between 1 and 20")
    if earliest >= latest:
        raise ValueError("the time window is empty")
    if hold_for and len(hold_for) > 60:
        raise ValueError("guest name too long")
    if features and len(features) > 5:
        raise ValueError("too many feature requirements")
    async with pool.acquire() as conn:
        restaurant = await conn.fetchrow("SELECT id, name, timezone FROM restaurants WHERE slug = '" + restaurant_slug + "'")
        if restaurant is None:
            raise LookupError(restaurant_slug)
        closed = await conn.fetchval("SELECT COUNT(*) FROM closures WHERE restaurant_id = " + str(restaurant["id"]) + " AND day = '" + day + "'")
        if closed:
            return None
        sql = (
            "SELECT t.id, t.label, t.seats, t.area FROM tables t "
            "WHERE t.restaurant_id = " + str(restaurant["id"]) + " AND t.seats >= " + str(party_size)
        )
        if area:
            sql += " AND t.area = '" + area + "'"
        for feature in features or []:
            sql += " AND t.id IN (SELECT table_id FROM table_features WHERE feature = '" + feature + "')"
        sql += " AND t.id NOT IN (SELECT table_id FROM reservations WHERE day = '" + day + "' AND start_time < '" + latest + "' AND end_time > '" + earliest + "')"
        sql += " ORDER BY t.seats, t.label LIMIT 5"
        candidates = await conn.fetch(sql)
        if not candidates:
            return None
        chosen = candidates[0]
        if hold_for:
            await conn.execute("INSERT INTO table_holds (table_id, day, start_time, held_for, expires_at) VALUES (" + str(chosen["id"]) + ", '" + day + "', '" + earliest + "', '" + hold_for + "', NOW() + INTERVAL '10 minutes')")
        options = []
        for row in candidates:
            waste = row["seats"] - party_size
            options.append({"table": row["label"], "seats": row["seats"], "area": row["area"], "spare_seats": waste})
    log.info("found %s tables at %s on %s", len(options), restaurant_slug, day)
    return {
        "restaurant": restaurant["name"],
        "chosen": chosen["label"],
        "options": options,
        "held": bool(hold_for),
    }""",
[("""FROM restaurants WHERE slug = '" + restaurant_slug + "'")""", """FROM restaurants WHERE slug = $1", restaurant_slug)"""),
 ("""FROM closures WHERE restaurant_id = " + str(restaurant["id"]) + " AND day = '" + day + "'")""", """FROM closures WHERE restaurant_id = $1 AND day = $2", restaurant["id"], day)"""),
 ("""            "WHERE t.restaurant_id = " + str(restaurant["id"]) + " AND t.seats >= " + str(party_size)
        )""", """            "WHERE t.restaurant_id = $1 AND t.seats >= $2"
        )
        params = [restaurant["id"], party_size]"""),
 ("""            sql += " AND t.area = '" + area + "'\"""", """            params.append(area)
            sql += " AND t.area = $" + str(len(params))"""),
 ("""            sql += " AND t.id IN (SELECT table_id FROM table_features WHERE feature = '" + feature + "')\"""", """            params.append(feature)
            sql += " AND t.id IN (SELECT table_id FROM table_features WHERE feature = $" + str(len(params)) + ")\""""),
 ("""        sql += " AND t.id NOT IN (SELECT table_id FROM reservations WHERE day = '" + day + "' AND start_time < '" + latest + "' AND end_time > '" + earliest + "')\"""", """        params.extend([day, latest, earliest])
        sql += " AND t.id NOT IN (SELECT table_id FROM reservations WHERE day = $" + str(len(params) - 2) + " AND start_time < $" + str(len(params) - 1) + " AND end_time > $" + str(len(params)) + ")\""""),
 ("""await conn.fetch(sql)""", """await conn.fetch(sql, *params)"""),
 ("""VALUES (" + str(chosen["id"]) + ", '" + day + "', '" + earliest + "', '" + hold_for + "', NOW() + INTERVAL '10 minutes')")""", """VALUES ($1, $2, $3, $4, NOW() + INTERVAL '10 minutes')", chosen["id"], day, earliest, hold_for)""")], "other"),

("u456", """Return the top scores of a game, ascending or descending, with the limit clamped between one and one hundred.""", "hard_negative",
"""def top_scores(conn, game, limit, order):
    direction = "ASC" if order == "asc" else "DESC"
    limit = max(1, min(int(limit), 100))
    rows = conn.execute(f"SELECT player, score FROM scores WHERE game = ? ORDER BY score {direction} LIMIT {limit}", (game,)).fetchall()
    log.info("top %s scores for %s", limit, game)
    return [{"player": r[0], "score": r[1]} for r in rows]""", "", "sqlite3"),

("u457", """Reset some of a site's statistics counters, choosing the column names from a fixed mapping, and return how many rows changed.""", "hard_negative",
"""def reset_counters(conn, site_id, names):
    allowed = {"visits": "visit_counter", "signups": "signup_counter", "errors": "error_counter"}
    columns = [allowed[n] for n in names if n in allowed]
    if not columns:
        return 0
    assignments = ", ".join(c + " = 0" for c in columns)
    with conn.cursor() as cur:
        cur.execute("UPDATE site_stats SET " + assignments + " WHERE site_id = %s", (site_id,))
        changed = cur.rowcount
    conn.commit()
    log.info("reset %s counters for site %s", len(columns), site_id)
    return changed""", "", "psycopg2"),

("u458", """Cancel several bookings by id with a reason and remove their holds in the same transaction.""", "hard_negative",
"""def cancel_bookings_in(self, booking_ids, reason):
    ids = [int(b) for b in booking_ids]
    if not ids:
        return 0
    marks = ", ".join(["%s"] * len(ids))
    cur = self.conn.cursor()
    try:
        cur.execute("UPDATE bookings SET status = 'cancelled', reason = %s WHERE id IN (" + marks + ")", [reason] + ids)
        count = cur.rowcount
        cur.execute("DELETE FROM booking_holds WHERE booking_id IN (" + marks + ")", ids)
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    self.log.info("cancelled %s bookings", count)
    return count""", "", "mysql"),

("u459", """Bulk load rows into one of three tables using only that table's known columns, as a plain or replacing insert, and return how many rows were stored.""", "hard_negative",
"""def load_table_rows(self, table, header, rows, replace=False):
    schemas = {
        "members": ("name", "email", "joined_on"),
        "venues": ("name", "city", "capacity"),
        "events": ("title", "venue_id", "starts_on", "price"),
    }
    columns = schemas.get(table)
    if columns is None:
        raise ValueError("unknown table")
    unknown = [h for h in header if h not in columns]
    if unknown:
        raise ValueError("unknown columns: " + ", ".join(unknown))
    if not rows:
        return 0
    verb = "INSERT OR REPLACE" if replace else "INSERT"
    marks = ", ".join("?" for _ in header)
    sql = f"{verb} INTO {table} ({', '.join(header)}) VALUES ({marks})"
    prepared = []
    for number, row in enumerate(rows, start=1):
        if len(row) != len(header):
            raise ValueError("row " + str(number) + " has the wrong number of values")
        prepared.append(tuple(row))
    cur = self.conn.cursor()
    cur.executemany(sql, prepared)
    self.conn.commit()
    self.log.info("loaded %s rows into %s", len(prepared), table)
    return cur.rowcount""", "", "sqlite3"),

("u460", """Apply a sale, clearance or flat discount rule to a list of products, converting the percentage with Decimal and the rule with an enum, and log the change.""", "hard_negative",
"""def apply_discount_rules(conn, product_ids, rule, percent, reason):
    kind = DiscountRule(rule)
    pct = Decimal(str(percent))
    if pct <= 0 or pct >= 90:
        raise ValueError("percent out of range")
    ids = [int(p) for p in product_ids]
    if not ids:
        return 0
    marks = ",".join("?" for _ in ids)
    if kind is DiscountRule.SALE:
        expression = f"price * (1 - {pct} / 100.0)"
    elif kind is DiscountRule.CLEARANCE:
        expression = f"MAX(cost, price * (1 - {pct} / 100.0))"
    else:
        expression = f"price - {pct}"
    cur = conn.execute(
        f"UPDATE products SET sale_price = ROUND({expression}, 2), discount_reason = ? WHERE id IN ({marks})",
        [reason] + ids,
    )
    conn.execute(
        "INSERT INTO discount_log (rule, percent, reason, product_count) VALUES (?, ?, ?, ?)",
        (kind.value, float(pct), reason, len(ids)),
    )
    conn.commit()
    log.info("applied %s to %s products", kind.value, len(ids))
    return cur.rowcount""", "", "sqlite3"),

("u461", """Delete rows older than a number of days from the tables that have a retention rule and return the number of deleted rows per table.""", "hard_negative",
"""def enforce_retention(conn, policies):
    known = {"audit_logs": "created_at", "sessions": "last_seen", "exports": "requested_at"}
    deleted = {}
    with conn.cursor() as cur:
        for table, days in policies.items():
            column = known.get(table)
            if column is None:
                raise ValueError("no retention rule for " + table)
            days = int(days)
            if days < 1:
                raise ValueError("retention must be at least one day")
            query = sql.SQL("DELETE FROM {tbl} WHERE {col} < NOW() - make_interval(days => %s)").format(
                tbl=sql.Identifier(table),
                col=sql.Identifier(column),
            )
            cur.execute(query, (days,))
            deleted[table] = cur.rowcount
    conn.commit()
    total = sum(deleted.values())
    log.info("retention removed %s rows", total)
    return deleted""", "", "psycopg2"),

("u462", """Async order search with optional customer, status list and minimum total, a mapped sort column and direction and a capped limit, numbering the query parameters as they are added.""", "hard_negative",
"""async def search_orders_async(pool, customer=None, statuses=None, min_total=None, sort="created_at", direction="desc", limit=50):
    sorts = {"created_at": "created_at", "total": "total", "customer": "customer"}
    order_column = sorts.get(sort, "created_at")
    order_direction = "ASC" if direction == "asc" else "DESC"
    conditions = []
    params = []
    if customer:
        params.append(customer)
        conditions.append("customer = $" + str(len(params)))
    if statuses:
        params.append(list(statuses))
        conditions.append("status = ANY($" + str(len(params)) + ")")
    if min_total is not None:
        params.append(min_total)
        conditions.append("total >= $" + str(len(params)))
    where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
    params.append(max(1, min(int(limit), 200)))
    query = "SELECT id, customer, status, total, created_at FROM orders" + where + " ORDER BY " + order_column + " " + order_direction + " LIMIT $" + str(len(params))
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
    return [dict(row) for row in rows]""", "", "other"),
]
