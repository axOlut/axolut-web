// En-tête, menu mobile, heure de Yaoundé et formulaire « Parlons de votre projet ».
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const lang = document.documentElement.lang === "en" ? "en" : "fr";

  // En-tête : fond plein dès qu'on a quitté le haut de la page
  const head = $(".site-head");
  const onScroll = () => head && head.classList.toggle("solid", scrollY > 24);
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Menu mobile
  const btn = $(".menu-btn"), nav = $("#menu");
  if (btn && nav) {
    const set = (open) => {
      btn.setAttribute("aria-expanded", String(open));
      document.body.classList.toggle("menu-open", open);
    };
    btn.addEventListener("click", () => set(btn.getAttribute("aria-expanded") !== "true"));
    $$("a", nav).forEach((a) => a.addEventListener("click", () => set(false)));
    addEventListener("keydown", (e) => { if (e.key === "Escape") set(false); });
  }

  // Heure à Yaoundé (UTC+1, sans heure d'été)
  const clocks = $$("[data-clock]");
  if (clocks.length) {
    const fmt = new Intl.DateTimeFormat(lang === "en" ? "en-GB" : "fr-FR", { hour: "2-digit", minute: "2-digit", timeZone: "Africa/Douala" });
    const hourFmt = new Intl.DateTimeFormat("en-GB", { hour: "numeric", hourCycle: "h23", timeZone: "Africa/Douala" });
    const dayFmt = new Intl.DateTimeFormat("en-GB", { weekday: "short", timeZone: "Africa/Douala" });
    const tick = () => {
      const now = new Date();
      const hr = +hourFmt.format(now), day = dayFmt.format(now);
      const open = day !== "Sun" && hr >= 8 && hr < 19;
      clocks.forEach((c) => {
        $("[data-time]", c).textContent = fmt.format(now);
        c.classList.toggle("open", open);
        const st = $("[data-status]", c);
        if (st) st.textContent = open ? st.dataset.open : st.dataset.closed;
      });
    };
    tick();
    setInterval(tick, 20000);
  }

  // Formulaire de projet : construit un message prêt à envoyer sur WhatsApp ou par e-mail
  const form = $("[data-brief]");
  if (form) {
    const wa = form.dataset.wa, mail = form.dataset.mail;
    const L = lang === "en"
      ? { hello: "Hello axOlut,", type: "Project", when: "Timing", name: "Name", idea: "Idea", subject: "New project" }
      : { hello: "Bonjour axOlut,", type: "Projet", when: "Délai", name: "Nom", idea: "Idée", subject: "Nouveau projet" };
    const message = () => {
      const fd = new FormData(form);
      const lines = [L.hello, ""];
      const type = fd.getAll("type").join(", ");
      if (type) lines.push(`${L.type} : ${type}`);
      if (fd.get("when")) lines.push(`${L.when} : ${fd.get("when")}`);
      if ((fd.get("name") || "").trim()) lines.push(`${L.name} : ${fd.get("name").trim()}`);
      if ((fd.get("idea") || "").trim()) lines.push("", `${L.idea} :`, fd.get("idea").trim());
      return lines.join("\n");
    };
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const via = e.submitter && e.submitter.value === "mail" ? "mail" : "wa";
      const text = message();
      const url = via === "mail"
        ? `mailto:${mail}?subject=${encodeURIComponent(L.subject)}&body=${encodeURIComponent(text)}`
        : `https://wa.me/${wa}?text=${encodeURIComponent(text)}`;
      if (via === "mail") location.href = url; else window.open(url, "_blank", "noopener");
    });
  }

  // Galerie des modèles FAFIO : un modèle à l'avant, au toucher
  $$("[data-fan]").forEach((fan) => {
    const cards = $$(".fan-card", fan);
    cards.forEach((c, i) => c.addEventListener("click", () => {
      cards.forEach((x) => x.classList.remove("front"));
      c.classList.add("front");
    }));
  });

  $$("[data-year]").forEach((y) => (y.textContent = new Date().getFullYear()));
})();
