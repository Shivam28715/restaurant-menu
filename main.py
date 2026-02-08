import sqlite3
from fastapi import FastAPI, Request, Body
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import socketio 
import uvicorn
from datetime import datetime

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("orders.db")
    curr = conn.cursor()
    curr.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_num TEXT,
            items TEXT,
            total REAL,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- APP CONFIG ---
ADMIN_PASSWORD = "jugnuu_admin"
app = FastAPI()

# --- SOCKET.IO SETUP ---
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)
templates = Jinja2Templates(directory="templates")

# --- HELPER: SECURITY ---
def is_logged_in(request: Request):
    return request.cookies.get("admin_session") == ADMIN_PASSWORD

# --- ROUTES ---

@app.get("/")
async def home(request: Request, table: str = "1"):
    menu_data = [
        {"id": 1, "name": "Kurkure Dahi Ke Kebab (6pc.)", "price": 379, "cat": "Veg Starters"},
        {"id": 2, "name": "Peri Peri Potato", "price": 379, "cat": "Veg Starters"},
        {"id": 3, "name": "Shahi Bharwan Khumb (6pc.)", "price": 389, "cat": "Veg Starters"},
        {"id": 4, "name": "Achari Chaap (6pc.)", "price": 389, "cat": "Veg Starters"},
        {"id": 5, "name": "Paneer Angara Tikka (6pc.)", "price": 399, "cat": "Veg Starters"},
        {"id": 6, "name": "Paneer Ajwaini Tikka (6pc.)", "price": 399, "cat": "Veg Starters"},
        {"id": 7, "name": "Chilli Paneer Dry", "price": 399, "cat": "Veg Starters"},
        {"id": 8, "name": "Chilli Mushroom Dry", "price": 389, "cat": "Veg Starters"},
        {"id": 9, "name": "Veg Manchurian Dry", "price": 389, "cat": "Veg Starters"},
        {"id": 10, "name": "Crispy Corn Kernels", "price": 379, "cat": "Veg Starters"},
        {"id": 11, "name": "Churrasco Pineapple", "price": 389, "cat": "Veg Starters"},
        {"id": 12, "name": "Cajun Spicy Potato (10pcs)", "price": 275, "cat": "Veg Starters"},
        {"id": 13, "name": "Tandoori Chicken Tangri (4pc.)", "price": 489, "cat": "Non-Veg Starters"},
        {"id": 14, "name": "Smokey Tandoori Chicken Tikka (6pc.)", "price": 489, "cat": "Non-Veg Starters"},
        {"id": 15, "name": "Kastoori Murgh Malai Tikka (6pc.)", "price": 489, "cat": "Non-Veg Starters"},
        {"id": 16, "name": "Sarson Ka Macchi Tikka (6pc.)", "price": 569, "cat": "Non-Veg Starters"},
        {"id": 17, "name": "Mutton Seekh Kebab (6pc.)", "price": 549, "cat": "Non-Veg Starters"},
        {"id": 18, "name": "Chilli Chicken Dry", "price": 489, "cat": "Non-Veg Starters"},
        {"id": 19, "name": "Chilli Garlic Fish", "price": 569, "cat": "Non-Veg Starters"},
        {"id": 20, "name": "Wok Tossed Lemon Fish", "price": 569, "cat": "Non-Veg Starters"},
        {"id": 21, "name": "Pani Puri (8 PCS)", "price": 195, "cat": "Street Chaat"},
        {"id": 22, "name": "Dahi Bhalla", "price": 195, "cat": "Street Chaat"},
        {"id": 23, "name": "Dahi Puchka", "price": 195, "cat": "Street Chaat"},
        {"id": 24, "name": "Papdi Chaat", "price": 195, "cat": "Street Chaat"},
        {"id": 25, "name": "Palak Patta Chaat", "price": 195, "cat": "Street Chaat"},
        {"id": 26, "name": "Themis Special Masala Dosa", "price": 375, "cat": "South Indian"},
        {"id": 27, "name": "Paneer Masala Dosa", "price": 375, "cat": "South Indian"},
        {"id": 28, "name": "Masala Uttapam", "price": 365, "cat": "South Indian"},
        {"id": 29, "name": "Rice & Rawa Idli (4PCS)", "price": 249, "cat": "South Indian"},
        {"id": 30, "name": "Subziyon Ka Mel", "price": 349, "cat": "Veg Main Course"},
        {"id": 31, "name": "Dal Dhaba Tadka", "price": 349, "cat": "Veg Main Course"},
        {"id": 32, "name": "Paneer Makhani", "price": 410, "cat": "Veg Main Course"},
        {"id": 33, "name": "Mushroom Do Pyaza", "price": 375, "cat": "Veg Main Course"},
        {"id": 34, "name": "Paneer Lababdaar", "price": 410, "cat": "Veg Main Course"},
        {"id": 35, "name": "Paneer Tikka Kadai Masala", "price": 410, "cat": "Veg Main Course"},
        {"id": 36, "name": "Dal Makhani", "price": 410, "cat": "Veg Main Course"},
        {"id": 37, "name": "Chana Pind Wala", "price": 375, "cat": "Veg Main Course"},
        {"id": 38, "name": "Soya Chaap Butter Masala", "price": 375, "cat": "Veg Main Course"},
        {"id": 39, "name": "Veg Manchurian Gravy", "price": 339, "cat": "Veg Main Course"},
        {"id": 40, "name": "Home Style Chicken Curry", "price": 465, "cat": "Non-Veg Main Course"},
        {"id": 41, "name": "Themis Spl. Butter Chicken", "price": 485, "cat": "Non-Veg Main Course"},
        {"id": 42, "name": "Kadai Chicken", "price": 485, "cat": "Non-Veg Main Course"},
        {"id": 43, "name": "Murgh Bagmati", "price": 485, "cat": "Non-Veg Main Course"},
        {"id": 44, "name": "Bhuna Gosht (4pc.)", "price": 545, "cat": "Non-Veg Main Course"},
        {"id": 45, "name": "Mutton Rogan Josh (4pc.)", "price": 545, "cat": "Non-Veg Main Course"},
        {"id": 46, "name": "Rahra Shikari Gosht (4pc.)", "price": 545, "cat": "Non-Veg Main Course"},
        {"id": 47, "name": "Chilli Chicken Gravy", "price": 439, "cat": "Non-Veg Main Course"},
        {"id": 48, "name": "Fish in Hot Garlic Sauce", "price": 450, "cat": "Non-Veg Main Course"},
        {"id": 49, "name": "Gulab Jamun (2pc.)", "price": 130, "cat": "Desserts"},
        {"id": 50, "name": "Moong Dal Ka Halwa", "price": 185, "cat": "Desserts"},
        {"id": 51, "name": "Chocolate Brownie with Ice Cream", "price": 275, "cat": "Desserts"},
        {"id": 52, "name": "Paan Kulfi 2pcs", "price": 149, "cat": "Desserts"},
        {"id": 53, "name": "Malai Kulfi 2pcs", "price": 149, "cat": "Desserts"},
        {"id": 54, "name": "Mango Kulfi 2pcs", "price": 149, "cat": "Desserts"},
        {"id": 55, "name": "Exotic Veg Pizza", "price": 310, "cat": "World Cuisine"},
        {"id": 56, "name": "Margheritta Pizza", "price": 285, "cat": "World Cuisine"},
        {"id": 57, "name": "Chicken Tikka Pizza", "price": 355, "cat": "World Cuisine"},
        {"id": 58, "name": "Pasta Veg (Red/White/Mix)", "price": 310, "cat": "World Cuisine"},
        {"id": 59, "name": "Chicken Pasta (Red/White/Mix)", "price": 355, "cat": "World Cuisine"},
        {"id": 60, "name": "Themis Veg Burger", "price": 349, "cat": "World Cuisine"},
        {"id": 61, "name": "Grilled Cottage Cheese Burger", "price": 375, "cat": "World Cuisine"},
        {"id": 62, "name": "Peri Peri Chicken Burger", "price": 415, "cat": "World Cuisine"},
        {"id": 63, "name": "Roast Mutton Burger", "price": 439, "cat": "World Cuisine"}
    ]
    categories = ["Veg Starters", "Non-Veg Starters", "Street Chaat", "South Indian", "Veg Main Course", "Non-Veg Main Course", "World Cuisine", "Desserts"]
    return templates.TemplateResponse("menu.html", {"request": request, "table": table, "menu": menu_data, "categories": categories})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def do_login(data: dict = Body(...)):
    if data.get("password") == ADMIN_PASSWORD:
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="admin_session", value=ADMIN_PASSWORD, httponly=True)
        return response
    return {"error": "Invalid Password"}

@app.get("/dashboard")
async def dashboard_page(request: Request):
    if not is_logged_in(request): return RedirectResponse(url="/login")
    conn = sqlite3.connect("orders.db")
    curr = conn.cursor()
    curr.execute("SELECT id, table_num, items, total FROM orders WHERE status='Pending' ORDER BY id ASC")
    active_orders = curr.fetchall()
    conn.close()
    return templates.TemplateResponse("dashboard.html", {"request": request, "active_orders": active_orders})

@app.get("/billing")
async def billing_page(request: Request):
    if not is_logged_in(request): return RedirectResponse(url="/login")
    conn = sqlite3.connect("orders.db")
    curr = conn.cursor()
    curr.execute("SELECT id, table_num, items, total FROM orders WHERE status IN ('Pending', 'Served') ORDER BY id ASC")
    active_orders = curr.fetchall()
    conn.close()
    return templates.TemplateResponse("billing.html", {"request": request, "active_orders": active_orders})

@app.get("/sales")
async def sales(request: Request):
    if not is_logged_in(request): return RedirectResponse(url="/login")
    
    conn = sqlite3.connect("orders.db")
    conn.row_factory = sqlite3.Row
    curr = conn.cursor()

    # 1. Lifetime Totals
    curr.execute("SELECT SUM(total) as rev, COUNT(*) as cnt FROM orders WHERE status='Paid'")
    res = curr.fetchone()
    overall_rev_val = res['rev'] if res and res['rev'] else 0
    overall_count = res['cnt'] if res and res['cnt'] else 0
    total_revenue = f"{overall_rev_val:,.2f}"

    # 2. Fetch Today's Data
    curr.execute("SELECT * FROM orders WHERE status='Paid' AND date(created_at) = date('now', 'localtime') ORDER BY id DESC")
    today_orders = [dict(row) for row in curr.fetchall()]
    today_rev_val = sum(o['total'] for o in today_orders)
    today_rev_str = f"{today_rev_val:,.2f}"

    # 3. Fetch Weekly Data
    curr.execute("SELECT * FROM orders WHERE status='Paid' AND date(created_at) >= date('now', '-7 days') ORDER BY id DESC")
    week_orders = [dict(row) for row in curr.fetchall()]
    week_rev_val = sum(o['total'] for o in week_orders)
    week_rev_str = f"{week_rev_val:,.2f}"

    # 4. Fetch Monthly Data
    curr.execute("SELECT * FROM orders WHERE status='Paid' AND date(created_at) >= date('now', '-30 days') ORDER BY id DESC")
    month_orders = [dict(row) for row in curr.fetchall()]
    month_rev_val = sum(o['total'] for o in month_orders)
    month_rev_str = f"{month_rev_val:,.2f}"

    conn.close()

    # We use the _str versions for the UI display
    return templates.TemplateResponse("sales.html", {
        "request": request,
        "total_revenue": total_revenue,
        "count": overall_count,
        "today_orders": today_orders, 
        "today_rev": today_rev_str,
        "week_orders": week_orders, 
        "week_rev": week_rev_str,
        "month_orders": month_orders, 
        "month_rev": month_rev_str
    })
@app.post("/order")
async def place_order(data: dict = Body(...)):
    table = str(data.get("table", "1"))
    items = data.get("items", []) 
    total = data.get("total", 0)
    item_string = ", ".join([f"{i['name']} x{i.get('qty', 1)}" for i in items])
    
    # --- ADD THIS LINE TO GET CURRENT TIME ---
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("orders.db")
    curr = conn.cursor()
    # Add created_at to the INSERT statement
    curr.execute("""
        INSERT INTO orders (table_num, items, total, status, created_at) 
        VALUES (?, ?, ?, ?, ?)
    """, (table, item_string, total, "Pending", now))
    
    new_id = curr.lastrowid 
    conn.commit()
    conn.close()
    await sio.emit('new_order_alert', {"id": new_id, "table": table, "type": "ORDER"})
    return {"status": "Success", "id": new_id}

@app.post("/call-waiter")
async def call_waiter(data: dict = Body(...)):
    table = str(data.get("table", "1"))
    await sio.emit('waiter_call_alert', {"table": table, "type": "WAITER"})
    return {"status": "Waiter called"}

@app.post("/complete-order/{order_id}")
async def complete_order(order_id: int):
    conn = sqlite3.connect("orders.db")
    curr = conn.cursor()
    curr.execute("UPDATE orders SET status='Served' WHERE id=?", (order_id,))
    conn.commit()
    conn.close()
    await sio.emit('order_served', {"id": order_id})
    return {"status": "Done"}

@app.post("/checkout/{order_id}")
async def checkout_order(order_id: int):
    conn = sqlite3.connect("orders.db")
    curr = conn.cursor()
    curr.execute("UPDATE orders SET status='Paid' WHERE id=?", (order_id,))
    conn.commit()
    conn.close()
    return {"status": "Table Cleared"}

if __name__ == '__main__':
    uvicorn.run(socket_app, host='0.0.0.0', port=5000)
