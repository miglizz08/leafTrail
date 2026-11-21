(() => {
  const toggle = document.querySelector(".menu-toggle");
  const navigation = document.querySelector(".sidebar");

  if (!toggle || !navigation) return;

  const setExpanded = (expanded) => {
    toggle.setAttribute("aria-expanded", String(expanded));
    toggle.setAttribute("aria-label", expanded ? "Fechar menu" : "Abrir menu");
    navigation.classList.toggle("is-open", expanded);
  };

  toggle.addEventListener("click", () => {
    setExpanded(toggle.getAttribute("aria-expanded") !== "true");
  });

  navigation.addEventListener("click", (event) => {
    if (event.target.closest("a")) setExpanded(false);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setExpanded(false);
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth >= 768) setExpanded(false);
  });
})();
