
PRICER – System Architecture Project

PRICER este o aplicație web pentru căutarea și compararea prețurilor produselor din mai multe magazine online, integrând:

arhitectură Layered (N-Tier)

micro-modul de Clean Architecture pentru use-case-uri

căutare în timp real prin SerpAPI Google Shopping

extragere specificații

gestionarea produselor favorite

alerte automate de preț (email)

sistem de utilizatori cu autentificare

🚀 Funcționalități principale
🔍 Căutare produse

Interogări în timp real prin Google Shopping (SerpAPI)

Afișare preț + valută + magazin

Încărcare progresivă Load More

Sortare după preț (asc/desc)

❤️ Favorite

Adăugare și eliminare produse

Afișare listă favorite

Activare / dezactivare alertă de modificare preț

📩 Alerte de preț

Scheduler automat (Flask-APScheduler)

Verifică la fiecare minut prețurile curente

Dacă prețul scade → trimite email utilizatorului

🧱 Arhitectură

Proiectul este organizat pe arhitectură Layered, cu zone clare:

1. Presentation Layer

Flask (rute, API, HTML templates)

2. Application Layer

Use-case-uri, logică business (ex: SearchProductsUseCase, CheckPriceAlertsUseCase)

3. Domain Layer

Entități: Product, User, FavoriteProduct, PriceAlert

Logică de business pură

4. Infrastructure Layer

SQLAlchemy repository implementations

Email notifier

SerpAPI integration

Scraper module

📦 Tehnologii utilizate
Componentă	Tehnologie
Backend	Python Flask
DB ORM	SQLAlchemy
BD	SQL Server / SQLite (ambele suportate)
Frontend	HTML + CSS + JS
Arhitectură	Layered Architecture + Clean Architecture patterns
Email	SMTP
Scheduler	APScheduler
API extern	SerpAPI Google Shopping