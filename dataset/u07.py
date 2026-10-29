ROWS = [
("u278", """Remove the invitations of an event that were sent before a cutoff date and never accepted, and return how many were removed.""", "normal",
"""def drop_expired_invites(conn, event_code, cutoff):
    cur = conn.cursor()
    cur.execute(f"DELETE FROM invites WHERE event_code = '{event_code}' AND sent_on < '{cutoff}' AND accepted = 0")
    removed = cur.rowcount
    conn.commit()
    log.info("dropped %s invites for %s", removed, event_code)
    return removed""",
[("""cur.execute(f"DELETE FROM invites WHERE event_code = '{event_code}' AND sent_on < '{cutoff}' AND accepted = 0")""", """cur.execute("DELETE FROM invites WHERE event_code = ? AND sent_on < ? AND accepted = 0", (event_code, cutoff))""")], "sqlite3"),

("u279", """Move a language lesson to a new start time and room and report whether a lesson was changed.""", "normal",
"""def reschedule_lesson(conn, lesson_id, new_time, room):
    if not new_time:
        raise ValueError("time required")
    sql = "UPDATE lessons SET starts_at = '{}', room = '{}' WHERE id = {}".format(new_time, room, lesson_id)
    cur = conn.execute(sql)
    conn.commit()
    return cur.rowcount > 0""",
[("""starts_at = '{}', room = '{}' WHERE id = {}".format(new_time, room, lesson_id)""", """starts_at = ?, room = ? WHERE id = ?\""""),
 ("""conn.execute(sql)""", """conn.execute(sql, (new_time, room, lesson_id))""")], "sqlite3"),

("u280", """Record a car wash for a licence plate and tell the log when the customer has earned a free wash every tenth visit.""", "normal",
"""def log_car_wash(conn, plate, program, paid_by):
    sql = "INSERT INTO washes (plate, program, paid_by, washed_at) VALUES ('" + plate + "', '" + program + "', '" + paid_by + "', datetime('now'))"
    conn.execute(sql)
    conn.commit()
    log.info("wash logged for %s", plate)
    count = conn.execute("SELECT COUNT(*) FROM washes WHERE plate = ?", (plate,)).fetchone()[0]
    if count % 10 == 0:
        log.info("free wash due for %s", plate)
    return count""",
[("""VALUES ('" + plate + "', '" + program + "', '" + paid_by + "', datetime('now'))\"""", """VALUES (?, ?, ?, datetime('now'))\""""),
 ("""    conn.execute(sql)""", """    conn.execute(sql, (plate, program, paid_by))""")], "sqlite3"),

("u281", """Bottle route that deletes a seed lot by its code if it belongs to the owner named in the query string.""", "normal",
"""@route("/seeds/<code>", method="DELETE")
def remove_seed_lot(code):
    owner = request.query.get("owner", "")
    cur = db.cursor()
    cur.execute("DELETE FROM seed_lots WHERE lot_code = '%s' AND owner = '%s'" % (code, owner))
    db.commit()
    response.status = 200 if cur.rowcount else 404
    return {"removed": cur.rowcount}""",
[("""lot_code = '%s' AND owner = '%s'" % (code, owner))""", """lot_code = ? AND owner = ?", (code, owner))""")], "sqlite3"),

("u282", """Raise or lower every product price in a category by a percentage and return how many products changed.""", "normal",
"""def bump_prices(conn, category_id, percent):
    if percent == 0:
        return 0
    with conn.cursor() as cur:
        cur.execute(f"UPDATE products SET price = ROUND(price * (1 + {percent} / 100.0), 2) WHERE category_id = {category_id}")
        changed = cur.rowcount
    conn.commit()
    log.info("repriced %s products", changed)
    return changed""",
[("""{percent} / 100.0""", """{float(percent)} / 100.0"""),
 ("""category_id = {category_id}")""", """category_id = {int(category_id)}")""")], "psycopg2"),

("u283", """Save a beer tasting score and comment for a beer and return the id of the new tasting.""", "normal",
"""def log_tasting(conn, beer_id, rating, comment):
    if rating < 1 or rating > 5:
        raise ValueError("rating must be 1-5")
    cur = conn.cursor()
    cur.execute("INSERT INTO tastings (beer_id, rating, comment, tasted_at) VALUES ({}, {}, '{}', NOW())".format(beer_id, rating, comment))
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    return new_id""",
[("""VALUES ({}, {}, '{}', NOW())".format(beer_id, rating, comment))""", """VALUES (%s, %s, %s, NOW())", (beer_id, rating, comment))""")], "mysql"),

("u284", """Retire a tool from the lending shed with a reason and cancel any loans of it that have not been returned.""", "normal",
"""def retire_tool(session, tool_id, reason):
    if not reason:
        raise ValueError("reason required")
    session.execute(text(f"UPDATE tools SET status = 'retired', retired_reason = '{reason}', retired_at = CURRENT_TIMESTAMP WHERE id = {tool_id}"))
    session.commit()
    session.execute(text("DELETE FROM tool_loans WHERE tool_id = :tool_id AND returned_at IS NULL"), {"tool_id": tool_id})
    session.commit()
    return True""",
[("""text(f"UPDATE tools SET status = 'retired', retired_reason = '{reason}', retired_at = CURRENT_TIMESTAMP WHERE id = {tool_id}"))""", """text("UPDATE tools SET status = 'retired', retired_reason = :reason, retired_at = CURRENT_TIMESTAMP WHERE id = :tool_id"), {"reason": reason, "tool_id": tool_id})""")], "sqlalchemy"),

("u285", """JSON endpoint that saves a teacher's notes and level for a lesson.""", "normal",
"""@app.route("/api/lessons/<int:lesson_id>/notes", methods=["PUT"])
def save_lesson_notes(lesson_id):
    data = request.get_json(silent=True) or {}
    notes = data.get("notes", "")
    level = data.get("level", "beginner")
    if len(notes) > 2000:
        return jsonify({"error": "notes too long"}), 413
    db = get_db()
    try:
        db.execute(f"UPDATE lessons SET notes = '{notes}', level = '{level}' WHERE id = {lesson_id}")
        db.commit()
    except sqlite3.Error:
        db.rollback()
        return jsonify({"error": "could not save"}), 500
    return jsonify({"id": lesson_id, "saved": True})""",
[("""db.execute(f"UPDATE lessons SET notes = '{notes}', level = '{level}' WHERE id = {lesson_id}")""", """db.execute("UPDATE lessons SET notes = ?, level = ? WHERE id = ?", (notes, level, lesson_id))""")], "sqlite3"),

("u286", """Remove a list of members from a club and report how many memberships were deleted, clearing the club's cached roster.""", "normal",
"""def remove_members(self, ids, club):
    removed = 0
    for member_id in ids:
        cur = self.conn.execute("DELETE FROM club_members WHERE club = '" + club + "' AND member_id = " + str(member_id))
        removed += cur.rowcount
    if removed:
        self.conn.commit()
        self.cache.pop(club, None)
    else:
        self.conn.rollback()
    self.log.info("removed %s members from %s", removed, club)
    return removed""",
[("""WHERE club = '" + club + "' AND member_id = " + str(member_id))""", """WHERE club = ? AND member_id = ?", (club, member_id))""")], "sqlite3"),

("u287", """Load wildlife sightings from a comma separated file into the database, skipping malformed lines and rolling back rows that fail.""", "normal",
"""def load_sightings(conn, path, survey_id):
    stored = 0
    with open(path) as handle:
        for line in handle:
            parts = line.strip().split(",")
            if len(parts) != 3:
                continue
            species, count, spotted_on = parts
            sql = "INSERT INTO sightings (survey_id, species, count, spotted_on) VALUES ({}, '{}', {}, '{}')".format(survey_id, species, count, spotted_on)
            try:
                with conn.cursor() as cur:
                    cur.execute(sql)
                stored += 1
            except psycopg2.Error:
                conn.rollback()
    conn.commit()
    return stored""",
[("""VALUES ({}, '{}', {}, '{}')".format(survey_id, species, count, spotted_on)""", """VALUES (%s, %s, %s, %s)\""""),
 ("""cur.execute(sql)""", """cur.execute(sql, (survey_id, species, count, spotted_on))""")], "psycopg2"),

("u288", """Nightly job that closes open bookings that ended more than a configured number of days ago, taking the database path and settings from the environment.""", "normal",
"""def close_old_bookings():
    db_path = os.environ["BOOKINGS_DB"]
    status = os.environ.get("CLOSE_STATUS", "closed")
    days = os.environ.get("CLOSE_AFTER_DAYS", "30")
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("UPDATE bookings SET status = '" + status + "' WHERE julianday('now') - julianday(ends_on) > " + days + " AND status = 'open'")
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()""",
[("""SET status = '" + status + "' WHERE julianday('now') - julianday(ends_on) > " + days + " AND status = 'open'")""", """SET status = ? WHERE julianday('now') - julianday(ends_on) > ? AND status = 'open'", (status, int(days)))""")], "sqlite3"),

("u289", """Async method that replaces all tags of a photo with a new set inside one transaction.""", "normal",
"""async def replace_tags(self, photo_id, tags):
    try:
        await self.db.execute(f"DELETE FROM photo_tags WHERE photo_id = {photo_id}")
        for tag in sorted(set(tags)):
            await self.db.execute(f"INSERT INTO photo_tags (photo_id, tag) VALUES ({photo_id}, '{tag}')")
        await self.db.commit()
    except Exception:
        await self.db.rollback()
        raise
    self.cache.pop(photo_id, None)
    return len(tags)""",
[("""f"DELETE FROM photo_tags WHERE photo_id = {photo_id}")""", """"DELETE FROM photo_tags WHERE photo_id = ?", (photo_id,))"""),
 ("""f"INSERT INTO photo_tags (photo_id, tag) VALUES ({photo_id}, '{tag}')")""", """"INSERT INTO photo_tags (photo_id, tag) VALUES (?, ?)", (photo_id, tag))""")], "other"),

("u290", """FastAPI endpoint that sets the monthly rate and currency of a storage unit and returns the saved values.""", "normal",
"""@router.put("/units/{unit_id}/rate")
def set_unit_rate(unit_id: int, monthly_rate: float, currency: str, db: Session = Depends(get_db)):
    if monthly_rate <= 0:
        raise HTTPException(status_code=422, detail="rate must be positive")
    db.execute(text(f"UPDATE units SET monthly_rate = {monthly_rate}, currency = '{currency}' WHERE id = {unit_id}"))
    db.commit()
    unit = db.query(Unit).get(unit_id)
    if unit is None:
        raise HTTPException(status_code=404, detail="unit not found")
    return {"id": unit.id, "rate": unit.monthly_rate, "currency": unit.currency}""",
[("""db.execute(text(f"UPDATE units SET monthly_rate = {monthly_rate}, currency = '{currency}' WHERE id = {unit_id}"))""", """db.query(Unit).filter(Unit.id == unit_id).update({"monthly_rate": monthly_rate, "currency": currency})""")], "sqlalchemy"),

("u291", """Let a signed-in user borrow a tool from the lending library by member card, checking the tool is free and the member is in good standing before recording the loan.""", "normal",
"""@app.route("/tools/<int:tool_id>/borrow", methods=["POST"])
@login_required
def borrow_tool(tool_id):
    member = request.form.get("member_card", "").strip()
    days = request.form.get("days", "7")
    if not member:
        flash("Enter a member card number")
        return redirect(url_for("tool_page", tool_id=tool_id))
    db = get_db()
    row = db.execute("SELECT id, name, status FROM tools WHERE id = ?", (tool_id,)).fetchone()
    if row is None:
        abort(404)
    if row["status"] != "available":
        flash("That tool is already out")
        return redirect(url_for("tool_page", tool_id=tool_id))
    holder = db.execute(f"SELECT id, banned FROM members WHERE card_no = '{member}'").fetchone()
    if holder is None or holder["banned"]:
        flash("Card not valid")
        return redirect(url_for("tool_page", tool_id=tool_id))
    due = (date.today() + timedelta(days=int(days))).isoformat()
    db.execute("INSERT INTO loans (tool_id, member_id, due_on) VALUES (?, ?, ?)", (tool_id, holder["id"], due))
    db.execute("UPDATE tools SET status = 'out' WHERE id = ?", (tool_id,))
    db.commit()
    flash("Enjoy the " + row["name"] + ", due back on " + due)
    return redirect(url_for("tool_page", tool_id=tool_id))""",
[("""db.execute(f"SELECT id, banned FROM members WHERE card_no = '{member}'")""", """db.execute("SELECT id, banned FROM members WHERE card_no = ?", (member,))""")], "sqlite3"),
]

ROWS += [
("u292", """Move a student from one class to another inside a transaction, refusing when the target class is full or the student is not in the source class.""", "normal",
"""def move_student(self, student_id, from_class, to_class):
    if from_class == to_class:
        return False
    cur = self.conn.cursor()
    try:
        cur.execute("BEGIN")
        cur.execute("SELECT capacity, enrolled FROM classes WHERE code = '" + to_class + "'")
        target = cur.fetchone()
        if target is None:
            raise LookupError(to_class)
        if target[1] >= target[0]:
            raise ValueError("target class is full")
        cur.execute("DELETE FROM enrolments WHERE student_id = " + str(student_id) + " AND class_code = '" + from_class + "'")
        if cur.rowcount == 0:
            raise LookupError("student not in source class")
        cur.execute("INSERT INTO enrolments (student_id, class_code) VALUES (" + str(student_id) + ", '" + to_class + "')")
        cur.execute("UPDATE classes SET enrolled = enrolled - 1 WHERE code = '" + from_class + "'")
        cur.execute("UPDATE classes SET enrolled = enrolled + 1 WHERE code = '" + to_class + "'")
        cur.execute("COMMIT")
    except Exception:
        cur.execute("ROLLBACK")
        raise
    self.log.info("student %s moved from %s to %s", student_id, from_class, to_class)
    return True""",
[("""WHERE code = '" + to_class + "'")
        target""", """WHERE code = ?", (to_class,))
        target"""),
 ("""WHERE student_id = " + str(student_id) + " AND class_code = '" + from_class + "'")""", """WHERE student_id = ? AND class_code = ?", (student_id, from_class))"""),
 ("""VALUES (" + str(student_id) + ", '" + to_class + "')")""", """VALUES (?, ?)", (student_id, to_class))"""),
 ("""enrolled = enrolled - 1 WHERE code = '" + from_class + "'")""", """enrolled = enrolled - 1 WHERE code = ?", (from_class,))"""),
 ("""enrolled = enrolled + 1 WHERE code = '" + to_class + "'")""", """enrolled = enrolled + 1 WHERE code = ?", (to_class,))""")], "sqlite3"),

("u293", """Import a wedding guest list from a JSON file, skipping entries without a name or valid email and guests already on the list.""", "normal",
"""def import_guest_list(conn, path, wedding_id):
    with open(path) as handle:
        guests = json.load(handle)
    added = 0
    skipped = []
    cur = conn.cursor()
    for guest in guests:
        name = guest.get("name", "").strip()
        email = guest.get("email", "").strip().lower()
        if not name or "@" not in email:
            skipped.append(guest)
            continue
        cur.execute("SELECT 1 FROM guests WHERE wedding_id = %d AND email = '%s'" % (wedding_id, email))
        if cur.fetchone():
            skipped.append(guest)
            continue
        meal = guest.get("meal", "standard")
        cur.execute("INSERT INTO guests (wedding_id, name, email, meal) VALUES (%d, '%s', '%s', '%s')" % (wedding_id, name, email, meal))
        added += 1
    conn.commit()
    cur.close()
    return {"added": added, "skipped": len(skipped)}""",
[("""wedding_id = %d AND email = '%s'" % (wedding_id, email))""", """wedding_id = %s AND email = %s", (wedding_id, email))"""),
 ("""VALUES (%d, '%s', '%s', '%s')" % (wedding_id, name, email, meal))""", """VALUES (%s, %s, %s, %s)", (wedding_id, name, email, meal))""")], "psycopg2"),

("u294", """aiohttp handler that saves a signed-in user's display name, bio and website and returns the stored profile.""", "normal",
"""async def update_profile(request):
    user = request["user"]
    form = await request.post()
    display_name = form.get("display_name", "").strip()
    bio = form.get("bio", "").strip()
    website = form.get("website", "").strip()
    if not display_name:
        raise web.HTTPBadRequest(text="display name required")
    if len(bio) > 500:
        raise web.HTTPBadRequest(text="bio too long")
    if website and not website.startswith(("http://", "https://")):
        raise web.HTTPBadRequest(text="bad website")
    async with request.app["pool"].acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE profiles SET display_name = '" + display_name + "', bio = '" + bio + "', website = '" + website + "' WHERE user_id = " + str(user["id"]))
            await conn.commit()
            await cur.execute("SELECT display_name, bio, website FROM profiles WHERE user_id = %s", (user["id"],))
            row = await cur.fetchone()
    return web.json_response({"display_name": row[0], "bio": row[1], "website": row[2]})""",
[("""SET display_name = '" + display_name + "', bio = '" + bio + "', website = '" + website + "' WHERE user_id = " + str(user["id"]))""", """SET display_name = %s, bio = %s, website = %s WHERE user_id = %s", (display_name, bio, website, user["id"]))""")], "mysql"),

("u295", """Command line helper that deletes a project by name together with its tasks, comments and attachments, with a dry-run option that only prints the counts.""", "normal",
"""def delete_project(db_path, project_name, dry_run=False):
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute("SELECT id FROM projects WHERE name = '%s'" % project_name).fetchone()
        if row is None:
            print("no such project")
            return 1
        project_id = row[0]
        counts = {}
        for table in ("tasks", "comments", "attachments"):
            counts[table] = conn.execute("SELECT COUNT(*) FROM %s WHERE project_id = %d" % (table, project_id)).fetchone()[0]
        print("will remove", counts)
        if dry_run:
            return 0
        for table in ("tasks", "comments", "attachments"):
            conn.execute("DELETE FROM %s WHERE project_id = %d" % (table, project_id))
        conn.execute("DELETE FROM projects WHERE id = %d" % project_id)
        conn.commit()
        return 0
    finally:
        conn.close()""",
[("""conn.execute("SELECT id FROM projects WHERE name = '%s'" % project_name)""", """conn.execute("SELECT id FROM projects WHERE name = ?", (project_name,))""")], "sqlite3"),

("u296", """Extend the memberships of a club tier that expire within thirty days by a chosen term, recording who referred the renewal and logging an event per membership.""", "normal",
"""def renew_memberships(self, club_id, tier, months, referrer):
    if months not in (1, 3, 12):
        raise ValueError("unsupported term")
    renewed = 0
    with self.engine.begin() as conn:
        rows = conn.execute(text(f"SELECT id, expires_on FROM memberships WHERE club_id = {club_id} AND tier = '{tier}' AND expires_on < date('now', '+30 days')")).fetchall()
        for row in rows:
            base = max(row.expires_on, date.today())
            new_expiry = base + timedelta(days=30 * months)
            conn.execute(text(f"UPDATE memberships SET expires_on = '{new_expiry.isoformat()}', referrer = '{referrer}' WHERE id = {row.id}"))
            conn.execute(text("INSERT INTO membership_events (membership_id, kind) VALUES (:id, 'renewed')"), {"id": row.id})
            renewed += 1
    self.log.info("renewed %s memberships in club %s", renewed, club_id)
    return renewed""",
[("""text(f"SELECT id, expires_on FROM memberships WHERE club_id = {club_id} AND tier = '{tier}' AND expires_on < date('now', '+30 days')"))""", """text("SELECT id, expires_on FROM memberships WHERE club_id = :club_id AND tier = :tier AND expires_on < date('now', '+30 days')"), {"club_id": club_id, "tier": tier})"""),
 ("""text(f"UPDATE memberships SET expires_on = '{new_expiry.isoformat()}', referrer = '{referrer}' WHERE id = {row.id}"))""", """text("UPDATE memberships SET expires_on = :expires_on, referrer = :referrer WHERE id = :id"), {"expires_on": new_expiry.isoformat(), "referrer": referrer, "id": row.id})""")], "sqlalchemy"),

("u297", """Create or update a vendor contact by email inside a transaction and stamp the vendor's last contact time.""", "normal",
"""async def save_vendor_contact(pool, vendor_id, name, email, phone):
    name = name.strip()
    email = email.strip().lower()
    if not name:
        raise ValueError("name required")
    if "@" not in email:
        raise ValueError("bad email")
    async with pool.acquire() as conn:
        async with conn.transaction():
            existing = await conn.fetchrow("SELECT id FROM vendor_contacts WHERE vendor_id = " + str(vendor_id) + " AND email = '" + email + "'")
            if existing:
                await conn.execute("UPDATE vendor_contacts SET name = '" + name + "', phone = '" + phone + "' WHERE id = " + str(existing["id"]))
                contact_id = existing["id"]
            else:
                contact_id = await conn.fetchval("INSERT INTO vendor_contacts (vendor_id, name, email, phone) VALUES (" + str(vendor_id) + ", '" + name + "', '" + email + "', '" + phone + "') RETURNING id")
            await conn.execute("UPDATE vendors SET last_contact_at = NOW() WHERE id = " + str(vendor_id))
    return contact_id""",
[("""WHERE vendor_id = " + str(vendor_id) + " AND email = '" + email + "'")""", """WHERE vendor_id = $1 AND email = $2", vendor_id, email)"""),
 ("""SET name = '" + name + "', phone = '" + phone + "' WHERE id = " + str(existing["id"]))""", """SET name = $1, phone = $2 WHERE id = $3", name, phone, existing["id"])"""),
 ("""VALUES (" + str(vendor_id) + ", '" + name + "', '" + email + "', '" + phone + "') RETURNING id")""", """VALUES ($1, $2, $3, $4) RETURNING id", vendor_id, name, email, phone)"""),
 ("""WHERE id = " + str(vendor_id))""", """WHERE id = $1", vendor_id)""")], "other"),

("u298", """Import a list of print job rows for a customer code: validate paper, copies and finish, price each valid row with the customer's discount, store the accepted jobs and return a summary.""", "normal",
"""def import_print_jobs(conn, rows, customer_code, operator):
    accepted = []
    rejected = []
    customer = conn.execute("SELECT id, discount FROM customers WHERE code = '" + customer_code + "'").fetchone()
    if customer is None:
        raise LookupError("unknown customer " + customer_code)
    customer_id, discount = customer
    for index, row in enumerate(rows, start=1):
        reason = None
        paper = row.get("paper", "").strip()
        copies = row.get("copies")
        finish = row.get("finish", "none").strip()
        if not paper:
            reason = "missing paper"
        elif not isinstance(copies, int) or copies < 1:
            reason = "bad copies"
        elif finish not in ("none", "laminate", "staple", "bind"):
            reason = "bad finish"
        if reason:
            rejected.append({"row": index, "reason": reason})
            continue
        price_row = conn.execute("SELECT unit_price FROM papers WHERE name = '" + paper + "'").fetchone()
        if price_row is None:
            rejected.append({"row": index, "reason": "unknown paper"})
            continue
        total = price_row[0] * copies * (1 - discount)
        accepted.append((customer_id, paper, copies, finish, round(total, 2)))
    for customer_id, paper, copies, finish, total in accepted:
        conn.execute("INSERT INTO print_jobs (customer_id, paper, copies, finish, total, operator) VALUES (" + str(customer_id) + ", '" + paper + "', " + str(copies) + ", '" + finish + "', " + str(total) + ", '" + operator + "')")
    conn.commit()
    summary = {
        "accepted": len(accepted),
        "rejected": rejected,
        "revenue": round(sum(item[4] for item in accepted), 2),
    }
    log.info("print jobs imported for %s: %s accepted", customer_code, len(accepted))
    return summary""",
[("""WHERE code = '" + customer_code + "'")""", """WHERE code = ?", (customer_code,))"""),
 ("""WHERE name = '" + paper + "'")""", """WHERE name = ?", (paper,))"""),
 ("""VALUES (" + str(customer_id) + ", '" + paper + "', " + str(copies) + ", '" + finish + "', " + str(total) + ", '" + operator + "')")""", """VALUES (?, ?, ?, ?, ?, ?)", (customer_id, paper, copies, finish, total, operator))""")], "sqlite3"),

("u299", """Book a place in a fitness class for the signed-in member, applying an optional promo code and putting the member on the waitlist when the class is full.""", "normal",
"""@app.route("/classes/<int:class_id>/book", methods=["POST"])
@login_required
def book_class(class_id):
    member_id = current_user.id
    guest_name = request.form.get("guest_name", "").strip()
    note = request.form.get("note", "").strip()
    promo = request.form.get("promo", "").strip()
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT capacity, starts_at, price FROM fitness_classes WHERE id = %s FOR UPDATE", (class_id,))
        row = cur.fetchone()
        if row is None:
            abort(404)
        capacity, starts_at, price = row
        if starts_at < datetime.utcnow():
            flash("That class has already started")
            return redirect(url_for("schedule"))
        discount = 0
        if promo:
            cur.execute("SELECT percent FROM promos WHERE code = '{}' AND valid_until >= CURRENT_DATE".format(promo))
            promo_row = cur.fetchone()
            if promo_row is None:
                flash("That promo code is not valid")
                return redirect(url_for("class_page", class_id=class_id))
            discount = promo_row[0]
        cur.execute("SELECT COUNT(*) FROM bookings WHERE class_id = %s AND status = 'confirmed'", (class_id,))
        taken = cur.fetchone()[0]
        status = "confirmed" if taken < capacity else "waitlist"
        amount = round(price * (100 - discount) / 100, 2)
        cur.execute("INSERT INTO bookings (class_id, member_id, guest_name, note, status, amount) VALUES (%s, %s, '{}', '{}', %s, %s) RETURNING id".format(guest_name, note), (class_id, member_id, status, amount))
        booking_id = cur.fetchone()[0]
        conn.commit()
    except psycopg2.Error:
        conn.rollback()
        flash("Could not book that class")
        return redirect(url_for("class_page", class_id=class_id))
    finally:
        cur.close()
    if status == "waitlist":
        flash("The class is full, you are on the waitlist")
    else:
        flash("Booked! Reference " + str(booking_id))
    return redirect(url_for("schedule"))""",
[("""WHERE code = '{}' AND valid_until >= CURRENT_DATE".format(promo))""", """WHERE code = %s AND valid_until >= CURRENT_DATE", (promo,))"""),
 ("""VALUES (%s, %s, '{}', '{}', %s, %s) RETURNING id".format(guest_name, note), (class_id, member_id, status, amount))""", """VALUES (%s, %s, %s, %s, %s, %s) RETURNING id", (class_id, member_id, guest_name, note, status, amount))""")], "psycopg2"),
]

ROWS += [
("u300", """Update only the permitted fields of a scout kit item from a dictionary of changes and return the number of rows updated.""", "hard_positive",
"""def update_kit_fields(conn, kit_id, changes):
    allowed = ("name", "color", "size", "notes")
    assignments = []
    for key, value in changes.items():
        if key in allowed:
            assignments.append(key + " = '" + str(value) + "'")
    if not assignments:
        return 0
    cur = conn.execute("UPDATE kits SET " + ", ".join(assignments) + " WHERE id = " + str(int(kit_id)))
    conn.commit()
    log.info("kit %s updated: %s", kit_id, ", ".join(sorted(changes)))
    return cur.rowcount""",
[("""    assignments = []
""", """    assignments = []
    values = []
"""),
 ("""            assignments.append(key + " = '" + str(value) + "'")""", """            assignments.append(key + " = ?")
            values.append(value)"""),
 ("""conn.execute("UPDATE kits SET " + ", ".join(assignments) + " WHERE id = " + str(int(kit_id)))""", """conn.execute("UPDATE kits SET " + ", ".join(assignments) + " WHERE id = ?", values + [kit_id])""")], "sqlite3"),

("u301", """Delete rows from the labels table whose text matches the given label, refusing labels that contain unusual punctuation.""", "hard_positive",
"""def delete_by_label(conn, label):
    forbidden = ("'", '"', ";", "--")
    if any(mark in label for mark in forbidden):
        raise ValueError("invalid label")
    cur = conn.execute("DELETE FROM labels WHERE text = '" + label + "'")
    conn.commit()
    log.info("deleted %s labels", cur.rowcount)
    return cur.rowcount""",
[("""WHERE text = '" + label + "'")""", """WHERE text = ?", (label,))""")], "sqlite3"),

("u302", """Delete scout records, narrowed by any combination of troop, cutoff date and status, but never all of them at once.""", "hard_positive",
"""def purge_scout_records(conn, troop=None, before=None, status=None):
    sql = "DELETE FROM scout_records WHERE 1 = 1"
    if troop:
        sql += " AND troop = '" + troop + "'"
    if before:
        if len(before) != 10:
            raise ValueError("dates must look like YYYY-MM-DD")
        sql += " AND recorded_on < '" + before + "'"
    if status:
        sql += " AND status = '" + status + "'"
    if sql.endswith("1 = 1"):
        raise ValueError("refusing to delete everything")
    log.info("purging scout records: %s", sql)
    cur = conn.execute(sql)
    conn.commit()
    log.info("purged %s scout records", cur.rowcount)
    return cur.rowcount""",
[("""    sql = "DELETE FROM scout_records WHERE 1 = 1\"""", """    sql = "DELETE FROM scout_records WHERE 1 = 1"
    params = []"""),
 ("""        sql += " AND troop = '" + troop + "'\"""", """        sql += " AND troop = ?"
        params.append(troop)"""),
 ("""        sql += " AND recorded_on < '" + before + "'\"""", """        sql += " AND recorded_on < ?"
        params.append(before)"""),
 ("""        sql += " AND status = '" + status + "'\"""", """        sql += " AND status = ?"
        params.append(status)"""),
 ("""conn.execute(sql)""", """conn.execute(sql, params)""")], "sqlite3"),

("u303", """Record stock counts for a warehouse as one multi-row insert through the shared gateway object.""", "hard_positive",
"""def add_stock_counts(self, warehouse, counts):
    rows = []
    for sku, qty in counts.items():
        rows.append("('" + warehouse + "', '" + sku + "', " + str(int(qty)) + ")")
    if not rows:
        return 0
    sql = "INSERT INTO stock_counts (warehouse, sku, qty) VALUES " + ", ".join(rows)
    self.gateway.execute(sql)
    self.log.info("recorded %s counts for %s", len(rows), warehouse)
    self.dirty.add(warehouse)
    return len(rows)""",
[("""    rows = []
""", """    rows = []
    params = []
"""),
 ("""        rows.append("('" + warehouse + "', '" + sku + "', " + str(int(qty)) + ")")""", """        rows.append("(%s, %s, %s)")
        params.extend([warehouse, sku, int(qty)])"""),
 ("""self.gateway.execute(sql)""", """self.gateway.execute(sql, params)""")], "psycopg2"),

("u304", """Apply a customer's club discount to an order: look up the club name stored for the customer, find its discount percentage and update the order total with a note and an event.""", "hard_positive",
"""def apply_club_discount(conn, order_id):
    row = conn.execute("SELECT customer_id, subtotal FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        raise LookupError(order_id)
    customer_id, subtotal = row
    club = conn.execute("SELECT club_name FROM customers WHERE id = ?", (customer_id,)).fetchone()
    if club is None or club[0] is None:
        return subtotal
    club_name = club[0]
    discount_row = conn.execute("SELECT percent FROM club_discounts WHERE club_name = '" + club_name + "'").fetchone()
    if discount_row is None:
        return subtotal
    percent = discount_row[0]
    total = round(subtotal * (100 - percent) / 100, 2)
    conn.execute("UPDATE orders SET total = ?, discount_note = '" + club_name + " " + str(percent) + "%' WHERE id = ?", (total, order_id))
    conn.execute("INSERT INTO order_events (order_id, kind, detail) VALUES (?, 'discount', '" + club_name + "')", (order_id,))
    conn.commit()
    return total""",
[("""WHERE club_name = '" + club_name + "'").fetchone()""", """WHERE club_name = ?", (club_name,)).fetchone()"""),
 ("""discount_note = '" + club_name + " " + str(percent) + "%' WHERE id = ?", (total, order_id))""", """discount_note = ? WHERE id = ?", (total, club_name + " " + str(percent) + "%", order_id))"""),
 ("""VALUES (?, 'discount', '" + club_name + "')", (order_id,))""", """VALUES (?, 'discount', ?)", (order_id, club_name))""")], "sqlite3"),

("u305", """Summarise nights booked per room and floor for a coworking site and month, optionally limited to some floors.""", "hard_positive",
"""def occupancy_for_site(conn, site, month, floors=None):
    sql = "SELECT room, floor, SUM(nights) FROM stays WHERE site = '@site' AND month = '@month' GROUP BY room, floor ORDER BY floor, room"
    sql = sql.replace("@site", site).replace("@month", month)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
    finally:
        cur.close()
    by_floor = {}
    for room, floor, nights in rows:
        if floors is not None and floor not in floors:
            continue
        by_floor.setdefault(floor, []).append({"room": room, "nights": int(nights)})
    summary = []
    for floor in sorted(by_floor):
        rooms = by_floor[floor]
        total = sum(item["nights"] for item in rooms)
        busiest = max(rooms, key=lambda item: item["nights"])
        summary.append({"floor": floor, "rooms": rooms, "total": total, "busiest": busiest["room"]})
    log.info("occupancy for %s %s: %s floors", site, month, len(summary))
    return summary""",
[("""WHERE site = '@site' AND month = '@month' GROUP BY""", """WHERE site = %s AND month = %s GROUP BY"""),
 ("""    sql = sql.replace("@site", site).replace("@month", month)""", """    params = (site, month)"""),
 ("""cur.execute(sql)""", """cur.execute(sql, params)""")], "mysql"),

("u306", """Set a moderation flag on many rows of a table named by the caller, in chunks of two hundred ids, and write one summary row to the flag log.""", "hard_positive",
"""def bulk_set_flag(session, table_name, flag, ids, actor):
    if not ids:
        return 0
    if len(flag) > 20:
        raise ValueError("flag too long")
    updated = 0
    for start in range(0, len(ids), 200):
        chunk = ids[start:start + 200]
        id_list = ", ".join(str(int(i)) for i in chunk)
        result = session.execute(text(f"UPDATE {table_name} SET flag = '{flag}', flagged_by = '{actor}' WHERE id IN ({id_list})"))
        updated += result.rowcount
        log.info("flagged chunk starting at %s in %s", start, table_name)
    session.commit()
    session.execute(text("INSERT INTO flag_log (table_name, flag, actor, n) VALUES (:t, :f, :a, :n)"), {"t": table_name, "f": flag, "a": actor, "n": updated})
    session.commit()
    log.info("flagged %s rows in %s", updated, table_name)
    return updated""",
[("""    if not ids:
        return 0
""", """    if not ids:
        return 0
    if table_name not in ("articles", "comments", "uploads"):
        raise ValueError(table_name)
"""),
 ("""text(f"UPDATE {table_name} SET flag = '{flag}', flagged_by = '{actor}' WHERE id IN ({id_list})"))""", """text(f"UPDATE {table_name} SET flag = :flag, flagged_by = :actor WHERE id IN ({id_list})"), {"flag": flag, "actor": actor})""")], "sqlalchemy"),

("u307", """Build a player roster report filtered by team, position, status, city, an age range and a name search, with a caller-chosen sort and optional per-team totals.""", "hard_positive",
"""def build_roster_report(conn, filters, sort="last_name", descending=False, include_totals=True):
    fields = {"team": "team", "position": "position", "status": "status", "city": "city"}
    clauses = []
    for name, value in filters.items():
        column = fields.get(name)
        if column is None:
            continue
        if isinstance(value, (list, tuple, set)):
            clauses.append(column + " IN (" + ",".join("'" + str(v) + "'" for v in value) + ")")
        else:
            clauses.append(column + " = '" + str(value) + "'")
    min_age = filters.get("min_age")
    max_age = filters.get("max_age")
    if min_age is not None:
        clauses.append("age >= " + str(min_age))
    if max_age is not None:
        clauses.append("age <= " + str(max_age))
    search = filters.get("search")
    if search:
        clauses.append("(first_name LIKE '%" + search + "%' OR last_name LIKE '%" + search + "%')")
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    order_columns = {"last_name": "last_name", "age": "age", "team": "team", "joined": "joined_on"}
    order = order_columns.get(sort, "last_name")
    direction = " DESC" if descending else ""
    sql = "SELECT id, first_name, last_name, team, position, status, city, age, joined_on FROM players" + where + " ORDER BY " + order + direction
    rows = conn.execute(sql).fetchall()
    players = []
    for row in rows:
        players.append({
            "id": row[0],
            "name": row[1] + " " + row[2],
            "team": row[3],
            "position": row[4],
            "status": row[5],
            "city": row[6],
            "age": row[7],
            "joined": row[8],
        })
    report = {"count": len(players), "players": players}
    if include_totals:
        totals_sql = "SELECT team, COUNT(*), AVG(age) FROM players" + where + " GROUP BY team ORDER BY team"
        report["teams"] = [
            {"team": team, "players": count, "average_age": round(avg, 1)}
            for team, count, avg in conn.execute(totals_sql).fetchall()
        ]
    return report""",
[("""    clauses = []
""", """    clauses = []
    params = []
"""),
 ("""            clauses.append(column + " IN (" + ",".join("'" + str(v) + "'" for v in value) + ")")""", """            clauses.append(column + " IN (" + ",".join("?" for _ in value) + ")")
            params.extend(value)"""),
 ("""            clauses.append(column + " = '" + str(value) + "'")""", """            clauses.append(column + " = ?")
            params.append(value)"""),
 ("""        clauses.append("age >= " + str(min_age))""", """        clauses.append("age >= ?")
        params.append(int(min_age))"""),
 ("""        clauses.append("age <= " + str(max_age))""", """        clauses.append("age <= ?")
        params.append(int(max_age))"""),
 ("""        clauses.append("(first_name LIKE '%" + search + "%' OR last_name LIKE '%" + search + "%')")""", """        clauses.append("(first_name LIKE ? OR last_name LIKE ?)")
        params.extend(["%" + search + "%", "%" + search + "%"])"""),
 ("""rows = conn.execute(sql).fetchall()""", """rows = conn.execute(sql, params).fetchall()"""),
 ("""conn.execute(totals_sql)""", """conn.execute(totals_sql, params)""")], "sqlite3"),

("u308", """Count the members, events or venues registered since a date, choosing the table by kind.""", "hard_negative",
"""def count_registered(conn, kind, since):
    tables = {"members": "members", "events": "events", "venues": "venues"}
    name = tables.get(kind)
    if name is None:
        raise ValueError(kind)
    cur = conn.execute(f"SELECT COUNT(*) FROM {name} WHERE created_on >= ?", (since,))
    total = cur.fetchone()[0]
    log.info("%s registered since %s: %s", kind, since, total)
    return total""", "", "sqlite3"),

("u309", """Return one page of volunteers for a team ordered by name, with the page number and size clamped to sensible values.""", "hard_negative",
"""def page_of_volunteers(conn, page, size, team):
    page = max(int(page), 1)
    size = min(int(size), 100)
    offset = (page - 1) * size
    query = f"SELECT id, name, hours FROM volunteers WHERE team = ? ORDER BY name LIMIT {size} OFFSET {offset}"
    rows = conn.execute(query, (team,)).fetchall()
    return [{"id": r[0], "name": r[1], "hours": r[2]} for r in rows]""", "", "sqlite3"),

("u310", """Change one editable field of a listing, choosing the column from a fixed mapping, and say whether exactly one row changed.""", "hard_negative",
"""def set_listing_field(conn, listing_id, field, value):
    columns = {"title": "title", "summary": "summary_text", "price": "price_cents"}
    column = columns.get(field)
    if column is None:
        raise ValueError(field)
    query = sql.SQL("UPDATE listings SET {col} = %s, updated_at = NOW() WHERE id = %s").format(col=sql.Identifier(column))
    with conn.cursor() as cur:
        cur.execute(query, (value, listing_id))
        changed = cur.rowcount
    conn.commit()
    return changed == 1""", "", "psycopg2"),

("u311", """Assign several volunteers to a shift, rejecting the request if the shift has too few free places and skipping volunteers who are already assigned.""", "hard_negative",
"""def assign_volunteers(conn, shift_id, volunteer_ids, assigned_by):
    ids = [int(v) for v in volunteer_ids]
    if not ids:
        return {"assigned": 0, "skipped": []}
    shift = conn.execute("SELECT capacity, assigned FROM shifts WHERE id = ?", (shift_id,)).fetchone()
    if shift is None:
        raise LookupError(shift_id)
    free = shift[0] - shift[1]
    if len(ids) > free:
        raise ValueError("not enough free places")
    marks = ",".join("?" for _ in ids)
    busy = conn.execute(
        f"SELECT volunteer_id FROM assignments WHERE shift_id = ? AND volunteer_id IN ({marks})",
        [shift_id] + ids,
    ).fetchall()
    already = {row[0] for row in busy}
    todo = [i for i in ids if i not in already]
    for volunteer_id in todo:
        conn.execute(
            "INSERT INTO assignments (shift_id, volunteer_id, assigned_by) VALUES (?, ?, ?)",
            (shift_id, volunteer_id, assigned_by),
        )
    conn.execute("UPDATE shifts SET assigned = assigned + ? WHERE id = ?", (len(todo), shift_id))
    conn.commit()
    return {"assigned": len(todo), "skipped": sorted(already)}""", "", "sqlite3"),

("u312", """Record a donation for a campaign after parsing the donor reference as a UUID, the amount as a two-decimal number and the campaign code as an enum, then return the campaign total.""", "hard_negative",
"""def record_donation(conn, donor_ref, amount, currency, campaign_code):
    try:
        donor_uuid = uuid.UUID(str(donor_ref))
    except ValueError:
        raise ValueError("donor reference must be a UUID")
    value = Decimal(str(amount)).quantize(Decimal("0.01"))
    if value <= 0:
        raise ValueError("amount must be positive")
    channel = Channel(campaign_code)
    if currency not in ("EUR", "USD", "GBP"):
        raise ValueError("unsupported currency")
    campaign = conn.execute("SELECT id, goal FROM campaigns WHERE code = ?", (channel.value,)).fetchone()
    if campaign is None:
        raise LookupError(campaign_code)
    conn.execute(
        f"INSERT INTO donations (donor, amount, currency, campaign_id) VALUES ('{donor_uuid}', {value}, ?, ?)",
        (currency, campaign[0]),
    )
    raised = conn.execute("SELECT SUM(amount) FROM donations WHERE campaign_id = ?", (campaign[0],)).fetchone()[0]
    conn.commit()
    return {"campaign": channel.value, "raised": float(raised), "goal": campaign[1]}""", "", "sqlite3"),

("u313", """Search recipes in a list of cuisines under a cooking time, with a fixed set of sort orders and a capped limit, and return them as dictionaries.""", "hard_negative",
"""def search_recipes_by_cuisine(session, cuisines, max_minutes, order, limit):
    orders = {"quick": "minutes ASC", "popular": "saves DESC", "new": "created_on DESC"}
    order_clause = orders.get(order, "created_on DESC")
    limit = max(1, min(int(limit), 50))
    if not cuisines:
        return []
    stmt = text(
        "SELECT id, title, cuisine, minutes, saves FROM recipes "
        "WHERE cuisine IN :cuisines AND minutes <= :max_minutes "
        f"ORDER BY {order_clause} LIMIT :limit"
    ).bindparams(bindparam("cuisines", expanding=True))
    rows = session.execute(stmt, {"cuisines": list(cuisines), "max_minutes": max_minutes, "limit": limit}).fetchall()
    recipes = []
    for row in rows:
        recipes.append({
            "id": row.id,
            "title": row.title,
            "cuisine": row.cuisine,
            "minutes": row.minutes,
            "saves": row.saves,
        })
    log.info("recipe search returned %s rows", len(recipes))
    return recipes""", "", "sqlalchemy"),

("u314", """Export selected columns of a registered table as CSV lines with an optional date range and row cap, followed by a footer with the row count and column totals.""", "hard_negative",
"""def export_csv_lines(conn, table, columns, since=None, until=None, max_rows=1000):
    registry = {
        "donations": ("donations", ("id", "donor", "amount", "currency", "given_on")),
        "volunteers": ("volunteers", ("id", "name", "team", "hours", "joined_on")),
        "events": ("events", ("id", "title", "venue", "starts_on", "capacity")),
    }
    entry = registry.get(table)
    if entry is None:
        raise ValueError("unknown table")
    table_name, known = entry
    selected = []
    for column in columns:
        if column not in known:
            raise ValueError("unknown column: " + str(column))
        selected.append(column)
    if not selected:
        selected = list(known)
    date_column = known[-1]
    conditions = []
    values = []
    if since:
        conditions.append(date_column + " >= ?")
        values.append(since)
    if until:
        conditions.append(date_column + " <= ?")
        values.append(until)
    where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
    limit = max(1, min(int(max_rows), 5000))
    query = "SELECT " + ", ".join(selected) + " FROM " + table_name + where + " ORDER BY " + known[0] + " LIMIT " + str(limit)
    rows = conn.execute(query, values).fetchall()
    lines = [",".join(selected)]
    totals = {}
    for row in rows:
        lines.append(",".join(str(cell) for cell in row))
        for name, cell in zip(selected, row):
            if isinstance(cell, (int, float)):
                totals[name] = totals.get(name, 0) + cell
    footer = ["rows=" + str(len(rows))]
    for name in selected:
        if name in totals:
            footer.append(name + "_total=" + str(round(totals[name], 2)))
    lines.append(";".join(footer))
    return lines""", "", "sqlite3"),
]
