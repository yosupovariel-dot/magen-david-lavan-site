/* מחיל העדפות נגישות שמורות לפני ציור העמוד (מונע הבהוב). */
(function () {
  var root = document.documentElement;
  root.classList.add("js");
  try {
    var raw = window.localStorage.getItem("mdl-a11y");
    if (!raw) return;
    var p = JSON.parse(raw);
    if (typeof p !== "object" || p === null) return;
    var allowed = ["contrast", "mono", "links", "readable", "motion", "cursor"];
    for (var i = 0; i < allowed.length; i++) {
      if (p[allowed[i]] === true) root.classList.add("a11y-" + allowed[i]);
    }
    var fs = parseInt(p.fs, 10);
    if (fs >= -1 && fs <= 3 && fs !== 0) root.classList.add("fs-" + fs);
  } catch (e) { /* אחסון חסום - ממשיכים ללא העדפות */ }
})();
