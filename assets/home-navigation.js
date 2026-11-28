const menu = document.getElementById("navbarCollapse");
const toggle = document.querySelector('[aria-controls="navbarCollapse"]');

menu?.addEventListener("click", (event) => {
  const link = event.target.closest("a[href]");
  if (!link || !menu.classList.contains("show") || link.origin !== location.origin ||
      link.pathname !== location.pathname || !link.hash ||
      event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;

  const target = document.getElementById(link.hash.slice(1));
  if (!target) return;

  event.preventDefault();
  menu.addEventListener("hidden.bs.collapse", () => {
    if (location.hash !== link.hash) history.pushState(null, "", link.hash);
    target.tabIndex = -1;
    target.focus({ preventScroll: true });
    target.scrollIntoView();
  }, { once: true });
  toggle.click();
});

menu?.addEventListener("keydown", (event) => {
  if (event.key !== "Escape" || !menu.classList.contains("show") ||
      menu.querySelector(".dropdown-menu.show")) return;

  event.preventDefault();
  toggle.click();
  toggle.focus();
});
