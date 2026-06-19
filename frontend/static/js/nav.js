(function () {
  'use strict';

  var PAGES = {
    start: [
      { href: '/', icon: 'home', label: 'Home / Landing' },
      { href: '/customer', icon: 'users', label: 'Customer Track' },
      { href: '/agent', icon: 'briefcase', label: 'Agent Track' },
    ],
    account: [
      { href: '/register/customer', icon: 'user-plus', label: 'Create Customer Account' },
      { href: '/register/agent', icon: 'user-plus', label: 'Create Agent Account' },
      { href: '/login/customer', icon: 'log-in', label: 'Customer Login' },
      { href: '/login/agent', icon: 'log-in', label: 'Agent Login' },
      { href: '/verify-email', icon: 'mail-check', label: 'Verify Email' },
    ],
    learn: [
      { href: '/webinar/customer', icon: 'video', label: 'Customer Webinar' },
      { href: '/webinar/agent', icon: 'video', label: 'Agent Webinar' },
      { href: '/course', icon: 'book-open', label: 'Course Lessons' },
      { href: '/coaching', icon: 'headphones', label: 'Coaching' },
    ],
    dashboards: [
      { href: '/customer/dashboard', icon: 'layout-dashboard', label: 'Customer Dashboard' },
      { href: '/agent/dashboard', icon: 'layout-dashboard', label: 'Agent Dashboard' },
      { href: '/admin', icon: 'shield', label: 'Admin Dashboard' },
    ],
    info: [
      { href: '/faq', icon: 'help-circle', label: 'FAQ' },
      { href: '/disclosures', icon: 'file-text', label: 'Disclosures & Privacy' },
      { href: '/a2p', icon: 'message-square', label: 'SMS / A2P' },
    ],
  };

  var ICONS = {
    'home': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    'users': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    'briefcase': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>',
    'help-circle': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>',
    'file-text': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
    'message-square': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    'log-in': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>',
    'user-plus': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/></svg>',
    'mail-check': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 13V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v12c0 1.1.9 2 2 2h8"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/><path d="m16 19 2 2 4-4"/></svg>',
    'layout-dashboard': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>',
    'shield': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    'video': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>',
    'headphones': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>',
    'book-open': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
  };

  function icon(name) {
    return ICONS[name] || '';
  }

  function listSection(title, items) {
    var lis = items.map(function (p) {
      return '<li><a href="' + p.href + '" class="block rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-emerald-50 hover:text-emerald-700">'
        + '<span class="mr-2 inline-block align-middle">' + icon(p.icon) + '</span>'
        + '<span class="align-middle">' + p.label + '</span></a></li>';
    }).join('');
    return '<div><h3 class="text-xs font-semibold uppercase tracking-wider text-slate-400">' + title + '</h3><ul class="mt-3 space-y-1.5">' + lis + '</ul></div>';
  }

  function navHTML(dropdownId) {
    var ddId = dropdownId || 'tn-nav-dd';
    return '<header class="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80">\
      <div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">\
        <a href="/" class="flex items-center gap-2 font-bold text-slate-900">\
          <span class="grid h-8 w-8 place-items-center rounded-lg bg-emerald-500 text-white text-sm">TN</span>\
          <span class="hidden sm:inline">Tranzformation Nation</span>\
        </a>\
        <div class="relative" id="' + ddId + '-wrap">\
          <button id="' + ddId + '-btn" class="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-colors">\
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>\
            <span class="hidden sm:inline">Pages</span>\
            <svg id="' + ddId + '-chevron" class="h-3.5 w-3.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>\
          </button>\
          <div id="' + ddId + '" class="hidden absolute right-0 z-50 mt-2 w-[700px] max-w-[calc(100vw-2rem)] rounded-xl border border-slate-200 bg-white p-5 shadow-xl">\
            <div class="grid gap-5 sm:grid-cols-3 md:grid-cols-5">'
              + listSection('Get Started', PAGES.start)
              + listSection('My Account', PAGES.account)
              + listSection('Learn', PAGES.learn)
              + listSection('Dashboards', PAGES.dashboards)
              + listSection('Info', PAGES.info)
            + '</div>\
          </div>\
        </div>\
        <div id="tn-auth-area" class="flex items-center gap-2 text-sm"></div>\
      </div>\
    </header>';
  }

  function setupNav(dropdownId) {
    var ddId = dropdownId || 'tn-nav-dd';
    var navRoot = document.getElementById('tn-nav-root');
    if (!navRoot) return;
    navRoot.innerHTML = navHTML(ddId);

    var dd = document.getElementById(ddId);
    var btn = document.getElementById(ddId + '-btn');
    var chevron = document.getElementById(ddId + '-chevron');
    var wrap = document.getElementById(ddId + '-wrap');

    if (btn && dd) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        dd.classList.toggle('hidden');
        if (chevron) chevron.classList.toggle('rotate-180');
      });
      document.addEventListener('click', function () {
        dd.classList.add('hidden');
        if (chevron) chevron.classList.remove('rotate-180');
      });
      dd.addEventListener('click', function (e) {
        e.stopPropagation();
        var link = e.target.closest('a');
        if (link) {
          dd.classList.add('hidden');
          if (chevron) chevron.classList.remove('rotate-180');
        }
      });
    }
  }

  function renderAuth() {
    var area = document.getElementById('tn-auth-area');
    if (!area) return;
    area.innerHTML = '<span class="text-xs text-slate-400">Loading…</span>';
    fetch('/api/me').then(function (r) {
      if (r.status === 401) {
        area.innerHTML = '<div class="flex items-center gap-2">\
          <a href="/login/customer" class="rounded-lg px-3 py-2 font-medium text-slate-700 hover:bg-slate-100 hidden sm:inline-block text-sm">Customer Login</a>\
          <a href="/login/agent" class="rounded-lg bg-slate-900 px-3 py-2 font-medium text-white hover:bg-slate-700 text-sm">Agent Login</a>\
        </div>';
        return;
      }
      return r.json().then(function (d) {
        if (d.authenticated && d.user) {
          var url = '/customer/dashboard';
          if (d.user.role === 'admin') url = '/admin';
          else if (d.user.role === 'agent') url = '/agent/dashboard';
          area.innerHTML = '<div class="flex items-center gap-2">\
            <a href="' + url + '" class="rounded-lg bg-emerald-500 px-3 py-2 font-medium text-white hover:bg-emerald-600 text-sm">Dashboard (' + d.user.role + ')</a>\
            <button onclick="tnLogout()" class="rounded-lg px-3 py-2 font-medium text-slate-600 hover:bg-slate-100 text-sm">Logout</button>\
          </div>';
        }
      });
    }).catch(function () {
      area.innerHTML = '<div class="flex items-center gap-2">\
        <a href="/login/customer" class="rounded-lg px-3 py-2 font-medium text-slate-700 hover:bg-slate-100 hidden sm:inline-block text-sm">Customer Login</a>\
        <a href="/login/agent" class="rounded-lg bg-slate-900 px-3 py-2 font-medium text-white hover:bg-slate-700 text-sm">Agent Login</a>\
      </div>';
    });
  }

  window.tnLogout = function () {
    fetch('/api/logout', { method: 'POST' }).then(function () { window.location.href = '/'; });
  };

  document.addEventListener('DOMContentLoaded', function () {
    setupNav();
    renderAuth();
  });
})();
