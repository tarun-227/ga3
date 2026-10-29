ROWS = [
("u201", """List the members assigned to a named gym trainer, with the date each one joined.""", "normal",
"""def members_for_trainer(conn, trainer_name):
    query = f"SELECT m.id, m.full_name, m.joined_on FROM members m JOIN trainers t ON t.id = m.trainer_id WHERE t.name = '{trainer_name}' ORDER BY m.joined_on"
    rows = conn.execute(query).fetchall()
    result = []
    for member_id, full_name, joined_on in rows:
        result.append({"id": member_id, "name": full_name, "joined": joined_on})
    return result""",
[("""query = f"SELECT m.id""", """query = "SELECT m.id"""),
 ("""WHERE t.name = '{trainer_name}' ORDER""", """WHERE t.name = ? ORDER"""),
 ("""conn.execute(query)""", """conn.execute(query, (trainer_name,))""")], "sqlite3"),

("u202", """Change the monthly price of a subscription plan identified by its plan code and report the new price.""", "normal",
"""def set_plan_price(self, plan_code, new_price):
    with self.conn.cursor() as cur:
        cur.execute("UPDATE plans SET monthly_price = " + str(new_price) + " WHERE code = '" + plan_code + "'")
        if cur.rowcount == 0:
            raise KeyError(plan_code)
    self.conn.commit()
    self.plan_cache.pop(plan_code, None)
    return new_price""",
[("""cur.execute("UPDATE plans SET monthly_price = " + str(new_price) + " WHERE code = '" + plan_code + "'")""",
  """params = (new_price, plan_code)
        cur.execute("UPDATE plans SET monthly_price = %s WHERE code = %s", params)""")], "psycopg2"),

("u203", """HTTP endpoint that removes a track from a playlist by title and returns how many rows were removed.""", "normal",
"""@app.route("/playlists/<int:playlist_id>/tracks", methods=["DELETE"])
def remove_track(playlist_id):
    title = request.args.get("title", "")
    stmt = "DELETE FROM playlist_tracks WHERE playlist_id = {} AND title = '{}'".format(playlist_id, title)
    try:
        result = db.session.execute(text(stmt))
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "delete failed"}), 500
    return jsonify({"removed": result.rowcount})""",
[("""playlist_id = {} AND title = '{}'".format(playlist_id, title)""", """playlist_id = :pid AND title = :title\""""),
 ("""db.session.execute(text(stmt))""", """db.session.execute(text(stmt), {"pid": playlist_id, "title": title})""")], "sqlalchemy"),

("u204", """Store a batch of weather readings for one station, one row per reading, and return the number stored.""", "normal",
"""def add_readings(conn, station_id, readings):
    cur = conn.cursor()
    inserted = 0
    for ts, temp, humidity in readings:
        cur.execute(f"INSERT INTO weather_readings (station_id, taken_at, temperature, humidity) VALUES ({station_id}, '{ts}', {temp}, {humidity})")
        inserted += 1
    conn.commit()
    return inserted""",
[("""cur.execute(f"INSERT INTO weather_readings (station_id, taken_at, temperature, humidity) VALUES ({station_id}, '{ts}', {temp}, {humidity})")""",
  """cur.execute("INSERT INTO weather_readings (station_id, taken_at, temperature, humidity) VALUES (%s, %s, %s, %s)", (station_id, ts, temp, humidity))""")], "mysql"),

("u205", """Read a text file of usernames, one per line, and delete each listed account unless it is an administrator.""", "normal",
"""def remove_listed_users(conn, path):
    with open(path) as handle:
        names = [line.strip() for line in handle if line.strip()]
    removed = 0
    for name in names:
        cur = conn.execute("DELETE FROM accounts WHERE username = '" + name + "' AND role != 'admin'")
        removed += cur.rowcount
    conn.commit()
    return removed""",
[("""conn.execute("DELETE FROM accounts WHERE username = '" + name + "' AND role != 'admin'")""",
  """conn.execute("DELETE FROM accounts WHERE username = ? AND role != 'admin'", (name,))""")], "sqlite3"),

("u206", """Django view that sets the stock quantity of a catalogue item from a posted form and answers with JSON.""", "normal",
"""@require_POST
def update_stock_level(request, sku):
    quantity = request.POST.get("quantity", "0")
    if not sku:
        return HttpResponseBadRequest("missing sku")
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE catalog_stock SET quantity = {quantity} WHERE sku = '{sku}'")
    return JsonResponse({"sku": sku, "quantity": quantity})""",
[("""cursor.execute(f"UPDATE catalog_stock SET quantity = {quantity} WHERE sku = '{sku}'")""",
  """cursor.execute("UPDATE catalog_stock SET quantity = %s WHERE sku = %s", [int(quantity), sku])""")], "django_orm"),

("u207", """Return the bookings of a rental car in a given calendar year together with the length of each rental in days.""", "normal",
"""async def bookings_for_vehicle(pool, plate, year):
    query = "SELECT id, renter, starts_at, ends_at FROM rentals WHERE plate = '" + plate + "' AND EXTRACT(YEAR FROM starts_at) = " + str(year) + " ORDER BY starts_at"
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
    bookings = []
    for row in rows:
        days = (row["ends_at"] - row["starts_at"]).days
        bookings.append({"id": row["id"], "renter": row["renter"], "days": days})
    return bookings""",
[("""query = "SELECT id, renter, starts_at, ends_at FROM rentals WHERE plate = '" + plate + "' AND EXTRACT(YEAR FROM starts_at) = " + str(year) + " ORDER BY starts_at\"""",
  """query = "SELECT id, renter, starts_at, ends_at FROM rentals WHERE plate = $1 AND EXTRACT(YEAR FROM starts_at) = $2 ORDER BY starts_at\""""),
 ("""conn.fetch(query)""", """conn.fetch(query, plate, int(year))""")], "other"),

("u208", """Bottle route that searches football clubs by part of their name and returns at most twenty-five of them.""", "normal",
"""@route("/clubs/search")
def search_clubs():
    term = request.query.get("q", "").strip()
    if len(term) < 2:
        return {"clubs": []}
    rows = db.execute("SELECT name, city, founded FROM clubs WHERE name LIKE '%" + term + "%' ORDER BY name LIMIT 25").fetchall()
    return {"clubs": [{"name": r[0], "city": r[1], "founded": r[2]} for r in rows]}""",
[("""LIKE '%" + term + "%' ORDER""", """LIKE ? ORDER"""),
 ("""LIMIT 25").fetchall()""", """LIMIT 25", ("%" + term + "%",)).fetchall()""")], "sqlite3"),

("u209", """Fetch several insurance policies by id and return their number, holder and premium as a list of dictionaries.""", "normal",
"""def fetch_policies(conn, policy_ids):
    id_list = ",".join(str(pid) for pid in policy_ids)
    with conn.cursor() as cur:
        cur.execute(f"SELECT number, holder, premium FROM policies WHERE id IN ({id_list}) ORDER BY number")
        rows = cur.fetchall()
    return [{"number": n, "holder": h, "premium": float(p)} for n, h, p in rows]""",
[("""str(pid) for pid""", """str(int(pid)) for pid""")], "psycopg2"),

("u210", """Rename a bus route and drop its entry from the in-memory cache.""", "normal",
"""def rename_route(self, route_id, new_label):
    stmt = "UPDATE bus_routes SET label = '{0}' WHERE id = {1}".format(new_label, route_id)
    with self.engine.begin() as conn:
        conn.execute(text(stmt))
    self.cache.pop(route_id, None)
    self.log.info("route renamed")
    return new_label""",
[("""label = '{0}' WHERE id = {1}".format(new_label, route_id)""", """label = :label WHERE id = :rid\""""),
 ("""conn.execute(text(stmt))""", """conn.execute(text(stmt), {"label": new_label, "rid": route_id})""")], "sqlalchemy"),
]

ROWS += [
("u211", """FastAPI endpoint listing beehives with a caller-chosen sort column and row limit.""", "normal",
"""@router.get("/hives")
def list_hives(sort: str = "name", limit: int = 20):
    query = "SELECT id, name, apiary, queen_year, last_inspection FROM hives ORDER BY " + sort + " LIMIT " + str(limit)
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="query failed")
    hives = []
    for r in rows:
        hives.append({"id": r[0], "name": r[1], "apiary": r[2], "queen_year": r[3], "last_inspection": r[4]})
    return hives""",
[("""    query = "SELECT id, name, apiary""", """    sort = sort if sort in ("name", "apiary") else "name"
    query = "SELECT id, name, apiary""")], "psycopg2"),

("u212", """Tornado handler returning a vendor's purchase orders in a given status as JSON.""", "normal",
"""def get_vendor_orders(self, vendor_id):
    status = self.get_argument("status", "open")
    cur = self.application.db.cursor()
    cur.execute("SELECT id, total, due_date FROM purchase_orders WHERE vendor_id = " + vendor_id + " AND status = '" + status + "'")
    orders = cur.fetchall()
    cur.close()
    self.write({"orders": [{"id": o[0], "total": float(o[1]), "due": str(o[2])} for o in orders]})""",
[("""vendor_id = " + vendor_id + " AND status = '" + status + "'")""", """vendor_id = %s AND status = %s", (vendor_id, status))""")], "mysql"),

("u213", """Load museum exhibits from a CSV file into the database and return how many were added.""", "normal",
"""def load_museum_exhibits(db_path, csv_path):
    conn = sqlite3.connect(db_path)
    count = 0
    with open(csv_path, newline="") as handle:
        reader = csv.DictReader(handle)
        for record in reader:
            conn.execute("INSERT INTO exhibits (title, hall, acquired) VALUES ('{}', '{}', '{}')".format(record["title"], record["hall"], record["acquired"]))
            count += 1
    conn.commit()
    conn.close()
    return count""",
[("""VALUES ('{}', '{}', '{}')".format(record["title"], record["hall"], record["acquired"]))""", """VALUES (?, ?, ?)", (record["title"], record["hall"], record["acquired"]))""")], "sqlite3"),

("u214", """JSON endpoint that updates a member's email address and phone number.""", "normal",
"""@app.route("/members/<int:member_id>/contact", methods=["PUT"])
@login_required
def update_contact(member_id):
    body = request.get_json(force=True)
    email = body.get("email", "")
    phone = body.get("phone", "")
    if not email and not phone:
        return jsonify({"error": "nothing to update"}), 400
    if email and "@" not in email:
        return jsonify({"error": "bad email"}), 422
    if phone and len(phone) < 7:
        return jsonify({"error": "bad phone"}), 422
    if current_user.id != member_id and not current_user.is_staff:
        return jsonify({"error": "forbidden"}), 403
    stmt = f"UPDATE members SET email = '{email}', phone = '{phone}' WHERE id = {member_id}"
    try:
        db.session.execute(text(stmt))
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "update failed"}), 500
    audit.info("contact updated for member %s", member_id)
    return jsonify({"id": member_id, "email": email, "phone": phone})""",
[("""stmt = f"UPDATE members SET email = '{email}', phone = '{phone}' WHERE id = {member_id}\"""", """stmt = "UPDATE members SET email = :email, phone = :phone WHERE id = :member_id\""""),
 ("""db.session.execute(text(stmt))""", """db.session.execute(text(stmt), {"email": email, "phone": phone, "member_id": member_id})""")], "sqlalchemy"),

("u215", """Delete permits that expired more than a given number of days ago and return how many were removed.""", "normal",
"""def purge_expired_permits(conn, older_than_days):
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM permits WHERE expires_on < CURRENT_DATE - INTERVAL '%s days' AND status = 'expired'" % older_than_days)
        deleted = cur.rowcount
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
    return deleted""",
[("""% older_than_days)""", """% int(older_than_days))""")], "psycopg2"),

("u216", """Search recipes whose title or tags contain a keyword, one page at a time, ordered by cooking time.""", "normal",
"""def search_recipes(self, keyword, page=1, per_page=10):
    offset = (page - 1) * per_page
    sql = "SELECT id, title, minutes FROM recipes WHERE title LIKE '%{}%' OR tags LIKE '%{}%' ORDER BY minutes LIMIT {} OFFSET {}".format(keyword, keyword, per_page, offset)
    rows = self.conn.execute(sql).fetchall()
    return [{"id": r[0], "title": r[1], "minutes": r[2]} for r in rows]""",
[("""LIKE '%{}%' OR tags LIKE '%{}%' ORDER BY minutes LIMIT {} OFFSET {}".format(keyword, keyword, per_page, offset)""", """LIKE ? OR tags LIKE ? ORDER BY minutes LIMIT ? OFFSET ?\""""),
 ("""self.conn.execute(sql)""", """self.conn.execute(sql, ("%" + keyword + "%", "%" + keyword + "%", per_page, offset))""")], "sqlite3"),

("u217", """Record a parcel scan at a depot and update the parcel's last known depot.""", "normal",
"""def record_shipment_scan(conn, parcel_code, depot, scanned_at):
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO scans (parcel_code, depot, scanned_at) VALUES ('{parcel_code}', '{depot}', '{scanned_at}')")
    cursor.execute(f"UPDATE parcels SET last_depot = '{depot}' WHERE code = '{parcel_code}'")
    conn.commit()
    updated = cursor.rowcount
    cursor.close()
    return updated""",
[("""cursor.execute(f"INSERT INTO scans (parcel_code, depot, scanned_at) VALUES ('{parcel_code}', '{depot}', '{scanned_at}')")""", """cursor.execute("INSERT INTO scans (parcel_code, depot, scanned_at) VALUES (?, ?, ?)", (parcel_code, depot, scanned_at))"""),
 ("""cursor.execute(f"UPDATE parcels SET last_depot = '{depot}' WHERE code = '{parcel_code}'")""", """cursor.execute("UPDATE parcels SET last_depot = ? WHERE code = ?", (depot, parcel_code))""")], "other"),

("u218", """Build text lines for rentals in the region named in the environment that are late by at least the configured number of days.""", "normal",
"""def pending_rentals_report(conn):
    region = os.environ.get("REPORT_REGION", "north")
    min_days = os.environ.get("MIN_OVERDUE_DAYS", "3")
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT r.id, c.name, r.due_date, DATEDIFF(NOW(), r.due_date) AS late_days FROM rentals r JOIN customers c ON c.id = r.customer_id WHERE c.region = '" + region + "' AND DATEDIFF(NOW(), r.due_date) >= " + min_days)
    rows = cur.fetchall()
    cur.close()
    lines = []
    for row in rows:
        lines.append("{}: {} ({} days late)".format(row["id"], row["name"], row["late_days"]))
    return lines""",
[("""WHERE c.region = '" + region + "' AND DATEDIFF(NOW(), r.due_date) >= " + min_days)""", """WHERE c.region = %s AND DATEDIFF(NOW(), r.due_date) >= %s", (region, int(min_days)))""")], "mysql"),

("u219", """Cancel every booking of a guest that is still in the given state.""", "normal",
"""def cancel_pending(self, guest_id, status):
    with self.Session() as session:
        session.execute(text(f"DELETE FROM bookings WHERE guest_id = {guest_id} AND status = '{status}'"))
        session.commit()
    self.events.append(("cancelled", guest_id))
    return len(self.events)""",
[("""session.execute(text(f"DELETE FROM bookings WHERE guest_id = {guest_id} AND status = '{status}'"))""", """session.query(Booking).filter(Booking.guest_id == guest_id, Booking.status == status).delete()""")], "sqlalchemy"),

("u220", """Pyramid view that counts bike rides grouped by a column the caller picks and returns the groups with their average duration.""", "normal",
"""@view_config(route_name="stats", renderer="json")
def ride_stats(request):
    group_by = request.params.get("group_by", "station")
    cur = request.db.cursor()
    cur.execute(f"SELECT {group_by}, COUNT(*), AVG(duration_min) FROM bike_rides GROUP BY {group_by} ORDER BY COUNT(*) DESC")
    rows = cur.fetchall()
    cur.close()
    return [{"key": row[0], "rides": row[1], "avg_minutes": float(row[2])} for row in rows]""",
[("""group_by = request.params.get("group_by", "station")""", """group_by = {"station": "station", "type": "bike_type"}.get(request.params.get("group_by"), "station")""")], "psycopg2"),

("u221", """Delete a review through the API, but only if the reviewer named in the request header wrote it.""", "normal",
"""@app.route("/reviews/<review_id>", methods=["DELETE"])
def delete_review(review_id):
    reviewer = request.headers.get("X-Reviewer", "")
    row = get_db().execute("SELECT reviewer FROM reviews WHERE id = " + review_id).fetchone()
    if row is None:
        abort(404)
    if row[0] != reviewer:
        abort(403)
    get_db().execute("DELETE FROM reviews WHERE id = " + review_id)
    get_db().commit()
    return "", 204""",
[("""WHERE id = " + review_id).fetchone()""", """WHERE id = ?", (review_id,)).fetchone()"""),
 ("""WHERE id = " + review_id)
    get_db().commit()""", """WHERE id = ?", (review_id,))
    get_db().commit()""")], "sqlite3"),

("u222", """Django view returning the top scorers of a league as JSON, using a raw query.""", "normal",
"""def top_scorers(request):
    league = request.GET.get("league", "premier")
    limit = request.GET.get("limit", "10")
    players = Player.objects.raw("SELECT * FROM league_player WHERE league_slug = '%s' ORDER BY goals DESC LIMIT %s" % (league, limit))
    data = [{"name": p.name, "goals": p.goals} for p in players]
    return JsonResponse({"players": data})""",
[("""WHERE league_slug = '%s' ORDER BY goals DESC LIMIT %s" % (league, limit))""", """WHERE league_slug = %s ORDER BY goals DESC LIMIT %s", [league, int(limit)])""")], "django_orm"),

("u223", """Async endpoint that adds an episode to a podcast and returns its new id.""", "normal",
"""@router.post("/podcasts/{podcast_id}/episodes")
async def add_episode(podcast_id: int, title: str, duration_sec: int, published: str):
    if duration_sec <= 0:
        raise HTTPException(status_code=422, detail="bad duration")
    if not title.strip():
        raise HTTPException(status_code=422, detail="missing title")
    if podcast_id <= 0:
        raise HTTPException(status_code=404, detail="unknown podcast")
    if len(published) != 10:
        raise HTTPException(status_code=422, detail="bad publication date")
    query = f"INSERT INTO episodes (podcast_id, title, duration_sec, published) VALUES ({podcast_id}, '{title}', {duration_sec}, '{published}')"
    episode_id = await database.execute(query)
    minutes = round(duration_sec / 60, 1)
    log.info("episode %s added to podcast %s", episode_id, podcast_id)
    return {"id": episode_id, "title": title, "minutes": minutes}""",
[("""query = f"INSERT INTO episodes (podcast_id, title, duration_sec, published) VALUES ({podcast_id}, '{title}', {duration_sec}, '{published}')\"""", """query = "INSERT INTO episodes (podcast_id, title, duration_sec, published) VALUES (:podcast_id, :title, :duration_sec, :published)\""""),
 ("""database.execute(query)""", """database.execute(query, values={"podcast_id": podcast_id, "title": title, "duration_sec": duration_sec, "published": published})""")], "other"),

("u224", """Move a booking to another seat on the same flight inside a transaction, returning False if the seat is taken.""", "normal",
"""def transfer_seat(self, booking_id, new_seat):
    if not new_seat or len(new_seat) > 4:
        raise ValueError("bad seat")
    current = self.conn.execute("SELECT seat FROM bookings WHERE id = {}".format(booking_id)).fetchone()
    if current is None:
        raise LookupError(booking_id)
    if current[0] == new_seat:
        return True
    try:
        self.conn.execute("BEGIN")
        taken = self.conn.execute("SELECT 1 FROM bookings WHERE seat = '{}' AND flight = (SELECT flight FROM bookings WHERE id = {})".format(new_seat, booking_id)).fetchone()
        if taken:
            self.conn.execute("ROLLBACK")
            return False
        self.conn.execute("UPDATE bookings SET seat = '{}' WHERE id = {}".format(new_seat, booking_id))
        self.conn.execute("COMMIT")
        self.history.append((booking_id, current[0], new_seat))
    except sqlite3.Error:
        self.conn.execute("ROLLBACK")
        raise
    return True""",
[("""WHERE id = {}".format(booking_id)).fetchone()""", """WHERE id = ?", (booking_id,)).fetchone()"""),
 ("""WHERE seat = '{}' AND flight = (SELECT flight FROM bookings WHERE id = {})".format(new_seat, booking_id))""", """WHERE seat = ? AND flight = (SELECT flight FROM bookings WHERE id = ?)", (new_seat, booking_id))"""),
 ("""SET seat = '{}' WHERE id = {}".format(new_seat, booking_id))""", """SET seat = ? WHERE id = ?", (new_seat, booking_id))""")], "sqlite3"),
]

ROWS += [
("u225", """Search insurance claims by any combination of allowed fields and an opened-date range, returning one page of results with totals.""", "hard_positive",
"""def search_claims(conn, filters, page=1, page_size=25):
    allowed = ("policy_no", "status", "adjuster", "region", "kind")
    clauses = []
    for key, value in filters.items():
        if key not in allowed:
            continue
        if isinstance(value, (list, tuple)):
            options = ["'" + str(v) + "'" for v in value]
            clauses.append(key + " IN (" + ", ".join(options) + ")")
        else:
            clauses.append(key + " = '" + str(value) + "'")
    opened_from = filters.get("opened_from")
    opened_to = filters.get("opened_to")
    if opened_from:
        clauses.append("opened_on >= '" + opened_from + "'")
    if opened_to:
        clauses.append("opened_on <= '" + opened_to + "'")
    where = " AND ".join(clauses) if clauses else "1=1"
    offset = max(page - 1, 0) * page_size
    sql = "SELECT claim_no, policy_no, status, amount, opened_on FROM claims WHERE " + where + " ORDER BY opened_on DESC LIMIT %d OFFSET %d" % (page_size, offset)
    count_sql = "SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM claims WHERE " + where
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
        cur.execute(count_sql)
        total, total_amount = cur.fetchone()
    claims = []
    for claim_no, policy_no, status, amount, opened_on in rows:
        claims.append({
            "claim_no": claim_no,
            "policy_no": policy_no,
            "status": status,
            "amount": float(amount),
            "opened_on": opened_on.isoformat(),
        })
    pages = (total + page_size - 1) // page_size
    return {
        "total": total,
        "total_amount": float(total_amount),
        "page": page,
        "pages": pages,
        "claims": claims,
    }""",
[("""    clauses = []
""", """    clauses = []
    params = []
"""),
 ("""            options = ["'" + str(v) + "'" for v in value]
            clauses.append(key + " IN (" + ", ".join(options) + ")")""", """            clauses.append(key + " IN (" + ", ".join(["%s"] * len(value)) + ")")
            params.extend(value)"""),
 ("""            clauses.append(key + " = '" + str(value) + "'")""", """            clauses.append(key + " = %s")
            params.append(value)"""),
 ("""        clauses.append("opened_on >= '" + opened_from + "'")""", """        clauses.append("opened_on >= %s")
        params.append(opened_from)"""),
 ("""        clauses.append("opened_on <= '" + opened_to + "'")""", """        clauses.append("opened_on <= %s")
        params.append(opened_to)"""),
 ("""cur.execute(sql)""", """cur.execute(sql, params)"""),
 ("""cur.execute(count_sql)""", """cur.execute(count_sql, params)""")], "psycopg2"),

("u226", """Give every unassigned task of a project to the project's owner and return how many tasks were reassigned.""", "hard_positive",
"""def reassign_orphaned_tasks(self, project_id):
    cur = self.conn.cursor()
    cur.execute("SELECT owner FROM projects WHERE id = ?", (project_id,))
    row = cur.fetchone()
    if row is None:
        return 0
    owner = row[0]
    cur.execute("SELECT id FROM tasks WHERE project_id = ? AND assignee IS NULL", (project_id,))
    task_ids = [r[0] for r in cur.fetchall()]
    for task_id in task_ids:
        cur.execute("UPDATE tasks SET assignee = '" + owner + "' WHERE id = ?", (task_id,))
    self.conn.commit()
    return len(task_ids)""",
[("""SET assignee = '" + owner + "' WHERE id = ?", (task_id,))""", """SET assignee = ? WHERE id = ?", (owner, task_id))""")], "sqlite3"),

("u227", """Return twelve monthly totals of an account for a year, optionally limited to some entry kinds, using the shared database wrapper.""", "hard_positive",
"""def monthly_totals(self, account, year, kinds=None):
    sql = "SELECT MONTH(posted_on) AS m, SUM(amount) FROM entries WHERE account = '" + account + "' AND YEAR(posted_on) = " + str(year)
    if kinds:
        quoted = ["'" + k + "'" for k in kinds]
        sql += " AND kind IN (" + ",".join(quoted) + ")"
    sql += " GROUP BY m ORDER BY m"
    rows = self.db.run(sql)
    totals = {m: 0 for m in range(1, 13)}
    for month, amount in rows:
        totals[month] = float(amount)
    return totals""",
[("""account = '" + account + "' AND YEAR(posted_on) = " + str(year)""", """account = %s AND YEAR(posted_on) = %s"
    params = [account, int(year)]"""),
 ("""        quoted = ["'" + k + "'" for k in kinds]
        sql += " AND kind IN (" + ",".join(quoted) + ")\"""", """        sql += " AND kind IN (" + ",".join(["%s"] * len(kinds)) + ")"
        params.extend(kinds)"""),
 ("""self.db.run(sql)""", """self.db.run(sql, params)""")], "mysql"),

("u228", """Run one of the stored report templates for a region and quarter and return the rows as dictionaries.""", "hard_positive",
"""def run_quarter_report(session, report_name, region, quarter):
    template = REPORT_TEMPLATES.get(report_name)
    if template is None:
        raise KeyError(report_name)
    if not region or not quarter:
        raise ValueError("region and quarter are required")
    sql = template.replace(":region_value", "'" + region + "'").replace(":quarter_value", "'" + quarter + "'")
    result = session.execute(text(sql))
    columns = list(result.keys())
    rows = []
    for record in result.fetchall():
        item = dict(zip(columns, record))
        for key, value in item.items():
            if isinstance(value, Decimal):
                item[key] = float(value)
        rows.append(item)
    totals = {}
    for column in columns:
        values = [r[column] for r in rows if isinstance(r[column], (int, float))]
        if values:
            totals[column] = sum(values)
    return {
        "report": report_name,
        "region": region,
        "quarter": quarter,
        "rows": rows,
        "totals": totals,
    }""",
[("""    sql = template.replace(":region_value", "'" + region + "'").replace(":quarter_value", "'" + quarter + "'")
    result = session.execute(text(sql))""", """    sql = template
    result = session.execute(text(sql), {"region_value": region, "quarter_value": quarter})""")], "sqlalchemy"),

("u229", """Export up to a given number of rows from a named device table ordered by a column the caller chooses.""", "hard_positive",
"""def export_table_rows(conn, table, order_by, limit=100):
    if limit < 1 or limit > 1000:
        raise ValueError("limit out of range")
    blocked = (";", "--", "/*", "'")
    for part in (table, order_by):
        if any(token in part for token in blocked):
            raise ValueError("invalid name")
    sql = "SELECT * FROM " + table + " ORDER BY " + order_by + " LIMIT " + str(int(limit))
    with conn.cursor() as cur:
        cur.execute(sql)
        names = [d[0] for d in cur.description]
        rows = cur.fetchall()
    result = []
    for row in rows:
        record = dict(zip(names, row))
        for key, value in record.items():
            if isinstance(value, datetime):
                record[key] = value.isoformat()
        result.append(record)
    meta = {"table": table, "order_by": order_by, "count": len(result)}
    return {"meta": meta, "rows": result}""",
[("""    blocked = (";", "--", "/*", "'")
    for part in (table, order_by):
        if any(token in part for token in blocked):
            raise ValueError("invalid name")""", """    if table not in ("devices", "stations") or order_by not in ("id", "name", "installed_on"):
        raise ValueError("invalid name")""")], "psycopg2"),

("u230", """Django view that returns active marketplace listings whose title contains any of the words from the search box.""", "hard_positive",
"""def find_listings(request):
    terms = request.GET.get("q", "").split()
    conditions = []
    for term in terms:
        conditions.append("title LIKE '%" + term + "%'")
    where = " OR ".join(conditions) or "1=1"
    sql = "SELECT id, title, price FROM market_listing WHERE (" + where + ") AND active = 1 ORDER BY price LIMIT 50"
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
    return JsonResponse({"results": [{"id": r[0], "title": r[1], "price": str(r[2])} for r in rows]})""",
[("""    conditions = []
""", """    conditions = []
    params = []
"""),
 ("""        conditions.append("title LIKE '%" + term + "%'")""", """        conditions.append("title LIKE %s")
        params.append("%" + term + "%")"""),
 ("""cursor.execute(sql)""", """cursor.execute(sql, params)""")], "django_orm"),

("u231", """Async helper that lists work shifts, optionally for one employee and one day, up to a row limit.""", "hard_positive",
"""async def list_shifts(db, employee_id=None, day=None, limit=50):
    sql = "SELECT id, employee_id, day, start_time, end_time FROM shifts"
    clauses = []
    if employee_id:
        clauses.append("employee_id = " + str(employee_id))
    if day:
        clauses.append("day = '" + day + "'")
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY day, start_time LIMIT " + str(int(limit))
    async with db.execute(sql) as cursor:
        rows = await cursor.fetchall()
    return [{"id": r[0], "employee": r[1], "day": r[2], "start": r[3], "end": r[4]} for r in rows]""",
[("""    clauses = []
""", """    clauses = []
    params = []
"""),
 ("""        clauses.append("employee_id = " + str(employee_id))""", """        clauses.append("employee_id = ?")
        params.append(employee_id)"""),
 ("""        clauses.append("day = '" + day + "'")""", """        clauses.append("day = ?")
        params.append(day)"""),
 ("""db.execute(sql)""", """db.execute(sql, params)""")], "other"),

("u232", """Look up the audience segment of an email campaign, collect its active subscribers and record how many greetings were produced.""", "hard_positive",
"""def send_followups(conn, campaign_id):
    cur = conn.cursor()
    cur.execute("SELECT segment FROM campaigns WHERE id = %s", (campaign_id,))
    row = cur.fetchone()
    if not row:
        return []
    segment = row[0]
    if not segment:
        return []
    cur.execute("SELECT email, name FROM subscribers WHERE segment = '" + segment + "' AND unsubscribed = 0")
    recipients = cur.fetchall()
    if not recipients:
        return []
    sent = []
    seen = set()
    for email, name in recipients:
        if email in seen:
            continue
        seen.add(email)
        sent.append({"to": email, "greeting": "Hello " + name})
    cur.execute("UPDATE campaigns SET sent_count = %s WHERE id = %s", (len(sent), campaign_id))
    conn.commit()
    return sent""",
[("""WHERE segment = '" + segment + "' AND unsubscribed = 0")""", """WHERE segment = %s AND unsubscribed = 0", (segment,))""")], "mysql"),

("u233", """Move closed rows of a table into its archive table in batches and return the number of rows moved.""", "hard_positive",
"""def archive_rows(session, source_table, cutoff, batch=500):
    if batch < 1 or batch > 5000:
        raise ValueError("batch out of range")
    started = time.monotonic()
    target = source_table + "_archive"
    moved = 0
    while True:
        ids = session.execute(
            text(f"SELECT id FROM {source_table} WHERE closed_on < :cutoff ORDER BY id LIMIT :batch"),
            {"cutoff": cutoff, "batch": batch},
        ).scalars().all()
        if not ids:
            break
        marks = ", ".join(str(i) for i in ids)
        session.execute(text(f"INSERT INTO {target} SELECT * FROM {source_table} WHERE id IN ({marks})"))
        session.execute(text(f"DELETE FROM {source_table} WHERE id IN ({marks})"))
        session.commit()
        moved += len(ids)
        log.info("archived %s rows from %s", len(ids), source_table)
    log.info("archive of %s finished in %.1fs", source_table, time.monotonic() - started)
    return moved""",
[("""    target = source_table + "_archive\"""", """    if source_table not in ("tickets", "invoices", "sessions"):
        raise ValueError(source_table)
    target = source_table + "_archive\"""")], "sqlalchemy"),

("u234", """Count a user's notes, tasks or files with an id at or above a minimum, choosing the table by kind.""", "hard_negative",
"""def count_records(conn, kind, owner_id, min_id):
    tables = {"notes": "user_notes", "tasks": "user_tasks", "files": "user_files"}
    table = tables.get(kind)
    if table is None:
        raise ValueError(kind)
    owner_id = int(owner_id)
    query = f"SELECT COUNT(*) FROM {table} WHERE owner_id = {owner_id} AND id >= ?"
    row = conn.execute(query, (min_id,)).fetchone()
    return {"kind": kind, "count": row[0]}""", "", "sqlite3"),

("u235", """Fetch users by a list of ids in ascending or descending name order.""", "hard_negative",
"""def users_with_ids(conn, ids, order="asc"):
    if not ids:
        return []
    direction = "DESC" if order == "desc" else "ASC"
    marks = ", ".join(["%s"] * len(ids))
    query = "SELECT id, name, email FROM users WHERE id IN (" + marks + ") ORDER BY name " + direction
    with conn.cursor() as cur:
        cur.execute(query, list(ids))
        rows = cur.fetchall()
    return [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]""", "", "psycopg2"),

("u236", """Update only the profile fields that appear in a change dictionary and return the number of rows updated.""", "hard_negative",
"""def update_profile_fields(self, user_id, changes):
    if not isinstance(changes, dict):
        raise TypeError("changes must be a dict")
    if len(changes) > 10:
        raise ValueError("too many fields")
    user_id = int(user_id)
    columns = {"display_name": "display_name", "bio": "bio_text", "city": "home_city", "website": "site_url"}
    limits = {"display_name": 60, "bio": 500, "city": 80, "website": 200}
    assignments = []
    values = []
    for field, value in changes.items():
        column = columns.get(field)
        if column is None:
            raise ValueError("unknown field: " + field)
        if isinstance(value, str) and len(value) > limits[field]:
            raise ValueError(field + " too long")
        assignments.append(column + " = %s")
        values.append(value)
    if not assignments:
        return 0
    values.append(user_id)
    sql = "UPDATE profiles SET " + ", ".join(assignments) + " WHERE user_id = %s"
    cur = self.conn.cursor()
    try:
        cur.execute(sql, values)
        self.conn.commit()
        updated = cur.rowcount
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    cur = self.conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT display_name, bio_text, home_city, site_url FROM profiles WHERE user_id = %s", (user_id,))
        profile = cur.fetchone()
    finally:
        cur.close()
    if profile is not None:
        self.cache[user_id] = profile
        self.log.info("profile %s refreshed", user_id)
    return updated""", "", "mysql"),

("u237", """List electric vehicles with an optional maker filter, a chosen sort field and direction, and a capped row limit.""", "hard_negative",
"""@app.route("/api/vehicles")
def list_vehicles():
    sort_options = {"year": "model_year", "range": "range_km", "price": "list_price"}
    sort_key = sort_options.get(request.args.get("sort", "price"), "list_price")
    direction = "DESC" if request.args.get("dir") == "desc" else "ASC"
    try:
        limit = min(int(request.args.get("limit", 20)), 100)
    except ValueError:
        return jsonify({"error": "bad limit"}), 400
    maker = request.args.get("maker")
    sql = "SELECT id, maker, model, model_year, range_km, list_price FROM vehicles"
    params = {"limit": limit}
    if maker:
        sql += " WHERE maker = :maker"
        params["maker"] = maker
    sql += f" ORDER BY {sort_key} {direction} LIMIT :limit"
    rows = db.session.execute(text(sql), params).fetchall()
    return jsonify([dict(r._mapping) for r in rows])""", "", "sqlalchemy"),

("u238", """Build an attendance report grouped by team, site or role with a chosen set of metrics, a date range and a minimum number of hours.""", "hard_negative",
"""def build_attendance_report(conn, group, columns, since, until, min_hours):
    groups = {"team": "team_name", "site": "site_code", "role": "role_title"}
    metrics = {
        "hours": "SUM(hours_worked)",
        "days": "COUNT(DISTINCT work_date)",
        "late": "SUM(CASE WHEN late_minutes > 0 THEN 1 ELSE 0 END)",
        "overtime": "SUM(MAX(hours_worked - 8, 0))",
    }
    group_column = groups.get(group)
    if group_column is None:
        raise ValueError("unknown grouping: " + str(group))
    selected = []
    for name in columns:
        expression = metrics.get(name)
        if expression is None:
            raise ValueError("unknown metric: " + str(name))
        selected.append(expression + " AS " + name)
    if not selected:
        raise ValueError("no metrics requested")
    threshold = float(min_hours)
    sql = (
        "SELECT " + group_column + ", " + ", ".join(selected)
        + " FROM attendance WHERE work_date BETWEEN ? AND ?"
        + " GROUP BY " + group_column
        + " HAVING SUM(hours_worked) >= " + repr(threshold)
        + " ORDER BY " + group_column
    )
    cursor = conn.execute(sql, (since, until))
    headers = [d[0] for d in cursor.description]
    rows = []
    for record in cursor.fetchall():
        rows.append(dict(zip(headers, record)))
    totals = {}
    for name in columns:
        totals[name] = sum(row[name] or 0 for row in rows)
    ranked = sorted(rows, key=lambda row: row.get(columns[0]) or 0, reverse=True)
    for position, row in enumerate(ranked, start=1):
        row["rank"] = position
    grand = totals.get(columns[0]) or 0
    for row in ranked:
        share = (row.get(columns[0]) or 0) / grand if grand else 0
        row["share"] = round(share * 100, 1)
    header = [group_column] + list(columns) + ["rank", "share"]
    lines = [",".join(header)]
    for row in ranked:
        lines.append(",".join(str(row.get(h, "")) for h in header))
    return {"group": group, "since": since, "until": until, "rows": ranked, "totals": totals, "csv": chr(10).join(lines)}""", "", "sqlite3"),

("u239", """Check a bike out to a member at a station inside one transaction, refusing members who are suspended or bikes that are already out.""", "safe_db",
"""def checkout_bike(session, member_id, bike_id, station_id):
    member = session.execute(
        text("SELECT id, status FROM members WHERE id = :member_id"),
        {"member_id": member_id},
    ).first()
    if member is None or member.status != "active":
        raise PermissionError("member cannot rent")
    bike = session.execute(
        text("SELECT id, station_id, state FROM bikes WHERE id = :bike_id FOR UPDATE"),
        {"bike_id": bike_id},
    ).first()
    if bike is None or bike.state != "docked" or bike.station_id != station_id:
        raise LookupError("bike not available at this station")
    session.execute(
        text("UPDATE bikes SET state = 'out', station_id = NULL WHERE id = :bike_id"),
        {"bike_id": bike_id},
    )
    session.execute(
        text("INSERT INTO rides (member_id, bike_id, start_station, started_at) VALUES (:member_id, :bike_id, :station_id, NOW())"),
        {"member_id": member_id, "bike_id": bike_id, "station_id": station_id},
    )
    session.commit()
    return {"member": member_id, "bike": bike_id, "station": station_id}""", "", "sqlalchemy"),
]
