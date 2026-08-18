(function () {
  "use strict";

  const measurementId = "G-BMKYWEPNHB";
  const consentKey = "hessenAktuellAnalyticsConsent";
  const productionHost = "sandro-abashishvili.de";
  const scriptUrl = new URL(document.currentScript?.src || "shared/js/analytics-consent.js", location.href);
  const siteRoot = new URL("../../", scriptUrl);
  const privacyUrl = new URL("legal/datenschutz.html", siteRoot).href;
  let banner = null;
  let analyticsLoaded = false;

  function setConsent(value) {
    if (typeof window.gtag !== "function") return;
    window.gtag("consent", "update", {
      analytics_storage: value,
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied",
    });
  }

  function loadAnalytics(savedConsent) {
    if (analyticsLoaded || location.hostname !== productionHost) return;
    analyticsLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag("consent", "default", {
      analytics_storage: "denied",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied",
    });
    if (savedConsent === "granted") setConsent("granted");
    window.gtag("js", new Date());
    window.gtag("config", measurementId, {
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
    });
    const script = document.createElement("script");
    script.async = true;
    script.dataset.analyticsId = measurementId;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(measurementId)}`;
    document.head.appendChild(script);
  }

  function clearAnalyticsCookies() {
    document.cookie.split(";").forEach((part) => {
      const name = part.split("=")[0].trim();
      if (!/^_ga(?:_|$)/.test(name)) return;
      const expired = "expires=Thu, 01 Jan 1970 00:00:00 GMT";
      document.cookie = `${name}=;${expired};path=/;SameSite=Lax`;
      document.cookie = `${name}=;${expired};path=/;domain=${location.hostname};SameSite=Lax`;
      document.cookie = `${name}=;${expired};path=/;domain=.${location.hostname};SameSite=Lax`;
    });
  }

  function saveConsent(value) {
    try { localStorage.setItem(consentKey, value); } catch (_) {}
    setConsent(value);
    if (value === "denied") clearAnalyticsCookies();
    banner?.remove();
    banner = null;
  }

  function showBanner() {
    banner?.remove();
    banner = document.createElement("aside");
    banner.className = "consent-banner";
    banner.setAttribute("role", "dialog");
    banner.setAttribute("aria-modal", "true");
    banner.setAttribute("aria-labelledby", "hessen-consent-title");
    banner.innerHTML = `
      <div class="consent-copy">
        <strong id="hessen-consent-title">Optionale Statistik</strong>
        <p>Mit Ihrer Einwilligung verwenden wir Google Analytics für die vollständige Nutzungsanalyse von Hessen Aktuell. Ohne Zustimmung werden keine Analytics-Cookies gesetzt; Google kann cookielose Messsignale erhalten. <a href="${privacyUrl}">Mehr erfahren</a></p>
      </div>
      <div class="consent-actions">
        <button type="button" class="consent-button" data-consent="denied">Ablehnen</button>
        <button type="button" class="consent-button consent-accept" data-consent="granted">Statistik erlauben</button>
      </div>`;
    banner.addEventListener("click", (event) => {
      const button = event.target.closest("[data-consent]");
      if (button) saveConsent(button.dataset.consent);
    });
    document.body.appendChild(banner);
    banner.querySelector('[data-consent="denied"]')?.focus();
  }

  function addSettingsControl() {
    const footer = document.querySelector(".site-footer__links");
    if (!footer || footer.querySelector("[data-consent-settings]")) return;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "footer-link-button";
    button.dataset.consentSettings = "";
    button.textContent = "Cookie-Einstellungen";
    footer.appendChild(button);
  }

  let consent = null;
  try { consent = localStorage.getItem(consentKey); } catch (_) {}
  loadAnalytics(consent);
  if (consent !== "granted" && consent !== "denied") showBanner();
  addSettingsControl();
  document.addEventListener("click", (event) => {
    if (!event.target.closest("[data-consent-settings]")) return;
    event.preventDefault();
    showBanner();
  });
})();
