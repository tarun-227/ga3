ROWS = [
("u315", """Delete the scores of a game that are older than a number of days and return how many were removed.""", "normal",
"""def clear_old_scores(self, game, keep_days):
    cur = self.conn.cursor()
    cur.execute(f"DELETE FROM arcade_scores WHERE game = '{game}' AND played_on < date('now', '-{keep_days} days')")
    removed = cur.rowcount
    self.conn.commit()
    self.log.info("cleared %s scores of %s", removed, game)
    return removed""",
[("""cur.execute(f"DELETE FROM arcade_scores WHERE game = '{game}' AND played_on < date('now', '-{keep_days} days')")""", """cur.execute("DELETE FROM arcade_scores WHERE game = ? AND played_on < date('now', ?)", (game, "-" + str(int(keep_days)) + " days"))""")], "sqlite3"),

("u316", """Guestbook endpoint that stores a visitor's name and message with the current time and redirects back to the page.""", "normal",
"""@app.route("/guestbook", methods=["POST"])
def sign_guestbook():
    name = request.form.get("name", "anonymous").strip()
    message = request.form.get("message", "").strip()
    if not message:
        return redirect(url_for("guestbook"))
    db = get_db()
    db.execute(f"INSERT INTO guestbook (name, message, signed_at) VALUES ('{name}', '{message}', datetime('now'))")
    db.commit()
    return redirect(url_for("guestbook"))""",
[("""db.execute(f"INSERT INTO guestbook (name, message, signed_at) VALUES ('{name}', '{message}', datetime('now'))")""", """db.execute("INSERT INTO guestbook (name, message, signed_at) VALUES (?, ?, datetime('now'))", (name, message))""")], "sqlite3"),

("u317", """Set the status of a ringed bird in the sanctuary register and note who changed it.""", "normal",
"""def set_bird_status(self, ring_code, status, keeper):
    with self.conn.cursor() as cur:
        cur.execute("UPDATE birds SET status = '" + status + "', updated_by = '" + keeper + "' WHERE ring_code = '" + ring_code + "'")
        if cur.rowcount == 0:
            raise KeyError(ring_code)
    self.conn.commit()
    self.history.append((ring_code, status, keeper))
    self.log.info("bird %s is now %s", ring_code, status)
    return status""",
[("""SET status = '" + status + "', updated_by = '" + keeper + "' WHERE ring_code = '" + ring_code + "'")""", """SET status = %s, updated_by = %s WHERE ring_code = %s", (status, keeper, ring_code))""")], "psycopg2"),

("u318", """Book a tattoo artist for a time slot and return the id of the booking.""", "normal",
"""def add_tattoo_booking(self, artist, client, slot, deposit):
    if deposit < 0:
        raise ValueError("deposit cannot be negative")
    cur = self.conn.cursor()
    cur.execute("INSERT INTO bookings (artist, client, slot, deposit) VALUES ('{}', '{}', '{}', {})".format(artist, client, slot, deposit))
    self.conn.commit()
    booking_id = cur.lastrowid
    cur.close()
    return booking_id""",
[("""VALUES ('{}', '{}', '{}', {})".format(artist, client, slot, deposit))""", """VALUES (%s, %s, %s, %s)", (artist, client, slot, deposit))""")], "mysql"),

("u319", """Remove a customer's saved payment method of a given type from the laundromat account.""", "normal",
"""def remove_payment_method(self, customer_id, kind):
    with self.Session() as session:
        session.execute(text(f"DELETE FROM payment_methods WHERE customer_id = {customer_id} AND kind = '{kind}'"))
        session.commit()
    self.cache.pop(customer_id, None)
    self.log.info("payment method %s removed", kind)
    return True""",
[("""text(f"DELETE FROM payment_methods WHERE customer_id = {customer_id} AND kind = '{kind}'"))""", """text("DELETE FROM payment_methods WHERE customer_id = :customer_id AND kind = :kind"), {"customer_id": customer_id, "kind": kind})""")], "sqlalchemy"),

("u320", """Bottle route that changes the opening hours of a tea shop branch.""", "normal",
"""@route("/branches/<branch_id>/hours", method="POST")
def set_branch_hours(branch_id):
    opens = request.forms.get("opens", "09:00")
    closes = request.forms.get("closes", "18:00")
    db.execute("UPDATE branches SET opens = '%s', closes = '%s' WHERE id = %s" % (opens, closes, branch_id))
    db.commit()
    response.status = 204
    return ""
""", 
[("""opens = '%s', closes = '%s' WHERE id = %s" % (opens, closes, branch_id))""", """opens = ?, closes = ? WHERE id = ?", (opens, closes, branch_id))""")], "sqlite3"),

("u321", """Delete a comma separated list of session ids supplied by the caller and return the number of deleted rows.""", "normal",
"""def drop_sessions(conn, ids_csv):
    if not ids_csv:
        return 0
    cur = conn.execute("DELETE FROM user_sessions WHERE id IN (" + ids_csv + ")")
    conn.commit()
    log.info("dropped %s sessions", cur.rowcount)
    return cur.rowcount""",
[("""IN (" + ids_csv + ")")""", """IN (" + ",".join(str(int(part)) for part in ids_csv.split(",")) + ")")""")], "sqlite3"),

("u322", """FastAPI endpoint that deletes the bookings of an escape room on a given date and returns the count.""", "normal",
"""@router.delete("/rooms/{room}/bookings")
def cancel_room_bookings(room: str, day: str):
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM room_bookings WHERE room = '{room}' AND play_date = '{day}'")
        removed = cur.rowcount
    conn.commit()
    if removed == 0:
        raise HTTPException(status_code=404, detail="nothing to cancel")
    return {"room": room, "day": day, "removed": removed}""",
[("""cur.execute(f"DELETE FROM room_bookings WHERE room = '{room}' AND play_date = '{day}'")""", """cur.execute("DELETE FROM room_bookings WHERE room = %s AND play_date = %s", (room, day))""")], "psycopg2"),

("u323", """Mark an order from the comic store as shipped with its tracking code, rolling back if the order does not exist.""", "normal",
"""def ship_comic_order(self, order_id, tracking):
    try:
        cur = self.conn.execute("UPDATE comic_orders SET status = 'shipped', tracking = '" + tracking + "' WHERE id = " + str(order_id))
        if cur.rowcount != 1:
            raise LookupError(order_id)
        self.conn.execute("INSERT INTO order_log (order_id, note) VALUES (" + str(order_id) + ", 'shipped with " + tracking + "')")
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    self.notify(order_id, tracking)
    return tracking""",
[("""tracking = '" + tracking + "' WHERE id = " + str(order_id))""", """tracking = ? WHERE id = ?", (tracking, order_id))"""),
 ("""VALUES (" + str(order_id) + ", 'shipped with " + tracking + "')")""", """VALUES (?, ?)", (order_id, "shipped with " + tracking))""")], "sqlite3"),

("u324", """Async method that stores a batch of drone flight logs in one transaction and returns how many were stored.""", "normal",
"""async def save_flights(self, drone_id, flights):
    stored = 0
    try:
        for flight in flights:
            await self.db.execute(f"INSERT INTO flights (drone_id, started_at, minutes, battery_end) VALUES ({drone_id}, '{flight['started_at']}', {flight['minutes']}, {flight['battery_end']})")
            stored += 1
        await self.db.commit()
    except Exception:
        await self.db.rollback()
        raise
    self.stats["flights"] += stored
    return stored""",
[("""await self.db.execute(f"INSERT INTO flights (drone_id, started_at, minutes, battery_end) VALUES ({drone_id}, '{flight['started_at']}', {flight['minutes']}, {flight['battery_end']})")""", """await self.db.execute("INSERT INTO flights (drone_id, started_at, minutes, battery_end) VALUES (?, ?, ?, ?)", (drone_id, flight["started_at"], flight["minutes"], flight["battery_end"]))""")], "other"),

("u325", """Tornado handler that records a new lighthouse inspection from form fields.""", "normal",
"""def post(self):
    lighthouse = self.get_argument("lighthouse")
    inspector = self.get_argument("inspector")
    result = self.get_argument("result", "pass")
    notes = self.get_argument("notes", "")
    cur = self.settings["db"].cursor()
    cur.execute("INSERT INTO inspections (lighthouse, inspector, result, notes, inspected_on) VALUES ('" + lighthouse + "', '" + inspector + "', '" + result + "', '" + notes + "', CURDATE())")
    self.settings["db"].commit()
    cur.close()
    self.set_status(201)
    self.finish({"lighthouse": lighthouse, "result": result})""",
[("""VALUES ('" + lighthouse + "', '" + inspector + "', '" + result + "', '" + notes + "', CURDATE())")""", """VALUES (%s, %s, %s, %s, CURDATE())", (lighthouse, inspector, result, notes))""")], "mysql"),

("u326", """Read board game stock changes from a file with one 'name,delta' line each and apply them to the shop's stock table.""", "normal",
"""def apply_stock_file(conn, path):
    applied = 0
    with open(path) as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            name, delta = line.rsplit(",", 1)
            conn.execute("UPDATE games SET stock = stock + {} WHERE name = '{}'".format(delta, name))
            applied += 1
    conn.commit()
    log.info("applied %s stock lines", applied)
    return applied""",
[("""stock = stock + {} WHERE name = '{}'".format(delta, name))""", """stock = stock + ? WHERE name = ?", (int(delta), name))""")], "sqlite3"),

("u327", """Delete the out-of-stock items of a category from a thrift shop's catalogue and clear the shop's cached catalogue.""", "normal",
"""def retire_shop_items(self, shop, category):
    with self.engine.begin() as conn:
        result = conn.execute(text(f"DELETE FROM shop_items WHERE shop = '{shop}' AND category = '{category}' AND stock = 0"))
    self.log.info("retired %s items from %s", result.rowcount, shop)
    self.catalog_cache.pop(shop, None)
    return result.rowcount""",
[("""text(f"DELETE FROM shop_items WHERE shop = '{shop}' AND category = '{category}' AND stock = 0"))""", """text("DELETE FROM shop_items WHERE shop = :shop AND category = :category AND stock = 0"), {"shop": shop, "category": category})""")], "sqlalchemy"),
]

ROWS += [
("u328", """Reserve seats at a planetarium show inside a transaction, applying an unused coupon if one is given, and return the price charged.""", "normal",
"""def reserve_show_seats(self, show_id, visitor, seats, coupon):
    if seats < 1 or seats > 8:
        raise ValueError("between 1 and 8 seats")
    cur = self.conn.cursor()
    try:
        cur.execute("BEGIN")
        cur.execute("SELECT capacity, booked, price FROM shows WHERE id = " + str(show_id))
        show = cur.fetchone()
        if show is None:
            raise LookupError(show_id)
        if show[1] + seats > show[0]:
            raise ValueError("not enough seats")
        price = show[2] * seats
        if coupon:
            cur.execute("SELECT percent FROM coupons WHERE code = '" + coupon + "' AND used = 0")
            found = cur.fetchone()
            if found:
                price = price * (100 - found[0]) / 100
                cur.execute("UPDATE coupons SET used = 1 WHERE code = '" + coupon + "'")
        cur.execute("INSERT INTO reservations (show_id, visitor, seats, price) VALUES (" + str(show_id) + ", '" + visitor + "', " + str(seats) + ", " + str(price) + ")")
        cur.execute("UPDATE shows SET booked = booked + " + str(seats) + " WHERE id = " + str(show_id))
        cur.execute("COMMIT")
    except Exception:
        cur.execute("ROLLBACK")
        raise
    return price""",
[("""FROM shows WHERE id = " + str(show_id))""", """FROM shows WHERE id = ?", (show_id,))"""),
 ("""WHERE code = '" + coupon + "' AND used = 0")""", """WHERE code = ? AND used = 0", (coupon,))"""),
 ("""SET used = 1 WHERE code = '" + coupon + "'")""", """SET used = 1 WHERE code = ?", (coupon,))"""),
 ("""VALUES (" + str(show_id) + ", '" + visitor + "', " + str(seats) + ", " + str(price) + ")")""", """VALUES (?, ?, ?, ?)", (show_id, visitor, seats, price))"""),
 ("""booked = booked + " + str(seats) + " WHERE id = " + str(show_id))""", """booked = booked + ? WHERE id = ?", (seats, show_id))""")], "sqlite3"),

("u329", """Add a part to a bike repair work order from the form, checking the part exists and is in stock, then reduce the stock.""", "normal",
"""@app.route("/workorders/<int:order_id>/parts", methods=["POST"])
@login_required
def add_work_order_part(order_id):
    part_no = request.form.get("part_no", "").strip()
    qty = request.form.get("qty", "1")
    note = request.form.get("note", "").strip()
    if not part_no:
        flash("Part number required")
        return redirect(url_for("work_order", order_id=order_id))
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, price, stock FROM parts WHERE part_no = '%s'" % part_no)
    part = cur.fetchone()
    if part is None:
        flash("Unknown part")
        cur.close()
        return redirect(url_for("work_order", order_id=order_id))
    if part[2] < int(qty):
        flash("Not enough in stock")
        cur.close()
        return redirect(url_for("work_order", order_id=order_id))
    cur.execute("INSERT INTO work_order_parts (order_id, part_id, qty, unit_price, note) VALUES (%s, %s, %s, %s, '%s')" % (order_id, part[0], int(qty), part[1], note))
    cur.execute("UPDATE parts SET stock = stock - %s WHERE id = %s" % (int(qty), part[0]))
    conn.commit()
    cur.close()
    flash("Part added")
    return redirect(url_for("work_order", order_id=order_id))""",
[("""WHERE part_no = '%s'" % part_no)""", """WHERE part_no = %s", (part_no,))"""),
 ("""VALUES (%s, %s, %s, %s, '%s')" % (order_id, part[0], int(qty), part[1], note))""", """VALUES (%s, %s, %s, %s, %s)", (order_id, part[0], int(qty), part[1], note))""")], "psycopg2"),

("u330", """Close the open tab of a table at the board game cafe, store the payment method and tip, free the table and return a plain text receipt.""", "normal",
"""def close_tab(self, table_no, payment_method, tip):
    cur = self.conn.cursor()
    cur.execute("SELECT id, opened_at FROM tabs WHERE table_no = %d AND closed_at IS NULL" % table_no)
    tab = cur.fetchone()
    if tab is None:
        raise LookupError("no open tab")
    tab_id = tab[0]
    cur.execute("SELECT item, qty, unit_price FROM tab_items WHERE tab_id = %d" % tab_id)
    items = cur.fetchall()
    subtotal = sum(qty * price for item, qty, price in items)
    if subtotal == 0:
        raise ValueError("empty tab")
    total = round(subtotal + tip, 2)
    cur.execute("UPDATE tabs SET closed_at = datetime('now'), payment_method = '%s', tip = %s, total = %s WHERE id = %d" % (payment_method, tip, total, tab_id))
    cur.execute("UPDATE tables SET occupied = 0 WHERE table_no = %d" % table_no)
    self.conn.commit()
    receipt = []
    for item, qty, price in items:
        receipt.append("%-20s %2d x %6.2f" % (item, qty, price))
    receipt.append("Total: %.2f" % total)
    return chr(10).join(receipt)""",
[("""payment_method = '%s', tip = %s, total = %s WHERE id = %d" % (payment_method, tip, total, tab_id))""", """payment_method = ?, tip = ?, total = ? WHERE id = ?", (payment_method, tip, total, tab_id))""")], "sqlite3"),

("u331", """Pyramid view that freezes a yoga membership for a number of weeks with a reason and pushes the expiry date forward.""", "normal",
"""@view_config(route_name="freeze_membership", request_method="POST", renderer="json")
def freeze_membership(request):
    member_id = request.matchdict["member_id"]
    weeks = request.json_body.get("weeks", 4)
    reason = request.json_body.get("reason", "")
    if weeks < 1 or weeks > 12:
        request.response.status = 422
        return {"error": "weeks must be between 1 and 12"}
    cur = request.db.cursor()
    cur.execute("SELECT status, expires_on FROM memberships WHERE member_id = " + member_id)
    row = cur.fetchone()
    if row is None:
        request.response.status = 404
        return {"error": "no membership"}
    if row[0] == "frozen":
        request.response.status = 409
        return {"error": "already frozen"}
    cur.execute("UPDATE memberships SET status = 'frozen', frozen_reason = '" + reason + "', expires_on = DATE_ADD(expires_on, INTERVAL " + str(weeks) + " WEEK) WHERE member_id = " + member_id)
    request.db.commit()
    cur.close()
    return {"member": member_id, "frozen_weeks": weeks}""",
[("""FROM memberships WHERE member_id = " + member_id)""", """FROM memberships WHERE member_id = %s", (member_id,))"""),
 ("""frozen_reason = '" + reason + "', expires_on = DATE_ADD(expires_on, INTERVAL " + str(weeks) + " WEEK) WHERE member_id = " + member_id)""", """frozen_reason = %s, expires_on = DATE_ADD(expires_on, INTERVAL %s WEEK) WHERE member_id = %s", (reason, weeks, member_id))""")], "mysql"),

("u332", """Add money to a ski lift pass inside a transaction, refusing blocked passes, and record who took the payment and how.""", "normal",
"""def top_up_pass(self, pass_code, amount, cashier, method):
    if amount <= 0:
        raise ValueError("amount must be positive")
    with self.engine.begin() as conn:
        row = conn.execute(text(f"SELECT id, balance, blocked FROM lift_passes WHERE code = '{pass_code}'")).first()
        if row is None:
            raise LookupError(pass_code)
        if row.blocked:
            raise PermissionError("pass is blocked")
        new_balance = row.balance + amount
        conn.execute(text(f"UPDATE lift_passes SET balance = {new_balance} WHERE id = {row.id}"))
        conn.execute(text(f"INSERT INTO pass_topups (pass_id, amount, cashier, method) VALUES ({row.id}, {amount}, '{cashier}', '{method}')"))
    self.log.info("pass %s topped up by %s", pass_code, amount)
    self.events.append(("topup", pass_code, amount))
    return new_balance""",
[("""text(f"SELECT id, balance, blocked FROM lift_passes WHERE code = '{pass_code}'"))""", """text("SELECT id, balance, blocked FROM lift_passes WHERE code = :code"), {"code": pass_code})"""),
 ("""text(f"INSERT INTO pass_topups (pass_id, amount, cashier, method) VALUES ({row.id}, {amount}, '{cashier}', '{method}')"))""", """text("INSERT INTO pass_topups (pass_id, amount, cashier, method) VALUES (:pass_id, :amount, :cashier, :method)"), {"pass_id": row.id, "amount": amount, "cashier": cashier, "method": method})""")], "sqlalchemy"),

("u333", """Import orchard harvest entries from a JSON file, skipping incomplete ones, and update each tree's last harvest date.""", "normal",
"""def import_harvest_log(db_path, json_path):
    with open(json_path) as handle:
        entries = json.load(handle)
    conn = sqlite3.connect(db_path)
    stored = 0
    problems = []
    try:
        for entry in entries:
            tree = entry.get("tree")
            kilos = entry.get("kilos")
            picked = entry.get("picked_on")
            if not tree or kilos is None or not picked:
                problems.append(entry)
                continue
            conn.execute("INSERT INTO harvests (tree, kilos, picked_on) VALUES ('%s', %s, '%s')" % (tree, kilos, picked))
            conn.execute("UPDATE trees SET last_harvest = '%s' WHERE label = '%s'" % (picked, tree))
            stored += 1
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()
    return {"stored": stored, "problems": len(problems)}""",
[("""VALUES ('%s', %s, '%s')" % (tree, kilos, picked))""", """VALUES (?, ?, ?)", (tree, kilos, picked))"""),
 ("""SET last_harvest = '%s' WHERE label = '%s'" % (picked, tree))""", """SET last_harvest = ? WHERE label = ?", (picked, tree))""")], "sqlite3"),

("u334", """Sanic endpoint that changes the delivery address, time window and card message of a florist order that has not been dispatched yet.""", "normal",
"""@bp.put("/orders/<order_id:int>/delivery")
async def set_delivery(request, order_id):
    body = request.json or {}
    address = body.get("address", "").strip()
    window = body.get("window", "morning")
    message = body.get("card_message", "")
    if not address:
        return json({"error": "address required"}, status=422)
    if window not in ("morning", "afternoon", "evening"):
        return json({"error": "bad window"}, status=422)
    pool = request.app.ctx.pool
    async with pool.acquire() as conn:
        order = await conn.fetchrow("SELECT id, status FROM florist_orders WHERE id = $1", order_id)
        if order is None:
            return json({"error": "unknown order"}, status=404)
        if order["status"] not in ("new", "confirmed"):
            return json({"error": "too late to change"}, status=409)
        await conn.execute("UPDATE florist_orders SET address = '" + address + "', window = '" + window + "', card_message = '" + message + "' WHERE id = " + str(order_id))
    return json({"order": order_id, "address": address, "window": window})""",
[("""SET address = '" + address + "', window = '" + window + "', card_message = '" + message + "' WHERE id = " + str(order_id))""", """SET address = $1, window = $2, card_message = $3 WHERE id = $4", address, window, message, order_id)""")], "other"),

("u335", """Find the cheapest free harbour berth that fits a vessel for a stay, register the vessel if it is new, price the stay with any extra services and store the allocation.""", "normal",
"""def allocate_berth(conn, vessel_name, length_m, draft_m, arrival, departure, services):
    if length_m <= 0 or draft_m <= 0:
        raise ValueError("dimensions must be positive")
    if departure <= arrival:
        raise ValueError("departure must be after arrival")
    vessel = conn.execute("SELECT id, owner, flag FROM vessels WHERE name = '" + vessel_name + "'").fetchone()
    if vessel is None:
        cur = conn.execute("INSERT INTO vessels (name, length_m, draft_m) VALUES ('" + vessel_name + "', " + str(length_m) + ", " + str(draft_m) + ")")
        vessel_id = cur.lastrowid
    else:
        vessel_id = vessel[0]
    candidates = conn.execute(
        "SELECT id, pier, max_length, max_draft, daily_rate FROM berths "
        "WHERE max_length >= ? AND max_draft >= ? ORDER BY daily_rate",
        (length_m, draft_m),
    ).fetchall()
    chosen = None
    for berth_id, pier, max_length, max_draft, rate in candidates:
        clash = conn.execute(
            "SELECT COUNT(*) FROM allocations WHERE berth_id = ? AND arrival < ? AND departure > ?",
            (berth_id, departure, arrival),
        ).fetchone()[0]
        if clash == 0:
            chosen = (berth_id, pier, rate)
            break
    if chosen is None:
        return None
    berth_id, pier, rate = chosen
    nights = max((date.fromisoformat(departure) - date.fromisoformat(arrival)).days, 1)
    cost = rate * nights
    extras = 0
    for service in services:
        row = conn.execute("SELECT price FROM harbor_services WHERE name = '" + service + "'").fetchone()
        if row is None:
            continue
        extras += row[0]
    total = cost + extras
    conn.execute("INSERT INTO allocations (berth_id, vessel_id, arrival, departure, total) VALUES (" + str(berth_id) + ", " + str(vessel_id) + ", '" + arrival + "', '" + departure + "', " + str(total) + ")")
    for service in services:
        conn.execute("INSERT INTO allocation_services (vessel_id, service, booked_on) VALUES (" + str(vessel_id) + ", '" + service + "', '" + arrival + "')")
    conn.commit()
    return {"berth": berth_id, "pier": pier, "nights": nights, "total": total}""",
[("""FROM vessels WHERE name = '" + vessel_name + "'")""", """FROM vessels WHERE name = ?", (vessel_name,))"""),
 ("""VALUES ('" + vessel_name + "', " + str(length_m) + ", " + str(draft_m) + ")")""", """VALUES (?, ?, ?)", (vessel_name, length_m, draft_m))"""),
 ("""FROM harbor_services WHERE name = '" + service + "'")""", """FROM harbor_services WHERE name = ?", (service,))"""),
 ("""VALUES (" + str(berth_id) + ", " + str(vessel_id) + ", '" + arrival + "', '" + departure + "', " + str(total) + ")")""", """VALUES (?, ?, ?, ?, ?)", (berth_id, vessel_id, arrival, departure, total))"""),
 ("""VALUES (" + str(vessel_id) + ", '" + service + "', '" + arrival + "')")""", """VALUES (?, ?, ?)", (vessel_id, service, arrival))""")], "sqlite3"),

("u336", """Place a tea shop order for pickup: find or create the customer by email, check stock for each line, apply loyalty points if asked, store the order and its lines and update stock and points in one transaction.""", "normal",
"""def place_tea_order(self, customer_email, lines, pickup_time, use_points):
    if not lines:
        raise ValueError("order is empty")
    cur = self.conn.cursor()
    try:
        cur.execute("SELECT id, points FROM tea_customers WHERE email = '{}'".format(customer_email))
        customer = cur.fetchone()
        if customer is None:
            cur.execute("INSERT INTO tea_customers (email, points) VALUES ('{}', 0) RETURNING id".format(customer_email))
            customer = (cur.fetchone()[0], 0)
        customer_id, points = customer
        subtotal = 0
        priced = []
        for sku, qty in lines:
            cur.execute("SELECT name, price, stock FROM teas WHERE sku = %s FOR UPDATE", (sku,))
            tea = cur.fetchone()
            if tea is None:
                raise LookupError(sku)
            if tea[2] < qty:
                raise ValueError("not enough " + tea[0])
            subtotal += tea[1] * qty
            priced.append((sku, qty, tea[1]))
        discount = 0
        if use_points:
            discount = min(points, int(subtotal))
        total = subtotal - discount
        cur.execute(
            "INSERT INTO tea_orders (customer_id, pickup_time, subtotal, discount, total) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (customer_id, pickup_time, subtotal, discount, total),
        )
        order_id = cur.fetchone()[0]
        for sku, qty, price in priced:
            cur.execute("INSERT INTO tea_order_lines (order_id, sku, qty, price) VALUES (%s, %s, %s, %s)", (order_id, sku, qty, price))
            cur.execute("UPDATE teas SET stock = stock - %s WHERE sku = %s", (qty, sku))
        earned = int(total)
        cur.execute("UPDATE tea_customers SET points = points - %s + %s WHERE id = %s", (discount, earned, customer_id))
        self.conn.commit()
    except Exception:
        self.conn.rollback()
        raise
    finally:
        cur.close()
    self.log.info("tea order %s placed for %s", order_id, customer_email)
    return {"order": order_id, "total": total, "points_earned": earned}""",
[("""WHERE email = '{}'".format(customer_email))""", """WHERE email = %s", (customer_email,))"""),
 ("""VALUES ('{}', 0) RETURNING id".format(customer_email))""", """VALUES (%s, 0) RETURNING id", (customer_email,))""")], "psycopg2"),
]

ROWS += [
("u337", """Return the cheapest tools in the lending shed ordered by a column the caller chooses.""", "hard_positive",
"""def cheapest_tools(conn, order_column, limit):
    sql = "SELECT id, name, daily_fee, condition FROM tools WHERE status = 'available' ORDER BY " + order_column + " LIMIT " + str(int(limit))
    rows = conn.execute(sql).fetchall()
    tools = []
    for tool_id, name, fee, condition in rows:
        tools.append({"id": tool_id, "name": name, "fee": fee, "condition": condition})
    log.info("listed %s tools by %s", len(tools), order_column)
    return tools""",
[("""ORDER BY " + order_column + " LIMIT""", """ORDER BY " + ("daily_fee" if order_column == "daily_fee" else "name") + " LIMIT""")], "sqlite3"),

("u338", """Insert a row into the pledges table from a dictionary of pledge fields, ignoring unknown keys.""", "hard_positive",
"""def store_pledge(conn, fields):
    known = ("donor", "amount", "campaign", "pledged_on")
    names = [key for key in known if key in fields]
    values = ["'" + str(fields[key]) + "'" for key in names]
    if not names:
        raise ValueError("no pledge fields")
    cur = conn.execute("INSERT INTO pledges (" + ", ".join(names) + ") VALUES (" + ", ".join(values) + ")")
    conn.commit()
    log.info("pledge %s stored", cur.lastrowid)
    return cur.lastrowid""",
[("""    values = ["'" + str(fields[key]) + "'" for key in names]""", """    values = [fields[key] for key in names]"""),
 ("""conn.execute("INSERT INTO pledges (" + ", ".join(names) + ") VALUES (" + ", ".join(values) + ")")""", """conn.execute("INSERT INTO pledges (" + ", ".join(names) + ") VALUES (" + ", ".join("?" for _ in names) + ")", values)""")], "sqlite3"),

("u339", """List open support cases for a customer, optionally filtered by priority and assignee, through the repository object.""", "hard_positive",
"""def open_cases(self, customer_id, priority=None, assignee=None):
    sql = "SELECT id, subject, priority, assignee FROM cases WHERE status = 'open' AND customer_id = " + str(int(customer_id))
    if priority:
        sql += " AND priority = '" + priority + "'"
    if assignee:
        sql += " AND assignee = '" + assignee + "'"
    sql += " ORDER BY opened_at DESC"
    rows = self.repo.run(sql)
    cases = [{"id": r[0], "subject": r[1], "priority": r[2], "assignee": r[3]} for r in rows]
    self.log.info("found %s open cases", len(cases))
    return cases""",
[("""    sql = "SELECT id, subject, priority, assignee FROM cases WHERE status = 'open' AND customer_id = " + str(int(customer_id))""", """    sql = "SELECT id, subject, priority, assignee FROM cases WHERE status = 'open' AND customer_id = %s"
    params = [customer_id]"""),
 ("""        sql += " AND priority = '" + priority + "'\"""", """        sql += " AND priority = %s"
        params.append(priority)"""),
 ("""        sql += " AND assignee = '" + assignee + "'\"""", """        sql += " AND assignee = %s"
        params.append(assignee)"""),
 ("""self.repo.run(sql)""", """self.repo.run(sql, params)""")], "psycopg2"),

("u340", """Find ski rental items whose description contains any of several words and return their ids and names.""", "hard_positive",
"""def find_rental_items(conn, words):
    conditions = []
    for word in words:
        conditions.append("description LIKE '%" + word + "%'")
    if not conditions:
        return []
    sql = "SELECT id, name FROM rental_items WHERE " + " OR ".join(conditions) + " ORDER BY name"
    rows = conn.execute(sql).fetchall()
    items = [{"id": row[0], "name": row[1]} for row in rows]
    log.info("%s items match %s words", len(items), len(words))
    return items""",
[("""        conditions.append("description LIKE '%" + word + "%'")""", """        conditions.append("description LIKE ?")"""),
 ("""conn.execute(sql).fetchall()""", """conn.execute(sql, ["%" + word + "%" for word in words]).fetchall()""")], "sqlite3"),

("u341", """Credit a referral bonus to the member who invited a new member, using the inviter code stored on the new member's record.""", "hard_positive",
"""def credit_referral_bonus(conn, new_member_id, bonus):
    row = conn.execute("SELECT inviter_code FROM members WHERE id = ?", (new_member_id,)).fetchone()
    if row is None or not row[0]:
        return False
    inviter_code = row[0]
    inviter = conn.execute("SELECT id, points FROM members WHERE referral_code = '" + inviter_code + "'").fetchone()
    if inviter is None:
        return False
    already = conn.execute(
        "SELECT COUNT(*) FROM referral_bonuses WHERE new_member_id = ? AND inviter_id = ?",
        (new_member_id, inviter[0]),
    ).fetchone()[0]
    if already:
        return False
    conn.execute("UPDATE members SET points = points + ? WHERE referral_code = '" + inviter_code + "'", (bonus,))
    conn.execute(
        "INSERT INTO referral_bonuses (new_member_id, inviter_id, bonus, note) VALUES (?, ?, ?, 'joined with code " + inviter_code + "')",
        (new_member_id, inviter[0], bonus),
    )
    conn.commit()
    log.info("credited %s points to %s", bonus, inviter[0])
    return True""",
[("""WHERE referral_code = '" + inviter_code + "'").fetchone()""", """WHERE referral_code = ?", (inviter_code,)).fetchone()"""),
 ("""WHERE referral_code = '" + inviter_code + "'", (bonus,))""", """WHERE referral_code = ?", (bonus, inviter_code))"""),
 ("""VALUES (?, ?, ?, 'joined with code " + inviter_code + "')",
        (new_member_id, inviter[0], bonus),""", """VALUES (?, ?, ?, ?)",
        (new_member_id, inviter[0], bonus, "joined with code " + inviter_code),""")], "sqlite3"),

("u342", """Show a cinema's screenings for a week using a query template that is filled in with the hall and genre before it runs.""", "hard_positive",
"""def weekly_screenings(self, hall, genre, week_start):
    template = "SELECT s.id, f.title, s.starts_at FROM screenings s JOIN films f ON f.id = s.film_id WHERE s.hall = '{hall}' AND f.genre = '{genre}' AND s.starts_at >= '{start}' AND s.starts_at < DATE_ADD('{start}', INTERVAL 7 DAY) ORDER BY s.starts_at"
    sql = template.format(hall=hall, genre=genre, start=week_start)
    cur = self.conn.cursor(dictionary=True)
    try:
        cur.execute(sql)
        rows = cur.fetchall()
    finally:
        cur.close()
    by_day = {}
    for row in rows:
        day = row["starts_at"].strftime("%Y-%m-%d")
        by_day.setdefault(day, []).append({"id": row["id"], "title": row["title"], "time": row["starts_at"].strftime("%H:%M")})
    for day in by_day:
        by_day[day].sort(key=lambda item: item["time"])
    self.log.info("%s days with screenings in hall %s", len(by_day), hall)
    return by_day""",
[("""WHERE s.hall = '{hall}' AND f.genre = '{genre}' AND s.starts_at >= '{start}' AND s.starts_at < DATE_ADD('{start}', INTERVAL 7 DAY)""", """WHERE s.hall = %s AND f.genre = %s AND s.starts_at >= %s AND s.starts_at < DATE_ADD(%s, INTERVAL 7 DAY)"""),
 ("""    sql = template.format(hall=hall, genre=genre, start=week_start)""", """    sql = template
    params = (hall, genre, week_start, week_start)"""),
 ("""cur.execute(sql)""", """cur.execute(sql, params)""")], "mysql"),

("u343", """Admin endpoint that deletes rows of a table named in the URL that match a status from the query string, after rejecting names with unusual punctuation, and logs the deletion.""", "hard_positive",
"""@app.route("/admin/clean/<table>", methods=["POST"])
@admin_required
def clean_table(table):
    status = request.args.get("status", "stale")
    blocked = (";", "--", "'", " ", "/*")
    if any(token in table for token in blocked):
        return jsonify({"error": "invalid table"}), 400
    try:
        result = db.session.execute(text(f"DELETE FROM {table} WHERE status = '{status}'"))
        db.session.execute(text("INSERT INTO admin_log (action, target, detail) VALUES ('clean', :target, :detail)"), {"target": table, "detail": status})
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "clean failed"}), 500
    log.info("cleaned %s rows from %s", result.rowcount, table)
    return jsonify({"table": table, "removed": result.rowcount})""",
[("""    blocked = (";", "--", "'", " ", "/*")
    if any(token in table for token in blocked):
        return jsonify({"error": "invalid table"}), 400""", """    if table not in ("sessions", "invites", "drafts"):
        return jsonify({"error": "invalid table"}), 400"""),
 ("""text(f"DELETE FROM {table} WHERE status = '{status}'"))""", """text(f"DELETE FROM {table} WHERE status = :status"), {"status": status})""")], "sqlalchemy"),

("u344", """Build a vineyard harvest report with optional filters for block, grape, picker and a date range, a caller-chosen sort, a page of rows and per-grape totals.""", "hard_positive",
"""def harvest_report(conn, block=None, grape=None, picker=None, since=None, until=None, sort="picked_on", page=1, per_page=25):
    sql = "SELECT h.id, h.block, h.grape, h.picker, h.kilos, h.picked_on FROM harvests h WHERE 1 = 1"
    totals_sql = "SELECT grape, COUNT(*), SUM(kilos) FROM harvests WHERE 1 = 1"
    if block:
        sql += " AND h.block = '" + block + "'"
        totals_sql += " AND block = '" + block + "'"
    if grape:
        sql += " AND h.grape = '" + grape + "'"
        totals_sql += " AND grape = '" + grape + "'"
    if picker:
        sql += " AND h.picker LIKE '%" + picker + "%'"
        totals_sql += " AND picker LIKE '%" + picker + "%'"
    if since:
        sql += " AND h.picked_on >= '" + since + "'"
        totals_sql += " AND picked_on >= '" + since + "'"
    if until:
        sql += " AND h.picked_on <= '" + until + "'"
        totals_sql += " AND picked_on <= '" + until + "'"
    sort_columns = {"picked_on": "h.picked_on", "kilos": "h.kilos", "block": "h.block", "picker": "h.picker"}
    sql += " ORDER BY " + sort_columns.get(sort, "h.picked_on") + " DESC"
    sql += " LIMIT " + str(int(per_page)) + " OFFSET " + str((int(page) - 1) * int(per_page))
    totals_sql += " GROUP BY grape ORDER BY grape"
    rows = conn.execute(sql).fetchall()
    entries = []
    for harvest_id, block_name, grape_name, picker_name, kilos, picked_on in rows:
        entries.append({
            "id": harvest_id,
            "block": block_name,
            "grape": grape_name,
            "picker": picker_name,
            "kilos": kilos,
            "picked_on": picked_on,
        })
    totals = []
    for grape_name, count, kilos in conn.execute(totals_sql).fetchall():
        totals.append({"grape": grape_name, "harvests": count, "kilos": kilos or 0})
    grand_total = sum(item["kilos"] for item in totals)
    log.info("harvest report: %s rows on page %s", len(entries), page)
    return {"page": page, "entries": entries, "totals": totals, "grand_total": grand_total}""",
[("""    sql = "SELECT h.id, h.block, h.grape, h.picker, h.kilos, h.picked_on FROM harvests h WHERE 1 = 1\"""", """    sql = "SELECT h.id, h.block, h.grape, h.picker, h.kilos, h.picked_on FROM harvests h WHERE 1 = 1"
    params = []"""),
 ("""        sql += " AND h.block = '" + block + "'"
        totals_sql += " AND block = '" + block + "'\"""", """        sql += " AND h.block = ?"
        totals_sql += " AND block = ?"
        params.append(block)"""),
 ("""        sql += " AND h.grape = '" + grape + "'"
        totals_sql += " AND grape = '" + grape + "'\"""", """        sql += " AND h.grape = ?"
        totals_sql += " AND grape = ?"
        params.append(grape)"""),
 ("""        sql += " AND h.picker LIKE '%" + picker + "%'"
        totals_sql += " AND picker LIKE '%" + picker + "%'\"""", """        sql += " AND h.picker LIKE ?"
        totals_sql += " AND picker LIKE ?"
        params.append("%" + picker + "%")"""),
 ("""        sql += " AND h.picked_on >= '" + since + "'"
        totals_sql += " AND picked_on >= '" + since + "'\"""", """        sql += " AND h.picked_on >= ?"
        totals_sql += " AND picked_on >= ?"
        params.append(since)"""),
 ("""        sql += " AND h.picked_on <= '" + until + "'"
        totals_sql += " AND picked_on <= '" + until + "'\"""", """        sql += " AND h.picked_on <= ?"
        totals_sql += " AND picked_on <= ?"
        params.append(until)"""),
 ("""rows = conn.execute(sql).fetchall()""", """rows = conn.execute(sql, params).fetchall()"""),
 ("""conn.execute(totals_sql).fetchall()""", """conn.execute(totals_sql, params).fetchall()""")], "sqlite3"),

("u345", """Return the number of rows of one of three logging tables newer than a given date.""", "hard_negative",
"""def newer_than(conn, kind, since):
    tables = {"scans": "gate_scans", "alerts": "gate_alerts", "visits": "gate_visits"}
    table = tables.get(kind)
    if table is None:
        raise ValueError(kind)
    row = conn.execute(f"SELECT COUNT(*) FROM {table} WHERE logged_at > ?", (since,)).fetchone()
    log.info("%s newer than %s: %s", kind, since, row[0])
    return row[0]""", "", "sqlite3"),

("u346", """Fetch the latest readings of a sensor, with the row count converted to an integer and limited to five hundred.""", "hard_negative",
"""def latest_sensor_readings(conn, sensor_id, count):
    count = max(1, min(int(count), 500))
    query = f"SELECT taken_at, value FROM sensor_readings WHERE sensor_id = ? ORDER BY taken_at DESC LIMIT {count}"
    rows = conn.execute(query, (sensor_id,)).fetchall()
    readings = [{"at": r[0], "value": r[1]} for r in rows]
    log.info("fetched %s readings for sensor %s", len(readings), sensor_id)
    return readings""", "", "sqlite3"),

("u347", """Flask endpoint listing tickets of a service desk filtered by any of several priorities, with the number of placeholders matched to the list.""", "hard_negative",
"""@app.route("/desk/tickets")
@login_required
def desk_tickets():
    priorities = request.args.getlist("priority")
    team = request.args.get("team", "")
    if not priorities:
        priorities = ["high", "urgent"]
    marks = ", ".join(["%s"] * len(priorities))
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, priority FROM desk_tickets WHERE team = %s AND priority IN (" + marks + ") ORDER BY opened_at DESC LIMIT 100", [team] + priorities)
    rows = cur.fetchall()
    cur.close()
    return jsonify([{"id": r[0], "title": r[1], "priority": r[2]} for r in rows])""", "", "mysql"),

("u348", """Move many tasks to a new board column and return how many changed, choosing the ordering column from a fixed mapping and binding every value.""", "hard_negative",
"""def move_tasks_to_column(self, task_ids, column_name, order_by):
    orders = {"priority": "priority DESC", "due": "due_on ASC", "created": "created_at ASC"}
    order_clause = orders.get(order_by, "created_at ASC")
    ids = [int(t) for t in task_ids]
    if not ids:
        return 0
    marks = ",".join("?" for _ in ids)
    rows = self.conn.execute(
        f"SELECT id FROM tasks WHERE id IN ({marks}) ORDER BY {order_clause}",
        ids,
    ).fetchall()
    position = self.conn.execute("SELECT COALESCE(MAX(position), 0) FROM tasks WHERE column_name = ?", (column_name,)).fetchone()[0]
    moved = 0
    for (task_id,) in rows:
        position += 1
        self.conn.execute(
            "UPDATE tasks SET column_name = ?, position = ? WHERE id = ?",
            (column_name, position, task_id),
        )
        moved += 1
    self.conn.commit()
    self.log.info("moved %s tasks to %s", moved, column_name)
    return moved""", "", "sqlite3"),

("u349", """Return one page of rows from a table that is listed in the registry, with caller-chosen columns checked against the registry and values bound as parameters.""", "hard_negative",
"""def registry_page(conn, table, columns, filters, page, per_page=20):
    entry = REGISTRY.get(table)
    if entry is None:
        raise ValueError("unknown table")
    for name in list(columns) + list(filters):
        if name not in entry:
            raise ValueError("unknown column: " + name)
    selected = sql.SQL(", ").join(sql.Identifier(c) for c in columns)
    conditions = []
    values = []
    for name, value in filters.items():
        conditions.append(sql.SQL("{} = %s").format(sql.Identifier(name)))
        values.append(value)
    query = sql.SQL("SELECT {cols} FROM {tbl}").format(cols=selected, tbl=sql.Identifier(table))
    if conditions:
        query = query + sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions)
    query = query + sql.SQL(" ORDER BY 1 LIMIT %s OFFSET %s")
    values.extend([per_page, (max(int(page), 1) - 1) * per_page])
    with conn.cursor() as cur:
        cur.execute(query, values)
        rows = cur.fetchall()
    return [dict(zip(columns, row)) for row in rows]""", "", "psycopg2"),

("u350", """Flask endpoint that lists charter boats with filters for harbour and minimum capacity, a mapped sort order and a capped page size, returning JSON.""", "hard_negative",
"""@app.route("/api/boats")
def list_boats():
    sorts = {"price": "day_rate", "size": "capacity", "name": "name"}
    sort_column = sorts.get(request.args.get("sort", "name"), "name")
    harbour = request.args.get("harbour")
    min_capacity = request.args.get("min_capacity", "0")
    try:
        per_page = min(int(request.args.get("per_page", 20)), 50)
        offset = max(int(request.args.get("offset", 0)), 0)
        capacity = int(min_capacity)
    except ValueError:
        return jsonify({"error": "numbers expected"}), 400
    sql = "SELECT id, name, harbour, capacity, day_rate FROM boats WHERE capacity >= :capacity"
    params = {"capacity": capacity, "per_page": per_page, "offset": offset}
    if harbour:
        sql += " AND harbour = :harbour"
        params["harbour"] = harbour
    sql += " ORDER BY " + sort_column + " LIMIT :per_page OFFSET :offset"
    rows = db.session.execute(text(sql), params).fetchall()
    return jsonify([dict(row._mapping) for row in rows])""", "", "sqlalchemy"),

("u351", """Write a sales ledger export for a bookshop: pick the table and columns from a registry, bind the date and shop filters, cap the rows and add per-column totals and a checksum line.""", "hard_negative",
"""def sales_export(conn, view, columns, shop=None, since=None, until=None, limit=1000):
    views = {
        "sales": ("sales", ("id", "shop", "isbn", "qty", "amount", "sold_on")),
        "returns": ("returns", ("id", "shop", "isbn", "qty", "amount", "returned_on")),
        "orders": ("supplier_orders", ("id", "shop", "isbn", "qty", "amount", "ordered_on")),
    }
    entry = views.get(view)
    if entry is None:
        raise ValueError("unknown view")
    table, known = entry
    chosen = list(columns) if columns else list(known)
    for name in chosen:
        if name not in known:
            raise ValueError("unknown column: " + str(name))
    date_column = known[-1]
    where = []
    values = []
    if shop:
        where.append("shop = ?")
        values.append(shop)
    if since:
        where.append(date_column + " >= ?")
        values.append(since)
    if until:
        where.append(date_column + " <= ?")
        values.append(until)
    limit = max(1, min(int(limit), 10000))
    query = "SELECT " + ", ".join(chosen) + " FROM " + table
    if where:
        query += " WHERE " + " AND ".join(where)
    query += " ORDER BY id LIMIT " + str(limit)
    rows = conn.execute(query, values).fetchall()
    lines = [",".join(chosen)]
    totals = dict.fromkeys(chosen, 0)
    counted = set()
    for row in rows:
        lines.append(",".join(str(cell) for cell in row))
        for name, cell in zip(chosen, row):
            if isinstance(cell, (int, float)) and name != "id":
                totals[name] += cell
                counted.add(name)
    footer = ["rows=" + str(len(rows))]
    for name in chosen:
        if name in counted:
            footer.append(name + "=" + str(round(totals[name], 2)))
    checksum = sum(len(line) for line in lines) % 9973
    lines.append(";".join(footer))
    lines.append("check=" + str(checksum))
    log.info("exported %s rows from %s", len(rows), table)
    return lines""", "", "sqlite3"),
]
