#!/usr/bin/env python3
"""从 data/sites.json 生成 GitHub Pages 静态网站（单文件 index.html）。

设计哲学：
- 大气优雅格局：极具人文感与现代高级审美的 Hero 区域，彻底消除“一人一站”标题生硬重复。
- 环境微光与层次：柔和光晕（Ambient Glow）+ 精致玻璃边框 + 质感分层，告别死黑与局促小气。
- 搜索与筛选一体化：原生即搜即见的居中搜索框（支持 / 快捷键聚焦）与分类胶囊、排序控制器紧密结合。
- 极致纯净卡片：彻底移除每个卡片右上角重复冗余的灰预览按钮，释放空间，悬浮展现灵动微交互。
- 小窗实时预览系统 (Live Browser Modal)：macOS 拟态浏览器窗口，支持交互式轻量预览。
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
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>一人一站 · One Person, One Site</title>
<meta name="description" content="精选平台与算法之外的独立博客、数字花园与创作者主页。发现那些在喧嚣时代，认真经营自己互联网家园的人。">
<meta property="og:title" content="一人一站 · One Person, One Site">
<meta property="og:description" content="精选平台与算法之外的独立博客、数字花园与创作者主页。发现那些在喧嚣时代，认真经营自己互联网家园的人。">
<meta property="og:type" content="website">
<meta property="og:url" content="https://realchendahuang.github.io/one-person-one-site/">
<meta name="twitter:card" content="summary_large_image">
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
   一人一站 · 现代高端设计系统
   大气格局 · 人文温度 · 信号橙 #ff6a00 · 质感微光
   ============================================================ */
:root {
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 18px;
  --radius-xl: 24px;
  --radius-full: 9999px;

  color-scheme: light;

  /* 浅色体系：柔和纸感与暖质调 */
  --bg-base: #f7f7f9;
  --bg-subtle: #eeeff3;
  --surface: #ffffff;
  --surface-hover: #fafafc;
  --surface-active: #f2f3f7;
  --line: #e3e4eb;
  --line-subtle: #ececf2;
  --ink: #111215;
  --ink-soft: #2e3038;
  --mist: #5e606e;
  --fog: #9698a6;

  /* 品牌橙色系 */
  --signal: #ff6a00;
  --signal-hover: #ff7e1e;
  --signal-soft: rgba(255, 106, 0, 0.08);
  --signal-border: rgba(255, 106, 0, 0.24);
  --signal-glow: rgba(255, 106, 0, 0.16);

  /* 阴影与微光 */
  --card-shadow: 0 1px 3px rgba(0, 0, 0, 0.03), 0 6px 16px -4px rgba(0, 0, 0, 0.05);
  --card-shadow-hover: 0 12px 32px -8px rgba(0, 0, 0, 0.1), 0 4px 12px -2px rgba(255, 106, 0, 0.12);
  --header-bg: rgba(247, 247, 249, 0.85);

  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

html.dark {
  color-scheme: dark;

  /* 深色体系：深邃暗黑与高级悬浮质感 */
  --bg-base: #09090b;
  --bg-subtle: #121215;
  --surface: #141418;
  --surface-hover: #1c1c22;
  --surface-active: #24242c;
  --line: #222228;
  --line-subtle: #19191f;
  --ink: #f5f5f7;
  --ink-soft: #d3d3dc;
  --mist: #9898a6;
  --fog: #626270;

  /* 品牌橙色系 */
  --signal: #ff6a00;
  --signal-hover: #ff7e1e;
  --signal-soft: rgba(255, 106, 0, 0.14);
  --signal-border: rgba(255, 106, 0, 0.38);
  --signal-glow: rgba(255, 106, 0, 0.28);

  /* 阴影与微光 */
  --card-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.05), 0 4px 20px -2px rgba(0, 0, 0, 0.5);
  --card-shadow-hover: inset 0 1px 0 0 rgba(255, 255, 255, 0.1), 0 18px 40px -10px rgba(0, 0, 0, 0.8), 0 0 20px -4px rgba(255, 106, 0, 0.25);
  --header-bg: rgba(9, 9, 11, 0.85);
}

*, *::before, *::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  background-color: var(--bg-base);
  color: var(--ink);
  font-family: var(--font-sans);
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
}

/* ================= 顶栏 ================= */
.site-header {
  position: sticky;
  top: 0;
  z-index: 50;
  width: 100%;
  border-bottom: 1px solid var(--line);
  background: var(--header-bg);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.header-inner {
  max-width: 1180px;
  height: 56px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  text-decoration: none;
  color: var(--ink);
  font-weight: 700;
  font-size: 1.05rem;
  letter-spacing: -0.02em;
  user-select: none;
}
.brand-pulse {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--signal);
  box-shadow: 0 0 12px var(--signal);
}
.brand-sub {
  font-size: 0.82rem;
  font-weight: 400;
  color: var(--fog);
  margin-left: 0.2rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.38rem 0.85rem;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--mist);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-full);
  text-decoration: none;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  cursor: pointer;
  transition: all 0.16s ease;
  line-height: 1;
}
.header-btn:hover {
  color: var(--ink);
  background: var(--surface-hover);
  border-color: var(--fog);
}
.header-btn svg {
  width: 14px;
  height: 14px;
}

.header-btn-primary {
  background: var(--signal);
  color: #ffffff !important;
  border-color: var(--signal);
  font-weight: 600;
  box-shadow: 0 2px 10px var(--signal-glow);
}
.header-btn-primary:hover {
  background: var(--signal-hover);
  border-color: var(--signal-hover);
  transform: translateY(-1px);
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-full);
  background: var(--surface);
  border: 1px solid var(--line);
  color: var(--mist);
  cursor: pointer;
  transition: all 0.16s ease;
  padding: 0;
  text-decoration: none;
}
.icon-btn:hover {
  color: var(--ink);
  background: var(--surface-hover);
  border-color: var(--mist);
}
.icon-btn svg {
  width: 15px;
  height: 15px;
}

.theme-icon-sun, .theme-icon-moon, .theme-icon-system {
  display: none;
}
html[data-theme-mode="light"] .theme-icon-sun { display: block; }
html[data-theme-mode="dark"] .theme-icon-moon { display: block; }
html[data-theme-mode="system"] .theme-icon-system { display: block; }

/* ================= 主容器 ================= */
.main-wrapper {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 1.5rem 5rem;
  flex: 1;
  width: 100%;
  position: relative;
  z-index: 1;
}

/* ================= 大气 Hero 英雄区 ================= */
.hero-section {
  position: relative;
  text-align: center;
  padding: 3.8rem 1rem 2.8rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 顶部环境微光 (Ambient Glow) */
.ambient-glow {
  position: absolute;
  top: -60px;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 860px;
  height: 360px;
  background: radial-gradient(ellipse at 50% 25%, rgba(255, 106, 0, 0.14), rgba(255, 106, 0, 0.03) 55%, transparent 75%);
  pointer-events: none;
  z-index: -1;
  filter: blur(36px);
}
html.dark .ambient-glow {
  background: radial-gradient(ellipse at 50% 25%, rgba(255, 106, 0, 0.18), rgba(255, 106, 0, 0.04) 55%, transparent 75%);
}

.hero-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.3rem 0.95rem;
  border-radius: var(--radius-full);
  background: var(--surface);
  border: 1px solid var(--line);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--mist);
  margin-bottom: 1.25rem;
  user-select: none;
}
.hero-pill-badge {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--signal);
}

.hero-title {
  font-size: clamp(2.1rem, 4.4vw, 3.2rem);
  font-weight: 800;
  letter-spacing: -0.035em;
  line-height: 1.18;
  margin: 0 0 1rem;
  color: var(--ink);
  max-width: 800px;
}

.hero-subtitle {
  font-size: clamp(0.95rem, 1.8vw, 1.1rem);
  color: var(--mist);
  line-height: 1.65;
  margin: 0 0 1.8rem;
  max-width: 620px;
}

.hero-stats-row {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  font-size: 0.84rem;
  color: var(--fog);
  user-select: none;
}
.hero-stat-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.hero-stat-item strong {
  color: var(--ink);
  font-weight: 700;
  font-family: var(--font-mono);
}

/* ================= 搜索与筛选一体化控制栏 ================= */
.control-dock {
  width: 100%;
  max-width: 100%;
  margin: 0 auto 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

/* 优雅居中的原生实时搜索框 */
.search-bar-wrap {
  position: relative;
  width: 100%;
  max-width: 620px;
  margin: 0 auto;
}
.search-icon-left {
  position: absolute;
  left: 1.1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--fog);
  pointer-events: none;
  display: flex;
  align-items: center;
}
.search-input {
  width: 100%;
  height: 48px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-full);
  padding: 0 5.5rem 0 3rem;
  font-size: 0.95rem;
  font-family: inherit;
  color: var(--ink);
  outline: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
  transition: all 0.2s ease;
}
.search-input:focus {
  border-color: var(--signal);
  box-shadow: 0 0 0 3px var(--signal-soft), 0 4px 16px rgba(0, 0, 0, 0.06);
}
.search-input::placeholder {
  color: var(--fog);
}
.search-right-actions {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.search-clear-btn {
  background: var(--bg-subtle);
  border: none;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  display: none;
  align-items: center;
  justify-content: center;
  color: var(--mist);
  cursor: pointer;
  padding: 0;
  transition: all 0.15s ease;
}
.search-clear-btn:hover {
  background: var(--line);
  color: var(--ink);
}
.search-clear-btn.visible {
  display: flex;
}
.search-kbd-hint {
  font-size: 0.75rem;
  font-family: var(--font-mono);
  background: var(--bg-subtle);
  color: var(--fog);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 0.15rem 0.45rem;
  line-height: 1;
  user-select: none;
}

/* 标签与排序一体行 */
.toolbar-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.tags-scroll-wrap {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  flex-wrap: wrap;
  flex: 1;
}

.tag-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.8rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  color: var(--mist);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.16s ease;
  user-select: none;
}
.tag-pill:hover {
  color: var(--ink);
  background: var(--surface-hover);
  border-color: var(--fog);
}
.tag-pill.active {
  background: var(--ink);
  color: var(--bg-base);
  border-color: var(--ink);
  font-weight: 600;
}
html.dark .tag-pill.active {
  background: #ffffff;
  color: #000000;
  border-color: #ffffff;
}
.tag-pill-count {
  font-size: 0.72rem;
  opacity: 0.65;
  font-family: var(--font-mono);
}

/* 分段控制器 */
.segmented-control {
  display: inline-flex;
  align-items: center;
  background: var(--bg-subtle);
  border: 1px solid var(--line);
  border-radius: var(--radius-full);
  padding: 3px;
  gap: 2px;
  user-select: none;
  flex-shrink: 0;
}
.segment-btn {
  background: transparent;
  border: none;
  color: var(--mist);
  font-size: 0.8rem;
  font-weight: 500;
  padding: 0.28rem 0.75rem;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all 0.16s ease;
  line-height: 1;
}
.segment-btn:hover {
  color: var(--ink);
}
.segment-btn.active {
  background: var(--surface);
  color: var(--ink);
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

/* 过滤状态提示 */
.filter-status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.82rem;
  color: var(--mist);
  padding: 0 0.2rem;
}

/* ================= 站点卡片网格 ================= */
.sites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.35rem;
}

.site-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 1.4rem;
  box-shadow: var(--card-shadow);
  transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.22s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease;
  color: inherit;
  overflow: hidden;
  cursor: pointer;
}
.site-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-shadow-hover);
  border-color: var(--signal-border);
}

/* 卡片顶部行：头像 + 标题 + 悬浮指示 */
.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.85rem;
  margin-bottom: 0.85rem;
}
.card-brand-group {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  min-width: 0;
  flex: 1;
}
.site-favicon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: var(--bg-subtle);
  border: 1px solid var(--line);
  object-fit: cover;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--mist);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
  overflow: hidden;
}
.site-favicon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-title-group {
  min-width: 0;
  flex: 1;
}
.site-name {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: -0.015em;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.3;
}
.site-owner-badge {
  font-size: 0.82rem;
  color: var(--mist);
  margin-top: 0.15rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

/* 悬浮微交互指示器（取代傻傻的灰预览按钮） */
.card-hover-hint {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--bg-subtle);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--fog);
  opacity: 0.4;
  transform: scale(0.9);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  flex-shrink: 0;
}
.site-card:hover .card-hover-hint {
  opacity: 1;
  color: var(--signal);
  background: var(--signal-soft);
  transform: scale(1) translateY(-1px);
}
.card-hover-hint svg {
  width: 14px;
  height: 14px;
}

/* 简介 */
.site-desc {
  margin: 0 0 1.15rem;
  font-size: 0.88rem;
  color: var(--mist);
  line-height: 1.62;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

/* 底部信息行 */
.card-meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
  flex-wrap: wrap;
  padding-top: 0.85rem;
  border-top: 1px solid var(--line-subtle);
  margin-top: auto;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}
.card-tag {
  font-size: 0.72rem;
  font-weight: 500;
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius-full);
  background: var(--bg-subtle);
  color: var(--mist);
  border: 1px solid transparent;
  transition: all 0.15s ease;
}
.card-tag:hover {
  border-color: var(--line);
  color: var(--ink);
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}
.card-mini-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 7px;
  background: transparent;
  border: 1px solid transparent;
  color: var(--fog);
  cursor: pointer;
  padding: 0;
  transition: all 0.15s ease;
  text-decoration: none;
}
.card-mini-btn:hover {
  background: var(--bg-subtle);
  color: var(--ink);
  border-color: var(--line);
}
.card-mini-btn svg {
  width: 14px;
  height: 14px;
}

/* ================= 小窗预览模态框 (macOS Live Browser) ================= */
.preview-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.68);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.22s ease;
}
.preview-backdrop.open {
  opacity: 1;
  pointer-events: auto;
}

.preview-window {
  width: 100%;
  max-width: 980px;
  height: 86vh;
  max-height: 820px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transform: scale(0.96) translateY(12px);
  transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}
.preview-backdrop.open .preview-window {
  transform: scale(1) translateY(0);
}

.window-titlebar {
  height: 48px;
  background: var(--bg-subtle);
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.15rem;
  gap: 1rem;
  user-select: none;
  flex-shrink: 0;
}
.window-dots {
  display: flex;
  align-items: center;
  gap: 7px;
  width: 60px;
}
.window-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--line);
}
.dot-close { background: #ff5f56; cursor: pointer; }
.dot-min { background: #ffbd2e; }
.dot-max { background: #27c93f; }

.window-address-bar {
  flex: 1;
  max-width: 540px;
  height: 30px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0 0.85rem;
  font-size: 0.8rem;
  color: var(--mist);
  font-family: var(--font-mono);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.window-address-bar svg {
  color: var(--fog);
  flex-shrink: 0;
}

.window-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.window-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--mist);
  padding: 0.28rem 0.75rem;
  border-radius: var(--radius-sm);
  background: var(--surface);
  border: 1px solid var(--line);
  cursor: pointer;
  text-decoration: none;
  transition: all 0.15s ease;
}
.window-btn:hover {
  color: var(--ink);
  border-color: var(--fog);
}

.preview-body {
  flex: 1;
  position: relative;
  background: #ffffff;
  overflow: hidden;
}
html.dark .preview-body {
  background: #111114;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: #ffffff;
}

.preview-loading-overlay {
  position: absolute;
  inset: 0;
  background: var(--surface);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.85rem;
  color: var(--mist);
  font-size: 0.9rem;
  transition: opacity 0.2s ease;
}
.preview-loading-overlay.hidden {
  opacity: 0;
  pointer-events: none;
}
.spinner {
  width: 28px;
  height: 28px;
  border: 2.5px solid var(--line);
  border-top-color: var(--signal);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ================= 浮动 Toast 提示 ================= */
.toast-notice {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 120;
  background: var(--ink);
  color: var(--bg-base);
  padding: 0.65rem 1.25rem;
  border-radius: var(--radius-md);
  font-size: 0.86rem;
  font-weight: 500;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  gap: 0.55rem;
  opacity: 0;
  transform: translateY(12px);
  pointer-events: none;
  transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-notice.show {
  opacity: 1;
  transform: translateY(0);
}

/* ================= 页脚 ================= */
.site-footer {
  border-top: 1px solid var(--line);
  background: var(--surface);
  padding: 3.5rem 1.5rem 4rem;
  margin-top: auto;
}
.footer-inner {
  max-width: 1180px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1.25rem;
}
.footer-quote {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
  max-width: 600px;
  line-height: 1.6;
}
.footer-links {
  display: flex;
  align-items: center;
  gap: 1.35rem;
  flex-wrap: wrap;
  font-size: 0.86rem;
  color: var(--mist);
}
.footer-links a {
  color: var(--mist);
  text-decoration: none;
  transition: color 0.15s ease;
}
.footer-links a:hover {
  color: var(--signal);
}
.footer-meta {
  font-size: 0.8rem;
  color: var(--fog);
}

@media (max-width: 768px) {
  .hero-section { padding: 2.5rem 0.5rem 2rem; }
  .hero-title { font-size: 1.95rem; }
  .hero-subtitle { font-size: 0.95rem; }
  .toolbar-row { flex-direction: column; align-items: flex-start; gap: 0.85rem; }
  .sites-grid { grid-template-columns: 1fr; }
  .window-address-bar { display: none; }
  .toast-notice { bottom: 1.5rem; right: 1.5rem; left: 1.5rem; justify-content: center; }
}
</style>
</head>
<body>

<!-- 顶栏：品牌与核心全局入口 -->
<header class="site-header">
  <div class="header-inner">
    <a href="./" class="brand" aria-label="一人一站 首页">
      <span class="brand-pulse"></span>
      <span>一人一站</span>
      <span class="brand-sub">One Person, One Site</span>
    </a>

    <div class="header-actions">
      <!-- 随机漫游按钮 -->
      <button id="btn-shuffle" class="header-btn" title="随机探索一个站点">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect width="18" height="18" x="3" y="3" rx="2"/><path d="M16 8h.01"/><path d="M8 8h.01"/><path d="M8 16h.01"/><path d="M16 16h.01"/><path d="M12 12h.01"/>
        </svg>
        <span>漫游</span>
      </button>

      <!-- 提交网站高亮按钮 -->
      <a href="https://github.com/realchendahuang/one-person-one-site/issues/new?template=submit-site.yml" target="_blank" rel="noopener" class="header-btn header-btn-primary">
        <span>提交网站</span>
      </a>

      <!-- 主题切换 -->
      <button id="btn-theme" class="icon-btn" title="切换主题 (浅色/深色/跟随系统)" aria-label="切换主题">
        <svg class="theme-icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>
        </svg>
        <svg class="theme-icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
        </svg>
        <svg class="theme-icon-system" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect width="20" height="14" x="2" y="3" rx="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/>
        </svg>
      </button>

      <!-- GitHub 仓库 -->
      <a href="https://github.com/realchendahuang/one-person-one-site" target="_blank" rel="noopener" class="icon-btn" title="GitHub 仓库">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/>
        </svg>
      </a>
    </div>
  </div>
</header>

<main class="main-wrapper">
  <!-- 大气且富有精神共鸣的 Hero 英雄区（不重复一人一站） -->
  <section class="hero-section">
    <div class="ambient-glow"></div>

    <div class="hero-pill">
      <span class="hero-pill-badge"></span>
      <span>平台与算法之外的个人互联网家园</span>
    </div>

    <h1 class="hero-title">在平台与算法之外<br>发现真实的个人世界</h1>

    <p class="hero-subtitle">
      收集值得驻足的独立个人网站、博客与数字花园。<br>
      逃离信息茧房与算法投喂，回归纯粹、独立与自由。
    </p>

    <div class="hero-stats-row">
      <div class="hero-stat-item">
        <span>收录</span>
        <strong id="stat-total-sites">13</strong>
        <span>个独立站点</span>
      </div>
      <span>·</span>
      <div class="hero-stat-item">
        <span>纯静态架构</span>
      </div>
      <span>·</span>
      <div class="hero-stat-item">
        <span>社区开放共建</span>
      </div>
    </div>
  </section>

  <!-- 搜索与筛选一体化控制栏 -->
  <section class="control-dock">
    <!-- 原生即时搜索框 -->
    <div class="search-bar-wrap">
      <div class="search-icon-left">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
        </svg>
      </div>
      <input
        id="search-input"
        type="search"
        class="search-input"
        placeholder="搜索站点名称、作者、简介或标签…"
        autocomplete="off"
        aria-label="搜索站点"
      >
      <div class="search-right-actions">
        <button id="search-clear-btn" class="search-clear-btn" title="清空搜索" aria-label="清空搜索">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        </button>
        <span class="search-kbd-hint">/</span>
      </div>
    </div>

    <!-- 标签分类与排序 -->
    <div class="toolbar-row">
      <div id="tags-bar" class="tags-scroll-wrap"></div>

      <div class="segmented-control" role="tablist" aria-label="排序选项">
        <button type="button" class="segment-btn active" data-sort="default">推荐</button>
        <button type="button" class="segment-btn" data-sort="name">字母序</button>
        <button type="button" class="segment-btn" data-sort="random">探索</button>
      </div>
    </div>

    <!-- 过滤状态行 -->
    <div class="filter-status-row">
      <span id="results-count-text">显示全部 13 个站点</span>
      <button id="btn-reset-filters" class="header-btn" style="display:none;padding:0.25rem 0.65rem;font-size:0.75rem;">重置筛选</button>
    </div>
  </section>

  <!-- 站点卡片网格 -->
  <div id="sites-grid" class="sites-grid"></div>

  <!-- 空状态 -->
  <div id="empty-state" class="empty-state" style="text-align:center;padding:4rem 1rem;display:none;">
    <p style="color:var(--mist);font-size:1.02rem;margin:0 0 1rem;">未找到与搜索条件匹配的站点</p>
    <button id="btn-empty-reset" class="header-btn header-btn-primary">清除所有筛选条件</button>
  </div>
</main>

<!-- 小窗实时预览系统 (macOS Live Browser) -->
<div id="preview-modal" class="preview-backdrop" role="dialog" aria-modal="true" aria-label="网站小窗预览">
  <div class="preview-window">
    <div class="window-titlebar">
      <div class="window-dots">
        <div id="modal-close-dot" class="window-dot dot-close" title="关闭 (ESC)"></div>
        <div class="window-dot dot-min"></div>
        <div class="window-dot dot-max"></div>
      </div>
      <div class="window-address-bar">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        <span id="modal-address">https://example.com</span>
      </div>
      <div class="window-actions">
        <a id="modal-external-link" href="#" target="_blank" rel="noopener noreferrer" class="window-btn" title="在新窗口直接打开">
          <span>在新标签页打开</span>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>
        </a>
      </div>
    </div>
    <div class="preview-body">
      <iframe
        id="modal-iframe"
        class="preview-iframe"
        src="about:blank"
        sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
        title="网站实时预览"
      ></iframe>
      <div id="modal-loading" class="preview-loading-overlay">
        <div class="spinner"></div>
        <span>正在载入实时预览…</span>
        <span style="font-size:0.8rem;color:var(--fog);">若站点设置了防内嵌安全策略，可点击右上角在新标签页直达</span>
      </div>
    </div>
  </div>
</div>

<!-- 浮动 Toast 提示 -->
<div id="toast" class="toast-notice" role="status" aria-live="polite">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
  <span id="toast-text">已复制到剪贴板</span>
</div>

<!-- 页脚 -->
<footer class="site-footer">
  <div class="footer-inner">
    <p class="footer-quote">
      “每个人，都应该在互联网上拥有一个真正属于自己的地方。”
    </p>
    <div class="footer-links">
      <a href="https://github.com/realchendahuang/one-person-one-site" target="_blank" rel="noopener">GitHub 仓库</a>
      <span>·</span>
      <a href="https://github.com/realchendahuang/one-person-one-site/issues/new?template=submit-site.yml" target="_blank" rel="noopener">提交新站</a>
      <span>·</span>
      <a href="./DIRECTORY.md" target="_blank" rel="noopener">站点全览</a>
      <span>·</span>
      <a href="https://github.com/realchendahuang/one-person-one-site/blob/main/LICENSE" target="_blank" rel="noopener">MIT License</a>
    </div>
    <div class="footer-meta">
      由社区共同构建维护 · 纯静态架构 · 零商业追踪
    </div>
  </div>
</footer>

<!-- 站点数据 -->
<script id="sites-data" type="application/json">__SITES_DATA__</script>

<script>
(function() {
  "use strict";

  /* 1. 主题切换状态机 */
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
    var current = document.documentElement.getAttribute("data-theme-mode");
    if (current === "system") {
      if (e.matches) {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
    }
  });

  /* 2. 数据解析与状态管理 */
  var rawData = JSON.parse(document.getElementById("sites-data").textContent || '{"sites":[]}');
  var sites = rawData.sites || [];

  var statTotal = document.getElementById("stat-total-sites");
  if (statTotal) statTotal.textContent = sites.length;

  var searchInput = document.getElementById("search-input");
  var searchClearBtn = document.getElementById("search-clear-btn");
  var tagsBar = document.getElementById("tags-bar");
  var grid = document.getElementById("sites-grid");
  var emptyState = document.getElementById("empty-state");
  var btnReset = document.getElementById("btn-reset-filters");
  var btnEmptyReset = document.getElementById("btn-empty-reset");
  var segmentBtns = document.querySelectorAll(".segment-btn");
  var btnShuffle = document.getElementById("btn-shuffle");
  var resultsCountText = document.getElementById("results-count-text");
  var toast = document.getElementById("toast");
  var toastText = document.getElementById("toast-text");

  // 小窗预览 DOM
  var previewModal = document.getElementById("preview-modal");
  var modalCloseDot = document.getElementById("modal-close-dot");
  var modalAddress = document.getElementById("modal-address");
  var modalExternalLink = document.getElementById("modal-external-link");
  var modalIframe = document.getElementById("modal-iframe");
  var modalLoading = document.getElementById("modal-loading");

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
    toastTimer = setTimeout(function() {
      toast.classList.remove("show");
    }, 2200);
  }

  /* 3. 小窗预览功能 */
  function openPreview(site) {
    if (!previewModal) return;
    modalAddress.textContent = site.url;
    modalExternalLink.href = site.url;
    modalLoading.classList.remove("hidden");
    modalIframe.src = site.url;

    previewModal.classList.add("open");
    document.body.style.overflow = "hidden";

    modalIframe.onload = function() {
      modalLoading.classList.add("hidden");
    };

    clearTimeout(iframeTimer);
    iframeTimer = setTimeout(function() {
      modalLoading.classList.add("hidden");
    }, 4500);
  }

  function closePreview() {
    if (!previewModal) return;
    previewModal.classList.remove("open");
    document.body.style.overflow = "";
    modalIframe.src = "about:blank";
  }

  if (modalCloseDot) modalCloseDot.addEventListener("click", closePreview);
  if (previewModal) {
    previewModal.addEventListener("click", function(e) {
      if (e.target === previewModal) closePreview();
    });
  }

  /* 4. 辅助函数 */
  function extractDomain(urlStr) {
    try {
      var u = new URL(urlStr);
      return u.hostname;
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

  /* 5. 标签栏统计与渲染 */
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
    allBtn.className = "tag-pill" + (activeTag === null ? " active" : "");
    allBtn.innerHTML = '<span>全部</span> <span class="tag-pill-count">' + sites.length + '</span>';
    allBtn.addEventListener("click", function() {
      activeTag = null;
      renderTagsBar();
      render();
    });
    tagsBar.appendChild(allBtn);

    allTags.forEach(function(tag) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "tag-pill" + (activeTag === tag ? " active" : "");
      btn.innerHTML = '<span>' + escapeHtml(tag) + '</span> <span class="tag-pill-count">' + tagCounts[tag] + '</span>';
      btn.addEventListener("click", function() {
        activeTag = activeTag === tag ? null : tag;
        renderTagsBar();
        render();
      });
      tagsBar.appendChild(btn);
    });
  }

  /* 6. 生成精致站点卡片 */
  function createCard(site) {
    var domain = extractDomain(site.url);
    var faviconUrl = domain ? "https://www.google.com/s2/favicons?domain=" + encodeURIComponent(domain) + "&sz=64" : "";
    var firstChar = getFirstChar(site.name || domain);

    var PALETTE = [
      "linear-gradient(135deg, #ff6a00, #ff8c37)",
      "linear-gradient(135deg, #0284c7, #38bdf8)",
      "linear-gradient(135deg, #059669, #34d399)",
      "linear-gradient(135deg, #7c3aed, #a78bfa)",
      "linear-gradient(135deg, #d97706, #fbbf24)",
      "linear-gradient(135deg, #db2777, #f472b6)"
    ];
    var charCode = firstChar.charCodeAt(0) || 0;
    var grad = PALETTE[charCode % PALETTE.length];

    var card = document.createElement("div");
    card.className = "site-card";

    // 顶部行
    var topRow = document.createElement("div");
    topRow.className = "card-top";

    var brandGroup = document.createElement("div");
    brandGroup.className = "card-brand-group";

    var favBox = document.createElement("div");
    favBox.className = "site-favicon";

    function applyFallback() {
      favBox.textContent = firstChar;
      favBox.style.background = grad;
      favBox.style.color = "#ffffff";
      favBox.style.fontWeight = "700";
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

    var titleGroup = document.createElement("div");
    titleGroup.className = "card-title-group";

    var nameEl = document.createElement("h3");
    nameEl.className = "site-name";
    nameEl.textContent = site.name;

    var ownerEl = document.createElement("div");
    ownerEl.className = "site-owner-badge";
    ownerEl.textContent = (site.owner ? site.owner : "") + (domain ? " · " + domain : "");

    titleGroup.appendChild(nameEl);
    titleGroup.appendChild(ownerEl);

    brandGroup.appendChild(favBox);
    brandGroup.appendChild(titleGroup);

    // 悬浮指示器（取代傻傻的灰预览按钮）
    var hint = document.createElement("div");
    hint.className = "card-hover-hint";
    hint.title = "点击小窗预览";
    hint.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M7 17 17 7"/><path d="M7 7h10v10"/></svg>';

    topRow.appendChild(brandGroup);
    topRow.appendChild(hint);

    // 简介
    var descEl = document.createElement("p");
    descEl.className = "site-desc";
    descEl.textContent = site.description || "独立个人站点";

    // 底部信息行
    var metaRow = document.createElement("div");
    metaRow.className = "card-meta-row";

    var tagsWrap = document.createElement("div");
    tagsWrap.className = "card-tags";
    (site.tags || []).slice(0, 4).forEach(function(t) {
      var tagSpan = document.createElement("span");
      tagSpan.className = "card-tag";
      tagSpan.textContent = t;
      tagsWrap.appendChild(tagSpan);
    });

    var actionsWrap = document.createElement("div");
    actionsWrap.className = "card-actions";

    // 复制 RSS 源
    if (site.feed) {
      var rssBtn = document.createElement("button");
      rssBtn.type = "button";
      rssBtn.className = "card-mini-btn";
      rssBtn.title = "复制 RSS 订阅源";
      rssBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 11a9 9 0 0 1 9 9"/><path d="M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="1"/></svg>';
      rssBtn.addEventListener("click", function(e) {
        e.stopPropagation();
        navigator.clipboard.writeText(site.feed).then(function() {
          showToast("已复制 RSS 订阅源");
        });
      });
      actionsWrap.appendChild(rssBtn);
    }

    // 复制网址
    var copyBtn = document.createElement("button");
    copyBtn.type = "button";
    copyBtn.className = "card-mini-btn";
    copyBtn.title = "复制网站链接";
    copyBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>';
    copyBtn.addEventListener("click", function(e) {
      e.stopPropagation();
      navigator.clipboard.writeText(site.url).then(function() {
        showToast("已复制站点网址");
      });
    });
    actionsWrap.appendChild(copyBtn);

    // 在新标签页直达
    var extBtn = document.createElement("a");
    extBtn.className = "card-mini-btn";
    extBtn.href = site.url;
    extBtn.target = "_blank";
    extBtn.rel = "noopener noreferrer";
    extBtn.title = "在新标签页打开";
    extBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>';
    extBtn.addEventListener("click", function(e) {
      e.stopPropagation();
    });
    actionsWrap.appendChild(extBtn);

    metaRow.appendChild(tagsWrap);
    metaRow.appendChild(actionsWrap);

    card.appendChild(topRow);
    card.appendChild(descEl);
    card.appendChild(metaRow);

    // 点击卡片进入小窗预览
    card.addEventListener("click", function(e) {
      if (e.target.closest("button") || e.target.closest("a")) return;
      openPreview(site);
    });

    return card;
  }

  /* 7. 列表渲染与实时过滤 */
  function render() {
    var q = searchQuery.toLowerCase();

    var filtered = sites.filter(function(s) {
      if (activeTag && (s.tags || []).indexOf(activeTag) === -1) {
        return false;
      }
      if (!q) return true;
      var textPool = [s.name, s.owner, s.description, (s.tags || []).join(" "), s.region, s.url].join(" ").toLowerCase();
      var terms = q.split(/\s+/).filter(Boolean);
      return terms.every(function(t) { return textPool.indexOf(t) !== -1; });
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

    // 状态统计与空状态更新
    emptyState.style.display = filtered.length === 0 ? "block" : "none";
    grid.style.display = filtered.length === 0 ? "none" : "grid";

    var isFiltered = (q.length > 0 || activeTag !== null);
    if (btnReset) btnReset.style.display = isFiltered ? "inline-flex" : "none";

    if (resultsCountText) {
      if (isFiltered) {
        resultsCountText.textContent = "找到 " + filtered.length + " 个站点（共 " + sites.length + " 个）";
      } else {
        resultsCountText.textContent = "显示全部 " + sites.length + " 个站点";
      }
    }
  }

  /* 8. 随机漫游 */
  function handleShuffle() {
    if (!sites || sites.length === 0) return;
    var randomSite = sites[Math.floor(Math.random() * sites.length)];
    openPreview(randomSite);
  }

  if (btnShuffle) btnShuffle.addEventListener("click", handleShuffle);

  /* 9. 搜索交互 */
  if (searchInput) {
    searchInput.addEventListener("input", function() {
      searchQuery = (searchInput.value || "").trim();
      if (searchClearBtn) {
        searchClearBtn.classList.toggle("visible", searchQuery.length > 0);
      }
      render();
    });
  }

  if (searchClearBtn) {
    searchClearBtn.addEventListener("click", function() {
      if (searchInput) searchInput.value = "";
      searchQuery = "";
      searchClearBtn.classList.remove("visible");
      if (searchInput) searchInput.focus();
      render();
    });
  }

  /* 10. 重置筛选 */
  function resetAllFilters() {
    searchQuery = "";
    if (searchInput) searchInput.value = "";
    if (searchClearBtn) searchClearBtn.classList.remove("visible");
    activeTag = null;
    sortMode = "default";
    segmentBtns.forEach(function(b) {
      b.classList.toggle("active", b.getAttribute("data-sort") === "default");
    });
    renderTagsBar();
    render();
  }

  if (btnReset) btnReset.addEventListener("click", resetAllFilters);
  if (btnEmptyReset) btnEmptyReset.addEventListener("click", resetAllFilters);

  // 排序分段控制器切换
  segmentBtns.forEach(function(btn) {
    btn.addEventListener("click", function() {
      segmentBtns.forEach(function(b) { b.classList.remove("active"); });
      btn.classList.add("active");
      sortMode = btn.getAttribute("data-sort") || "default";
      render();
    });
  });

  // 全局键盘快捷键: '/' 聚焦搜索，'ESC' 关闭预览
  window.addEventListener("keydown", function(e) {
    if (e.key === "Escape") {
      if (previewModal && previewModal.classList.contains("open")) {
        closePreview();
      }
    } else if (e.key === "/" && document.activeElement !== searchInput) {
      e.preventDefault();
      if (searchInput) {
        searchInput.focus();
        searchInput.select();
      }
    }
  });

  // 初始化
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