import pyodbc

# 🔧 Configurare conexiune SQL Server
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DONTLOOK;"
    "DATABASE=pricer_db;"
    "UID=user_pricer;"
    "PWD=12345679"
)

cursor = conn.cursor()

def show_intro():
    print("\n===== MODIFICARE PRODUSE PRICER =====")
    print("🔎 Caută după ID, nume sau link")
    print("✏️  Modifică ce dorești și apasă Enter ca să sari peste un câmp")
    print("❌ Scrie 'exit' ca să ieși\n")

def edit_product(product):
    print(f"\n📝 Edităm: {product.name}")
    new_price = input(f"💰 Preț actual: {product.price} | Nou preț: ").strip()
    new_image = input(f"🖼️ Imagine actuală: {product.image} | Nou link imagine: ").strip()
    new_specs = input(f"📄 Specificații actuale: {product.specs} | Noi specificații: ").strip()

    updates = []
    values = []

    if new_price:
        updates.append("price = ?")
        values.append(new_price)
    if new_image:
        updates.append("image = ?")
        values.append(new_image)
    if new_specs:
        updates.append("specs = ?")
        values.append(new_specs)

    if updates:
        values.append(product.id)
        query = f"UPDATE product SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        print("✅ Produs actualizat cu succes.\n")
    else:
        print("ℹ️ Nu s-au făcut modificări.\n")

def search_loop():
    show_intro()
    while True:
        keyword = input("🔍 Caută produs (sau 'exit'): ").strip()
        if keyword.lower() == "exit":
            break

        if keyword.isdigit():
            cursor.execute("SELECT id, name, price, image, link, specs FROM product WHERE id = ?", keyword)
        else:
            like_term = f"%{keyword}%"
            cursor.execute("""
                SELECT id, name, price, image, link, specs
                FROM product
                WHERE name LIKE ? OR link LIKE ?
            """, like_term, like_term)

        results = cursor.fetchall()
        if not results:
            print("❌ Niciun produs găsit.")
            continue

        print("\n📦 Produse găsite:")
        for prod in results:
            print(f"ID: {prod.id} | Nume: {prod.name} | Preț: {prod.price or '❌'}")

        selected_id = input("\n✏️ ID produs de modificat (sau 'skip'): ").strip()
        if selected_id.lower() == "skip":
            continue

        cursor.execute("SELECT id, name, price, image, link, specs FROM product WHERE id = ?", selected_id)
        product = cursor.fetchone()

        if not product:
            print("❌ Produsul nu a fost găsit.")
            continue

        edit_product(product)

if __name__ == "__main__":
    try:
        search_loop()
    finally:
        cursor.close()
        conn.close()
        print("\n👋 Gata. Conexiune închisă.")
