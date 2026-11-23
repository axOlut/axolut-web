#!/usr/bin/env python3
"""Génère les pages statiques du site axOlut (français à la racine, anglais dans /en/).

    python3 tools/build.py                 # adresse par défaut (GitHub Pages)
    SITE_URL=https://axolut.com python3 tools/build.py

Les textes sont dans content_main.py et content_services.py ; les pages sont du HTML pur,
lisible par Google sans JavaScript.
"""
import html
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_main import CONTACT, FAFIO_WEB, ICON, SERVICES, STEPS, PLEDGES, FAQ, L  # noqa: E402
from content_services import DETAILS, T  # noqa: E402
from content_pages import P  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE = os.environ.get("SITE_URL", "https://axolut.github.io/axolut-web").rstrip("/")
PAGES = []  # (fr_path, en_path) pour le plan du site


def e(s):
    """Échappe le texte et applique la typographie : apostrophe courbe, espaces fines insécables."""
    s = str(s).replace("'", "’")
    for c in ":;?!":
        s = s.replace(" " + c, " " + c)
    return html.escape(s, quote=True)


def icon(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[name]}</svg>'


# ---------------------------------------------------------------- adresses
def route(lang, key):
    fr = lang == "fr"
    base = "" if fr else "en/"
    if key == "home":
        return base
    if key == "services":
        return base + "services/"
    if key.startswith("svc:"):
        slug = key[4:]
        return base + "services/" + (slug if fr else DETAILS[slug]["en"]) + "/"
    if key == "fafio":
        return base + ("realisations/fafio/" if fr else "work/fafio/")
    if key == "about":
        return base + ("a-propos/" if fr else "about/")
    raise KeyError(key)


def href(cur, target, anchor=""):
    rel = "../" * cur.count("/")
    out = rel + target
    if not out:
        out = "./"
    return out + anchor


def logo(h):
    return f'<a class="logo" href="{h}" aria-label="axOlut">ax<span class="o" aria-hidden="true"></span>lut</a>'


NAV = {
    "fr": [("services", "Services"), ("fafio", "Réalisations"), ("about", "À propos"), ("home#contact", "Contact")],
    "en": [("services", "Services"), ("fafio", "Work"), ("about", "About"), ("home#contact", "Contact")],
}


def link(lang, cur, key):
    k, _, anchor = key.partition("#")
    return href(cur, route(lang, k), "#" + anchor if anchor else "")


# ---------------------------------------------------------------- gabarit commun
def page(lang, cur, other, title, desc, body, lds=(), active=None, scripts=(), hero_dark=True):
    t = L[lang]
    rel = "../" * cur.count("/")
    fr_path, en_path = (cur, other) if lang == "fr" else (other, cur)
    if lang == "fr":
        PAGES.append((fr_path, en_path))
    org = {
        "@context": "https://schema.org", "@type": "ProfessionalService", "@id": f"{SITE}/#org",
        "name": "axOlut", "url": f"{SITE}/", "logo": f"{SITE}/assets/img/icon-512.png", "image": f"{SITE}/assets/img/og.png",
        "description": L[lang]["desc"], "email": CONTACT["email"], "telephone": CONTACT["tel"],
        "address": {"@type": "PostalAddress", "addressLocality": CONTACT["city"], "addressCountry": CONTACT["country"]},
        "areaServed": ["CM", "Africa", "Europe", "North America"], "knowsLanguage": ["fr", "en"],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], "opens": "08:00", "closes": "19:00"}],
    }
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (org, *lds))
    o_lang = "en" if lang == "fr" else "fr"
    o_short, o_long = ("EN", "English") if lang == "fr" else ("FR", "Français")
    o_href = href(cur, other)
    nav = "".join(f'<a href="{link(lang, cur, k)}"{" aria-current=\"page\"" if active == k else ""}>{e(lbl)}</a>' for k, lbl in NAV[lang])
    contact = link(lang, cur, "home#contact")
    home = link(lang, cur, "home")
    svc_links = "".join(f'<li><a href="{link(lang, cur, "svc:" + s[0])}">{e(s[1][lang])}</a></li>' for s in SERVICES[:6])
    nav_links = "".join(f'<li><a href="{link(lang, cur, k)}">{e(lbl)}</a></li>' for k, lbl in NAV[lang])
    js = "".join(f'<script src="{rel}assets/js/{s}" defer></script>' for s in ("site.js", *scripts))
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}/{cur}">
<link rel="alternate" hreflang="fr" href="{SITE}/{fr_path}">
<link rel="alternate" hreflang="en" href="{SITE}/{en_path}">
<link rel="alternate" hreflang="x-default" href="{SITE}/{fr_path}">
<meta name="theme-color" content="#050C1F">
<meta property="og:type" content="website">
<meta property="og:site_name" content="axOlut">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE}/{cur}">
<meta property="og:image" content="{SITE}/assets/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{'fr_FR' if lang == 'fr' else 'en_US'}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{rel}assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{rel}assets/img/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{rel}assets/img/apple-touch-icon.png">
<link rel="manifest" href="{rel}site.webmanifest">
<link rel="preload" href="{rel}assets/fonts/sora.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{rel}assets/fonts/geist.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{rel}assets/css/site.css">
{ld}
</head>
<body>
<a class="skip" href="#main">{e(t['skip'])}</a>
<header class="site-head">
  <div class="wrap head-row">
    {logo(home)}
    <nav class="nav" id="menu" aria-label="{'Principale' if lang == 'fr' else 'Main'}">
      {nav}
      <div class="nav-extra"><a class="btn primary" href="{contact}">{e(t['cta'])}</a><a class="lang" href="{o_href}" hreflang="{o_lang}" lang="{o_lang}">{o_long}</a></div>
    </nav>
    <a class="lang" href="{o_href}" hreflang="{o_lang}" lang="{o_lang}"><span aria-hidden="true">{o_short}</span><span class="sr">{o_long}</span></a>
    <a class="btn primary" href="{contact}">{e(t['cta'])}</a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu"><span class="sr">{e(t['menu'])}</span><span></span><span></span></button>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="dark foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>{logo(home)}<p>{e(t['foot_p'])}</p></div>
      <div><h2>{e(t['foot_nav'])}</h2><ul>{nav_links}</ul></div>
      <div><h2>{e(t['foot_svc'])}</h2><ul>{svc_links}</ul></div>
      <div><h2>{e(t['foot_contact'])}</h2><ul>
        <li><a href="https://wa.me/{CONTACT['wa']}" target="_blank" rel="noopener">WhatsApp</a></li>
        <li><a href="tel:{CONTACT['tel']}">{'Appel' if lang == 'fr' else 'Call'}</a></li>
        <li><a href="mailto:{CONTACT['email']}">{e(CONTACT['email'])}</a></li>
        <li><a href="{contact}">{'Yaoundé, Cameroun' if lang == 'fr' else 'Yaoundé, Cameroon'}</a></li>
      </ul></div>
    </div>
    <div class="foot-base"><span>© <span data-year>2026</span> axOlut. {e(t['rights'])}</span><span>{e(t['made'])}</span></div>
  </div>
</footer>
{js}
</body>
</html>
"""


def svc_rows(lang, cur, items=SERVICES):
    return "".join(f"""
      <li class="svc"><a href="{link(lang, cur, 'svc:' + slug)}"><h3>{e(name[lang])}</h3><p>{e(desc[lang])}</p><span class="go" aria-hidden="true">{icon('arrow')}</span></a></li>"""
                   for slug, name, desc in items)


def steps_html(lang):
    return "".join(f'<li class="step"><h3>{e(a[lang])}</h3><p>{e(b[lang])}</p></li>' for a, b in STEPS)


def cta_band(lang, cur):
    p = P[lang]
    return f"""
<section class="section cta-sec"><div class="wrap">
  <div class="cta-band dark">
    <div><h2>{e(p['cta_h'])}</h2><p class="lead">{e(p['cta_p'])}</p></div>
    <div class="cta-actions">
      <a class="btn primary" href="{link(lang, cur, 'home#contact')}">{e(L[lang]['cta'])}</a>
      <a class="btn ghost" href="https://wa.me/{CONTACT['wa']}" target="_blank" rel="noopener">{icon('wa')}WhatsApp</a>
    </div>
  </div>
</div></section>"""


def page_hero(lang, cur, crumbs, h1, lead, actions=""):
    """En-tête des pages intérieures, avec fil d'Ariane."""
    items = [(L[lang]["home_crumb"] if "home_crumb" in L[lang] else ("Accueil" if lang == "fr" else "Home"), route(lang, "home"))] + crumbs
    nav = "".join(
        (f'<li><a href="{href(cur, p)}">{e(n)}</a></li>' if p is not None and p != cur else f'<li aria-current="page">{e(n)}</li>')
        for n, p in items)
    return f"""
<section class="page-hero dark">
  <div class="ring-deco" aria-hidden="true"></div>
  <div class="wrap">
    <nav class="crumbs" aria-label="{'Fil d’Ariane' if lang == 'fr' else 'Breadcrumb'}"><ol>{nav}</ol></nav>
    <h1>{e(h1)}</h1>
    <p class="lead">{e(lead)}</p>
    {actions}
  </div>
</section>"""


def crumbs_ld(lang, items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": f"{SITE}/{p}"} for i, (n, p) in enumerate(items)]}


# ---------------------------------------------------------------- accueil
def home(lang):
    t = L[lang]
    cur = route(lang, "home")
    other = route("en" if lang == "fr" else "fr", "home")
    rel = "../" * cur.count("/")
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q[lang], "acceptedAnswer": {"@type": "Answer", "text": a[lang]}} for q, a in FAQ]}
    site_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "axOlut", "url": f"{SITE}/", "inLanguage": ["fr", "en"], "publisher": {"@id": f"{SITE}/#org"}}

    h1 = "".join(f'<span class="l" aria-hidden="true">{e(x)}</span>' for x in t["h1"])
    foot = "".join(f"<span>{icon(i)}{e(x)}</span>" for i, x in t["hero_foot"])
    facts = "".join(f"<div><dt>{a}</dt><dd>{e(b)}</dd></div>" for a, b in t["facts"])
    cards = "".join(f'<button class="fan-card{" front" if i == 1 else ""}" type="button"><img src="{rel}assets/img/fafio-cv-{m}.webp" alt="{e(alt)}" width="900" height="1273" loading="lazy" decoding="async"></button>'
                    for i, (m, alt) in enumerate(zip(["band", "center", "dark", "light"], t["fan_alt"])))
    pledges = "".join(f'<li class="pledge">{icon(i)}<h3>{e(a[lang])}</h3><p>{e(b[lang])}</p></li>' for i, a, b in PLEDGES)
    faq = "".join(f"<details><summary>{e(q[lang])}</summary><p>{e(a[lang])}</p></details>" for q, a in FAQ)
    clock_where, c_open, c_closed = t["clock"]
    hrefs = {"wa": f"https://wa.me/{CONTACT['wa']}", "phone": f"tel:{CONTACT['tel']}", "mail": f"mailto:{CONTACT['email']}"}
    ways = "".join(f'<li><a href="{hrefs[i]}"{" target=\"_blank\" rel=\"noopener\"" if i == "wa" else ""}>{icon(i)}<span><strong>{e(a)}</strong><small>{e(b)}</small></span></a></li>' for i, a, b in t["ways"])
    chips_t = "".join(f'<label class="chip"><input type="checkbox" name="type" value="{e(x)}"><span>{e(x)}</span></label>' for x in t["b_types"])
    chips_w = "".join(f'<label class="chip"><input type="radio" name="when" value="{e(x)}"><span>{e(x)}</span></label>' for x in t["b_whens"])
    fafio = link(lang, cur, "fafio")

    body = f"""
<section class="hero dark" aria-labelledby="h1">
  <canvas class="hero-canvas" data-ring aria-hidden="true"></canvas>
  <div class="ring-css" aria-hidden="true"></div>
  <div class="wrap">
    <div class="hero-text">
      <h1 id="h1"><span class="sr">{e(t['h1_sr'])}</span>{h1}</h1>
      <p class="lead">{e(t['lead'])}</p>
      <div class="hero-actions">
        <a class="btn primary" href="#contact">{e(t['cta'])}</a>
        <a class="btn ghost" href="#realisations">{e(t['see_work'])}</a>
      </div>
      <div class="hero-foot">{foot}</div>
    </div>
  </div>
</section>

<section class="section" id="services" aria-labelledby="svc-h">
  <div class="wrap">
    <div class="section-head"><h2 id="svc-h">{e(t['svc_h'])}</h2><p class="lead">{e(t['svc_lead'])}</p></div>
    <ul class="services">{svc_rows(lang, cur)}
    </ul>
  </div>
</section>

<section class="section tight" id="realisations" aria-labelledby="work-h">
  <div class="wrap">
    <div class="section-head"><h2 id="work-h">{e(t['work_h'])}</h2><p class="lead">{e(t['work_lead'])}</p></div>
    <article class="case">
      <div class="case-grid">
        <div>
          <div class="case-brand"><img src="{rel}assets/img/fafio-icon.webp" alt="" width="104" height="104" loading="lazy"><div><strong>FAFIO</strong>{e(t['case_tag'])}</div></div>
          <h3 class="h2like">{e(t['case_h'])}</h3>
          <p class="lead">{e(t['case_lead'])}</p>
          <dl class="facts">{facts}</dl>
          <div class="case-actions"><a class="btn primary" href="{fafio}">{e(P[lang]['case_more'])}</a><a class="btn ghost" href="{FAFIO_WEB}" target="_blank" rel="noopener">{e(t['case_try'])}</a></div>
        </div>
        <div class="case-visual">
          <div class="fan" data-fan>{cards}</div>
          <div class="phone"><img src="{rel}assets/img/fafio-welcome.webp" alt="{e(t['phone_alt'])}" width="780" height="1688" loading="lazy" decoding="async"></div>
          <p class="fan-hint">{e(t['fan_hint'])}</p>
        </div>
      </div>
    </article>
  </div>
</section>

<section class="section tight" id="methode" aria-labelledby="steps-h">
  <div class="wrap">
    <div class="section-head"><h2 id="steps-h">{e(t['steps_h'])}</h2><p class="lead">{e(t['steps_lead'])}</p></div>
    <ol class="steps">{steps_html(lang)}</ol>
  </div>
</section>

<section class="dark"><div class="section">
  <div class="wrap approach">
    <div class="approach-intro"><h2>{e(t['appr_h'])}</h2><p class="lead">{e(t['appr_lead'])}</p></div>
    <ul class="pledges">{pledges}</ul>
  </div>
</div></section>

<section class="section" aria-labelledby="faq-h">
  <div class="wrap">
    <div class="section-head"><h2 id="faq-h">{e(t['faq_h'])}</h2></div>
    <div class="faq">{faq}</div>
  </div>
</section>

<section class="dark" id="contact" aria-labelledby="contact-h"><div class="section">
  <div class="wrap contact-grid">
    <div>
      <h2 id="contact-h">{e(t['contact_h'])}</h2>
      <p class="lead spaced">{e(t['contact_lead'])}</p>
      <ul class="contact-ways">{ways}</ul>
      <p class="clock" data-clock><i></i><span><span data-time>--:--</span> {e(clock_where)}, <span data-status data-open="{e(c_open)}" data-closed="{e(c_closed)}">{e(c_open)}</span></span></p>
    </div>
    <form class="brief" data-brief data-wa="{CONTACT['wa']}" data-mail="{CONTACT['email']}">
      <fieldset><legend>{e(t['b_type'])}</legend><div class="chips">{chips_t}</div></fieldset>
      <fieldset><legend>{e(t['b_when'])}</legend><div class="chips">{chips_w}</div></fieldset>
      <div class="brief-row">
        <div><label class="t" for="b-name">{e(t['b_name'])}</label><input class="field" id="b-name" name="name" autocomplete="name" placeholder="{e(t['b_name_ph'])}"></div>
        <div><label class="t" for="b-idea">{e(t['b_idea'])}</label><textarea class="field" id="b-idea" name="idea" placeholder="{e(t['b_idea_ph'])}"></textarea></div>
      </div>
      <div class="brief-actions">
        <button class="btn primary" type="submit" value="wa">{icon('wa')}{e(t['b_wa'])}</button>
        <button class="btn ghost" type="submit" value="mail">{icon('mail')}{e(t['b_mail'])}</button>
      </div>
      <p class="brief-note">{e(t['b_note'])}</p>
    </form>
  </div>
</div></section>"""
    return page(lang, cur, other, t["title"], t["desc"], body, (site_ld, faq_ld), scripts=("ring.js",))


# ---------------------------------------------------------------- services
def services_index(lang):
    p = P[lang]
    cur, other = route(lang, "services"), route("en" if lang == "fr" else "fr", "services")
    home_n = "Accueil" if lang == "fr" else "Home"
    body = page_hero(lang, cur, [(p["svc_h1_short"], cur)], p["svc_h1"], p["svc_lead"]) + f"""
<section class="section">
  <div class="wrap">
    <ul class="services">{svc_rows(lang, cur)}
    </ul>
  </div>
</section>
<section class="section tight">
  <div class="wrap">
    <div class="section-head"><h2>{e(L[lang]['steps_h'])}</h2><p class="lead">{e(L[lang]['steps_lead'])}</p></div>
    <ol class="steps">{steps_html(lang)}</ol>
  </div>
</section>""" + cta_band(lang, cur)
    lds = (crumbs_ld(lang, [(home_n, route(lang, "home")), (p["svc_h1_short"], cur)]),)
    return page(lang, cur, other, p["svc_title"], p["svc_desc"], body, lds, active="services")


def service_page(lang, slug):
    d = DETAILS[slug]
    p = P[lang]
    name = next(s[1][lang] for s in SERVICES if s[0] == slug)
    cur = route(lang, "svc:" + slug)
    other = route("en" if lang == "fr" else "fr", "svc:" + slug)
    home_n = "Accueil" if lang == "fr" else "Home"
    crumbs = [(p["svc_h1_short"], route(lang, "services")), (name, cur)]
    actions = f'<div class="hero-actions"><a class="btn primary" href="{link(lang, cur, "home#contact")}">{e(L[lang]["cta"])}</a><a class="btn ghost" href="https://wa.me/{CONTACT["wa"]}" target="_blank" rel="noopener">{icon("wa")}WhatsApp</a></div>'
    items = "".join(f'<li><h3>{e(a[lang])}</h3><p>{e(b[lang])}</p></li>' for a, b in d["items"])
    for_ = "".join(f"<li>{icon('check')}<span>{e(x)}</span></li>" for x in d["for"][lang])
    idx = [s[0] for s in SERVICES].index(slug)
    related = [SERVICES[(idx + k) % len(SERVICES)] for k in (1, 2, 3)]
    fafio_note = ""
    if slug in ("applications-mobiles", "intelligence-artificielle", "documents-professionnels", "sites-web"):
        fafio_note = f"""
<section class="section tight"><div class="wrap">
  <a class="mini-case" href="{link(lang, cur, 'fafio')}">
    <img src="{'../' * cur.count('/')}assets/img/fafio-icon.webp" alt="" width="104" height="104" loading="lazy">
    <span><strong>{e(p['mini_case_t'])}</strong><span>{e(p['mini_case_p'])}</span></span>
    <span class="go" aria-hidden="true">{icon('arrow')}</span>
  </a>
</div></section>"""
    body = page_hero(lang, cur, crumbs, d["h1"][lang], d["lead"][lang], actions) + f"""
<section class="section">
  <div class="wrap split">
    <div><h2>{e(p['svc_why'])}</h2><p class="prose">{e(d['intro'][lang])}</p></div>
    <aside class="for"><h2 class="h-small">{e(p['svc_for'])}</h2><ul>{for_}</ul></aside>
  </div>
</section>
<section class="section tight">
  <div class="wrap">
    <div class="section-head"><h2>{e(p['svc_deliver'])}</h2></div>
    <ul class="deliver">{items}</ul>
  </div>
</section>{fafio_note}
<section class="section tight">
  <div class="wrap">
    <div class="section-head"><h2>{e(L[lang]['steps_h'])}</h2><p class="lead">{e(L[lang]['steps_lead'])}</p></div>
    <ol class="steps">{steps_html(lang)}</ol>
  </div>
</section>
<section class="section tight">
  <div class="wrap">
    <div class="section-head"><h2>{e(p['svc_related'])}</h2></div>
    <ul class="services">{svc_rows(lang, cur, related)}
    </ul>
  </div>
</section>""" + cta_band(lang, cur)
    svc_ld = {"@context": "https://schema.org", "@type": "Service", "name": d["h1"][lang], "description": d["desc"][lang],
              "provider": {"@id": f"{SITE}/#org"}, "areaServed": ["CM", "Africa", "Europe", "North America"], "url": f"{SITE}/{cur}"}
    lds = (svc_ld, crumbs_ld(lang, [(home_n, route(lang, "home")), (p["svc_h1_short"], route(lang, "services")), (name, cur)]))
    return page(lang, cur, other, d["title"][lang], d["desc"][lang], body, lds, active="services")


# ---------------------------------------------------------------- FAFIO
def fafio_page(lang):
    p = P[lang]
    t = L[lang]
    cur, other = route(lang, "fafio"), route("en" if lang == "fr" else "fr", "fafio")
    rel = "../" * cur.count("/")
    home_n = "Accueil" if lang == "fr" else "Home"
    crumbs = [(p["work_crumb"], None), ("FAFIO", cur)]
    actions = f'<div class="hero-actions"><a class="btn primary" href="{FAFIO_WEB}" target="_blank" rel="noopener">{e(t["case_try"])}</a><a class="btn ghost" href="{link(lang, cur, "home#contact")}">{e(p["fafio_like"])}</a></div>'
    facts = "".join(f"<div><dt>{a}</dt><dd>{e(b)}</dd></div>" for a, b in p["fafio_facts"])
    feats = "".join(f'<li><h3>{e(a)}</h3><p>{e(b)}</p></li>' for a, b in p["fafio_feats"])
    shots = "".join(f'<figure class="shot"><div class="phone static"><img src="{rel}assets/img/fafio-{n}.webp" alt="{e(cap)}" width="780" height="1688" loading="lazy" decoding="async"></div><figcaption>{e(cap)}</figcaption></figure>'
                    for n, cap in p["fafio_shots"])
    cvs = "".join(f'<figure><img src="{rel}assets/img/fafio-cv-{m}.webp" alt="{e(a)}" width="900" height="1273" loading="lazy" decoding="async"><figcaption>{e(c)}</figcaption></figure>'
                  for m, a, c in zip(["band", "center", "dark", "light"], t["fan_alt"], p["fafio_cv_caps"]))
    stack = "".join(f"<li>{e(x)}</li>" for x in p["fafio_stack"])
    body = page_hero(lang, cur, crumbs, p["fafio_h1"], p["fafio_lead"], actions) + f"""
<section class="section">
  <div class="wrap">
    <dl class="facts light">{facts}</dl>
    <div class="split" style="margin-top:72px">
      <div><h2>{e(p['fafio_problem_h'])}</h2><p class="prose">{e(p['fafio_problem'])}</p></div>
      <div><h2>{e(p['fafio_answer_h'])}</h2><p class="prose">{e(p['fafio_answer'])}</p></div>
    </div>
  </div>
</section>
<section class="dark"><div class="section">
  <div class="wrap">
    <div class="section-head"><h2>{e(p['fafio_screens_h'])}</h2><p class="lead">{e(p['fafio_screens_p'])}</p></div>
    <div class="shots">{shots}</div>
  </div>
</div></section>
<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>{e(p['fafio_feats_h'])}</h2></div>
    <ul class="deliver">{feats}</ul>
  </div>
</section>
<section class="section tight">
  <div class="wrap">
    <div class="section-head"><h2>{e(p['fafio_cv_h'])}</h2><p class="lead">{e(p['fafio_cv_p'])}</p></div>
    <div class="cv-grid">{cvs}</div>
  </div>
</section>
<section class="section tight">
  <div class="wrap split">
    <div><h2>{e(p['fafio_tech_h'])}</h2><p class="prose">{e(p['fafio_tech'])}</p></div>
    <ul class="tags">{stack}</ul>
  </div>
</section>""" + cta_band(lang, cur)
    app_ld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "FAFIO", "applicationCategory": "BusinessApplication",
              "operatingSystem": "Android, Web", "url": FAFIO_WEB, "description": p["fafio_lead"], "inLanguage": ["fr", "en", "ar"],
              "creator": {"@id": f"{SITE}/#org"}, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "XAF"}}
    lds = (app_ld, crumbs_ld(lang, [(home_n, route(lang, "home")), ("FAFIO", cur)]))
    return page(lang, cur, other, p["fafio_title"], p["fafio_desc"], body, lds, active="fafio")


# ---------------------------------------------------------------- à propos
def about_page(lang):
    p = P[lang]
    cur, other = route(lang, "about"), route("en" if lang == "fr" else "fr", "about")
    home_n = "Accueil" if lang == "fr" else "Home"
    values = "".join(f'<li class="pledge">{icon(i)}<h3>{e(a)}</h3><p>{e(b)}</p></li>' for i, a, b in p["about_values"])
    body = page_hero(lang, cur, [(p["about_crumb"], cur)], p["about_h1"], p["about_lead"]) + f"""
<section class="section">
  <div class="wrap split">
    <div><h2>{e(p['about_story_h'])}</h2></div>
    <div class="prose-block">{''.join(f'<p class="prose">{e(x)}</p>' for x in p['about_story'])}</div>
  </div>
</section>
<section class="dark"><div class="section">
  <div class="wrap approach">
    <div class="approach-intro"><h2>{e(p['about_values_h'])}</h2><p class="lead">{e(p['about_values_p'])}</p></div>
    <ul class="pledges">{values}</ul>
  </div>
</div></section>
<section class="section">
  <div class="wrap split">
    <div><h2>{e(p['about_where_h'])}</h2></div>
    <div class="prose-block"><p class="prose">{e(p['about_where'])}</p></div>
  </div>
</section>""" + cta_band(lang, cur)
    lds = (crumbs_ld(lang, [(home_n, route(lang, "home")), (p["about_crumb"], cur)]),)
    return page(lang, cur, other, p["about_title"], p["about_desc"], body, lds, active="about")


# ---------------------------------------------------------------- 404
def not_found():
    p = P["fr"]
    # Page servie à n'importe quelle profondeur : liens absolus depuis la racine du site
    base = SITE.split("://", 1)[1].split("/", 1)
    root = "/" + (base[1] + "/" if len(base) > 1 and base[1] else "")
    html_ = f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page introuvable | axOlut</title><meta name="robots" content="noindex">
<link rel="icon" href="{root}assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{root}assets/css/site.css"></head>
<body class="dark nf">
<main class="wrap nf-main">
  <a class="logo" href="{root}" aria-label="axOlut">ax<span class="o" aria-hidden="true"></span>lut</a>
  <h1>{e(p['nf_h'])}</h1>
  <p class="lead">{e(p['nf_p'])}</p>
  <p lang="en" class="lead en">This page doesn't exist or has moved.</p>
  <div class="hero-actions"><a class="btn primary" href="{root}">{e(p['nf_home'])}</a><a class="btn ghost" href="{root}en/">English site</a></div>
</main>
</body></html>
"""
    return html_


# ---------------------------------------------------------------- écriture
def write(rel_path, text):
    p = ROOT / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def main():
    for lang in ("fr", "en"):
        write(route(lang, "home") + "index.html", home(lang))
        write(route(lang, "services") + "index.html", services_index(lang))
        for slug in DETAILS:
            write(route(lang, "svc:" + slug) + "index.html", service_page(lang, slug))
        write(route(lang, "fafio") + "index.html", fafio_page(lang))
        write(route(lang, "about") + "index.html", about_page(lang))
    write("404.html", not_found())
    urls = "".join(f"<url><loc>{SITE}/{fr}</loc>"
                   f'<xhtml:link rel="alternate" hreflang="fr" href="{SITE}/{fr}"/>'
                   f'<xhtml:link rel="alternate" hreflang="en" href="{SITE}/{en}"/></url>'
                   f"<url><loc>{SITE}/{en}</loc>"
                   f'<xhtml:link rel="alternate" hreflang="fr" href="{SITE}/{fr}"/>'
                   f'<xhtml:link rel="alternate" hreflang="en" href="{SITE}/{en}"/></url>' for fr, en in PAGES)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">{urls}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    print("ok", SITE, len(PAGES) * 2, "pages")


if __name__ == "__main__":
    main()
