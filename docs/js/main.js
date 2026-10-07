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

  /* ---------- קרוסלת המלצות (נייד) ---------- */
  document.querySelectorAll("[data-rail]").forEach(function (rail) {
    var list = rail.querySelector(".quotes--rail");
    var items = list.querySelectorAll(".quote");
    var prev = rail.querySelector('[data-dir="prev"]');
    var next = rail.querySelector('[data-dir="next"]');
    var fill = rail.querySelector(".rail__fill");
    var cur = rail.querySelector(".rail__cur");
    function index() {
      var best = 0, bestD = Infinity, lr = list.getBoundingClientRect();
      items.forEach(function (it, i) {
        var d = Math.abs(it.getBoundingClientRect().right - lr.right);
        if (d < bestD) { bestD = d; best = i; }
      });
      return best;
    }
    function update() {
      var max = list.scrollWidth - list.clientWidth;
      var pos = Math.abs(list.scrollLeft);
      var i = index();
      fill.style.transform = "scaleX(" + (i + 1) / items.length + ")";
      cur.textContent = String(i + 1);
      prev.disabled = pos < 4;
      next.disabled = pos > max - 4;
    }
    function go(dir) {
      var i = Math.max(0, Math.min(items.length - 1, index() + dir));
      items[i].scrollIntoView({ behavior: motionOff() ? "auto" : "smooth", block: "nearest", inline: "start" });
    }
    prev.addEventListener("click", function () { go(-1); });
    next.addEventListener("click", function () { go(1); });
    var raf = 0;
    list.addEventListener("scroll", function () {
      if (raf) return;
      raf = window.requestAnimationFrame(function () { raf = 0; update(); });
    }, { passive: true });
    window.addEventListener("resize", update);
    update();
  });

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
  var revealSel = ".sec-head, .intro__grid > *, .arena, .stat, .chain__step, .dcard, .bento__item, .quote, .video__grid > *, .pillar, .leader, .track, .pay__item, .line, .dline, .album, .district__head, .strip figure";
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
