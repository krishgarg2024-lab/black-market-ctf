from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in a real scenario

# Item database
ITEMS = {
    'phone': {'name': 'Glitched Burner Phone', 'price': 5, 'weight': 0.1},
    'container': {'name': 'Lead-Lined \'Secure\' Container', 'price': 25, 'weight': 1000},
    'credentials': {'name': 'Server Zero Credentials', 'price': 1337000, 'weight': 0}
}

SHIPPING_RATE = 20  # $20 per kg

def calculate_shipping(cart):
    total_weight = sum(ITEMS[item]['weight'] * quantity for item, quantity in cart.items())
    return total_weight * SHIPPING_RATE

@app.route('/')
def index():
    return render_template('index.html', items=ITEMS)

@app.route('/add/<item_id>')
def add_item(item_id):
    if 'cart' not in session:
        session['cart'] = {}
    
    if item_id in ITEMS:
        if item_id in session['cart']:
            session['cart'][item_id] += 1
        else:
            session['cart'][item_id] = 1
    
    return redirect(url_for('view_cart'))

@app.route('/remove/<item_id>')
def remove_item(item_id):
    if 'cart' not in session or item_id not in session['cart']:
        return redirect(url_for('view_cart'))

    # The Logic Flaw: Storing and subtracting the old shipping cost
    old_shipping = calculate_shipping(session['cart'])
    
    session['cart'][item_id] -= 1
    if session['cart'][item_id] <= 0:
        del session['cart'][item_id]
    
    # Recalculate total with the flawed logic
    total_price = sum(ITEMS[item]['price'] * quantity for item, quantity in session['cart'].items())
    
    # Incorrectly subtracts the old shipping cost
    total_price -= old_shipping 

    # We need to save this flawed total and use it later
    session['flawed_total'] = total_price
    
    return redirect(url_for('view_cart'))


@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    total_price = sum(ITEMS[item]['price'] * quantity for item, quantity in cart.items())
    shipping_cost = calculate_shipping(cart)
    
    # Check for the flawed total from the 'remove' action
    flawed_total = session.get('flawed_total', None)
    
    final_total = total_price + shipping_cost if flawed_total is None else flawed_total

    return render_template('cart.html', cart_items=cart, items=ITEMS, total=final_total, shipping=shipping_cost)

@app.route('/checkout')
def checkout():
    cart = session.get('cart', {})
    total_price = sum(ITEMS[item]['price'] * quantity for item, quantity in cart.items())
    
    # We must use the flawed total from the session if it exists
    final_total = session.get('flawed_total', total_price + calculate_shipping(cart))
    
    if 'credentials' in cart and final_total <= 0:
        return render_template('success.html', flag='cubectf{success}')
    else:
        return render_template('checkout.html', total=final_total, items=ITEMS, cart_items=cart)

if __name__ == '__main__':
    app.run(debug=True)