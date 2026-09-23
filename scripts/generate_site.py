#!/usr/bin/env python3
"""从 data/sites.json 生成 GitHub Pages 静态网站（单文件 index.html）。

设计准则：
- 如无必要，勿增实体：彻底移除冗余大 Hero、空洞口号与虚假统计，正经内容首屏直达
- 移动端极简精调：顶栏严禁折行溢出，标签单行水平平滑滑动，手机端首屏直接看卡片
- 顶栏一站式收拢：搜索、漫游、提交网站、双主题、GitHub 极简集成
- 极致纯粹卡片：高密度、舒适间距、真实 Favicon、小窗预览与一键直达
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sites.json"
OUT = ROOT / "site"

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN" data-theme-mode="system">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, maximum-scale=1">
<title>一人一站 · One Person, One Site</title>
<meta name="description" content="收集值得关注的个人网站、独立博客与数字花园。">
<meta property="og:title" content="一人一站 · One Person, One Site">
<meta property="og:description" content="收集值得关注的个人网站、独立博客与数字花园。">
<meta property="og:type" content="website">
<meta property="og:url" content="https://realchendahuang.github.io/one-person-one-site/">
<meta name="twitter:card" content="summary">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><circle cx=%2250%22 cy=%2250%22 r=%2244%22 fill=%22%23ff6a00%22/><circle cx=%2250%22 cy=%2250%22 r=%2220%22 fill=%22%23ffffff%22/></svg>">
<script>
  (function() {
    var stored = localStorage.getItem("opos-theme") || "system";
    document.documentElement.setAttribute("data-theme-mode", stored);
    var prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    if (stored === "dark" || (stored === "system" && prefersDark)) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  })();
</script>
<style>
/* ============================================================
   一人一站 · 纯粹极简设计系统 (如无必要，勿增实体)
   ============================================================ */
:root {
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-full: 9999px;

  color-scheme: light;

  --paper: #f7f7f8;
  --soft-surface: #ededf0;
  --surface: #ffffff;
  --surface-hover: #fafafa;
  --line: #e3e3e7;
  --line-subtle: #eeeff1;
  --ink: #111113;
  --mist: #5e5e68;
  --fog: #9a9aa4;

  --signal: #ff6a00;
  --signal-hover: #ff7d1a;
  --signal-soft: rgba(255, 106, 0, 0.08);
  --signal-border: rgba(255, 106, 0, 0.25);

  --panel-elev: 0 1px 3px rgba(0, 0, 0, 0.04), 0 6px 18px -6px rgba(0, 0, 0, 0.06);
  --hover-lift: 0 3px 6px -2px rgba(0, 0, 0, 0.05), 0 12px 24px -6px rgba(0, 0, 0, 0.09);

  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", "PingFang SC", "Noto Sans SC", sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

html.dark {
  color-scheme: dark;

  --paper: #09090b;
  --soft-surface: #141417;
  --surface: #17171a;
  --surface-hover: #1f1f23;
  --line: #242429;
  --line-subtle: #1c1c20;
  --ink: #f5f5f7;
  --mist: #9898a4;
  --fog: #656570;

  --signal: #ff6a00;
  --signal-hover: #ff7d1a;
  --signal-soft: rgba(255, 106, 0, 0.14);
  --signal-border: rgba(255, 106, 0, 0.35);

  --panel-elev: inset 0 1px 0 0 rgba(255, 255, 255, 0.05), 0 4px 16px -4px rgba(0, 0, 0, 0.5);
  --hover-lift: inset 0 1px 0 0 rgba(255, 255, 255, 0.08), 0 14px 28px -8px rgba(0, 0, 0, 0.8), 0 0 0 1px var(--signal-border);
}

*, *::before, *::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  background-color: var(--paper);
  color: var(--ink);
  font-family: var(--font-sans);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ================= 顶栏 (精简、严禁折行) ================= */
.site-header {
  position: sticky;
  top: 0;
  z-index: 50;
  width: 100%;
  border-bottom: 1px solid var(--line);
  background: rgba(247, 247, 248, 0.88);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
html.dark .site-header {
  background: rgba(9, 9, 11, 0.88);
}

.header-inner {
  max-width: 1140px;
  height: 48px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  white-space: nowrap;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  text-decoration: none;
  color: var(--ink);
  font-weight: 700;
  font-size: 0.98rem;
  letter-spacing: -0.02em;
  flex-shrink: 0;
}
.brand-pulse {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--signal);
  flex-shrink: 0;
}
.brand-sub {
  font-size: 0.8rem;
  font-weight: 400;
  color: var(--fog);
}
@media (max-width: 600px) {
  .brand-sub { display: none; }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-shrink: 0;
}

.h-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  height: 28px;
  padding: 0 0.55rem;
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--mist);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-full);
  cursor: pointer;
  text-decoration: none;
  line-height: 1;
  flex-shrink: 0;
  transition: all 0.15s ease;
}
.h-btn:hover {
  color: var(--ink);
  border-color: var(--fog);
}
.h-btn svg {
  width: 13px;
  height: 13px;
  flex-shrink: 0;
}

.h-btn-primary {
  background: var(--signal);
  color: #ffffff;
  border-color: var(--signal);
  font-weight: 600;
}
.h-btn-primary:hover {
  background: var(--signal-hover);
  color: #ffffff;
  border-color: var(--signal-hover);
}

.h-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--surface);
  border: 1px solid var(--line);
  color: var(--mist);
  cursor: pointer;
  flex-shrink: 0;
  padding: 0;
  text-decoration: none;
  transition: all 0.15s ease;
}
.h-icon-btn:hover {
  color: var(--ink);
  border-color: var(--fog);
}
.h-icon-btn svg {
  width: 13px;
  height: 13px;
}

.theme-icon-sun, .theme-icon-moon, .theme-icon-system { display: none; }
html[data-theme-mode="light"] .theme-icon-sun { display: block; }
html[data-theme-mode="dark"] .theme-icon-moon { display: block; }
html[data-theme-mode="system"] .theme-icon-system { display: block; }

/* ================= 主内容容器 (首屏即内容) ================= */
.main-wrapper {
  max-width: 1140px;
  margin: 0 auto;
  padding: 0.75rem 1rem 3rem;
  flex: 1;
  width: 100%;
}

/* 控制条：单行横滑标签 + 极简排序 */
.bar-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.tags-scroll {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  overflow-x: auto;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
  padding-bottom: 2px;
}
.tags-scroll::-webkit-scrollbar {
  display: none;
}

.tag-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  height: 26px;
  padding: 0 0.65rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-full);
  font-size: 0.76rem;
  color: var(--mist);
  font-weight: 500;
  cursor: pointer;
  flex-shrink: 0;
  line-height: 1;
  user-select: none;
  transition: all 0.14s ease;
}
.tag-btn:hover {
  color: var(--ink);
  border-color: var(--fog);
}
.tag-btn.active {
  background: var(--ink);
  color: var(--paper);
  border-color: var(--ink);
  font-weight: 600;
}
html.dark .tag-btn.active {
  background: #ffffff;
  color: #000000;
  border-color: #ffffff;
}
.tag-count {
  font-size: 0.68rem;
  opacity: 0.7;
  font-family: var(--font-mono);
}

.sort-group {
  display: inline-flex;
  align-items: center;
  background: var(--soft-surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-full);
  padding: 2px;
  gap: 1px;
  flex-shrink: 0;
}
.sort-btn {
  background: transparent;
  border: none;
  color: var(--mist);
  font-size: 0.74rem;
  font-weight: 500;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-full);
  cursor: pointer;
  line-height: 1;
  transition: all 0.14s ease;
}
.sort-btn:hover { color: var(--ink); }
.sort-btn.active {
  background: var(--surface);
  color: var(--ink);
  font-weight: 600;
}

/* 活跃搜索指示胶囊 */
.active-search-chip {
  display: none;
  align-items: center;
  gap: 0.3rem;
  height: 26px;
  padding: 0 0.6rem;
  background: var(--signal-soft);
  color: var(--signal);
  border: 1px solid var(--signal-border);
  border-radius: var(--radius-full);
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
}

/* ================= 卡片网格 ================= */
.sites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 0.85rem;
}
@media (max-width: 600px) {
  .sites-grid {
    grid-template-columns: 1fr;
    gap: 0.65rem;
  }
}

.site-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  padding: 0.95rem;
  box-shadow: var(--panel-elev);
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
  color: inherit;
  overflow: hidden;
  cursor: pointer;
}
.site-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--hover-lift);
  border-color: var(--signal-border);
}

.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.65rem;
  margin-bottom: 0.45rem;
}
.card-header-main {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  min-width: 0;
}
.site-favicon {
  width: 30px;
  height: 30px;
  border-radius: 7px;
  background: var(--soft-surface);
  border: 1px solid var(--line);
  object-fit: cover;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--mist);
  overflow: hidden;
}
.site-favicon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-title-wrap {
  min-width: 0;
}
.site-name {
  margin: 0;
  font-size: 0.94rem;
  font-weight: 650;
  letter-spacing: -0.01em;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.site-owner-sub {
  font-size: 0.76rem;
  color: var(--mist);
  margin-top: 0.05rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-preview-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.2rem;
  height: 22px;
  padding: 0 0.45rem;
  border-radius: var(--radius-sm);
  background: var(--soft-surface);
  border: 1px solid var(--line);
  color: var(--mist);
  font-size: 0.72rem;
  font-weight: 500;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.14s ease;
}
.card-preview-btn:hover {
  background: var(--signal);
  color: #ffffff;
  border-color: var(--signal);
}
.card-preview-btn svg {
  width: 11px;
  height: 11px;
}

.site-desc {
  margin: 0 0 0.65rem;
  font-size: 0.83rem;
  color: var(--mist);
  line-height: 1.48;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.card-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.45rem;
  padding-top: 0.55rem;
  border-top: 1px solid var(--line-subtle);
  margin-top: auto;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}
.card-tag {
  font-size: 0.68rem;
  padding: 0.08rem 0.4rem;
  border-radius: var(--radius-full);
  background: var(--soft-surface);
  color: var(--mist);
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.mini-action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 5px;
  background: transparent;
  border: none;
  color: var(--mist);
  cursor: pointer;
  padding: 0;
  text-decoration: none;
  transition: all 0.14s ease;
}
.mini-action-btn:hover {
  background: var(--soft-surface);
  color: var(--ink);
}
.mini-action-btn svg {
  width: 12px;
  height: 12px;
}

/* ================= 全局搜索弹窗 (Command Palette) ================= */
.search-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 3rem 1rem 1rem;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.18s ease;
}
.search-backdrop.open {
  opacity: 1;
  pointer-events: auto;
}

.search-box {
  width: 100%;
  max-width: 520px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  box-shadow: 0 16px 40px -10px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 75vh;
}

.search-input-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--line);
}
.search-input-row svg {
  color: var(--fog);
  flex-shrink: 0;
}
.search-input-field {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 0.95rem;
  font-family: inherit;
  color: var(--ink);
}
.search-close-key {
  background: var(--soft-surface);
  border: 1px solid var(--line);
  color: var(--mist);
  border-radius: 4px;
  padding: 0.15rem 0.4rem;
  font-size: 0.7rem;
  cursor: pointer;
  font-family: var(--font-mono);
}

.search-results-list {
  overflow-y: auto;
  padding: 0.4rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.search-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.65rem;
  padding: 0.55rem 0.75rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.12s ease;
}
.search-item:hover {
  background: var(--soft-surface);
}
.search-item-title {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--ink);
}
.search-item-sub {
  font-size: 0.76rem;
  color: var(--mist);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ================= 小窗预览 (Live Modal) ================= */
.preview-backdrop {
  position: fixed;
  inset: 0;
  z-index: 110;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
}
.preview-backdrop.open {
  opacity: 1;
  pointer-events: auto;
}

.preview-window {
  width: 100%;
  max-width: 960px;
  height: 86vh;
  max-height: 800px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.45);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-titlebar {
  height: 42px;
  background: var(--soft-surface);
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 0.85rem;
  gap: 0.75rem;
  user-select: none;
  flex-shrink: 0;
}
.p-dots {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 50px;
}
.p-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.p-close { background: #ff5f56; cursor: pointer; }
.p-min { background: #ffbd2e; }
.p-max { background: #27c93f; }

.p-address {
  flex: 1;
  max-width: 500px;
  height: 26px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 0.65rem;
  font-size: 0.75rem;
  color: var(--mist);
  font-family: var(--font-mono);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
@media (max-width: 600px) {
  .p-address { display: none; }
}

.p-ext-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--mist);
  padding: 0.2rem 0.55rem;
  border-radius: var(--radius-sm);
  background: var(--surface);
  border: 1px solid var(--line);
  cursor: pointer;
  text-decoration: none;
}
.p-ext-btn:hover { color: var(--ink); }

.preview-frame-body {
  flex: 1;
  position: relative;
  background: #ffffff;
}
html.dark .preview-frame-body {
  background: #111114;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.preview-loading {
  position: absolute;
  inset: 0;
  background: var(--surface);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  color: var(--mist);
  font-size: 0.82rem;
  transition: opacity 0.2s ease;
}
.preview-loading.hidden {
  opacity: 0;
  pointer-events: none;
}
.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--line);
  border-top-color: var(--signal);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ================= Toast ================= */
.toast-notice {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 120;
  background: var(--ink);
  color: var(--paper);
  padding: 0.5rem 0.95rem;
  border-radius: var(--radius-md);
  font-size: 0.8rem;
  font-weight: 500;
  box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  gap: 0.4rem;
  opacity: 0;
  transform: translateY(8px);
  pointer-events: none;
  transition: all 0.2s ease;
}
.toast-notice.show {
  opacity: 1;
  transform: translateY(0);
}
@media (max-width: 600px) {
  .toast-notice { left: 1rem; right: 1rem; bottom: 1rem; justify-content: center; }
}

/* ================= 页脚 ================= */
.site-footer {
  border-top: 1px solid var(--line);
  background: var(--surface);
  padding: 2rem 1rem 2.5rem;
  margin-top: auto;
  text-align: center;
  font-size: 0.8rem;
  color: var(--mist);
}
.footer-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 0.65rem;
}
.footer-links a {
  color: var(--mist);
  text-decoration: none;
}
.footer-links a:hover { color: var(--signal); }
</style>
</head>
<body>

<!-- 顶栏：紧凑一站式，彻底消除折行 -->
<header class="site-header">
  <div class="header-inner">
    <a href="./" class="brand" aria-label="一人一站 首页">
      <span class="brand-pulse"></span>
      <span>一人一站</span>
      <span class="brand-sub">One Person, One Site</span>
    </a>

    <div class="header-actions">
      <!-- 搜索按钮 -->
      <button id="btn-search" class="h-btn" title="搜索 (/)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <span>搜索</span>
      </button>

      <!-- 漫游按钮 -->
      <button id="btn-shuffle" class="h-btn" title="随机探索">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M16 8h.01"/><path d="M8 8h.01"/><path d="M8 16h.01"/><path d="M16 16h.01"/><path d="M12 12h.01"/></svg>
        <span>漫游</span>
      </button>

      <!-- 提交网站 -->
      <a href="https://github.com/realchendahuang/one-person-one-site/issues/new?template=submit-site.yml" target="_blank" rel="noopener" class="h-btn h-btn-primary">
        <span>提交</span>
      </a>

      <!-- 主题切换 -->
      <button id="btn-theme" class="h-icon-btn" title="切换主题">
        <svg class="theme-icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
        <svg class="theme-icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
        <svg class="theme-icon-system" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="20" height="14" x="2" y="3" rx="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/></svg>
      </button>

      <!-- GitHub -->
      <a href="https://github.com/realchendahuang/one-person-one-site" target="_blank" rel="noopener" class="h-icon-btn" title="GitHub">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>
      </a>
    </div>
  </div>
</header>

<main class="main-wrapper">
  <!-- 控制条：标签单行横滑 + 排序分段 -->
  <div class="bar-controls">
    <div class="tags-scroll">
      <div id="tags-bar" style="display:inline-flex;gap:0.35rem;"></div>
      <div id="search-chip" class="active-search-chip" title="清除搜索">
        <span id="search-chip-text"></span>
        <span style="font-size:0.7rem;margin-left:2px;">✕</span>
      </div>
    </div>

    <div class="sort-group" role="tablist">
      <button type="button" class="sort-btn active" data-sort="default">推荐</button>
      <button type="button" class="sort-btn" data-sort="name">字母序</button>
      <button type="button" class="sort-btn" data-sort="random">随机</button>
    </div>
  </div>

  <!-- 正经内容：站点网格首屏直达 -->
  <div id="sites-grid" class="sites-grid"></div>

  <!-- 空状态 -->
  <div id="empty-state" style="text-align:center;padding:3rem 1rem;color:var(--mist);display:none;">
    <p style="margin:0 0 0.8rem;font-size:0.9rem;">未找到匹配站点</p>
    <button id="btn-reset" class="h-btn">清除筛选</button>
  </div>
</main>

<!-- 全局搜索弹窗 (Command Palette) -->
<div id="search-modal" class="search-backdrop" role="dialog" aria-modal="true" aria-label="搜索">
  <div class="search-box">
    <div class="search-input-row">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
      <input id="search-input" class="search-input-field" placeholder="搜索站点名称、作者、简介或标签…" autocomplete="off">
      <button id="search-esc" class="search-close-key">ESC</button>
    </div>
    <div id="search-results" class="search-results-list"></div>
  </div>
</div>

<!-- 小窗实时预览系统 (Live Modal) -->
<div id="preview-modal" class="preview-backdrop" role="dialog" aria-modal="true" aria-label="预览">
  <div class="preview-window">
    <div class="preview-titlebar">
      <div class="p-dots">
        <div id="p-close-btn" class="p-dot p-close" title="关闭 (ESC)"></div>
        <div class="p-dot p-min"></div>
        <div class="p-dot p-max"></div>
      </div>
      <div id="p-address" class="p-address">https://example.com</div>
      <a id="p-ext-link" href="#" target="_blank" rel="noopener noreferrer" class="p-ext-btn">
        <span>新窗口打开 ↗</span>
      </a>
    </div>
    <div class="preview-frame-body">
      <iframe id="p-iframe" class="preview-iframe" src="about:blank" sandbox="allow-scripts allow-same-origin allow-popups allow-forms" title="实时预览"></iframe>
      <div id="p-loading" class="preview-loading">
        <div class="spinner"></div>
        <span>正在载入实时预览…</span>
        <span style="font-size:0.75rem;color:var(--fog);">若站点限制内嵌，可点击右上角在新窗口直接打开</span>
      </div>
    </div>
  </div>
</div>

<!-- 浮动 Toast 提示 -->
<div id="toast" class="toast-notice" role="status" aria-live="polite">
  <span id="toast-text">已复制</span>
</div>

<!-- 页脚 -->
<footer class="site-footer">
  <div class="footer-links">
    <a href="./DIRECTORY.md" target="_blank" rel="noopener">目录</a>
    <span>·</span>
    <a href="https://github.com/realchendahuang/one-person-one-site" target="_blank" rel="noopener">GitHub</a>
    <span>·</span>
    <a href="https://github.com/realchendahuang/one-person-one-site/issues/new?template=submit-site.yml" target="_blank" rel="noopener">提交新站</a>
    <span>·</span>
    <a href="https://github.com/realchendahuang/one-person-one-site/blob/main/LICENSE" target="_blank" rel="noopener">MIT</a>
  </div>
  <div>一人一站 · 属于每一个人的独立互联网家园</div>
</footer>

<!-- 站点数据 -->
<script id="sites-data" type="application/json">__SITES_DATA__</script>

<script>
(function() {
  "use strict";

  /* 1. 主题切换 */
  var THEMES = ["system", "light", "dark"];
  var themeBtn = document.getElementById("btn-theme");

  function applyTheme(mode) {
    document.documentElement.setAttribute("data-theme-mode", mode);
    localStorage.setItem("opos-theme", mode);
    var prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    if (mode === "dark" || (mode === "system" && prefersDark)) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }

  if (themeBtn) {
    themeBtn.addEventListener("click", function() {
      var current = document.documentElement.getAttribute("data-theme-mode") || "system";
      var nextIdx = (THEMES.indexOf(current) + 1) % THEMES.length;
      applyTheme(THEMES[nextIdx]);
    });
  }

  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function(e) {
    if (document.documentElement.getAttribute("data-theme-mode") === "system") {
      document.documentElement.classList.toggle("dark", e.matches);
    }
  });

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

  // 搜索弹窗
  var searchModal = document.getElementById("search-modal");
  var btnSearch = document.getElementById("btn-search");
  var searchInput = document.getElementById("search-input");
  var searchEsc = document.getElementById("search-esc");
  var searchResults = document.getElementById("search-results");

  // 小窗预览
  var previewModal = document.getElementById("preview-modal");
  var pCloseBtn = document.getElementById("p-close-btn");
  var pAddress = document.getElementById("p-address");
  var pExtLink = document.getElementById("p-ext-link");
  var pIframe = document.getElementById("p-iframe");
  var pLoading = document.getElementById("p-loading");

  var activeTag = null;
  var searchQuery = "";
  var sortMode = "default";
  var toastTimer = null;
  var iframeTimer = null;

  function showToast(msg) {
    if (!toast) return;
    toastText.textContent = msg;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function() { toast.classList.remove("show"); }, 2000);
  }

  /* 3. 小窗预览 */
  function openPreview(site) {
    if (!previewModal) return;
    pAddress.textContent = site.url;
    pExtLink.href = site.url;
    pLoading.classList.remove("hidden");
    pIframe.src = site.url;

    previewModal.classList.add("open");
    document.body.style.overflow = "hidden";

    pIframe.onload = function() { pLoading.classList.add("hidden"); };
    clearTimeout(iframeTimer);
    iframeTimer = setTimeout(function() { pLoading.classList.add("hidden"); }, 3500);
  }

  function closePreview() {
    if (!previewModal) return;
    previewModal.classList.remove("open");
    document.body.style.overflow = "";
    pIframe.src = "about:blank";
  }

  if (pCloseBtn) pCloseBtn.addEventListener("click", closePreview);
  if (previewModal) {
    previewModal.addEventListener("click", function(e) {
      if (e.target === previewModal) closePreview();
    });
  }

  /* 4. 搜索功能 */
  function openSearch() {
    if (!searchModal) return;
    searchModal.classList.add("open");
    searchInput.value = searchQuery;
    renderSearchResults(searchQuery);
    setTimeout(function() { searchInput.focus(); }, 50);
  }

  function closeSearch() {
    if (!searchModal) return;
    searchModal.classList.remove("open");
  }

  if (btnSearch) btnSearch.addEventListener("click", openSearch);
  if (searchEsc) searchEsc.addEventListener("click", closeSearch);
  if (searchModal) {
    searchModal.addEventListener("click", function(e) {
      if (e.target === searchModal) closeSearch();
    });
  }

  function renderSearchResults(q) {
    q = (q || "").trim().toLowerCase();
    searchResults.textContent = "";

    var matches = sites.filter(function(s) {
      if (!q) return true;
      var pool = [s.name, s.owner, s.description, (s.tags || []).join(" "), s.region, s.url].join(" ").toLowerCase();
      return pool.indexOf(q) !== -1;
    });

    if (matches.length === 0) {
      var emptyEl = document.createElement("div");
      emptyEl.style.padding = "1.5rem 1rem";
      emptyEl.style.textAlign = "center";
      emptyEl.style.color = "var(--fog)";
      emptyEl.style.fontSize = "0.85rem";
      emptyEl.textContent = "无匹配站点";
      searchResults.appendChild(emptyEl);
      return;
    }

    matches.slice(0, 8).forEach(function(s) {
      var item = document.createElement("div");
      item.className = "search-item";
      var domain = extractDomain(s.url);
      item.innerHTML = '<div><div class="search-item-title">' + escapeHtml(s.name) + '</div>' +
        '<div class="search-item-sub">' + escapeHtml(s.owner || domain) + ' · ' + escapeHtml(s.description) + '</div></div>' +
        '<span style="font-size:0.75rem;color:var(--signal);font-weight:600;flex-shrink:0;">预览 ↗</span>';

      item.addEventListener("click", function() {
        closeSearch();
        openPreview(s);
      });
      searchResults.appendChild(item);
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", function() {
      searchQuery = searchInput.value.trim();
      renderSearchResults(searchQuery);
      updateSearchChip();
      render();
    });
  }

  function updateSearchChip() {
    if (searchQuery) {
      searchChip.style.display = "inline-flex";
      searchChipText.textContent = "搜: " + searchQuery;
    } else {
      searchChip.style.display = "none";
    }
  }

  if (searchChip) {
    searchChip.addEventListener("click", function() {
      searchQuery = "";
      if (searchInput) searchInput.value = "";
      updateSearchChip();
      render();
    });
  }

  /* 5. 标签栏 */
  var tagCounts = {};
  sites.forEach(function(s) {
    (s.tags || []).forEach(function(t) {
      tagCounts[t] = (tagCounts[t] || 0) + 1;
    });
  });
  var allTags = Object.keys(tagCounts).sort(function(a, b) {
    return tagCounts[b] - tagCounts[a];
  });

  function renderTagsBar() {
    tagsBar.textContent = "";

    var allBtn = document.createElement("button");
    allBtn.type = "button";
    allBtn.className = "tag-btn" + (activeTag === null ? " active" : "");
    allBtn.innerHTML = '<span>全部</span> <span class="tag-count">' + sites.length + '</span>';
    allBtn.addEventListener("click", function() {
      activeTag = null;
      renderTagsBar();
      render();
    });
    tagsBar.appendChild(allBtn);

    allTags.forEach(function(tag) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "tag-btn" + (activeTag === tag ? " active" : "");
      btn.innerHTML = '<span>' + escapeHtml(tag) + '</span> <span class="tag-count">' + tagCounts[tag] + '</span>';
      btn.addEventListener("click", function() {
        activeTag = activeTag === tag ? null : tag;
        renderTagsBar();
        render();
      });
      tagsBar.appendChild(btn);
    });
  }

  /* 6. 辅助函数 */
  function extractDomain(urlStr) {
    try {
      return (new URL(urlStr)).hostname;
    } catch(e) {
      return "";
    }
  }

  function escapeHtml(str) {
    return String(str || "").replace(/[&<>"']/g, function(m) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m];
    });
  }

  function getFirstChar(str) {
    var clean = (str || "").trim().replace(/^https?:\/\//, "");
    return clean ? clean.charAt(0).toUpperCase() : "?";
  }

  /* 7. 卡片生成 */
  function createCard(site) {
    var domain = extractDomain(site.url);
    var faviconUrl = domain ? "https://www.google.com/s2/favicons?domain=" + encodeURIComponent(domain) + "&sz=64" : "";
    var firstChar = getFirstChar(site.name || domain);

    var PALETTE = [
      "linear-gradient(135deg, #ff6a00, #ff8c37)",
      "linear-gradient(135deg, #0284c7, #38bdf8)",
      "linear-gradient(135deg, #059669, #34d399)",
      "linear-gradient(135deg, #7c3aed, #a78bfa)",
      "linear-gradient(135deg, #d97706, #fbbf24)"
    ];
    var grad = PALETTE[(firstChar.charCodeAt(0) || 0) % PALETTE.length];

    var card = document.createElement("div");
    card.className = "site-card";

    // 顶行
    var topRow = document.createElement("div");
    topRow.className = "card-top";

    var headerMain = document.createElement("div");
    headerMain.className = "card-header-main";

    var favBox = document.createElement("div");
    favBox.className = "site-favicon";
    
    function applyFallback() {
      favBox.textContent = firstChar;
      favBox.style.background = grad;
      favBox.style.color = "#ffffff";
      favBox.style.border = "none";
    }

    if (faviconUrl) {
      var img = document.createElement("img");
      img.src = faviconUrl;
      img.alt = "";
      img.loading = "lazy";
      img.onerror = applyFallback;
      favBox.appendChild(img);
    } else {
      applyFallback();
    }

    var titleWrap = document.createElement("div");
    titleWrap.className = "card-title-wrap";

    var nameEl = document.createElement("h3");
    nameEl.className = "site-name";
    nameEl.textContent = site.name;

    var ownerSub = document.createElement("div");
    ownerSub.className = "site-owner-sub";
    ownerSub.textContent = (site.owner ? site.owner : "") + (domain ? " · " + domain : "");

    titleWrap.appendChild(nameEl);
    titleWrap.appendChild(ownerSub);

    headerMain.appendChild(favBox);
    headerMain.appendChild(titleWrap);

    var previewBtn = document.createElement("button");
    previewBtn.type = "button";
    previewBtn.className = "card-preview-btn";
    previewBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg><span>预览</span>';
    previewBtn.title = "小窗预览";
    previewBtn.addEventListener("click", function(e) {
      e.stopPropagation();
      openPreview(site);
    });

    topRow.appendChild(headerMain);
    topRow.appendChild(previewBtn);

    // 描述
    var descEl = document.createElement("p");
    descEl.className = "site-desc";
    descEl.textContent = site.description || "独立个人站点";

    // 底行
    var bottomRow = document.createElement("div");
    bottomRow.className = "card-bottom";

    var tagsWrap = document.createElement("div");
    tagsWrap.className = "card-tags";
    (site.tags || []).slice(0, 3).forEach(function(t) {
      var tagSpan = document.createElement("span");
      tagSpan.className = "card-tag";
      tagSpan.textContent = t;
      tagsWrap.appendChild(tagSpan);
    });

    var actionsWrap = document.createElement("div");
    actionsWrap.className = "card-actions";

    if (site.feed) {
      var rssBtn = document.createElement("button");
      rssBtn.type = "button";
      rssBtn.className = "mini-action-btn";
      rssBtn.title = "复制 RSS 订阅源";
      rssBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 11a9 9 0 0 1 9 9"/><path d="M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="1"/></svg>';
      rssBtn.addEventListener("click", function(e) {
        e.stopPropagation();
        navigator.clipboard.writeText(site.feed).then(function() { showToast("已复制 RSS 源"); });
      });
      actionsWrap.appendChild(rssBtn);
    }

    var copyBtn = document.createElement("button");
    copyBtn.type = "button";
    copyBtn.className = "mini-action-btn";
    copyBtn.title = "复制网址";
    copyBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>';
    copyBtn.addEventListener("click", function(e) {
      e.stopPropagation();
      navigator.clipboard.writeText(site.url).then(function() { showToast("已复制网址"); });
    });
    actionsWrap.appendChild(copyBtn);

    var extBtn = document.createElement("a");
    extBtn.className = "mini-action-btn";
    extBtn.href = site.url;
    extBtn.target = "_blank";
    extBtn.rel = "noopener noreferrer";
    extBtn.title = "在新标签页打开";
    extBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>';
    extBtn.addEventListener("click", function(e) { e.stopPropagation(); });
    actionsWrap.appendChild(extBtn);

    bottomRow.appendChild(tagsWrap);
    bottomRow.appendChild(actionsWrap);

    card.appendChild(topRow);
    card.appendChild(descEl);
    card.appendChild(bottomRow);

    card.addEventListener("click", function(e) {
      if (e.target.closest("button") || e.target.closest("a")) return;
      openPreview(site);
    });

    return card;
  }

  /* 8. 列表渲染 */
  function render() {
    var q = searchQuery.toLowerCase();

    var filtered = sites.filter(function(s) {
      if (activeTag && (s.tags || []).indexOf(activeTag) === -1) {
        return false;
      }
      if (!q) return true;
      var pool = [s.name, s.owner, s.description, (s.tags || []).join(" "), s.region, s.url].join(" ").toLowerCase();
      return pool.indexOf(q) !== -1;
    });

    if (sortMode === "name") {
      filtered.sort(function(a, b) {
        return (a.name || "").localeCompare(b.name || "", "zh-CN");
      });
    } else if (sortMode === "random") {
      filtered.sort(function() { return 0.5 - Math.random(); });
    }

    grid.textContent = "";
    filtered.forEach(function(s) {
      grid.appendChild(createCard(s));
    });

    emptyState.style.display = filtered.length === 0 ? "block" : "none";
  }

  /* 9. 随机漫游 */
  function handleShuffle() {
    if (!sites || sites.length === 0) return;
    var randomSite = sites[Math.floor(Math.random() * sites.length)];
    openPreview(randomSite);
  }

  if (btnShuffle) btnShuffle.addEventListener("click", handleShuffle);

  /* 10. 事件 */
  if (btnReset) {
    btnReset.addEventListener("click", function() {
      searchQuery = "";
      activeTag = null;
      sortMode = "default";
      updateSearchChip();
      sortBtns.forEach(function(b) {
        b.classList.toggle("active", b.getAttribute("data-sort") === "default");
      });
      renderTagsBar();
      render();
    });
  }

  sortBtns.forEach(function(btn) {
    btn.addEventListener("click", function() {
      sortBtns.forEach(function(b) { b.classList.remove("active"); });
      btn.classList.add("active");
      sortMode = btn.getAttribute("data-sort") || "default";
      render();
    });
  });

  window.addEventListener("keydown", function(e) {
    if (e.key === "Escape") {
      if (previewModal && previewModal.classList.contains("open")) {
        closePreview();
      } else if (searchModal && searchModal.classList.contains("open")) {
        closeSearch();
      }
    } else if (e.key === "/" && (!searchModal || !searchModal.classList.contains("open")) && document.activeElement.tagName !== "INPUT") {
      e.preventDefault();
      openSearch();
    }
  });

  renderTagsBar();
  render();

})();
</script>
</body>
</html>
"""


def main() -> None:
    sites = json.loads(DATA.read_text(encoding="utf-8"))
    payload = json.dumps({"sites": sites}, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")
    html = HTML.replace("__SITES_DATA__", payload)
    out_dir = ROOT / "site"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    directory = ROOT / "DIRECTORY.md"
    if directory.exists():
        (out_dir / "DIRECTORY.md").write_text(directory.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Generated site/index.html with {len(sites)} site(s)")


if __name__ == "__main__":
    main()