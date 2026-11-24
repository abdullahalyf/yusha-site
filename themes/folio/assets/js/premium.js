/* Premium effects for the nocturne style. Vanilla, deferred.
   Everything here is skipped when the reader prefers reduced motion. */
(function () {
  "use strict";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce) return;
  var root = document.documentElement;
  root.classList.add("fx");

  /* One orchestrated intro: tiles rise in once, in order. */
  var tiles = document.querySelectorAll("[data-fx='rise']");
  tiles.forEach(function (el, i) { el.style.setProperty("--d", (i * 70) + "ms"); });
  requestAnimationFrame(function () { requestAnimationFrame(function () { root.classList.add("fx-go"); }); });

  /* Count-up for numbers when they scroll into view. */
  var nums = document.querySelectorAll("[data-count]");
  function run(el) {
    var end = parseFloat(el.getAttribute("data-count"));
    if (isNaN(end)) return;
    var dec = parseInt(el.getAttribute("data-decimals") || "0", 10);
    var t0 = null, dur = 1200;
    function step(t) {
      if (t0 === null) t0 = t;
      var k = Math.min(1, (t - t0) / dur);
      k = 1 - Math.pow(1 - k, 3);
      el.textContent = (end * k).toFixed(dec);
      if (k < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { run(e.target); io.unobserve(e.target); } });
    }, { threshold: 0.6 });
    nums.forEach(function (n) { n.textContent = (0).toFixed(parseInt(n.getAttribute("data-decimals") || "0", 10)); io.observe(n); });
  }

  /* Pointer spotlight on tiles (fine pointers only). */
  if (window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    document.addEventListener("pointermove", function (e) {
      var t = e.target.closest && e.target.closest(".tile");
      if (!t) return;
      var r = t.getBoundingClientRect();
      t.style.setProperty("--mx", (e.clientX - r.left) + "px");
      t.style.setProperty("--my", (e.clientY - r.top) + "px");
    }, { passive: true });
  }
})();
