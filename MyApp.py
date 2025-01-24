from venv import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

'''
# Load products from a JSON file"
def load_products():
       with open("products.json") as f:
         return json.load(f)
           
# Routes
@app.route("/")
def home():
    products = load_products()
    #print(products)
    return render_template("home.html", products=products)

@app.route("/toto")
def base():
    
    return render_template("home.html")


@app.route("/product/<int:product_id>")
def product(product_id):
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)
    if product is None:
        return "Product not found", 404
    return render_template("product.html", product=product)

@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)
    if product is None:
        return "Product not found", 404

    # Add product to cart in session
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(product)
    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    cart = session.get("cart", [])
    total = sum(item["price"] for item in cart)
    return render_template("cart.html", cart=cart, total=total)

@app.route("/checkout", methods=["POST"])
def checkout():
    session.pop("cart", None)  # Clear the cart
    return "Thank you for your purchase!"
    '''

