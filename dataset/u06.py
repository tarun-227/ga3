ROWS = [
("u240", """Delete a pet's vaccination records that were given before a cutoff date and return how many were removed.""", "normal",
"""def clear_vaccination_records(conn, pet_id, before_date):
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM vaccinations WHERE pet_id = {pet_id} AND given_on < '{before_date}'")
        count = cur.rowcount
    conn.commit()
    log.info("removed %s vaccination rows", count)
    return count""",
[("""cur.execute(f"DELETE FROM vaccinations WHERE pet_id = {pet_id} AND given_on < '{before_date}'")""", """cur.execute("DELETE FROM vaccinations WHERE pet_id = %s AND given_on < %s", (pet_id, before_date))""")], "psycopg2"),

("u241", """Add a bottle to the wine cellar inventory at a rack and shelf position and return the new row id.""", "normal",
"""def add_wine_bottle(conn, label, vintage, rack, shelf):
    if vintage < 1800:
        raise ValueError("vintage too old")
    if not label.strip():
        raise ValueError("label required")
    if shelf < 1 or shelf > 12:
        raise ValueError("shelf out of range")
    sql = "INSERT INTO cellar (label, vintage, rack, shelf) VALUES ('" + label + "', " + str(vintage) + ", '" + rack + "', " + str(shelf) + ")"
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    log.info("bottle %s stored at %s/%s", label, rack, shelf)
    return cur.lastrowid""",
[("""VALUES ('" + label + "', " + str(vintage) + ", '" + rack + "', " + str(shelf) + ")\"""", """VALUES (?, ?, ?, ?)\""""),
 ("""    cur.execute(sql)""", """    params = (label, vintage, rack, shelf)
    cur.execute(sql, params)""")], "sqlite3"),

("u242", """Endpoint that extends a fishing permit's expiry date by a number of years given in the form.""", "normal",
"""@app.route("/fishing/permits/<permit_no>/renew", methods=["POST"])
def renew_permit(permit_no):
    years = request.form.get("years", "1")
    cur = mysql.connection.cursor()
    cur.execute("UPDATE permits SET expires_on = DATE_ADD(expires_on, INTERVAL {} YEAR) WHERE permit_no = '{}'".format(years, permit_no))
    mysql.connection.commit()
    updated = cur.rowcount
    cur.close()
    return jsonify({"permit": permit_no, "renewed": updated == 1})""",
[("""INTERVAL {} YEAR) WHERE permit_no = '{}'".format(years, permit_no))""", """INTERVAL %s YEAR) WHERE permit_no = %s", (int(years), permit_no))""")], "mysql"),

("u243", """Return the electricity tariffs of a zone that start at or above a minimum usage, cheapest first.""", "normal",
"""def tariffs_for_zone(self, zone_id, min_kwh):
    stmt = "SELECT plan, rate_cents, min_kwh FROM tariffs WHERE zone_id = %d AND min_kwh >= %s ORDER BY rate_cents" % (zone_id, min_kwh)
    with self.engine.connect() as conn:
        rows = conn.execute(text(stmt)).fetchall()
    plans = []
    for plan, rate, floor in rows:
        plans.append({"plan": plan, "rate": rate / 100, "floor": floor})
    return plans""",
[("""zone_id = %d AND min_kwh >= %s ORDER BY rate_cents" % (zone_id, min_kwh)""", """zone_id = :zone_id AND min_kwh >= :min_kwh ORDER BY rate_cents\""""),
 ("""conn.execute(text(stmt))""", """conn.execute(text(stmt), {"zone_id": zone_id, "min_kwh": min_kwh})""")], "sqlalchemy"),

("u244", """Class-based Django view that saves a note and a new status on a maintenance job, then redirects to the job page.""", "normal",
"""def save_job_update(self, request, pk):
    note = request.POST.get("note", "")
    status = request.POST.get("status", "open")
    if not note:
        messages.error(request, "A note is required")
        return redirect("job-detail", pk=pk)
    with connection.cursor() as cursor:
        cursor.execute("UPDATE maintenance_job SET note = '" + note + "', status = '" + status + "' WHERE id = " + str(pk))
    return redirect("job-detail", pk=pk)""",
[("""SET note = '" + note + "', status = '" + status + "' WHERE id = " + str(pk))""", """SET note = %s, status = %s WHERE id = %s", [note, status, pk])""")], "django_orm"),

("u245", """Find shows at a venue whose title contains a given word, ordered by start time.""", "normal",
"""def find_shows(conn, title_part, venue_id):
    cursor = conn.cursor()
    cursor.execute(f"SELECT show_id, title, starts_at FROM shows WHERE venue_id = {venue_id} AND title LIKE '%{title_part}%' ORDER BY starts_at")
    shows = cursor.fetchall()
    cursor.close()
    return [{"id": s.show_id, "title": s.title, "starts": s.starts_at} for s in shows]""",
[("""cursor.execute(f"SELECT show_id, title, starts_at FROM shows WHERE venue_id = {venue_id} AND title LIKE '%{title_part}%' ORDER BY starts_at")""", """cursor.execute("SELECT show_id, title, starts_at FROM shows WHERE venue_id = ? AND title LIKE ? ORDER BY starts_at", (venue_id, "%" + title_part + "%"))""")], "other"),

("u246", """Read item names and prices from a comma separated file and store them in the bakery price table.""", "normal",
"""def import_bakery_prices(conn, path):
    inserted = 0
    with open(path) as source:
        for line in source:
            name, price = line.strip().split(",")
            conn.execute("INSERT OR REPLACE INTO bakery_prices (item, price) VALUES ('%s', %s)" % (name, price))
            inserted += 1
    conn.commit()
    return inserted""",
[("""VALUES ('%s', %s)" % (name, price))""", """VALUES (?, ?)", (name, price))""")], "sqlite3"),

("u247", """Return which telescope slots are booked on a list of nights for one instrument, as JSON.""", "normal",
"""@app.route("/api/telescope/slots")
def booked_slots():
    nights = request.args.get("nights", "")
    scope = request.args.get("scope", "main")
    if not nights:
        return jsonify([])
    dates = [d.strip() for d in nights.split(",") if d.strip()]
    quoted = ", ".join("'" + d + "'" for d in dates)
    sql = f"SELECT night, member, minutes FROM slots WHERE scope = '{scope}' AND night IN ({quoted}) ORDER BY night"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return jsonify([{"night": str(r[0]), "member": r[1], "minutes": r[2]} for r in rows])""",
[("""    quoted = ", ".join("'" + d + "'" for d in dates)""", """    marks = ", ".join(["%s"] * len(dates))"""),
 ("""WHERE scope = '{scope}' AND night IN ({quoted})""", """WHERE scope = %s AND night IN ({marks})"""),
 ("""cur.execute(sql)""", """cur.execute(sql, [scope] + dates)""")], "psycopg2"),

("u248", """Async method that deletes a shop's coupons that expired before a cutoff date, rolling back on failure.""", "normal",
"""async def delete_expired_coupons(self, shop, cutoff):
    async with self.pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute("DELETE FROM coupons WHERE shop = '" + shop + "' AND expires_on < '" + cutoff + "'")
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise
            removed = cur.rowcount
    self.stats["coupons_removed"] += removed
    return removed""",
[("""WHERE shop = '" + shop + "' AND expires_on < '" + cutoff + "'")""", """WHERE shop = %s AND expires_on < %s", (shop, cutoff))""")], "mysql"),

("u249", """Endpoint that stores a solar panel reading posted as JSON and answers with a status.""", "normal",
"""@app.route("/solar/readings", methods=["POST"])
def post_reading():
    data = request.get_json()
    panel = data["panel_id"]
    watts = data["watts"]
    taken = data.get("taken_at", datetime.utcnow().isoformat())
    if watts < 0:
        return jsonify({"error": "negative output"}), 400
    sql = f"INSERT INTO panel_readings (panel_id, watts, taken_at) VALUES ('{panel}', {watts}, '{taken}')"
    try:
        db.session.execute(text(sql))
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "could not save"}), 500
    return jsonify({"status": "saved"}), 201""",
[("""VALUES ('{panel}', {watts}, '{taken}')\"""", """VALUES (:panel, :watts, :taken)\""""),
 ("""sql = f"INSERT""", """sql = "INSERT"""),
 ("""db.session.execute(text(sql))""", """db.session.execute(text(sql), {"panel": panel, "watts": watts, "taken": taken})""")], "sqlalchemy"),

("u250", """List the most recent gigs at a venue with the page size and offset taken from the query string.""", "normal",
"""@app.route("/venues/<venue>/gigs")
def recent_gigs(venue):
    per_page = request.args.get("per_page", "20")
    offset = request.args.get("offset", "0")
    if not venue:
        abort(404)
    sql = "SELECT id, band, played_on FROM gigs WHERE venue = ? ORDER BY played_on DESC LIMIT " + per_page + " OFFSET " + offset
    rows = get_db().execute(sql, (venue,)).fetchall()
    return jsonify([{"id": r[0], "band": r[1], "played_on": r[2]} for r in rows])""",
[("""LIMIT " + per_page + " OFFSET " + offset""", """LIMIT " + str(int(per_page)) + " OFFSET " + str(int(offset))""")], "sqlite3"),

("u251", """Change one named field of a crop record and keep a list of the fields edited.""", "normal",
"""def set_crop_field(self, crop_id, field, value):
    if value is None or value == "":
        raise ValueError("empty value")
    sql = "UPDATE crops SET " + field + " = %s WHERE id = %s"
    with self.conn.cursor() as cur:
        cur.execute(sql, (value, crop_id))
        if cur.rowcount != 1:
            self.conn.rollback()
            raise KeyError(crop_id)
    self.conn.commit()
    self.audit.append((crop_id, field))
    self.cache.pop(crop_id, None)
    if field == "planted_on":
        self.schedule.pop(crop_id, None)
    elif field == "notes":
        self.notes_index.pop(crop_id, None)
    self.log.debug("audit trail length %s", len(self.audit))
    self.log.debug("cache size %s", len(self.cache))
    self.log.debug("schedule size %s", len(self.schedule))
    self.log.info("crop %s field %s changed", crop_id, field)
    return True""",
[("""    sql = "UPDATE crops""", """    if field not in ("name", "variety", "planted_on", "notes"):
        raise ValueError(field)
    sql = "UPDATE crops""")], "psycopg2"),

("u252", """Sanic route listing hiking trails of one difficulty sorted by a column from the query string.""", "normal",
"""@bp.get("/trails")
async def list_trails(request):
    difficulty = request.args.get("difficulty", "easy")
    sort = request.args.get("sort", "length_km")
    async with request.app.ctx.pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, length_km, difficulty FROM trails WHERE difficulty = '" + difficulty + "' ORDER BY " + sort)
    trails = []
    for row in rows:
        trails.append({"id": row["id"], "name": row["name"], "length": float(row["length_km"])})
    trails.sort(key=lambda trail: trail["length"])
    return json({"count": len(trails), "trails": trails})""",
[("""    sort = request.args.get("sort", "length_km")
""", """    sort = request.args.get("sort", "length_km")
    if sort not in ("length_km", "name"):
        sort = "length_km"
"""),
 ("""WHERE difficulty = '" + difficulty + "' ORDER BY " + sort)""", """WHERE difficulty = $1 ORDER BY " + sort, difficulty)""")], "other"),

("u253", """Load radio station records from a CSV file, skipping rows with no call sign, and return the loaded count and the skipped rows.""", "normal",
"""def load_station_catalog(conn, csv_path):
    loaded = 0
    skipped = []
    with open(csv_path, newline="") as handle:
        for row in csv.DictReader(handle):
            if not row["call_sign"]:
                skipped.append(row)
                continue
            sql = "INSERT INTO stations (call_sign, city, frequency) VALUES ('%s', '%s', %s)" % (row["call_sign"], row["city"], row["frequency"])
            try:
                with conn.cursor() as cur:
                    cur.execute(sql)
                loaded += 1
            except psycopg2.Error:
                conn.rollback()
                skipped.append(row)
    conn.commit()
    return loaded, skipped""",
[("""VALUES ('%s', '%s', %s)" % (row["call_sign"], row["city"], row["frequency"])""", """VALUES (%s, %s, %s)\""""),
 ("""cur.execute(sql)""", """cur.execute(sql, (row["call_sign"], row["city"], row["frequency"]))""")], "psycopg2"),

("u254", """DRF viewset method returning a team's matches for a season with a raw query.""", "normal",
"""def team_matches(self):
    team = self.request.query_params.get("team")
    season = self.request.query_params.get("season", "2024")
    if team is None:
        return Match.objects.none()
    if len(team) > 50:
        raise ValidationError("team name too long")
    logger.info("match lookup for %s", team)
    query = "SELECT * FROM league_match WHERE season = %s AND (home_team = '%s' OR away_team = '%s') ORDER BY played_on" % (season, team, team)
    return Match.objects.raw(query)""",
[("""season = %s AND (home_team = '%s' OR away_team = '%s') ORDER BY played_on" % (season, team, team)""", """season = %s AND (home_team = %s OR away_team = %s) ORDER BY played_on\""""),
 ("""Match.objects.raw(query)""", """Match.objects.raw(query, [season, team, team])""")], "django_orm"),
]

ROWS += [
("u255", """Register a new club member from a signup form, refusing duplicate usernames or emails, and log the new member in.""", "normal",
"""@app.route("/signup", methods=["POST"])
def signup_member():
    form = request.form
    username = form.get("username", "").strip()
    email = form.get("email", "").strip().lower()
    password = form.get("password", "")
    if len(username) < 3 or len(username) > 30:
        return render_template("signup.html", error="Username must be 3-30 characters"), 400
    if "@" not in email:
        return render_template("signup.html", error="Enter a valid email"), 400
    if len(password) < 8:
        return render_template("signup.html", error="Password too short"), 400
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM members WHERE username = '" + username + "' OR email = '" + email + "'")
    if cur.fetchone():
        cur.close()
        return render_template("signup.html", error="Already registered"), 409
    hashed = generate_password_hash(password)
    cur.execute("INSERT INTO members (username, email, password_hash, joined_on) VALUES ('" + username + "', '" + email + "', '" + hashed + "', NOW())")
    mysql.connection.commit()
    member_id = cur.lastrowid
    cur.close()
    session["member_id"] = member_id
    return redirect(url_for("dashboard"))""",
[("""WHERE username = '" + username + "' OR email = '" + email + "'")""", """WHERE username = %s OR email = %s", (username, email))"""),
 ("""VALUES ('" + username + "', '" + email + "', '" + hashed + "', NOW())")""", """VALUES (%s, %s, %s, NOW())", (username, email, hashed))""")], "mysql"),

("u256", """Book a catering order for a client: check the client's credit limit, price each menu item per head, then store the order and its items in one transaction.""", "normal",
"""def book_catering(self, client_id, menu_codes, event_date, headcount, notes):
    if headcount < 1:
        raise ValueError("headcount must be positive")
    if not menu_codes:
        raise ValueError("choose at least one menu item")
    if len(set(menu_codes)) != len(menu_codes):
        raise ValueError("duplicate menu items")
    event_day = datetime.strptime(event_date, "%Y-%m-%d").date()
    if event_day < date.today() + timedelta(days=2):
        raise ValueError("orders need two days notice")
    with self.engine.begin() as conn:
        client = conn.execute(text(f"SELECT id, name, credit_limit FROM clients WHERE id = {client_id}")).first()
        if client is None:
            raise LookupError("unknown client")
        total = 0
        courses = {}
        for code in menu_codes:
            row = conn.execute(text(f"SELECT price_per_head FROM menu WHERE code = '{code}'")).first()
            if row is None:
                raise LookupError(code)
            course = code.split("-")[0]
            courses[course] = courses.get(course, 0) + 1
            total += row[0] * headcount
        if courses.get("main", 0) == 0:
            raise ValueError("a main course is required")
        if headcount >= 50:
            total = total * 0.95
        elif headcount >= 20:
            total = total * 0.98
        total = round(total, 2)
        if total > client.credit_limit:
            raise ValueError("over credit limit")
        result = conn.execute(text(f"INSERT INTO catering_orders (client_id, event_date, headcount, total, notes) VALUES ({client_id}, '{event_date}', {headcount}, {total}, '{notes}')"))
        order_id = result.lastrowid
        for code in menu_codes:
            conn.execute(text(f"INSERT INTO catering_items (order_id, menu_code) VALUES ({order_id}, '{code}')"))
        if notes:
            self.log.info("order %s has notes", order_id)
    self.log.info("catering order %s booked for %s guests", order_id, headcount)
    self.stats["catering_orders"] += 1
    self.stats["catering_revenue"] += total
    self.mailer.send(client.name, "Catering confirmation", "Order %s for %s" % (order_id, event_date))
    return order_id""",
[("""text(f"SELECT id, name, credit_limit FROM clients WHERE id = {client_id}"))""", """text("SELECT id, name, credit_limit FROM clients WHERE id = :client_id"), {"client_id": client_id})"""),
 ("""text(f"SELECT price_per_head FROM menu WHERE code = '{code}'"))""", """text("SELECT price_per_head FROM menu WHERE code = :code"), {"code": code})"""),
 ("""text(f"INSERT INTO catering_orders (client_id, event_date, headcount, total, notes) VALUES ({client_id}, '{event_date}', {headcount}, {total}, '{notes}')"))""", """text("INSERT INTO catering_orders (client_id, event_date, headcount, total, notes) VALUES (:client_id, :event_date, :headcount, :total, :notes)"), {"client_id": client_id, "event_date": event_date, "headcount": headcount, "total": total, "notes": notes})"""),
 ("""text(f"INSERT INTO catering_items (order_id, menu_code) VALUES ({order_id}, '{code}')"))""", """text("INSERT INTO catering_items (order_id, menu_code) VALUES (:order_id, :code)"), {"order_id": order_id, "code": code})""")], "sqlalchemy"),

("u257", """Tornado handler that lets a customer change the delivery address and phone of one of their courier jobs after checking that the job is still pending.""", "normal",
"""def put(self, job_id):
    user = self.current_user
    if user is None:
        self.set_status(401)
        return self.finish({"error": "login required"})
    payload = json.loads(self.request.body)
    address = payload.get("address", "").strip()
    phone = payload.get("phone", "").strip()
    if not address:
        self.set_status(422)
        return self.finish({"error": "address required"})
    if len(address) > 200:
        self.set_status(422)
        return self.finish({"error": "address too long"})
    if phone and not phone.replace("+", "").replace(" ", "").isdigit():
        self.set_status(422)
        return self.finish({"error": "phone must contain digits only"})
    if not self.application.limiter.allow(user["id"]):
        self.set_status(429)
        return self.finish({"error": "slow down"})
    cur = self.application.db.cursor()
    cur.execute("SELECT status, customer_id FROM courier_jobs WHERE id = " + job_id)
    row = cur.fetchone()
    if row is None:
        self.set_status(404)
        return self.finish({"error": "unknown job"})
    if row[1] != user["id"]:
        self.set_status(403)
        return self.finish({"error": "not your job"})
    if row[0] != "pending":
        self.set_status(409)
        return self.finish({"error": "job already dispatched"})
    cur.execute("UPDATE courier_jobs SET address = '" + address + "', phone = '" + phone + "' WHERE id = " + job_id)
    self.application.db.commit()
    cur.close()
    self.application.log.info("job %s updated by %s", job_id, user["id"])
    self.application.events.publish("courier.updated", job_id)
    self.finish({"id": job_id, "address": address, "phone": phone})""",
[("""FROM courier_jobs WHERE id = " + job_id)""", """FROM courier_jobs WHERE id = %s", (job_id,))"""),
 ("""SET address = '" + address + "', phone = '" + phone + "' WHERE id = " + job_id)""", """SET address = %s, phone = %s WHERE id = %s", (address, phone, job_id))""")], "mysql"),

("u258", """Return the activity feed for a project, filtered by an event kind and a date window chosen by the caller, newest first.""", "normal",
"""@router.get("/projects/{project_id}/activity")
async def project_activity(project_id: int, kind: str = "", since: str = "", limit: int = 50):
    if limit < 1 or limit > 200:
        raise HTTPException(status_code=422, detail="limit out of range")
    if not since:
        since = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    query = (
        "SELECT id, actor, kind, summary, created_at FROM activity "
        "WHERE project_id = " + str(project_id) + " AND created_at >= '" + since + "' "
        "AND kind LIKE '" + kind + "%' ORDER BY created_at DESC LIMIT " + str(limit)
    )
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
    events = []
    for row in rows:
        events.append({
            "id": row["id"],
            "actor": row["actor"],
            "kind": row["kind"],
            "summary": row["summary"],
            "at": row["created_at"].isoformat(),
        })
    return {"project": project_id, "count": len(events), "events": events}""",
[("""        "WHERE project_id = " + str(project_id) + " AND created_at >= '" + since + "' "
        "AND kind LIKE '" + kind + "%' ORDER BY created_at DESC LIMIT " + str(limit)""", """        "WHERE project_id = $1 AND created_at >= $2 "
        "AND kind LIKE $3 ORDER BY created_at DESC LIMIT $4\""""),
 ("""conn.fetch(query)""", """conn.fetch(query, project_id, since, kind + "%", limit)""")], "other"),

("u259", """Method that records a repair ticket for a machine on the factory floor, closes any older open ticket for it and returns the new ticket id.""", "normal",
"""def open_repair_ticket(self, machine_id, reporter, description, priority):
    if priority not in (1, 2, 3):
        raise ValueError("priority must be 1, 2 or 3")
    cur = self.conn.cursor()
    try:
        cur.execute("SELECT id FROM repair_tickets WHERE machine_id = '%s' AND closed_at IS NULL" % machine_id)
        older = [row[0] for row in cur.fetchall()]
        for ticket_id in older:
            cur.execute("UPDATE repair_tickets SET closed_at = NOW(), closed_by = 'system' WHERE id = %s" % ticket_id)
        cur.execute("INSERT INTO repair_tickets (machine_id, reporter, description, priority, opened_at) VALUES ('%s', '%s', '%s', %s, NOW()) RETURNING id" % (machine_id, reporter, description, priority))
        new_id = cur.fetchone()[0]
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    self.notify("repairs", new_id)
    return new_id""",
[("""WHERE machine_id = '%s' AND closed_at IS NULL" % machine_id)""", """WHERE machine_id = %s AND closed_at IS NULL", (machine_id,))"""),
 ("""WHERE id = %s" % ticket_id)""", """WHERE id = %s", (ticket_id,))"""),
 ("""VALUES ('%s', '%s', '%s', %s, NOW()) RETURNING id" % (machine_id, reporter, description, priority))""", """VALUES (%s, %s, %s, %s, NOW()) RETURNING id", (machine_id, reporter, description, priority))""")], "psycopg2"),

("u260", """Bulk import of survey answers from a tab separated file, storing each respondent and their answers, then printing a one-line summary.""", "normal",
"""def import_survey_answers(conn, path, survey_id):
    respondents = 0
    answers = 0
    cur = conn.cursor()
    with open(path) as handle:
        header = handle.readline().rstrip(chr(10)).split(chr(9))
        questions = header[1:]
        for line in handle:
            fields = line.rstrip(chr(10)).split(chr(9))
            if len(fields) != len(header):
                continue
            email = fields[0]
            cur.execute("INSERT INTO respondents (survey_id, email) VALUES (" + str(survey_id) + ", '" + email + "')")
            respondent_id = cur.lastrowid
            respondents += 1
            for question, value in zip(questions, fields[1:]):
                if value == "":
                    continue
                cur.execute("INSERT INTO answers (respondent_id, question, value) VALUES (" + str(respondent_id) + ", '" + question + "', '" + value + "')")
                answers += 1
    conn.commit()
    cur.close()
    print(respondents, "respondents,", answers, "answers")
    return respondents, answers""",
[("""VALUES (" + str(survey_id) + ", '" + email + "')")""", """VALUES (?, ?)", (survey_id, email))"""),
 ("""VALUES (" + str(respondent_id) + ", '" + question + "', '" + value + "')")""", """VALUES (?, ?, ?)", (respondent_id, question, value))""")], "sqlite3"),

("u261", """Admin view that deletes a user's saved searches that match a name pattern and reports how many were removed.""", "normal",
"""@staff_member_required
@require_http_methods(["POST"])
def purge_saved_searches(request, user_id):
    pattern = request.POST.get("pattern", "").strip()
    if not pattern:
        return HttpResponseBadRequest("pattern required")
    before = SavedSearch.objects.filter(user_id=user_id).count()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM search_savedsearch WHERE user_id = " + str(user_id) + " AND name LIKE '%" + pattern + "%'")
    after = SavedSearch.objects.filter(user_id=user_id).count()
    messages.success(request, "Removed %d saved searches" % (before - after))
    return redirect("admin:search_savedsearch_changelist")""",
[("""WHERE user_id = " + str(user_id) + " AND name LIKE '%" + pattern + "%'")""", """WHERE user_id = %s AND name LIKE %s", [user_id, "%" + pattern + "%"])""")], "django_orm"),
]

ROWS += [
("u262", """Return users who hold any of the given role names, ordered by email.""", "hard_positive",
"""def users_with_roles(conn, role_names):
    parts = []
    for role in role_names:
        parts.append("'" + role + "'")
    listing = ",".join(parts)
    query = "SELECT u.id, u.email, r.name FROM users u JOIN roles r ON r.id = u.role_id WHERE r.name IN (" + listing + ") ORDER BY u.email"
    rows = conn.execute(query).fetchall()
    return [{"id": r[0], "email": r[1], "role": r[2]} for r in rows]""",
[("""parts.append("'" + role + "'")""", """parts.append("?")"""),
 ("""conn.execute(query)""", """conn.execute(query, list(role_names))""")], "sqlite3"),

("u263", """Return the most popular active courses ranked by a column the caller picks, through the shared repository object.""", "hard_positive",
"""def top_courses(self, sort_by, limit):
    sql = "SELECT code, title, enrolled, rating FROM courses WHERE active = true ORDER BY " + sort_by + " DESC LIMIT " + str(int(limit))
    rows = self.repo.query(sql)
    courses = []
    for code, title, enrolled, rating in rows:
        courses.append({"code": code, "title": title, "enrolled": enrolled, "rating": rating})
    self.log.info("top courses by %s", sort_by)
    self.last_ranking = courses
    return courses""",
[("""ORDER BY " + sort_by + " DESC""", """ORDER BY " + ("rating" if sort_by == "rating" else "enrolled") + " DESC""")], "psycopg2"),

("u264", """Total the sales of each product in a region for one year, optionally restricted to a list of products.""", "hard_positive",
"""def regional_revenue(conn, region, year, products):
    template = "SELECT product, SUM(amount) FROM sales WHERE region = '{region}' AND YEAR(sold_on) = {year}{extra} GROUP BY product"
    extra = ""
    if products:
        names = ", ".join("'" + p + "'" for p in products)
        extra = " AND product IN (" + names + ")"
    sql = template.format(region=region, year=year, extra=extra)
    rows = run_query(conn, sql)
    totals = {}
    for product, amount in rows:
        totals[product] = float(amount)
    return totals""",
[("""region = '{region}' AND YEAR(sold_on) = {year}{extra}""", """region = %s AND YEAR(sold_on) = %s{extra}"""),
 ("""        names = ", ".join("'" + p + "'" for p in products)
        extra = " AND product IN (" + names + ")\"""", """        extra = " AND product IN (" + ", ".join(["%s"] * len(products)) + ")\""""),
 ("""    sql = template.format(region=region, year=year, extra=extra)""", """    sql = template.format(extra=extra)
    params = [region, int(year)] + list(products or [])"""),
 ("""run_query(conn, sql)""", """run_query(conn, sql, params)""")], "mysql"),

("u265", """Find campsite pitches at a site, optionally in one area, under a maximum nightly price, or only the ones still free.""", "hard_positive",
"""def find_pitches(self, site_id, area=None, max_price=None, free_only=False):
    sql = f"SELECT id, area, label, nightly_price FROM pitches WHERE site_id = {int(site_id)}"
    if area:
        sql += f" AND area = '{area}'"
    if max_price:
        sql += f" AND nightly_price <= {max_price}"
    if free_only:
        sql += " AND booked = 0"
    sql += " ORDER BY nightly_price, area"
    with self.engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
    return [dict(row._mapping) for row in rows]""",
[("""    sql = f"SELECT id, area, label, nightly_price FROM pitches WHERE site_id = {int(site_id)}\"""", """    sql = "SELECT id, area, label, nightly_price FROM pitches WHERE site_id = :site_id"
    params = {"site_id": site_id}"""),
 ("""        sql += f" AND area = '{area}'\"""", """        sql += " AND area = :area"
        params["area"] = area"""),
 ("""        sql += f" AND nightly_price <= {max_price}\"""", """        sql += " AND nightly_price <= :max_price"
        params["max_price"] = float(max_price)"""),
 ("""conn.execute(text(sql))""", """conn.execute(text(sql), params)""")], "sqlalchemy"),

("u266", """Search seed bank lots by any of several attributes with a caller-chosen sort column and direction, 25 lots per page.""", "hard_positive",
"""def search_seed_lots(conn, criteria, sort="species", direction="asc", page=1):
    columns = {"species": "species", "origin": "origin_country", "year": "harvest_year", "grade": "grade"}
    conditions = []
    for name, value in criteria.items():
        column = columns.get(name)
        if column is None:
            continue
        if name == "year":
            conditions.append(column + " = " + str(value))
        else:
            conditions.append(column + " LIKE '%" + str(value) + "%'")
    where = ""
    if conditions:
        where = " WHERE " + " AND ".join(conditions)
    order = columns.get(sort, "species")
    sql = "SELECT lot_no, species, origin_country, harvest_year, grade FROM seed_lots" + where + " ORDER BY " + order + " " + direction + " LIMIT 25 OFFSET " + str((page - 1) * 25)
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    lots = []
    for lot_no, species, origin, year, grade in rows:
        lots.append({"lot": lot_no, "species": species, "origin": origin, "year": year, "grade": grade})
    return lots""",
[("""    conditions = []
""", """    conditions = []
    params = []
"""),
 ("""            conditions.append(column + " = " + str(value))""", """            conditions.append(column + " = %s")
            params.append(int(value))"""),
 ("""            conditions.append(column + " LIKE '%" + str(value) + "%'")""", """            conditions.append(column + " LIKE %s")
            params.append("%" + str(value) + "%")"""),
 ("""" ORDER BY " + order + " " + direction + " LIMIT""", """" ORDER BY " + order + " " + ("DESC" if direction == "desc" else "ASC") + " LIMIT"""),
 ("""cur.execute(sql)""", """cur.execute(sql, params)""")], "psycopg2"),

("u267", """Count new accounts per month for a plan over the last several months, using a query template filled in before execution.""", "hard_positive",
"""def monthly_signups(self, plan, months_back):
    sql = "SELECT to_char(created_at, 'YYYY-MM') AS month, COUNT(*) FROM accounts_account WHERE plan = '{plan}' AND created_at >= NOW() - INTERVAL '{n} months' GROUP BY month ORDER BY month"
    sql = sql.replace("{plan}", plan).replace("{n}", str(months_back))
    with self.using_cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
    result = {}
    for month, count in rows:
        result[month] = count
    self.last_report = result
    return result""",
[("""plan = '{plan}' AND created_at >= NOW() - INTERVAL '{n} months'""", """plan = %s AND created_at >= NOW() - (%s * INTERVAL '1 month')"""),
 ("""    sql = sql.replace("{plan}", plan).replace("{n}", str(months_back))""", """    params = [plan, int(months_back)]"""),
 ("""cursor.execute(sql)""", """cursor.execute(sql, params)""")], "django_orm"),

("u268", """Async season summary for a football league: matches, wins, draws, goals, top scorers and cards, filtered by any allowed combination of season, round, venue and referee.""", "hard_positive",
"""async def season_summary(db, filters, top_n=5):
    allowed = {"season": "m.season", "round": "m.round_no", "venue": "m.venue", "referee": "m.referee"}
    conditions = []
    for name, value in filters.items():
        column = allowed.get(name)
        if column is None:
            continue
        if isinstance(value, (list, tuple)):
            joined = ", ".join("'" + str(v) + "'" for v in value)
            conditions.append(column + " IN (" + joined + ")")
        else:
            conditions.append(column + " = '" + str(value) + "'")
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    match_sql = "SELECT m.id, m.home, m.away, m.home_goals, m.away_goals FROM matches m" + where + " ORDER BY m.played_on"
    async with db.execute(match_sql) as cursor:
        matches = await cursor.fetchall()
    scorer_sql = (
        "SELECT g.player, COUNT(*) FROM goals g JOIN matches m ON m.id = g.match_id"
        + where
        + " GROUP BY g.player ORDER BY COUNT(*) DESC LIMIT " + str(int(top_n))
    )
    async with db.execute(scorer_sql) as cursor:
        scorers = await cursor.fetchall()
    card_sql = "SELECT c.color, COUNT(*) FROM cards c JOIN matches m ON m.id = c.match_id" + where + " GROUP BY c.color"
    async with db.execute(card_sql) as cursor:
        cards = dict(await cursor.fetchall())
    home_wins = 0
    away_wins = 0
    draws = 0
    goals = 0
    for match_id, home, away, home_goals, away_goals in matches:
        goals += home_goals + away_goals
        if home_goals > away_goals:
            home_wins += 1
        elif away_goals > home_goals:
            away_wins += 1
        else:
            draws += 1
    played = len(matches)
    average = goals / played if played else 0
    return {
        "played": played,
        "home_wins": home_wins,
        "away_wins": away_wins,
        "draws": draws,
        "goals": goals,
        "average_goals": round(average, 2),
        "top_scorers": [{"player": p, "goals": g} for p, g in scorers],
        "cards": cards,
    }""",
[("""    conditions = []
""", """    conditions = []
    params = []
"""),
 ("""            joined = ", ".join("'" + str(v) + "'" for v in value)
            conditions.append(column + " IN (" + joined + ")")""", """            conditions.append(column + " IN (" + ", ".join("?" for _ in value) + ")")
            params.extend(value)"""),
 ("""            conditions.append(column + " = '" + str(value) + "'")""", """            conditions.append(column + " = ?")
            params.append(value)"""),
 ("""db.execute(match_sql)""", """db.execute(match_sql, params)"""),
 ("""db.execute(scorer_sql)""", """db.execute(scorer_sql, params)"""),
 ("""db.execute(card_sql)""", """db.execute(card_sql, params)""")], "other"),

("u269", """Look up a tenant by name and return its id, name and plan, or None when the name is not acceptable.""", "hard_positive",
"""def lookup_tenant(conn, name):
    for char in ("'", ";", "--", "/*"):
        if char in name:
            return None
    cur = conn.cursor()
    cur.execute("SELECT id, name, plan FROM tenants WHERE name = '" + name + "'")
    row = cur.fetchone()
    cur.close()
    return row""",
[("""WHERE name = '" + name + "'")""", """WHERE name = %s", (name,))""")], "mysql"),

("u270", """List exhibits of a museum hall sorted by title, year or hall, capped at a given number of rows.""", "hard_negative",
"""def list_exhibits(conn, hall, sort, limit):
    orders = {"title": "title", "year": "acquired_year", "hall": "hall"}
    order_column = orders.get(sort, "title")
    rows = conn.execute(
        f"SELECT id, title, hall, acquired_year FROM exhibits WHERE hall = ? ORDER BY {order_column} LIMIT {int(limit)}",
        (hall,),
    ).fetchall()
    return [{"id": r[0], "title": r[1], "hall": r[2], "year": r[3]} for r in rows]""", "", "sqlite3"),

("u271", """Stamp a list of wine bottles as checked by an inspector and return how many were updated.""", "hard_negative",
"""def mark_bottles_checked(conn, bottle_ids, inspector):
    if not bottle_ids:
        return 0
    marks = ", ".join(["%s"] * len(bottle_ids))
    with conn.cursor() as cur:
        cur.execute("UPDATE bottles SET checked_by = %s, checked_at = NOW() WHERE id IN (" + marks + ")", [inspector] + list(bottle_ids))
        updated = cur.rowcount
    conn.commit()
    return updated""", "", "psycopg2"),

("u272", """Admin endpoint that deletes old rows from one of three housekeeping tables chosen by name in the URL.""", "hard_negative",
"""@app.route("/admin/purge/<kind>", methods=["POST"])
@admin_required
def purge_old(kind):
    tables = {"logs": "audit_logs", "sessions": "web_sessions", "drafts": "post_drafts"}
    table = tables.get(kind)
    if table is None:
        abort(404)
    days = int(request.form.get("days", 30))
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM " + table + " WHERE created_at < NOW() - INTERVAL %s DAY", (days,))
    mysql.connection.commit()
    removed = cur.rowcount
    cur.close()
    return jsonify({"kind": kind, "removed": removed})""", "", "mysql"),

("u273", """Compute the minimum, maximum and an equal-width histogram of a numeric column of a table after checking both names against the database schema.""", "hard_negative",
"""def column_stats(engine, table_name, column_name, buckets=10):
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        raise ValueError("unknown table")
    known = {col["name"] for col in inspector.get_columns(table_name)}
    if column_name not in known:
        raise ValueError("unknown column")
    preparer = engine.dialect.identifier_preparer
    table = preparer.quote(table_name)
    column = preparer.quote(column_name)
    with engine.connect() as conn:
        low, high, count = conn.execute(text(f"SELECT MIN({column}), MAX({column}), COUNT({column}) FROM {table}")).one()
        if count == 0 or low == high:
            return {"count": count, "min": low, "max": high, "buckets": []}
        width = (high - low) / buckets
        result = []
        for index in range(buckets):
            start = low + index * width
            end = start + width
            hits = conn.execute(
                text(f"SELECT COUNT(*) FROM {table} WHERE {column} >= :start AND {column} < :end"),
                {"start": start, "end": end},
            ).scalar()
            result.append({"start": start, "end": end, "count": hits})
    return {"count": count, "min": low, "max": high, "buckets": result}""", "", "sqlalchemy"),

("u274", """Return one page of selected columns from a registered table, ordered by a column of the caller's choice, with the total row count.""", "hard_negative",
"""def fetch_page(self, table, columns, order_by, page, per_page=25):
    if table not in self.allowed_tables:
        raise ValueError("table not available")
    known = self.allowed_tables[table]
    for name in list(columns) + [order_by]:
        if name not in known:
            raise ValueError("unknown column: " + name)
    query = sql.SQL("SELECT {cols} FROM {tbl} ORDER BY {order} LIMIT %s OFFSET %s").format(
        cols=sql.SQL(", ").join(sql.Identifier(c) for c in columns),
        tbl=sql.Identifier(table),
        order=sql.Identifier(order_by),
    )
    offset = max(int(page) - 1, 0) * per_page
    with self.conn.cursor() as cur:
        cur.execute(query, (per_page, offset))
        rows = cur.fetchall()
        cur.execute(sql.SQL("SELECT COUNT(*) FROM {tbl}").format(tbl=sql.Identifier(table)))
        total = cur.fetchone()[0]
    return {
        "table": table,
        "page": int(page),
        "total": total,
        "rows": [dict(zip(columns, row)) for row in rows],
    }""", "", "psycopg2"),

("u275", """Django JSON view searching club members by name with a chosen sort column and a limit capped at one hundred.""", "hard_negative",
"""def search_members(request):
    sort_map = {"name": "full_name", "joined": "joined_on", "city": "city"}
    sort_col = sort_map.get(request.GET.get("sort"), "full_name")
    term = request.GET.get("q", "")
    limit = min(int(request.GET.get("limit", 25)), 100)
    sql = "SELECT id, full_name, city FROM clubs_member WHERE full_name LIKE %s ORDER BY " + sort_col + " LIMIT %s"
    with connection.cursor() as cursor:
        cursor.execute(sql, ["%" + term + "%", limit])
        rows = cursor.fetchall()
    return JsonResponse({"members": [{"id": r[0], "name": r[1], "city": r[2]} for r in rows]})""", "", "django_orm"),

("u276", """Edit a marketplace listing owned by the caller: apply only editable fields, replace its tags and write an audit row, all in one transaction, then return the updated listing.""", "hard_negative",
"""async def patch_listing(pool, listing_id, owner_id, changes, tags=None):
    editable = {
        "title": "title",
        "summary": "summary_text",
        "price": "price_cents",
        "currency": "currency_code",
        "status": "status",
        "category": "category_id",
    }
    statuses = ("draft", "published", "archived")
    assignments = []
    values = []
    for field, value in changes.items():
        column = editable.get(field)
        if column is None:
            raise ValueError("field cannot be edited: " + field)
        if field == "status" and value not in statuses:
            raise ValueError("bad status")
        if field == "price":
            value = int(round(float(value) * 100))
        values.append(value)
        assignments.append(column + " = $" + str(len(values)))
    if not assignments and tags is None:
        return None
    async with pool.acquire() as conn:
        async with conn.transaction():
            current = await conn.fetchrow("SELECT id, owner_id FROM listings WHERE id = $1 FOR UPDATE", listing_id)
            if current is None:
                raise LookupError("listing not found")
            if current["owner_id"] != owner_id:
                raise PermissionError("not the owner")
            if assignments:
                values.append(listing_id)
                query = "UPDATE listings SET " + ", ".join(assignments) + ", updated_at = NOW() WHERE id = $" + str(len(values))
                await conn.execute(query, *values)
            if tags is not None:
                await conn.execute("DELETE FROM listing_tags WHERE listing_id = $1", listing_id)
                for tag in sorted(set(tags)):
                    await conn.execute("INSERT INTO listing_tags (listing_id, tag) VALUES ($1, $2)", listing_id, tag.lower())
            await conn.execute(
                "INSERT INTO listing_audit (listing_id, actor_id, fields) VALUES ($1, $2, $3)",
                listing_id,
                owner_id,
                ",".join(sorted(changes)),
            )
            row = await conn.fetchrow("SELECT id, title, summary_text, price_cents, currency_code, status FROM listings WHERE id = $1", listing_id)
    return {
        "id": row["id"],
        "title": row["title"],
        "summary": row["summary_text"],
        "price": row["price_cents"] / 100,
        "currency": row["currency_code"],
        "status": row["status"],
    }""", "", "other"),

("u277", """Move stock of a part between two warehouse bins in a single transaction, recording the move and returning what remains in the source bin.""", "safe_db",
"""def transfer_stock(conn, sku, from_bin, to_bin, quantity):
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT quantity FROM bin_stock WHERE sku = %s AND bin = %s FOR UPDATE", (sku, from_bin))
            row = cur.fetchone()
            if row is None or row[0] < quantity:
                raise ValueError("not enough stock in source bin")
            cur.execute("UPDATE bin_stock SET quantity = quantity - %s WHERE sku = %s AND bin = %s", (quantity, sku, from_bin))
            cur.execute(
                "INSERT INTO bin_stock (sku, bin, quantity) VALUES (%s, %s, %s) "
                "ON CONFLICT (sku, bin) DO UPDATE SET quantity = bin_stock.quantity + EXCLUDED.quantity",
                (sku, to_bin, quantity),
            )
            cur.execute(
                "INSERT INTO stock_moves (sku, from_bin, to_bin, quantity, moved_at) VALUES (%s, %s, %s, %s, NOW())",
                (sku, from_bin, to_bin, quantity),
            )
            cur.execute("SELECT quantity FROM bin_stock WHERE sku = %s AND bin = %s", (sku, from_bin))
            remaining = cur.fetchone()[0]
    return {"sku": sku, "moved": quantity, "remaining_in_source": remaining}""", "", "psycopg2"),
]
