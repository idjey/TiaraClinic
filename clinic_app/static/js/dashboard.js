document.addEventListener("DOMContentLoaded", function () {
  const table = document.querySelector("#visitTable tbody");
  const addRowBtn = document.getElementById("addRowBtn");

  const flatpickrOptions = { dateFormat: "Y-m-d" };

  function initFlatpickrs() {
    document.querySelectorAll(".date-field").forEach((input) => {
      if (!input._flatpickr) flatpickr(input, flatpickrOptions);
    });
  }

  function calculateNet(row) {
    const actual = parseFloat(row.querySelector(".amount-field").value) || 0;
    const isPaid = row.querySelector(".deposit-check").checked;
    const netField = row.querySelector(".net-amount");
    netField.value = isPaid ? (actual - 100).toFixed(2) : actual.toFixed(2);
    updateTotal();
  }

  function updateTotal() {
    let total = 0;
    document.querySelectorAll(".amount-field").forEach((field) => {
      total += parseFloat(field.value) || 0;
    });
    document.getElementById("totalActual").textContent = `£${total.toFixed(2)}`;
  }

  function bindRowEvents(row) {
    flatpickr(row.querySelector(".date-field"), flatpickrOptions);

    const depositCheck = row.querySelector(".deposit-check");
    const depositSelect = row.querySelector(".deposit-method");
    const amountField = row.querySelector(".amount-field");

    depositCheck.addEventListener("change", () => {
      depositSelect.disabled = !depositCheck.checked;
      calculateNet(row);
    });

    amountField.addEventListener("input", () => calculateNet(row));

    row.querySelector(".saveRow").addEventListener("click", () => saveRow(row));
    row.querySelector(".deleteRow").addEventListener("click", () => deleteRow(row));
  }

  function showSaveStatus(row, status) {
    const statusCell = row.querySelector(".save-status");
    if (!statusCell) return;
    statusCell.textContent = status === "success" ? "✅" : "⚠️";
    setTimeout(() => (statusCell.textContent = ""), 2000);
  }

  function animateRow(row, type) {
    if (type === "save") {
      row.classList.add("row-saved");
      setTimeout(() => row.classList.remove("row-saved"), 1200);
    } else if (type === "delete") {
      row.classList.add("fade-out", "row-deleted");
      setTimeout(() => row.remove(), 500);
    }
  }

  function extractRowData(row) {
    const inputs = row.querySelectorAll("input");
    return {
      visit_date: row.querySelector(".date-field").value,
      treatment: inputs[1].value,
      payment_method: inputs[2].value,
      actual_amount: inputs[3].value,
      deposit_paid: row.querySelector(".deposit-check").checked,
      deposit_method: row.querySelector(".deposit-method").value,
      month: inputs[6].value,
      year: inputs[7].value,
    };
  }

  function saveRow(row) {
    const id = row.dataset.id;
    const data = extractRowData(row);
    const url = id ? `/visit/${id}` : `/visit`;
    const method = id ? "PUT" : "POST";

    fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Save failed");
        return res.json();
      })
      .then((json) => {
        if (!id) row.dataset.id = json.id;
        animateRow(row, "save");
        updateTotal();
        showSaveStatus(row, "success");
      })
      .catch(() => {
        showSaveStatus(row, "error");
      });
  }

  function deleteRow(row) {
    const id = row.dataset.id;
    if (!id) return animateRow(row, "delete");

    if (confirm("Delete this row?")) {
      fetch(`/visit/${id}`, { method: "DELETE" })
        .then((res) => {
          if (!res.ok) throw new Error("Delete failed");
          return res.json();
        })
        .then(() => animateRow(row, "delete"))
        .catch(() => alert("Delete failed ❌"));
    }
  }

  function createRowHTML() {
    return `
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
      </td>
    `;
  }

  addRowBtn.addEventListener("click", () => {
    const row = table.insertRow();
    row.innerHTML = createRowHTML();
    row.classList.add("fade-in");
    bindRowEvents(row);
    initFlatpickrs();
  });

  // Init all on load
  table.querySelectorAll("tr").forEach((row) => bindRowEvents(row));
  updateTotal();
  initFlatpickrs();

  // 🌙 Dark Mode Toggle
  const darkToggle = document.getElementById("darkModeToggle");
  if (darkToggle) {
    darkToggle.addEventListener("click", () => {
      document.body.classList.toggle("dark-mode");
    });
  }
});
