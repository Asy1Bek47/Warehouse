import json
import os
from django.shortcuts import render, redirect

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

WAREHOUSE_FILE = os.path.join(DATA_DIR, 'warehouse.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
LOGS_FILE = os.path.join(DATA_DIR, 'logs.json')


def read_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def write_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def index_redirect(request):
    return redirect('warehouse')

def login_view(request):
    if request.session.get('user'):
        return redirect('warehouse')
        
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        users = read_json(USERS_FILE)
        is_authenticated = False
        
        for u in users:
            if u.get('username') == username and u.get('password') == password:
                is_authenticated = True
                request.session['user'] = username
                break
                
        if not is_authenticated:
            error_message = 'Неверный логин или пароль'
        else:
            return redirect('warehouse')
            
    return render(request, 'login.html', {'error_message': error_message})

def logout_view(request):
    request.session.flush()
    return redirect('login')

# SRP - Single Responsibility Principle
def warehouse_view(request):
    user = request.session.get('user')
    if not user:
        return redirect('login')

    warehouse_data = read_json(WAREHOUSE_FILE)
    
    action = request.POST.get('action') if request.method == 'POST' else request.GET.get('action')

    if request.method == 'POST':
        if action == 'add_item':
            new_item = {
                "id": len(warehouse_data) + 1 if not warehouse_data else max(i.get('id', 0) for i in warehouse_data) + 1,
                "name": request.POST.get('name'),
                "category": request.POST.get('category'),
                "price": float(request.POST.get('price')),
                "quantity": int(request.POST.get('quantity'))
            }
            warehouse_data.append(new_item)
            write_json(WAREHOUSE_FILE, warehouse_data)
            return redirect('warehouse')
            
        elif action == 'edit_item':
            item_id = int(request.POST.get('id'))
            for item in warehouse_data:
                if item.get('id') == item_id:
                    item['name'] = request.POST.get('name')
                    item['price'] = float(request.POST.get('price'))
                    item['quantity'] = int(request.POST.get('quantity'))
                    break
            write_json(WAREHOUSE_FILE, warehouse_data)
            return redirect('warehouse')
            
        elif action == 'delete_item':
            item_id = int(request.POST.get('id'))
            warehouse_data = [item for item in warehouse_data if item.get('id') != item_id]
            write_json(WAREHOUSE_FILE, warehouse_data)
            return redirect('warehouse')
            
        elif action == 'purchase':
            item_id = int(request.POST.get('id'))
            purchase_qty = int(request.POST.get('qty', 1))
            
            for item in warehouse_data:
                if item.get('id') == item_id:
                    if item.get('quantity', 0) >= purchase_qty:
                        item['quantity'] -= purchase_qty
                        write_json(WAREHOUSE_FILE, warehouse_data)
                        
                        logs = read_json(LOGS_FILE)
                        log_entry = {
                            "user": user,
                            "action": "purchase",
                            "item": item.get('name'),
                            "qty": purchase_qty,
                            "total": float(item.get('price', 0)) * purchase_qty
                        }
                        logs.append(log_entry)
                        write_json(LOGS_FILE, logs)
                        

                            
                    break
            return redirect('warehouse')
            

    for item in warehouse_data:
        category = item.get('category', 'other')
        price = item.get('price', 0)
        
        tax = 0.0
        discount = 0.0
        
        # OCP - Open Closed Principle
        if category == 'electronics':
            tax = 0.20
            discount = 0.05
        elif category == 'food':
            tax = 0.05
            discount = 0.10
        elif category == 'clothing':
            tax = 0.15
            discount = 0.20
        elif category == 'furniture':
            tax = 0.25
            discount = 0.0
        else:
            tax = 0.10
            discount = 0.0
            
        final_price = price + (price * tax) - (price * discount)
        item['final_price'] = round(final_price, 2)
        item['tax_rate'] = tax
        item['discount_rate'] = discount

    context = {
        'items': warehouse_data,
        'user': user
    }
    return render(request, 'warehouse.html', context)
