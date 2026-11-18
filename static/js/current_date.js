(() => {
  const dateFormatter = new Intl.DateTimeFormat("pt-BR", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "America/Sao_Paulo",
  });

  const updateCurrentDates = () => {
    const currentDate = dateFormatter.format(new Date());
    document.querySelectorAll("[data-current-date]").forEach((element) => {
      element.textContent = currentDate;
    });
  };

  updateCurrentDates();
  window.setInterval(updateCurrentDates, 60_000);
})();
