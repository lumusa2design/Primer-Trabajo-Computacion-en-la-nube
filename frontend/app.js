const API_URL = "https://ndv7jgla69.execute-api.us-east-1.amazonaws.com/prod";

const statusBox = document.getElementById("status");
const itemsContainer = document.getElementById("items");

function setStatus(message) {
  statusBox.textContent = message;
}

async function createItem() {
  const item = {
    name: document.getElementById("name").value.trim(),
    description: document.getElementById("description").value.trim(),
    category: document.getElementById("category").value.trim()
  };

  if (!item.name || !item.description || !item.category) {
    setStatus("Rellena todos los campos antes de crear un item.");
    return;
  }

  setStatus("Creando item...");

  await fetch(`${API_URL}/items`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(item)
  });

  document.getElementById("name").value = "";
  document.getElementById("description").value = "";
  document.getElementById("category").value = "";

  setStatus("Item creado correctamente.");
  loadItems();
}

async function loadItems() {
  setStatus("Cargando items...");

  const response = await fetch(`${API_URL}/items`);
  const data = await response.json();

  const items = data.items || [];

  itemsContainer.innerHTML = "";

  if (items.length === 0) {
    itemsContainer.innerHTML = "<p>No hay items almacenados.</p>";
    setStatus("No hay items.");
    return;
  }

  items.forEach(renderItem);

  setStatus(`${items.length} item(s) cargados desde DynamoDB.`);
}

function renderItem(item) {
  const card = document.createElement("article");
  card.className = "card";

  card.innerHTML = `
    <h3>${escapeHtml(item.name)}</h3>
    <p>${escapeHtml(item.description)}</p>
    <p><strong>Categoría:</strong> ${escapeHtml(item.category)}</p>
    <p class="card-id"><strong>ID:</strong> ${item.id}</p>

    <div class="actions">
      <button class="warning" onclick="updateItem('${item.id}')">Actualizar</button>
      <button class="danger" onclick="deleteItem('${item.id}')">Eliminar</button>
    </div>
  `;

  itemsContainer.appendChild(card);
}

async function updateItem(id) {
  const name = prompt("Nuevo nombre:");
  if (!name) return;

  const description = prompt("Nueva descripción:") || "Actualizado desde frontend";
  const category = prompt("Nueva categoría:") || "frontend";

  setStatus("Actualizando item...");

  await fetch(`${API_URL}/items/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      name,
      description,
      category
    })
  });

  setStatus("Item actualizado.");
  loadItems();
}

async function deleteItem(id) {
  const confirmed = confirm("¿Seguro que quieres eliminar este item?");
  if (!confirmed) return;

  setStatus("Eliminando item...");

  await fetch(`${API_URL}/items/${id}`, {
    method: "DELETE"
  });

  setStatus("Item eliminado.");
  loadItems();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

loadItems();