#  PRICER – System Architecture Project

PRICER este o aplicație web pentru căutarea și compararea prețurilor produselor din mai multe magazine online, construită folosind **arhitectură Layered (N-Tier)** și un modul de **Clean Architecture** pentru logica use-case-urilor.

---

## 🏛️ Arhitectură

### 🔸 Layered Architecture (N-Tier)
Aplicația este structurată pe mai multe straturi:
- **UI Layer** – paginile HTML/Jinja + interfața utilizator
- **Application Layer** – rute Flask + orchestrare logică
- **Domain Layer** – entități și use-case-uri (Clean Architecture)
- **Data Layer** – acces la baza de date (SQLAlchemy) + scraping

### 🔸 Elemente Clean Architecture
- Use-case pentru căutarea produselor  
- Use-case pentru verificarea alertelor de preț  
- Repositories (interfaces + SQLAlchemy implementation)  
- Notificator prin email

---

##  Funcționalități principale

###  Căutare produse
- interogări în timp real prin **SerpAPI Google Shopping**  
- rezultate normalizate (nume, preț, valută, poză, magazin)

###  Afișare preț + valută + magazin
- extragere și afișare automată a valutei
- logo specific magazin (darwin.md, enter.online etc.)

###  Specificații produs
- extragere automată a specificațiilor din pagina produsului  
- normalizare format JSON

###  Produse favorite
- salvare în baza de date
- afișare personalizată per utilizator
- activare / dezactivare alertă preț

###  Alerte automate prin email
- verificare preț din 1 în 1 minut cu **APScheduler**
- notificare dacă prețul scade

###  Funcții UX:
- încărcare progresivă „Load More”
- sortare după preț (ascendent / descendent)
- responsive layout
- sistem de login + profil utilizator

---

##  Tehnologii folosite

| Componentă | Tehnologie |
|-----------|-------------|
| Backend | Python, Flask |
| Arhitectură | Layered + Clean Architecture |
| Bază de date | SQL Server / SQLAlchemy ORM |
| Scraping | SerpAPI + BeautifulSoup |
| Frontend | HTML, CSS, JS, Jinja2 |
| Scheduling | APScheduler |
| Autentificare | Flask-Login |

---