/* Theme toggle + mobile menu. Vanilla, no dependencies.
   The page works without JS: dark mode then follows the OS, and the nav
   is a plain list on small screens. */
(function () {
  "use strict";

  var root = document.documentElement;
  var toggle = document.getElementById("theme-toggle");
  var menuBtn = document.getElementById("menu-toggle");
  var nav = document.getElementById("site-nav");

  /* ---- Theme ---- */
  function currentTheme() {
    return root.getAttribute("data-theme") === "dark" ? "dark" : "light";
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    if (toggle) {
      var dark = theme === "dark";
      toggle.setAttribute("aria-pressed", String(dark));
      toggle.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
    }
    try {
      localStorage.setItem("theme", theme);
    } catch (e) {
      /* Private mode: the toggle still works for this page view. */
    }
  }

  if (toggle) {
    applyTheme(currentTheme());
    toggle.addEventListener("click", function () {
      applyTheme(currentTheme() === "dark" ? "light" : "dark");
    });
  }

  /* Follow the OS only while the user has not made an explicit choice. */
  try {
    if (!localStorage.getItem("theme") && window.matchMedia) {
      var mq = window.matchMedia("(prefers-color-scheme: dark)");
      var onChange = function (e) {
        applyTheme(e.matches ? "dark" : "light");
      };
      if (mq.addEventListener) {
        mq.addEventListener("change", onChange);
      } else if (mq.addListener) {
        mq.addListener(onChange);
      }
    }
  } catch (e) {
    /* No localStorage: OS preference already applied in the head script. */
  }

  /* ---- Mobile menu ---- */
  function closeMenu() {
    if (!menuBtn || !nav) return;
    nav.classList.remove("site-nav--open");
    menuBtn.setAttribute("aria-expanded", "false");
    menuBtn.setAttribute("aria-label", "Open menu");
  }

  if (menuBtn && nav) {
    menuBtn.addEventListener("click", function () {
      var open = nav.classList.toggle("site-nav--open");
      menuBtn.setAttribute("aria-expanded", String(open));
      menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });

    /* Close after following a link, and on Escape. */
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) closeMenu();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeMenu();
    });
  }

  /* ---- Header border on scroll ----
     The header is a solid bar. A hairline border only appears once the
     page has moved, so the top of the page reads as open and the border
     appears where it is needed.

     The class is only written when it actually changes. Writing it on
     every frame would force a style recalculation on every scroll frame,
     which is the thing this whole pass was about removing. */
  var header = document.querySelector(".site-header");
  if (header) {
    var ticking = false;
    var scrolled = null;
    var setScrolled = function () {
      var now = window.scrollY > 8;
      if (now !== scrolled) {
        scrolled = now;
        header.classList.toggle("site-header--scrolled", now);
      }
      ticking = false;
    };
    setScrolled();
    window.addEventListener(
      "scroll",
      function () {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(setScrolled);
      },
      { passive: true }
    );
  }

  /* ---- Pause the background when the tab is hidden ----
     The drifting background keeps the compositor awake. While nobody is
     looking at the tab there is no reason to spend frames on it, so the
     animation is paused and resumed with the page. */
  var bg = document.querySelector(".page-bg");
  if (bg) {
    var setRunning = function (running) {
      bg.style.animationPlayState = running ? "running" : "paused";
      var glows = bg.querySelectorAll(".page-bg__glow");
      for (var i = 0; i < glows.length; i++) {
        glows[i].style.animationPlayState = running ? "running" : "paused";
      }
    };

    document.addEventListener("visibilitychange", function () {
      setRunning(!document.hidden);
    });
  }

  /* ---- Lightbox ----
     One <dialog> on the page. Any element with data-lightbox-src becomes
     a trigger: it opens the dialog and swaps in the full-size image.
     Escape closes it (the browser does that for a <dialog>), and the
     focus goes back to the button that opened it. */
  var dialog = document.getElementById("lightbox");
  if (dialog && typeof dialog.showModal === "function") {
    var img = dialog.querySelector(".lightbox__img");
    var caption = dialog.querySelector(".lightbox__caption");
    var opener = null;

    document.addEventListener("click", function (e) {
      var trigger = e.target.closest("[data-lightbox-src]");
      if (!trigger || dialog.open) return;
      opener = trigger;
      if (img) {
        img.setAttribute("src", trigger.getAttribute("data-lightbox-src"));
        img.setAttribute("alt", trigger.getAttribute("data-lightbox-alt") || "");
        /* The image is hidden from the accessibility tree while the
           dialog is closed, because it has no source yet. */
        img.removeAttribute("aria-hidden");
      }
      if (caption) {
        var text = trigger.getAttribute("data-lightbox-caption") || "";
        caption.textContent = text;
        if (text) {
          caption.removeAttribute("hidden");
        } else {
          caption.setAttribute("hidden", "");
        }
      }
      dialog.showModal();
    });

    /* Clicking the backdrop (the dialog element itself, not the image)
       closes it. */
    dialog.addEventListener("click", function (e) {
      if (e.target === dialog) dialog.close();
    });

    dialog.addEventListener("close", function () {
      if (img) img.setAttribute("aria-hidden", "true");
      if (opener && typeof opener.focus === "function") opener.focus();
      opener = null;
    });
  }
})();

/* nocturne only: no right-click menu, copy, or image dragging. */
(function () {
  if (document.documentElement.getAttribute("data-style") !== "nocturne") return;
  var stop = function (e) { e.preventDefault(); };
  ["contextmenu", "copy", "cut", "dragstart", "selectstart"].forEach(function (t) {
    document.addEventListener(t, stop);
  });
})();
