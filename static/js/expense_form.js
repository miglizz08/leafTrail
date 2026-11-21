(() => {
  const form = document.querySelector("#form-gasto");
  if (!form) return;

  const fields = {
    descricao: form.elements.descricao,
    valor: form.elements.valor,
    categoria: form.elements.categoria,
    data: form.elements.data,
  };

  const getError = (name, value) => {
    if (name === "descricao") {
      return value.trim() ? "" : "Informe uma descrição para o gasto.";
    }

    if (name === "valor") {
      const normalized = value.trim().replace(/\./g, "").replace(",", ".");
      const amount = Number(normalized);
      return normalized && Number.isFinite(amount) && amount > 0
        ? ""
        : "Informe um valor maior que zero.";
    }

    if (name === "categoria") {
      return value ? "" : "Selecione uma categoria.";
    }

    if (name === "data") {
      return value ? "" : "Informe a data do gasto.";
    }

    return "";
  };

  const validateField = (name) => {
    const field = fields[name];
    const error = getError(name, field.value);
    const message = form.querySelector(`[data-error-for="${name}"]`);

    message.textContent = error;
    field.setAttribute("aria-invalid", String(Boolean(error)));
    return !error;
  };

  Object.entries(fields).forEach(([name, field]) => {
    const eventName = field.tagName === "SELECT" || field.type === "date" ? "change" : "input";
    field.addEventListener(eventName, () => {
      if (field.getAttribute("aria-invalid") === "true") validateField(name);
    });
  });

  form.addEventListener("submit", (event) => {
    const invalidFields = Object.keys(fields).filter((name) => !validateField(name));
    if (!invalidFields.length) return;

    event.preventDefault();
    fields[invalidFields[0]].focus();
  });
})();
