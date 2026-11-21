(() => {
  const dialog = document.querySelector(".delete-dialog");
  if (!dialog) return;

  let pendingForm = null;
  const expenseName = dialog.querySelector("[data-delete-expense-name]");

  document.querySelectorAll("[data-delete-trigger]").forEach((trigger) => {
    trigger.addEventListener("click", () => {
      pendingForm = trigger.closest("form[data-delete-form]");
      if (!pendingForm) return;

      expenseName.textContent = pendingForm.dataset.expenseName || "este gasto";
      dialog.showModal();
    });
  });

  dialog.addEventListener("close", () => {
    if (dialog.returnValue === "confirm" && pendingForm) {
      pendingForm.requestSubmit();
    }
    pendingForm = null;
  });
})();
