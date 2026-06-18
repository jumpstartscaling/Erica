// tracker.js -- drop-in anonymous analytics. Loaded on EVERY page.
//
// - Assigns an anonymous visitor_id (localStorage + cookie so the server can
//   read it for the login back-fill).
// - Auto-fires `page_view` on load.
// - Auto-fires `click` events for any element with a data-track="name" attr.
// - Uses navigator.sendBeacon so analytics NEVER block or break the page.
//
// See docs/TRACING.md.
(function () {
  "use strict";

  var STORAGE_KEY = "tn_visitor";
  var COOKIE_KEY = "tn_visitor";

  function uuid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return "v-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 10);
  }

  function getCookie(name) {
    var m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
    return m ? decodeURIComponent(m.pop()) : null;
  }

  function setCookie(name, value) {
    // 1 year, lax. Not httponly (the client needs to read/write it).
    var secure = location.protocol === "https:" ? "; Secure" : "";
    document.cookie =
      name + "=" + encodeURIComponent(value) +
      "; path=/; max-age=" + 60 * 60 * 24 * 365 + "; SameSite=Lax" + secure;
  }

  function getVisitorId() {
    var id = null;
    try { id = localStorage.getItem(STORAGE_KEY); } catch (e) {}
    if (!id) id = getCookie(COOKIE_KEY);
    if (!id) id = uuid();
    try { localStorage.setItem(STORAGE_KEY, id); } catch (e) {}
    setCookie(COOKIE_KEY, id);
    return id;
  }

  var visitorId = getVisitorId();

  function track(eventName, props) {
    var payload = JSON.stringify({
      visitor_id: visitorId,
      event_name: eventName,
      props: props || {},
      url: location.pathname + location.search,
    });
    try {
      if (navigator.sendBeacon) {
        var blob = new Blob([payload], { type: "application/json" });
        navigator.sendBeacon("/api/track", blob);
        return;
      }
    } catch (e) {}
    // Fallback: fire-and-forget fetch, keepalive so it survives navigation.
    try {
      fetch("/api/track", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: payload,
        keepalive: true,
      });
    } catch (e) {}
  }

  // Expose a tiny global API for pages to fire custom events.
  window.TN = window.TN || {};
  window.TN.visitorId = visitorId;
  window.TN.track = track;

  // Auto page_view.
  document.addEventListener("DOMContentLoaded", function () {
    track("page_view", { title: document.title });
  });

  // Auto click tracking for [data-track] elements.
  document.addEventListener(
    "click",
    function (e) {
      var el = e.target && e.target.closest ? e.target.closest("[data-track]") : null;
      if (!el) return;
      track(el.getAttribute("data-track") || "click", {
        text: (el.textContent || "").trim().slice(0, 80),
        href: el.getAttribute("href") || null,
      });
    },
    true
  );
})();
