
from app.core.use_cases.search_products import SearchProductsUseCase
from app.adapters.scraping.product_search_service_impl import ProductSearchServiceImpl
from flask import render_template, request, jsonify
from app import app
from app.scraper import search_product  # doar asta

from flask import session
from flask import request, Response
from flask import redirect, request, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
import requests, json, re
from app.models import FavoriteProduct, PriceAlert, User, Product
from run import check_alerts
from urllib.parse import urlparse
from flask import render_template, abort

cached_data = {}

@app.route("/", methods=["GET", "POST"])
def index():
    products = []
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            use_case = SearchProductsUseCase(ProductSearchServiceImpl())
            products_entities = use_case.execute(query)
            products = [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "currency": p.currency,
                    "image": p.image,
                    "link": p.link,
                    "specs": p.specs,
                    "domain": p.domain,
                }
                for p in products_entities
            ]
    return render_template("index.html", products=products)

@app.route("/search")
def search():
    from urllib.parse import urlparse

    query = request.args.get("query", "").lower()
    sort = request.args.get("sort", "recommended")

    results = search_product(query)

    # 👇 Pregătim lista ce va fi trimisă în JSON
    serialized = []

    for prod in results:
        # dacă e dict (venit direct din SerpAPI sau scraping)
        if isinstance(prod, dict):
            link = prod.get("link")
            if not link:
                continue

            existing = Product.query.filter_by(link=link).first()
            if not existing:
                new_product = Product(
                    name=prod.get("name"),
                    price=prod.get("price"),
                    currency=prod.get("currency"),
                    image=prod.get("image"),
                    specs=json.dumps(prod.get("specs", {})),
                    link=link,
                    domain=urlparse(link).netloc.replace("www.", "")
                )
                db.session.add(new_product)
                db.session.flush()
                prod["id"] = new_product.id
            else:
                prod["id"] = existing.id

            serialized.append({
                "id": prod.id,
                "name": prod.name,
                "price": prod.price,
                "currency": prod.currency,
                "image": prod.image,
                "link": prod.link,
                "specs": json.loads(prod.specs or "{}"),
                "domain": prod.domain,
            })

        # dacă e obiect Product
        else:
            serialized.append({
                "id": prod.id,
                "name": prod.name,
                "price": prod.price,
                "currency": prod.currency,   # ← ADĂUGAT
                "image": prod.image,
                "link": prod.link,
                "specs": json.loads(prod.specs or "{}"),
                "domain": prod.domain,
            })


    db.session.commit()


    # 🔽 sortare
    if sort == "price_asc":
        serialized = sorted(serialized, key=lambda x: x.get("price") or float('inf'))
    elif sort == "price_desc":
        serialized = sorted(serialized, key=lambda x: x.get("price") or 0, reverse=True)

    return jsonify(serialized)




@app.route("/incomplete_products")
def incomplete_products():
    incomplete = Product.query.filter(
        (Product.price == None) | (Product.price == '') |
        (Product.image == None) | (Product.image == '') |
        (Product.specs == None) | (Product.specs == '{}') | (Product.specs == '')
    ).all()

    return render_template("incomplete_products.html", products=incomplete)




@app.route('/add_favorite', methods=['POST'])
@login_required
def add_favorite():
    data = request.get_json()
    print("📩 Date primite de la client:", data)

    product_id = data.get('product_id')
    name = data.get('name')
    price = data.get('price')
    #currency = data.get('currency')
    image = data.get('image')
    link = data.get('link')

    try:
        # 1. Dacă avem product_id, îl folosim direct
        if product_id:
            product = Product.query.get(product_id)
            if not product:
                return jsonify({'message': 'Produsul nu există în baza de date!'}), 404

        # 2. Dacă nu avem product_id, căutăm/creăm pe baza linkului
        elif link:
            product = Product.query.filter_by(link=link).first()
            if not product:
                if not all([name, price]):
                    return jsonify({'message': 'Date incomplete!'}), 400
                product = Product(name=name, price=price, image=image, link=link)
                db.session.add(product)
                db.session.flush()  # obținem id-ul fără commit

        else:
            return jsonify({'message': 'ID produs sau link lipsă!'}), 400

        # 3. Verificăm dacă e deja în favorite
        favorite = FavoriteProduct.query.filter_by(
            user_id=current_user.id,
            product_id=product.id
        ).first()

        if favorite:
            return jsonify({'message': 'Produsul este deja în favorite.'}), 200

        # 4. Adăugăm la favorite
        new_favorite = FavoriteProduct(
            user_id=current_user.id,
            product_id=product.id
        )
        db.session.add(new_favorite)

        # 5. (Opțional) Adăugăm alertă dacă nu există
        existing_alert = PriceAlert.query.filter_by(
            user_id=current_user.id,
            product_id=product.id
        ).first()

        if not existing_alert:
            alert = PriceAlert(
                user_id=current_user.id,
                product_id=product.id,
                initial_price=price or product.price,
                active=False
            )
            db.session.add(alert)

        # 6. Commit
        db.session.commit()
        return jsonify({'message': 'Produs adăugat la favorite!'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Eroare la salvare: {e}")
        return jsonify({'message': 'Eroare la salvare!'}), 500


# Elimină din favorite
@app.route('/remove_favorite', methods=['POST'])
@login_required
def remove_favorite():
    data = request.get_json()
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({'message': 'ID produs lipsă!'}), 400

    product_to_remove = FavoriteProduct.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if product_to_remove:
        db.session.delete(product_to_remove)
        db.session.commit()
        return jsonify({'message': 'Produs eliminat din favorite!'}), 200
    else:
        return jsonify({'message': 'Produsul nu a fost găsit în favorite!'}), 404



@app.route("/favorites")
@login_required
def favorites():
    favorite_products = FavoriteProduct.query.filter_by(user_id=current_user.id).all()
    favorites_list = []

    for fav in favorite_products:
        product = fav.product

        if not product:
            continue  # evită crash dacă produsul e None

        alert = PriceAlert.query.filter_by(
            user_id=current_user.id,
            product_id=product.id,
            active=True
        ).first()

        favorites_list.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'currency': product.currency,
            'image': product.image,
            'link': product.link,
            'alert_active': bool(alert)
        })

    return render_template("favorites.html", favorites=favorites_list)


@app.route("/get_favorites")
@login_required
def get_favorites():
    favorites = FavoriteProduct.query.filter_by(user_id=current_user.id).all()
    
    data = []
    for fav in favorites:
        product = fav.product
        if not product:
            continue

        data.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'currency': product.currency,
            'image': product.image,
            'link': product.link
        })


    return jsonify(data)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("Acest email este deja folosit!", "danger")
            return redirect(url_for("register"))

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Cont creat cu succes! Acum poți să te autentifici.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Autentificare reușită!", "success")
            return redirect(url_for("index"))
        else:
            flash("Email sau parolă incorecte!", "danger")

    return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    current_user.username = request.form.get("username")
    db.session.commit()
    flash("Profil actualizat cu succes!", "success")
    return redirect(url_for("profile"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Te-ai deconectat!", "info")
    return redirect(url_for("login"))


@app.route('/set_alert', methods=['POST'])
@login_required
def set_alert():
    data = request.get_json()
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({'message': 'ID produs lipsă!'}), 400

    # Verificăm dacă deja există o alertă
    alert = PriceAlert.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if alert:
        if alert.active:
            return jsonify({'message': 'Alerta este deja activă.'})
        else:
            alert.active = True
            db.session.commit()
            return jsonify({'message': 'Alerta a fost activată.'})

    # Dacă nu există, o creăm
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'message': 'Produsul nu a fost găsit!'}), 404

    new_alert = PriceAlert(
        user_id=current_user.id,
        product_id=product.id,
        initial_price=product.price,
        active=True
    )


    db.session.add(new_alert)
    db.session.commit()
    return jsonify({'message': 'Alerta a fost setată!'})


@app.route('/disable_alert', methods=['POST'])
@login_required
def disable_alert():
    data = request.get_json()
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({'message': 'ID produs lipsă!'}), 400

    alert = PriceAlert.query.filter_by(user_id=current_user.id, product_id=product_id, active=True).first()

    if alert:
        alert.active = False
        db.session.commit()
        return jsonify({'message': f'Alerta a fost dezactivată.'})

    else:
        return jsonify({'message': 'Nu există alertă activă pentru acest produs.'}), 404



@app.route('/run_alert_check', methods=['POST'])
@login_required
def run_alert_check():
    try:
        check_alerts()
        return jsonify({'message': 'Verificarea alertelor a fost rulată cu succes!'})
    except Exception as e:
        return jsonify({'message': f'Eroare la rularea verificării: {str(e)}'}), 500

# app/routes.py
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        abort(404)

    specs = json.loads(product.specs) if product.specs else {}

    # mic mapping domeniu → logo
    DOMAIN_LOGO = {
        "darwin.md":  "darwin.png",
        "enter.online": "enter.png",
        "orange.md": "orange.png",
        "moldcell.md": "moldcell.png"
    }
    domain = urlparse(product.link).netloc.replace('www.', '')
    logo   = DOMAIN_LOGO.get(domain)

    return render_template("product_detail.html",
                        product=product,
                        specs=specs,
                        logo=logo)

def safe_json_loads(text):
    try:
        return json.loads(text)
    except Exception:
        return {}  # dacă e corupt, returnează dict gol

@app.route("/load_more")
def load_more():
    from flask import jsonify, request
    from app.models import Product

    query = request.args.get("query", "").lower()
    page = int(request.args.get("page", 1))
    sort = request.args.get("sort", "recommended")

    # folosim direct SerpAPI prin search_product
    products = search_product(query, page=page, per_page=10)

    # serializăm ca să trimitem în JSON
    serialized = []
    for prod in products:
        serialized.append({
            "id": prod.id,
            "name": prod.name,
            "price": prod.price,
            "currency": prod.currency, 
            "image": prod.image,
            "link": prod.link,
            "specs": json.loads(prod.specs or "{}"),
            "domain": prod.domain,
        })

    # sortare simplă pe preț
    if sort == "price_asc":
        serialized = sorted(serialized, key=lambda x: x.get("price") or float("inf"))
    elif sort == "price_desc":
        serialized = sorted(serialized, key=lambda x: x.get("price") or 0.0, reverse=True)

    # has_more e aproximativ – poți îmbunătăți cu numărul total din SerpAPI
    has_more = len(products) == 10

    return jsonify({
        "products": serialized,
        "has_more": has_more
    })

    return jsonify(product_list)
