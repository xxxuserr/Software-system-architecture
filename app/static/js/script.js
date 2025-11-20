//let allProducts = [];
let debounceTimer;
let allProducts = [];
let currentIndex = 0; // Începem de la primul produs
const productsPerPage = 10; // Câte produse încărcăm pe pagină
let searchTriggered = false;



// Funcția pentru afișarea produselor
function displayProducts(products) {
    const productList = document.getElementById('productList');
    const nextBatch = products.slice(currentIndex, currentIndex + productsPerPage);

    nextBatch.forEach((product) => {
        if (!product.image || !product.price) return;

        const li = document.createElement('li');
        li.classList.add('product-card');

        li.innerHTML = `
            <a href="/product/${product.id}" class="product-image-container">
                <img src="${product.image}" alt="${product.name}"
                    onerror="this.onerror=null; this.src='/static/img/placeholder.png';">
            </a>

            <button class="fav-button"
                    onclick="toggleFavorite(this)"
                    data-product-id="${product.id}">
                <i class="fa fa-heart"></i>
            </button>

            <div class="product-details">
                <strong class="product-title">
                    <a href="/product/${product.id}">${product.name}</a>
                </strong>
                <p class="product-specs">${product.specs || ''}</p>
                <span class="price">${product.price}  {{ product.currency or "" }}</span>
            </div>
        `;

        productList.appendChild(li);
    });

    currentIndex += productsPerPage;
}



// Fetch pentru produse de pe server
function displayProducts(products) {
    const productList = document.getElementById('productList');
    const nextBatch = products.slice(currentIndex, currentIndex + productsPerPage);

    nextBatch.forEach((product) => {
        if (!product.image || product.price == null) return;

        const li = document.createElement('li');
        li.classList.add('product-card');

        const priceNumber = Number(product.price);
        const priceText = isNaN(priceNumber) ? '' : priceNumber.toFixed(2);
        const currencyText = product.currency ? ` ${product.currency}` : '';

        li.innerHTML = `
            <a href="/product/${product.id}" class="product-image-container">
                <img src="${product.image}" alt="${product.name}">
            </a>
            <button class="fav-button"
                    onclick="toggleFavorite(this)"
                    data-product-id="${product.id}">
                <i class="fa fa-heart"></i>
            </button>
            <div class="product-details">
                <strong class="product-title">
                    <a href="/product/${product.id}">${product.name}</a>
                </strong>
                <span class="price">${priceText}${currencyText}</span>
            </div>
        `;

        productList.appendChild(li);
    });

    currentIndex += productsPerPage;
}


function fetchProducts(query = "") {
    showLoader();

    const sort = document.getElementById("sort")?.value || "recommended";
    fetch(`/search?query=${encodeURIComponent(query)}&sort=${sort}`)
        .then(response => response.json())
        .then(data => {
            console.log("📦 Produse primite:", data);
            allProducts = data;
            currentIndex = 0;
            document.getElementById('productList').innerHTML = "";
            displayProducts(allProducts);
            document.getElementById("sort-wrapper").classList.remove("hidden");
        })
        .catch(error => {
            console.error("❌ Eroare la fetchProducts:", error);
        });
}

document.getElementById("sort").addEventListener("change", () => {
    const query = document.getElementById("search").value;
    fetchProducts(query);  // Reîncarcă produsele sortate corect
});



document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("sort").addEventListener("change", (e) => {
        const value = e.target.value;

        if (value === "price_asc") {
            allProducts.sort((a, b) => (a.price || Infinity) - (b.price || Infinity));
        } else if (value === "price_desc") {
            allProducts.sort((a, b) => (b.price || 0) - (a.price || 0));
        }

        currentIndex = 0;
        document.getElementById('productList').innerHTML = "";
        displayProducts(allProducts);
    });
});



// Funcție pentru afișarea loader-ului
function showLoader() {
    let productList = document.getElementById('productList');
    productList.innerHTML = "";
    let loaderDiv = document.createElement("div");
    loaderDiv.className = "loader-container";
    loaderDiv.innerHTML = `<div class="spinner"></div>`;
    productList.appendChild(loaderDiv);
}

// Funcție pentru ascunderea loader-ului
function hideLoader() {
    let loader = document.querySelector(".loader-container");
    if (loader) loader.remove();
}

// Afișează loader în lista de produse (pentru încărcare suplimentară)
function showInlineLoader() {
    const list = document.getElementById("productList");
    const loaderDiv = document.createElement("div");
    loaderDiv.id = "inlineLoader";
    loaderDiv.className = "loader-container";
    loaderDiv.innerHTML = `<div class="spinner"></div>`;
    list.appendChild(loaderDiv);
}

function hideInlineLoader() {
    const loader = document.getElementById("inlineLoader");
    if (loader) loader.remove();
}

// Adaugă produs în listă
function renderProduct(product) {
    const li = document.createElement("li");
    li.classList.add("product-card");
    li.id = `card-${product.id}`;

    let priceHtml;
    if (product.price != null) {
        const priceNumber = Number(product.price);
        const priceText = isNaN(priceNumber) ? product.price : priceNumber.toFixed(2);
        const currencyText = product.currency ? ` ${product.currency}` : "";
        priceHtml = `${priceText}${currencyText}`;
    } else {
        priceHtml = '<span style="color:red">Preț necunoscut</span>';
    }

    li.innerHTML = `
        <a href="/product/${product.id}" class="product-image-container">
            <img src="${product.image}" alt="${product.name}" onerror="this.onerror=null; this.src='/static/img/placeholder.png';">
        </a>
        <button class="fav-button"
                onclick="toggleFavorite(this)"
                data-product-id="${product.id}">
            <i class="fas fa-heart"></i>
        </button>
        <div class="product-details">
            <strong class="product-title">
                <a href="/product/${product.id}">${product.name}</a>
            </strong>
            <span class="price">
                ${priceHtml}
            </span>
            ${product.domain ? `<div class="store-logo">
                <img src="/static/img/${product.domain}.png" alt="${product.domain}" onerror="this.style.display='none'">
            </div>` : ""}
        </div>
    `;

    document.getElementById("productList").appendChild(li);
}



// Funcție pentru detectarea scroll-ului și încărcarea produselor
window.addEventListener('scroll', function() {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
        if (currentIndex < allProducts.length) {
            displayProducts(allProducts);
        }
    }
});

// Debounce pentru căutare (evităm căutarea automată nedorită)
const searchInput = document.getElementById('search');
if (searchInput) {
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            console.log("Căutare inițiată");
        }, 500);
    });
}


let currentPage = 1;
let currentQuery = "";

// Căutare produse
const searchBtn = document.getElementById("searchButton");
if (searchBtn) {
    searchBtn.addEventListener("click", () => {
        currentPage = 1;
        currentQuery = document.getElementById("search").value.trim();

        if (currentQuery.length < 3) {
            alert("Introduceți cel puțin 3 caractere pentru căutare.");
            return;
        }

        showLoader();
        fetchAndDisplay(currentQuery, currentPage, true);
    });
}


function fetchAndDisplay(query, page = 1, clear = false) {
    if (clear) {
        document.getElementById("productList").innerHTML = "";
        document.getElementById("noResultsMessage").innerText = "";
        document.getElementById("loadMoreButton").classList.add("hidden");
    }

    if (page === 1) showLoader();
    else showInlineLoader();

    fetch(`/load_more?query=${encodeURIComponent(query)}&page=${page}`)
        .then(res => res.json())
        .then(data => {
            if (page === 1) hideLoader();
            else hideInlineLoader();

            if (data.length === 0 && page === 1) {
                document.getElementById("noResultsMessage").innerText = "Nu au fost găsite produse.";
                return;
            }

            data.forEach(renderProduct);

            // Afișăm butonul de încărcare doar dacă am primit produse
            if (data.length > 0) {
                document.getElementById("loadMoreButton").classList.remove("hidden");
            }
        })
        .catch(err => {
            console.error("Eroare la încărcarea produselor:", err);
            hideLoader();
            hideInlineLoader();
        });
}


const loadMoreBtn = document.getElementById("loadMoreButton");
if (loadMoreBtn) {
    loadMoreBtn.addEventListener("click", () => {
        currentPage++;
        fetchAndDisplay(currentQuery, currentPage);
    });
}


// Dark Mode Toggle
const toggleBtn = document.getElementById('darkModeToggle');
if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
    });
}


// Gestionare favorite
function addToFavorites(productId) {
    fetch('/add_favorite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId })
    })
    .then(response => response.json())
    .then(data => {
        showToast(data.message, 'success'); // dacă folosești toasturi
        updateFavCount();
    })
    .catch(error => console.error('Eroare la adăugarea în favorite:', error));
}



function loadFavorites() {
    fetch('/get_favorites')
        .then(response => response.json())
        .then(data => {
            let favoriteList = document.getElementById('favoriteList');
            favoriteList.innerHTML = '';

            if (data.length === 0) {
                favoriteList.innerHTML = '<p>Nu ai produse favorite.</p>';
            } else {
                data.forEach(product => {
                    const priceText = product.price != null ? product.price : '';
                    const currencyText = product.currency ? ` ${product.currency}` : '';

                    let li = document.createElement('li');
                    li.innerHTML = `
                        <img src="${product.image}" alt="${product.name}">
                        <div>
                            <strong><a href="${product.link}" target="_blank">${product.name}</a></strong><br>
                            <span class="price">
                                ${priceText ? priceText + currencyText : 'Preț necunoscut'}
                            </span>
                            <br>
                            <button onclick="setPriceAlert('${product.name}', '${product.price}', '${product.link}', '${product.image}')">
                                🔔 Activează alerta de modificare preț
                            </button>

                            <button class="remove-favorite" onclick="removeFromFavorites('${product.id}')">Elimină</button>
                        </div>
                    `;

                    favoriteList.appendChild(li);
                });
            }
        })
        .catch(error => console.error('Eroare la încărcarea favoritelor:', error));
}




function removeFromFavorites(productId) {
    fetch('/remove_favorite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId })
    })
    .then(res => res.json())
    .then(data => {
        showToast(data.message);

        // 🔄 Găsește și elimină cardul
        const card = document.querySelector(`.favorite-item[data-product-id="${productId}"]`);
        if (card) {
            card.remove();
        }
    });
}




function showToast(msg) {
    const toast = document.createElement('div');
    toast.className = 'toast-message';
    toast.textContent = msg;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}



function updateFavCount() {
    fetch('/get_favorites')
        .then(response => response.json())
        .then(data => {
            // Dacă vei dori în viitor să folosești numărul, îl ai aici:
            console.log("Favorite:", data.length);
        });
}


function toggleFavorite(button) {
    if (!button || typeof button.getAttribute !== 'function') {
        console.warn('❌ Buton invalid sau apel greșit!');
        return;
    }

    const productId = button.getAttribute('data-product-id');
    if (!productId) return;

    const favIcon = button.querySelector("i");

    if (favIcon.classList.contains("favorited")) {
        favIcon.classList.remove("favorited");
        favIcon.style.color = "#ccc";

        fetch('/remove_favorite', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId })
        })
        .then(res => res.json())
        .then(data => {
            showToast(data.message);
            updateFavCount();
        });

    } else {
        favIcon.classList.add("favorited");
        favIcon.style.color = "#ff4d4d";

        fetch('/add_favorite', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId })
        })
        .then(res => res.json())
        .then(data => {
            showToast(data.message);
            updateFavCount();
        });
    }
}



//Alerta pret
function setPriceAlert(productId) {
    fetch('/set_alert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId })
    })
    .then(res => res.json())
    .then(data => {
        showToast(data.message);

        // Actualizăm doar butonul
        const card = document.querySelector(`.favorite-item[data-product-id="${productId}"]`);
        if (card) {
            const alertDiv = card.querySelector('.alert-buttons');
            alertDiv.innerHTML = `
                <button class="btn-alert-deactivate" onclick="disablePriceAlert('${productId}')">
                    🛑 Dezactivează alerta
                </button>`;
        }
    });
}

function disablePriceAlert(productId) {
    fetch('/disable_alert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId })
    })
    .then(res => res.json())
    .then(data => {
        showToast(data.message);

        // Actualizăm doar butonul
        const card = document.querySelector(`.favorite-item[data-product-id="${productId}"]`);
        if (card) {
            const alertDiv = card.querySelector('.alert-buttons');
            alertDiv.innerHTML = `
                <button class="btn-alert-activate" onclick="setPriceAlert('${productId}')">
                    🔔 Activează alerta
                </button>`;
        }
    });
}




/* Comutarea butonului în UI */
function updateAlertButton(productId, active) {
    const card = document.querySelector(`.favorite-item[data-product-id="${productId}"]`);
    if (!card) return;

    const alertDiv = card.querySelector('.alert-buttons');
    if (active) {
        alertDiv.innerHTML =
        `<button class="btn-alert-deactivate" onclick="disablePriceAlert(${productId})">
            🛑 Dezactivează alerta
        </button>`;
    } else {
        alertDiv.innerHTML =
        `<button class="btn-alert-activate" onclick="setPriceAlert(${productId})">
            🔔 Activează alerta
        </button>`;
    }
}

document.getElementById("searchButton").addEventListener("click", function () {
    const banner = document.getElementById("banner");
    if (banner) {
        banner.style.display = "none";
    }

    // dacă ai deja funcția de căutare aici, o poți apela
    showLoader(); // presupunem că funcția ta de căutare se numește așa
});


document.getElementById("searchButton").addEventListener("click", () => {
    const query = document.getElementById("search").value;
    searchTriggered = true;  // ✅ acum știm că utilizatorul a apăsat pe buton
    fetchProducts(query);
});

