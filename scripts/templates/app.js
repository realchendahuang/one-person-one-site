(function() {
  "use strict";

  /* ============================================================
     渐进增强：卡片与标签由构建期静态渲染，本脚本只负责筛选、排序与
     弹窗交互。禁用 JS 时页面依然能完整浏览，这里只做能力叠加。
     ============================================================ */

  /* 1. 主题切换 */
  var THEMES = ["system", "light", "dark"];
  var themeBtn = document.getElementById("btn-theme");
  var darkQuery = window.matchMedia("(prefers-color-scheme: dark)");

  function applyTheme(mode) {
    document.documentElement.setAttribute("data-theme-mode", mode);
    try { localStorage.setItem("opos-theme", mode); } catch (e) {}
    if (mode === "dark" || (mode === "system" && darkQuery.matches)) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }

  if (themeBtn) {
    themeBtn.addEventListener("click", function() {
      var current = document.documentElement.getAttribute("data-theme-mode") || "system";
      applyTheme(THEMES[(THEMES.indexOf(current) + 1) % THEMES.length]);
    });
  }

  if (darkQuery.addEventListener) {
    darkQuery.addEventListener("change", function(e) {
      if (document.documentElement.getAttribute("data-theme-mode") === "system") {
        document.documentElement.classList.toggle("dark", e.matches);
      }
    });
  }

  /* 2. 数据与元素 */
  var rawData = JSON.parse(document.getElementById("sites-data").textContent || '{"sites":[]}');
  var sites = rawData.sites || [];

  var tagsBar = document.getElementById("tags-bar");
  var grid = document.getElementById("sites-grid");
  var emptyState = document.getElementById("empty-state");
  var btnReset = document.getElementById("btn-reset");
  var sortBtns = document.querySelectorAll(".sort-btn");
  var btnShuffle = document.getElementById("btn-shuffle");
  var toast = document.getElementById("toast");
  var toastText = document.getElementById("toast-text");
  var searchChip = document.getElementById("search-chip");
  var searchChipText = document.getElementById("search-chip-text");

  var searchModal = document.getElementById("search-modal");
  var btnSearch = document.getElementById("btn-search");
  var searchInput = document.getElementById("search-input");
  var searchCloseBtn = document.getElementById("search-close-btn");
  var searchModalTags = document.getElementById("search-modal-tags");
  var searchResults = document.getElementById("search-results");

  var activeTag = null;
  var searchQuery = "";
  var modalFilterTag = null;
  var sortMode = "default";
  var toastTimer = null;

  // 搜索弹窗里先展示这么多条，其余通过「显示全部」展开
  var SEARCH_PREVIEW = 10;

  function showToast(msg) {
    if (!toast) return;
    toastText.textContent = msg;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function() { toast.classList.remove("show"); }, 2000);
  }

  /* 3. 统计标签 */
  var tagCounts = {};
  sites.forEach(function(s) {
    (s.tags || []).forEach(function(t) {
      tagCounts[t] = (tagCounts[t] || 0) + 1;
    });
  });
  var allTags = Object.keys(tagCounts).sort(function(a, b) {
    if (tagCounts[b] !== tagCounts[a]) return tagCounts[b] - tagCounts[a];
    return a.localeCompare(b);
  });

  /* 4. 搜索辅助：一次构建检索文本，避免每次输入重复拼接 */
  var searchPools = sites.map(function(s) {
    return [s.name, s.owner, s.description, (s.tags || []).join(" "), s.region, s.url]
      .join(" ").toLowerCase();
  });

  function matchIndices(q, tag) {
    q = (q || "").trim().toLowerCase();
    var out = [];
    for (var i = 0; i < sites.length; i++) {
      if (tag && (sites[i].tags || []).indexOf(tag) === -1) continue;
      if (q && searchPools[i].indexOf(q) === -1) continue;
      out.push(i);
    }
    return out;
  }

  /* 5. 列表筛选与排序：直接复用构建期渲染好的 DOM */
  function render() {
    var matched = matchIndices(searchQuery, activeTag);
    var visible = {};

    matched.forEach(function(i) { visible[sites[i].url] = true; });

    var cards = grid.children;
    for (var i = 0; i < cards.length; i++) {
      var card = cards[i];
      card.classList.toggle("is-hidden", !visible[card.getAttribute("data-url")]);
    }

    if (sortMode !== "default" && matched.length) {
      reorder(matched);
    }

    if (emptyState) emptyState.hidden = matched.length !== 0;
  }

  function reorder(matched) {
    var order = matched.slice();

    if (sortMode === "name") {
      order.sort(function(a, b) {
        return (sites[a].name || "").localeCompare(sites[b].name || "", "zh-CN");
      });
    } else if (sortMode === "random") {
      // Fisher-Yates：sort() 配合随机比较器并不均匀
      for (var i = order.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var tmp = order[i];
        order[i] = order[j];
        order[j] = tmp;
      }
    }

    var byUrl = {};
    for (var k = 0; k < grid.children.length; k++) {
      byUrl[grid.children[k].getAttribute("data-url")] = grid.children[k];
    }
    order.forEach(function(idx) {
      var el = byUrl[sites[idx].url];
      if (el) grid.appendChild(el);
    });
  }

  /* 6. 搜索弹窗（含焦点陷阱与焦点归还） */
  var lastFocused = null;

  function focusable() {
    if (!searchModal) return [];
    return Array.prototype.filter.call(
      searchModal.querySelectorAll('a[href], button:not([disabled]), input:not([disabled])'),
      function(el) { return el.offsetParent !== null || el === searchInput; }
    );
  }

  function openSearch() {
    if (!searchModal) return;
    lastFocused = document.activeElement;
    searchModal.hidden = false;
    searchModal.classList.add("open");
    searchInput.value = searchQuery;
    renderModalTags();
    renderSearchResults(searchQuery);
    setTimeout(function() { searchInput.focus(); }, 60);
  }

  function closeSearch() {
    if (!searchModal || searchModal.hidden) return;
    searchModal.classList.remove("open");
    searchModal.hidden = true;
    if (lastFocused && typeof lastFocused.focus === "function") lastFocused.focus();
    lastFocused = null;
  }

  if (btnSearch) btnSearch.addEventListener("click", openSearch);
  if (searchCloseBtn) searchCloseBtn.addEventListener("click", closeSearch);
  if (searchModal) {
    searchModal.addEventListener("click", function(e) {
      if (e.target === searchModal) closeSearch();
    });
  }

  function renderModalTags() {
    searchModalTags.textContent = "";

    var allBtn = document.createElement("button");
    allBtn.type = "button";
    allBtn.className = "s-tag-pill" + (modalFilterTag === null ? " active" : "");
    allBtn.textContent = "全部";
    allBtn.setAttribute("aria-pressed", modalFilterTag === null ? "true" : "false");
    allBtn.addEventListener("click", function() {
      modalFilterTag = null;
      renderModalTags();
      renderSearchResults(searchInput.value);
    });
    searchModalTags.appendChild(allBtn);

    allTags.forEach(function(t) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "s-tag-pill" + (modalFilterTag === t ? " active" : "");
      btn.textContent = t;
      btn.setAttribute("aria-pressed", modalFilterTag === t ? "true" : "false");
      btn.addEventListener("click", function() {
        modalFilterTag = modalFilterTag === t ? null : t;
        renderModalTags();
        renderSearchResults(searchInput.value);
      });
      searchModalTags.appendChild(btn);
    });
  }

  var expanded = false;

  function renderSearchResults(q, forceExpand) {
    if (forceExpand) expanded = true;
    q = (q || "").trim().toLowerCase();

    var matched = matchIndices(q, modalFilterTag);
    searchResults.textContent = "";

    if (matched.length === 0) {
      var emptyEl = document.createElement("div");
      emptyEl.className = "search-empty";
      emptyEl.textContent = "没有匹配的站点";
      searchResults.appendChild(emptyEl);
      return;
    }

    var limit = expanded ? matched.length : SEARCH_PREVIEW;
    matched.slice(0, limit).forEach(function(i) {
      var s = sites[i];
      var item = document.createElement("a");
      item.className = "search-item";
      item.href = s.url;
      item.target = "_blank";
      item.rel = "noopener noreferrer";
      item.innerHTML = '<div class="search-item-info">' +
        '<div class="search-item-title">' + escapeHtml(s.name) + '</div>' +
        '<div class="search-item-sub">' + escapeHtml(s.owner || "") + ' · ' + escapeHtml(s.description) + '</div></div>' +
        '<span class="search-item-go">直达 ↗</span>';
      searchResults.appendChild(item);
    });

    if (matched.length > limit) {
      var more = document.createElement("div");
      more.className = "search-more";
      var moreBtn = document.createElement("button");
      moreBtn.type = "button";
      moreBtn.textContent = "还有 " + (matched.length - limit) + " 个站点，显示全部";
      moreBtn.addEventListener("click", function() {
        renderSearchResults(searchInput.value, true);
      });
      more.appendChild(moreBtn);
      searchResults.appendChild(more);
    }
  }

  if (searchInput) {
    searchInput.addEventListener("input", function() {
      searchQuery = searchInput.value.trim();
      expanded = false;
      renderSearchResults(searchQuery);
      updateSearchChip();
      render();
    });
  }

  function updateSearchChip() {
    if (!searchChip) return;
    searchChip.hidden = !searchQuery;
    if (searchQuery) searchChipText.textContent = "搜: " + searchQuery;
  }

  if (searchChip) {
    searchChip.addEventListener("click", function() {
      searchQuery = "";
      if (searchInput) searchInput.value = "";
      updateSearchChip();
      render();
    });
  }

  /* 7. 主页标签栏：优先展示高频标签，长尾折叠进搜索弹窗 */
  var TOP_TAGS = 10;

  function tagButton(tag, label, count) {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "tag-btn" + (activeTag === tag ? " active" : "");
    btn.setAttribute("aria-pressed", activeTag === tag ? "true" : "false");
    btn.innerHTML = '<span>' + escapeHtml(label) + "</span>" +
      (count === null ? "" : ' <span class="tag-count">' + count + "</span>");
    btn.addEventListener("click", onTagClick.bind(null, tag));
    return btn;
  }

  function onTagClick(tag) {
    activeTag = activeTag === tag ? null : tag;
    renderTagsBar();
    render();
  }

  function renderTagsBar() {
    if (!tagsBar) return;
    tagsBar.textContent = "";

    var allBtn = document.createElement("button");
    allBtn.type = "button";
    allBtn.className = "tag-btn" + (activeTag === null ? " active" : "");
    allBtn.setAttribute("aria-pressed", activeTag === null ? "true" : "false");
    allBtn.innerHTML = '<span>全部</span> <span class="tag-count">' + sites.length + "</span>";
    allBtn.addEventListener("click", function() { onTagClick(null); });
    tagsBar.appendChild(allBtn);

    var shown = allTags.slice(0, TOP_TAGS);

    // 当前选中的标签若在长尾里，也要显示出来，否则用户看不到自己筛了什么
    if (activeTag && shown.indexOf(activeTag) === -1) shown.push(activeTag);

    shown.forEach(function(tag) {
      tagsBar.appendChild(tagButton(tag, tag, tagCounts[tag]));
    });

    var rest = allTags.filter(function(t) { return shown.indexOf(t) === -1; });
    if (rest.length) {
      var more = document.createElement("button");
      more.type = "button";
      more.className = "tag-btn tag-more-btn";
      more.textContent = "更多 " + rest.length + " 个标签";
      more.title = "在搜索弹窗里查看全部标签";
      more.addEventListener("click", openSearch);
      tagsBar.appendChild(more);
    }
  }

  /* 8. 辅助函数 */
  function escapeHtml(str) {
    return String(str || "").replace(/[&<>"']/g, function(m) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m];
    });
  }

  function copyText(value, label) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(value).then(
        function() { showToast(label); },
        function() { showToast("复制失败，请手动复制"); }
      );
      return;
    }
    // 非安全上下文（如 file:// 本地预览）下 Clipboard API 不可用
    var helper = document.createElement("textarea");
    helper.value = value;
    helper.setAttribute("readonly", "");
    helper.style.position = "fixed";
    helper.style.opacity = "0";
    document.body.appendChild(helper);
    helper.select();
    try {
      document.execCommand("copy");
      showToast(label);
    } catch (e) {
      showToast("复制失败，请手动复制");
    }
    document.body.removeChild(helper);
  }

  /* 9. 卡片操作按钮（卡片本身是静态 HTML，这里只挂事件） */
  grid.addEventListener("click", function(e) {
    var trigger = e.target.closest("[data-copy]");
    if (!trigger) return;
    e.preventDefault();
    copyText(trigger.getAttribute("data-copy"), trigger.getAttribute("data-copy-label") || "已复制");
  });

  /* 10. 随机漫游 */
  function handleShuffle() {
    if (!sites.length) return;
    var site = sites[Math.floor(Math.random() * sites.length)];
    showToast("前往：" + site.name);
    setTimeout(function() {
      window.open(site.url, "_blank", "noopener,noreferrer");
    }, 250);
  }

  if (btnShuffle) btnShuffle.addEventListener("click", handleShuffle);

  /* 11. 事件绑定 */
  if (btnReset) {
    btnReset.addEventListener("click", function() {
      searchQuery = "";
      activeTag = null;
      sortMode = "default";
      updateSearchChip();
      syncSortButtons();
      renderTagsBar();
      render();
    });
  }

  function syncSortButtons() {
    sortBtns.forEach(function(b) {
      var on = b.getAttribute("data-sort") === sortMode;
      b.classList.toggle("active", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  sortBtns.forEach(function(btn) {
    btn.addEventListener("click", function() {
      sortMode = btn.getAttribute("data-sort") || "default";
      syncSortButtons();
      render();
    });
  });

  window.addEventListener("keydown", function(e) {
    if (e.key === "Escape") {
      if (searchModal && !searchModal.hidden) closeSearch();
      return;
    }
    if (e.key === "/" && (!searchModal || searchModal.hidden) &&
        document.activeElement.tagName !== "INPUT" &&
        document.activeElement.tagName !== "TEXTAREA") {
      e.preventDefault();
      openSearch();
      return;
    }
    // 焦点陷阱：弹窗打开时 Tab 不逃逸到背后的页面
    if (e.key === "Tab" && searchModal && !searchModal.hidden) {
      var items = focusable();
      if (!items.length) return;
      var first = items[0];
      var last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });

  renderTagsBar();
  render();
})();
