
(function () {
  var LANGS = ['pl','en','fr','de','uk'];
  var FALLBACK_LABEL = {
    pl: 'niedostępne',
    en: 'unavailable',
    fr: 'indisponible',
    de: 'nicht verfügbar',
    uk: 'недоступно'
  };
  var FALLBACK_TITLE = {
    pl: 'Licznik publiczny może być blokowany przez Twoją wtyczkę ochrony prywatności. Kliknij, aby otworzyć statystyki.',
    en: 'The public counter may be blocked by your privacy extension. Click to open the public stats page.',
    fr: 'Le compteur public peut être bloqué par votre extension de protection de la vie privée. Cliquez pour ouvrir les statistiques.',
    de: 'Der öffentliche Zähler kann durch Ihre Datenschutz-Erweiterung blockiert werden. Klicken zum Öffnen der Statistik.',
    uk: 'Публічний лічильник може бути заблокований розширенням приватності. Натисніть, щоб відкрити статистику.'
  };
  var STATS_URL = 'https://witekkilarski.goatcounter.com/';
  var JSON_ENDPOINT = 'https://witekkilarski.goatcounter.com/counter/TOTAL.json';
  var PNG_ENDPOINT  = 'https://witekkilarski.goatcounter.com/counter/TOTAL.png';
  // Same-origin fallback: plik aktualizowany co godzinę przez GitHub Action.
  // Serwowany z tego samego origin co strona (github.io), więc nieblokowalny
  // przez wtyczki prywatności (uBlock, AdGuard, Brave Shields, Pi-hole itd.).
  var REPO_FALLBACK = '/visitor-count.json';
  var CACHE_KEY = 'kncn_visitor_count_v2';
  var CACHE_TTL = 24 * 3600 * 1000; // 24 h

  function writeAll(text) {
    LANGS.forEach(function (lang) {
      var el = document.getElementById('gc-counter-' + lang);
      if (el) el.textContent = text;
    });
  }

  function showCachedOrFallback() {
    // Try cached value first — better than "unavailable".
    try {
      var raw = localStorage.getItem(CACHE_KEY);
      if (raw) {
        var p = JSON.parse(raw);
        if (p && p.value && p.ts && (Date.now() - p.ts) < CACHE_TTL) {
          writeAll(p.value + '+');
          return;
        }
      }
    } catch (e) {}
    // Final fallback — link to stats page.
    LANGS.forEach(function (lang) {
      var el = document.getElementById('gc-counter-' + lang);
      if (!el) return;
      if (/\d/.test(el.textContent)) return;
      var a = document.createElement('a');
      a.href = STATS_URL;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      a.textContent = FALLBACK_LABEL[lang] || FALLBACK_LABEL.en;
      a.title = FALLBACK_TITLE[lang] || FALLBACK_TITLE.en;
      el.textContent = '';
      el.appendChild(a);
    });
  }

  function cacheValue(formatted) {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify({ value: formatted, ts: Date.now() }));
    } catch (e) {}
  }

  function tryJSON(attempt) {
    return fetch(JSON_ENDPOINT + '?v=' + Date.now(), { mode: 'cors', cache: 'no-store', credentials: 'omit' })
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function (data) {
        var raw = data && (data.count_unique != null ? data.count_unique : data.count);
        if (raw == null) throw new Error('no count field');
        var n = Number(String(raw).replace(/[\s,\u00a0]/g, ''));
        if (!isFinite(n)) throw new Error('not finite');
        var formatted = n.toLocaleString();
        writeAll(formatted);
        cacheValue(formatted);
        return true;
      })
      .catch(function (err) {
        if (attempt < 2) {
          return new Promise(function (resolve) {
            setTimeout(function () { resolve(tryJSON(attempt + 1)); }, 1500);
          });
        }
        throw err;
      });
  }

  // PNG probe: if the image loads, GoatCounter is reachable and counter
  // exists; we cannot read pixel-text from a cross-origin image, but we
  // CAN confirm reachability and then ask JSON again from same browser
  // session in case the first attempt failed transiently. Most usefully,
  // the PNG itself lives inside the <span> as visible badge.
  function tryPNGProbe() {
    return new Promise(function (resolve, reject) {
      var img = new Image();
      var done = false;
      img.onload = function () { if (!done) { done = true; resolve(true); } };
      img.onerror = function () { if (!done) { done = true; reject(new Error('png blocked')); } };
      img.src = PNG_ENDPOINT + '?v=' + Date.now();
      setTimeout(function () { if (!done) { done = true; reject(new Error('png timeout')); } }, 5000);
    });
  }

  // Same-origin fallback — pobiera plik visitor-count.json z tego samego
  // hosta co strona. Plik jest aktualizowany co godzinę przez GitHub Action
  // (.github/workflows/update-visitor-count.yml). Ten endpoint NIE jest
  // blokowany przez wtyczki prywatności, ponieważ to ten sam origin.
  function tryRepoFallback() {
    return fetch(REPO_FALLBACK + '?v=' + Date.now(), { cache: 'no-store' })
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function (data) {
        var raw = data && (data.count_unique != null ? data.count_unique : data.count);
        if (raw == null) throw new Error('no count field');
        var n = Number(String(raw).replace(/[\s,\u00a0]/g, ''));
        if (!isFinite(n)) throw new Error('not finite');
        var formatted = n.toLocaleString();
        writeAll(formatted);
        cacheValue(formatted);
        return true;
      });
  }

  function start() {
    // 1) Próba bezpośrednia do GoatCounter (najświeższe dane).
    tryJSON(0)
      // 2) Sonda PNG + ponowna próba JSON (czasem działa po pierwszej porażce).
      .catch(function () {
        return tryPNGProbe().then(function () { return tryJSON(0); });
      })
      // 3) Same-origin fallback — plik w repo, aktualizowany co godzinę.
      .catch(function () { return tryRepoFallback(); })
      // 4) Cache localStorage lub link do statystyk publicznych.
      .catch(function () { showCachedOrFallback(); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
