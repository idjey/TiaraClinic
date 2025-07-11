import flatpickr from "flatpickr";
import Sortable from "https://cdn.jsdelivr.net/npm/sortablejs@1.15.2/+esm";
import Chart from "https://cdn.jsdelivr.net/npm/chart.js";

const flatpickrOptions = { dateFormat: "Y-m-d" };

export function initFlatpickrs(context = document) {
  context.querySelectorAll(".date-field").forEach((input) => {
    if (!input._flatpickr) flatpickr(input, flatpickrOptions);
  });
}

function showSpinner(row) {
  let spinner = row.querySelector(".row-spinner");
  if (!spinner) {
    spinner = document.createElement("span");
    spinner.className = "spinner-border spinner-border-sm row-spinner ms-2";
    row.querySelector(".saveRow").after(spinner);
  }
}

function hideSpinner(row) {
  const spinner = row.querySelector(".row-spinner");
  if (spinner) spinner.remove();
}

export function showSaveStatus(row, status) {
  const span = row.querySelector(".save-status");
  span.textContent = status === "success" ? "✅" : "⚠️";
  setTimeout(() => (span.textContent = ""), 2000);
}

export function animateRow(row, type) {
  if (type === "save") {
    row.classList.add("row-saved");
    setTimeout(() => row.classList.remove("row-saved"), 1200);
  } else if (type === "delete") {
    row.classList.add("fade-out", "row-deleted");
    setTimeout(() => row.remove(), 500);
  }
}

function extractRowData(row) {
  // Corrected: Use querySelector for select elements and more robust selectors for inputs
  return {
    visit_date: row.querySelector(".date-field").value,
    treatment: row.querySelector("td:nth-child(3) input").value,
    payment_method: row.querySelector("td:nth-child(4) input").value,
    actual_amount: parseFloat(row.querySelector(".amount-field").value) || 0,
    deposit_paid: row.querySelector(".deposit-check").checked,
    deposit_method: row.querySelector(".deposit-method").value,
    month: row.querySelector("td:nth-child(9) input").value,
    year: parseInt(row.querySelector("td:nth-child(10) input").value) || 0,
  };
}

export async function saveRow(row) {
  const id = row.dataset.id;
  const data = extractRowData(row);
  const url = id ? `/visit/${id}` : "/visit";
  const method = id ? "PUT" : "POST";

  showSpinner(row);
  try {
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Save failed");
    const json = await res.json();
    if (!id && json.id) row.dataset.id = json.id;

    animateRow(row, "save");
    showSaveStatus(row, "success");
  } catch (err) {
    console.error(err);
    showSaveStatus(row, "error");
  } finally {
    hideSpinner(row);
    document
      .getElementById("totalActual")
      .dispatchEvent(new Event("updateTotal"));
  }
}

export async function deleteRow(row) {
  const id = row.dataset.id;
  if (!id) return animateRow(row, "delete");

  if (confirm("Delete this row?")) {
    showSpinner(row);
    try {
      const res = await fetch(`/visit/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Delete failed");
      animateRow(row, "delete");
    } catch (err) {
      alert("Failed to delete ❌");
    } finally {
      hideSpinner(row);
    }
  }
}

export function bindRow(row) {
  initFlatpickrs(row);

  const depositCheck = row.querySelector(".deposit-check");
  const depositSelect = row.querySelector(".deposit-method");
  const amountField = row.querySelector(".amount-field");
  const totalCell = document.getElementById("totalActual");

  depositCheck.addEventListener("change", () => {
    depositSelect.disabled = !depositCheck.checked;
    amountField.dispatchEvent(new Event("input"));
  });

  amountField.addEventListener("input", () => {
    const net = row.querySelector(".net-amount");
    const actual = parseFloat(amountField.value) || 0;
    net.value = depositCheck.checked
      ? (actual - 100).toFixed(2)
      : actual.toFixed(2);
    totalCell.dispatchEvent(new Event("updateTotal"));
  });

  row.querySelector(".saveRow").addEventListener("click", () => saveRow(row));
  row
    .querySelector(".deleteRow")
    .addEventListener("click", () => deleteRow(row));
}

export async function loadChartData() {
  try {
    const res = await fetch("/api/dashboard/stats");
    const stats = await res.json();
    renderTreatmentPie(stats.treatment_counts);
    renderRevenueBar(stats.treatment_revenue);
  } catch (err) {
    console.error("Error loading chart data:", err);
  }
}

function renderTreatmentPie(counts) {
  const data = {
    labels: Object.keys(counts),
    datasets: [
      {
        data: Object.values(counts),
        backgroundColor: [
          "#4e73df",
          "#1cc88a",
          "#36b9cc",
          "#f6c23e",
          "#e74a3b",
        ],
      },
    ],
  };
  new Chart(document.getElementById("treatmentPieChart"), {
    type: "pie",
    data,
    options: { responsive: true },
  });
}

function renderRevenueBar(revenue) {
  const data = {
    labels: Object.keys(revenue),
    datasets: [
      {
        label: "Net Revenue (£)",
        data: Object.values(revenue),
        backgroundColor: "#4e73df",
      },
    ],
  };
  new Chart(document.getElementById("treatmentBarChart"), {
    type: "bar",
    data,
    options: {
      responsive: true,
      scales: { y: { beginAtZero: true } },
    },
  });
}

export function initSortableTable() {
  const visitTableBody = document.getElementById("visitTableBody");
  if (visitTableBody) {
    Sortable.create(visitTableBody, {
      animation: 150,
      handle: ".drag-handle",
    });
  }
}

export function createRowHTML() {
  return `
    <td class="drag-handle" style="cursor: move;">☰</td>
    <td><input class="form-control date-field" /></td>
    <td><input class="form-control" /></td>
    <td><input class="form-control" /></td>
    <td><input class="form-control amount-field" type="number" /></td>
    <td><input type="checkbox" class="deposit-check" /></td>
    <td>
      <select class="form-control deposit-method" disabled>
        <option value="">--</option>
        <option value="Online">Online</option>
        <option value="In-Store">In-Store</option>
      </select>
    </td>
    <td><input class="form-control net-amount" readonly /></td>
    <td><input class="form-control" /></td>
    <td><input class="form-control" type="number" /></td>
    <td>
      <button class="btn btn-sm btn-primary saveRow">💾</button>
      <span class="save-status ms-2"></span>
      <button class="btn btn-sm btn-danger deleteRow ms-1">🗑️</button>
    </td>`;
}
