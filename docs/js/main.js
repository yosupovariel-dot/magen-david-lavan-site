/* מגן דוד לבן — התנהגות האתר. ללא ספריות חיצוניות. */
(function () {
  "use strict";

  var root = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function motionOff() { return reduceMotion || root.classList.contains("a11y-motion"); }

  /* ---------- כותרת דביקה ---------- */
  var header = document.querySelector(".header");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------- תפריט נייד (מסך מלא) ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var mnav = document.getElementById("mnav");
  var lastFocus = null;
  function focusables() {
    return Array.prototype.slice.call(mnav.querySelectorAll("a[href], button:not([disabled])"));
  }
  function openMenu() {
    lastFocus = document.activeElement;
    mnav.hidden = false;
    root.classList.add("no-scroll");
    toggle.setAttribute("aria-expanded", "true");
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () { mnav.classList.add("is-open"); });
    });
    var close = mnav.querySelector(".mnav__close");
    if (close) close.focus();
  }
  function closeMenu(restore) {
    if (mnav.hidden) return;
    mnav.classList.remove("is-open");
    root.classList.remove("no-scroll");
    toggle.setAttribute("aria-expanded", "false");
    window.setTimeout(function () { mnav.hidden = true; }, motionOff() ? 0 : 320);
    if (restore !== false && lastFocus) lastFocus.focus();
  }
  if (toggle && mnav) {
    toggle.addEventListener("click", openMenu);
    mnav.querySelector(".mnav__close").addEventListener("click", function () { closeMenu(); });
    mnav.addEventListener("click", function (ev) {
      if (ev.target.closest("a[href]")) closeMenu(false);
    });
    mnav.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") { ev.preventDefault(); closeMenu(); return; }
      if (ev.key !== "Tab") return;
      var f = focusables(); if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (ev.shiftKey && document.activeElement === first) { ev.preventDefault(); last.focus(); }
      else if (!ev.shiftKey && document.activeElement === last) { ev.preventDefault(); first.focus(); }
    });
    window.matchMedia("(min-width: 1081px)").addEventListener("change", function (m) { if (m.matches) closeMenu(false); });
  }

  /* ---------- קרוסלת המלצות ---------- */
  document.querySelectorAll("[data-rail]").forEach(function (rail) {
    var list = rail.querySelector(".quotes--rail");
    var prev = rail.querySelector('[data-dir="prev"]');
    var next = rail.querySelector('[data-dir="next"]');
    var fill = rail.querySelector(".rail__fill");
    var cur = rail.querySelector(".rail__cur");
    var tot = rail.querySelector(".rail__total");
    function step() {
      var it = list.querySelector(".quote:not([hidden])");
      if (!it) return list.clientWidth || 1;
      var gap = parseFloat(getComputedStyle(list).columnGap) || 0;
      var unit = it.offsetWidth + gap;
      return Math.max(1, Math.round((list.clientWidth + gap) / unit)) * unit;
    }
    function pages() { return Math.max(1, Math.ceil((list.scrollWidth - list.clientWidth) / step() - 0.05) + 1); }
    function page() { return Math.min(pages(), Math.round(Math.abs(list.scrollLeft) / step()) + 1); }
    function update() {
      var max = list.scrollWidth - list.clientWidth;
      var pos = Math.abs(list.scrollLeft);
      var n = pages(), i = (max > 4 && pos > max - 4) ? n : page();
      fill.style.transform = "scaleX(" + i / n + ")";
      cur.textContent = String(i);
      if (tot) tot.textContent = String(n);
      prev.disabled = pos < 4;
      next.disabled = max <= 4 || pos > max - 4;
    }
    function go(dir) {
      list.scrollBy({ left: -dir * step(), behavior: motionOff() ? "auto" : "smooth" });
    }
    prev.addEventListener("click", function () { go(-1); });
    next.addEventListener("click", function () { go(1); });
    var raf = 0;
    list.addEventListener("scroll", function () {
      if (raf) return;
      raf = window.requestAnimationFrame(function () { raf = 0; update(); });
    }, { passive: true });
    window.addEventListener("resize", update);
    rail.addEventListener("rail:refresh", function () { list.scrollLeft = 0; update(); });
    update();
  });

  /* ---------- גלריה: לשוניות + תצוגה מוגדלת ---------- */
  var gtabs = Array.prototype.slice.call(document.querySelectorAll(".gtab"));
  function selectTab(t, focus) {
    gtabs.forEach(function (x) {
      var on = x === t;
      x.setAttribute("aria-selected", String(on));
      x.tabIndex = on ? 0 : -1;
      document.getElementById(x.getAttribute("aria-controls")).hidden = !on;
    });
    if (focus) t.focus();
  }
  gtabs.forEach(function (t, i) {
    t.addEventListener("click", function () { selectTab(t); });
    t.addEventListener("keydown", function (ev) {
      var n = null;
      if (ev.key === "ArrowLeft") n = gtabs[(i + 1) % gtabs.length];
      else if (ev.key === "ArrowRight") n = gtabs[(i - 1 + gtabs.length) % gtabs.length];
      else if (ev.key === "Home") n = gtabs[0];
      else if (ev.key === "End") n = gtabs[gtabs.length - 1];
      if (n) { ev.preventDefault(); selectTab(n, true); }
    });
  });

  var lb = document.getElementById("lightbox");
  if (lb) {
    var lbImg = lb.querySelector(".lb__img"), lbCap = lb.querySelector(".lb__cap");
    var set = [], pos = 0, opener = null;
    function show(i) {
      pos = (i + set.length) % set.length;
      var a = set[pos];
      lbImg.src = a.getAttribute("href");
      lbImg.alt = a.querySelector("img").alt;
      lbCap.textContent = (pos + 1) + " / " + set.length;
    }
    function close() {
      lb.hidden = true; root.classList.remove("no-scroll"); lbImg.removeAttribute("src");
      if (opener) opener.focus();
    }
    document.addEventListener("click", function (ev) {
      var a = ev.target.closest("a[data-lightbox]");
      if (!a) return;
      ev.preventDefault();
      opener = a;
      set = Array.prototype.slice.call(document.querySelectorAll('a[data-lightbox="' + a.getAttribute("data-lightbox") + '"]'));
      show(set.indexOf(a));
      lb.hidden = false; root.classList.add("no-scroll");
      lb.querySelector(".lb__close").focus();
    });
    lb.querySelector(".lb__close").addEventListener("click", close);
    lb.querySelector(".lb__nav--prev").addEventListener("click", function () { show(pos - 1); });
    lb.querySelector(".lb__nav--next").addEventListener("click", function () { show(pos + 1); });
    lb.addEventListener("click", function (ev) { if (ev.target === lb) close(); });
    lb.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") close();
      else if (ev.key === "ArrowLeft") show(pos + 1);
      else if (ev.key === "ArrowRight") show(pos - 1);
      else if (ev.key === "Tab") {
        var f = Array.prototype.slice.call(lb.querySelectorAll("button"));
        var i = f.indexOf(document.activeElement);
        ev.preventDefault();
        f[(i + (ev.shiftKey ? -1 : 1) + f.length) % f.length].focus();
      }
    });
    var tx = null;
    lb.addEventListener("touchstart", function (ev) { tx = ev.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (ev) {
      if (tx === null) return;
      var dx = ev.changedTouches[0].clientX - tx; tx = null;
      if (Math.abs(dx) > 50) show(pos + (dx > 0 ? 1 : -1));
    });
  }

  /* ---------- מונים ---------- */
  var counters = document.querySelectorAll(".count[data-to]");
  function fmt(n) { return n.toLocaleString("en-US"); }
  function runCounter(el) {
    var to = parseInt(el.getAttribute("data-to"), 10) || 0;
    if (motionOff()) { el.textContent = fmt(to); return; }
    var start = null, dur = 1600;
    function step(t) {
      if (!start) start = t;
      var p = Math.min((t - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(Math.round(to * eased));
      if (p < 1) window.requestAnimationFrame(step);
    }
    window.requestAnimationFrame(step);
  }

  /* ---------- חשיפה בגלילה ---------- */
  var revealSel = ".sec-head, .intro__grid > *, .arena, .stat, .chain__step, .dcard, .bento__item, .video__grid > *, .pillar, .leader, .track, .pay__item, .line, .dline, .album, .district__head, .strip figure";
  var revealEls = Array.prototype.filter.call(document.querySelectorAll(revealSel), function (el) {
    return !el.closest(".quotes--rail");
  });
  if ("IntersectionObserver" in window && !motionOff()) {
    revealEls.forEach(function (el, i) {
      el.setAttribute("data-reveal", "");
      el.style.transitionDelay = (i % 4) * 70 + "ms";
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        el.classList.add("is-in");
        io.unobserve(el);
        window.setTimeout(function () { el.style.transitionDelay = ""; }, 1100);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    revealEls.forEach(function (el) { io.observe(el); });

    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        runCounter(en.target);
        co.unobserve(en.target);
      });
    }, { threshold: 0.4 });
    counters.forEach(function (c) { c.textContent = "0"; co.observe(c); });
  }

  /* ---------- וידאו: טעינה רק לאחר לחיצה (פרטיות + ביצועים) ---------- */
  document.querySelectorAll(".vframe[data-yt]").forEach(function (box) {
    var btn = box.querySelector(".vframe__play");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var id = box.getAttribute("data-yt");
      if (!/^[A-Za-z0-9_-]{6,20}$/.test(id)) return;
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0";
      f.title = box.getAttribute("data-title") || "סרטון";
      f.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
      f.setAttribute("allowfullscreen", "");
      f.setAttribute("referrerpolicy", "strict-origin-when-cross-origin");
      f.setAttribute("sandbox", "allow-scripts allow-same-origin allow-presentation allow-popups");
      box.classList.add("is-playing");
      btn.remove();
      var img = box.querySelector("img");
      if (img) img.remove();
      box.appendChild(f);
      f.focus();
    });
  });

  /* ---------- חיפוש סיירות ---------- */
  var search = document.getElementById("city-search");
  if (search) {
    var status = document.getElementById("city-search-status");
    var patrols = document.querySelectorAll(".patrol[data-city]");
    var districts = document.querySelectorAll(".district");
    var norm = function (s) { return s.replace(/[״"'׳\-\s]/g, "").replace(/יי/g, "י"); };
    var t = null;
    search.addEventListener("input", function () {
      window.clearTimeout(t);
      t = window.setTimeout(function () {
        var q = norm(search.value.trim());
        var shown = 0;
        patrols.forEach(function (p) {
          var hit = !q || norm(p.getAttribute("data-city")).indexOf(q) !== -1;
          p.hidden = !hit;
          if (hit) shown++;
        });
        districts.forEach(function (d) {
          d.classList.toggle("is-empty", !!q && !d.querySelector(".patrol:not([hidden])"));
        });
        if (!q) status.textContent = "";
        else if (shown) status.textContent = "נמצאו " + shown + " סיירות";
        else status.textContent = "לא נמצאה סיירת. פנו למוקד ההתנדבות הארצי.";
      }, 120);
    });
  }

  /* ---------- סינון המלצות ---------- */
  var chips = document.querySelectorAll(".chip[data-filter]");
  if (chips.length) {
    var quotes = document.querySelectorAll("#quotes .quote");
    var fstatus = document.getElementById("filter-status");
    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        var f = chip.getAttribute("data-filter");
        chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c === chip)); });
        var n = 0;
        quotes.forEach(function (q) {
          var hit = f === "all" || q.getAttribute("data-group") === f;
          q.hidden = !hit;
          if (hit) { n++; q.classList.add("is-in"); }
        });
        if (fstatus) fstatus.textContent = "מוצגות " + n + " המלצות";
        var r = document.querySelector("[data-rail]");
        if (r) r.dispatchEvent(new Event("rail:refresh"));
      });
    });
  }

  /* ---------- תפריט נגישות ---------- */
  var fab = document.querySelector(".a11y-fab");
  var panel = document.getElementById("a11y-panel");
  var KEY = "mdl-a11y";
  var prefs = {};
  try { prefs = JSON.parse(window.localStorage.getItem(KEY) || "{}") || {}; } catch (e) { prefs = {}; }

  function save() { try { window.localStorage.setItem(KEY, JSON.stringify(prefs)); } catch (e) { /* חסום */ } }
  function applyFs() {
    ["fs--1", "fs-1", "fs-2", "fs-3"].forEach(function (c) { root.classList.remove(c); });
    var fs = prefs.fs || 0;
    if (fs) root.classList.add("fs-" + fs);
  }
  function syncToggles() {
    if (!panel) return;
    panel.querySelectorAll(".a11y-toggle").forEach(function (b) {
      var k = b.getAttribute("data-a11y");
      b.setAttribute("aria-pressed", String(prefs[k] === true));
    });
  }
  function openPanel(open) {
    panel.hidden = !open;
    fab.setAttribute("aria-expanded", String(open));
    if (open) { var f = panel.querySelector("button"); if (f) f.focus(); }
  }
  if (fab && panel) {
    syncToggles();
    fab.addEventListener("click", function () { openPanel(panel.hidden); });
    panel.querySelector(".a11y-close").addEventListener("click", function () { openPanel(false); fab.focus(); });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && !panel.hidden) { openPanel(false); fab.focus(); }
    });
    panel.addEventListener("click", function (ev) {
      var b = ev.target.closest("[data-a11y]");
      if (!b) return;
      var a = b.getAttribute("data-a11y");
      if (a === "font-up") prefs.fs = Math.min((prefs.fs || 0) + 1, 3);
      else if (a === "font-down") prefs.fs = Math.max((prefs.fs || 0) - 1, -1);
      else if (a === "font-reset") prefs.fs = 0;
      else if (a === "reset") {
        prefs = {};
        ["contrast", "mono", "links", "readable", "motion", "cursor"].forEach(function (k) { root.classList.remove("a11y-" + k); });
        try { window.localStorage.removeItem(KEY); } catch (e) { /* חסום */ }
        applyFs(); syncToggles();
        return;
      } else {
        prefs[a] = !prefs[a];
        root.classList.toggle("a11y-" + a, prefs[a]);
      }
      applyFs(); syncToggles(); save();
    });
  }
})();
