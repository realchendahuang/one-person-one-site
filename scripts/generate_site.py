#!/usr/bin/env python3
"""从 data/sites.json 生成 GitHub Pages 静态网站（单文件 index.html）。

设计哲学：
- 首屏即内容：极度压缩顶部冗余占位，正经站点卡片首屏直接呈现，极度适合截图与浏览
- 顶栏高度集成：搜索、提交网站、随机漫游全部收入顶栏，彻底移除非核心大部件
- 弹窗搜索系统 (Command Palette)：点击顶栏搜索按钮或按 / 键弹出全局命令板
- 小窗实时预览系统 (Live Browser Modal)：macOS 拟态浏览器窗口，支持直接交互式预览
- 高级设计系统：纸感浅色 + 纯深暗黑双主题，定制分段控制器，零商业 Logo 中立排版
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
<meta name="description" content="收集值得关注的个人网站、独立博客与数字花园。发现那些在平台与算法之外，认真经营自己互联网家园的人。">
<meta property="og:title" content="一人一站 · One Person, One Site">
<meta property="og:description" content="收集值得关注的个人网站、独立博客与数字花园。发现那些在平台与算法之外，认真经营自己互联网家园的人。">
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
   一人一站 · 高级极简设计系统
   首屏即内容 · 紧凑克制 · 信号橙 #ff6a00 · 质感分层
   ============================================================ */
:root {
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-full: 9999px;

  color-scheme: light;

  /* 浅色 */
  --paper: #f6f6f7;
  --soft-surface: #ededf0;
  --surface: #ffffff;
  --surface-hover: #fafafa;
  --line: #e3e3e8;
  --line-subtle: #eeeeef;
  --ink: #111113;
  --mist: #5c5c66;
  --fog: #9a9aa5;

  /* 信号色系 */
  --signal: #ff6a00;
  --signal-hover: #ff7d1a;
  --signal-soft: rgba(255, 106, 0, 0.08);
  --signal-border: rgba(255, 106, 0, 0.22);
  --signal-glow: rgba(255, 106, 0, 0.16);

  /* 质感槽 */
  --wash: rgba(0, 0, 0, 0.04);
  --wash-strong: rgba(0, 0, 0, 0.07);
  --panel-elev: 0 1px 3px rgba(0, 0, 0, 0.04), 0 8px 24px -8px rgba(0, 0, 0, 0.07);
  --panel-elev-sm: 0 1px 2px rgba(0, 0, 0, 0.03), 0 3px 8px -2px rgba(0, 0, 0, 0.04);
  --hover-lift: 0 4px 6px -2px rgba(0, 0, 0, 0.04), 0 16px 28px -6px rgba(0, 0, 0, 0.1);
  --dock-inset: inset 0 1px 0 0 rgba(255, 255, 255, 0.9);

  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

html.dark {
  color-scheme: dark;

  /* 深色 */
  --paper: #09090b;
  --soft-surface: #141416;
  --surface: #19191c;
  --surface-hover: #222226;
  --line: #26262b;
  --line-subtle: #1c1c20;
  --ink: #f5f5f7;
  --mist: #9f9fa9;
  --fog: #666670;

  /* 信号色系 */
  --signal: #ff6a00;
  --signal-hover: #ff7d1a;
  --signal-soft: rgba(255, 106, 0, 0.14);
  --signal-border: rgba(255, 106, 0, 0.35);
  --signal-glow: rgba(255, 106, 0, 0.28);

  /* 质感槽 */
  --wash: rgba(255, 255, 255, 0.04);
  --wash-strong: rgba(255, 255, 255, 0.08);
  --panel-elev: inset 0 1px 0 0 rgba(255, 255, 255, 0.06), inset 0 0 0 1px rgba(255, 255, 255, 0.06), 0 10px 24px -8px rgba(0, 0, 0, 0.6);
  --panel-elev-sm: inset 0 1px 0 0 rgba(255, 255, 255, 0.04), inset 0 0 0 1px rgba(255, 255, 255, 0.05);
  --hover-lift: inset 0 1px 0 0 rgba(255, 255, 255, 0.09), inset 0 0 0 1px rgba(255, 106, 0, 0.4), 0 18px 36px -10px rgba(0, 0, 0, 0.85);
  --dock-inset: inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
}

*, *::before, *::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  background-color: var(--paper);
  color: var(--ink);
  font-family: var(--font-sans);
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ================= 顶栏 ================= */
.site-header {
  position: sticky;
  top: 0;
  z-index: 40;
  width: 100%;
  border-bottom: 1px solid var(--line);
  background: rgba(246, 246, 247, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  transition: background-color 0.2s ease, border-color 0.2s ease;
}
html.dark .site-header {
  background: rgba(9, 9, 11, 0.85);
}

.header-inner {
  max-width: 1140px;
  height: 54px;
  margin: 0 auto;
  padding: 0 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  text-decoration: none;
  color: var(--ink);
  font-weight: 700;
  font-size: 1.02rem;
  letter-spacing: -0.02em;
  user-select: none;
}
.brand-pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--signal);
  box-shadow: 0 0 10px var(--signal);
}
.brand-sub {
  font-size: 0.82rem;
  font-weight: 400;
  color: var(--fog);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.header-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.75rem;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--mist);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-full);
  text-decoration: none;
  box-shadow: var(--panel-elev-sm);
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
  color: #ffffff;
  border-color: var(--signal);
  box-shadow: 0 2px 8px var(--signal-glow);
}
.header-btn-primary:hover {
  background: var(--signal-hover);
  color: #ffffff;
  border-color: var(--signal-hover);
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  background: var(--surface);
  border: 1px solid var(--line);
  color: var(--mist);
  cursor: pointer;
  box-shadow: var(--panel-elev-sm);
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

/* ================= 容器 (紧凑首屏) ================= */
.main-wrapper {
  max-width: 1140px;
  margin: 0 auto;
  padding: 1.35rem 1.25rem 4rem;
  flex: 1;
  width: 100%;
}

/* 紧凑首屏标题区 */
.page-intro {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1.25rem;
  margin-bottom: 1.15rem;
  flex-wrap: wrap;
}
.intro-left {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.page-title {
  font-size: 1.65rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  margin: 0;
  color: var(--ink);
  line-height: 1.2;
}
.page-desc {
  margin: 0;
  font-size: 0.88rem;
  color: var(--mist);
}

/* 分段控制器 */
.segmented-control {
  display: inline-flex;
  align-items: center;
  background: var(--soft-surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-full);
  padding: 2.5px;
  gap: 2px;
  user-select: none;
}
.segment-btn {
  background: transparent;
  border: none;
  color: var(--mist);
  font-size: 0.78rem;
  font-weight: 500;
  padding: 0.25rem 0.65rem;
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
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* 标签筛选栏 */
.tags-bar-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
  margin-bottom: 1.35rem;
}
.tag-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.7rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-full);
  font-size: 0.78rem;
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
  color: var(--paper);
  border-color: var(--ink);
  font-weight: 600;
}
html.dark .tag-pill.active {
  background: #ffffff;
  color: #000000;
  border-color: #ffffff;
}
.tag-pill-count {
  font-size: 0.7rem;
  opacity: 0.7;
  font-family: var(--font-mono);
}

.search-filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.65rem;
  background: var(--signal-soft);
  color: var(--signal);
  border: 1px solid var(--signal-border);
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}
.search-filter-chip:hover {
  background: rgba(255, 106, 0, 0.16);
}

/* ================= 站点卡片网格 ================= */
.sites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.15rem;
}

.site-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  box-shadow: var(--panel-elev);
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease;
  color: inherit;
  overflow: hidden;
  cursor: pointer;
}
.site-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--hover-lift);
  border-color: var(--signal-border);
}

.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.65rem;
}
.card-brand-group {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  min-width: 0;
}
.site-favicon {
  width: 34px;
  height: 34px;
  border-radius: 9px;
  background: var(--soft-surface);
  border: 1px solid var(--line);
  object-fit: cover;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--mist);
  box-shadow: var(--dock-inset);
  overflow: hidden;
}
.site-favicon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-title-group {
  min-width: 0;
}
.site-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: -0.015em;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.site-owner-badge {
  font-size: 0.8rem;
  color: var(--mist);
  margin-top: 0.1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 顶部预览按钮 */
.card-preview-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.28rem 0.55rem;
  border-radius: var(--radius-sm);
  background: var(--soft-surface);
  border: 1px solid var(--line);
  color: var(--mist);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.16s ease;
  flex-shrink: 0;
}
.card-preview-btn:hover {
  background: var(--signal);
  color: #ffffff;
  border-color: var(--signal);
}
.card-preview-btn svg {
  width: 12px;
  height: 12px;
}

.site-desc {
  margin: 0 0 0.85rem;
  font-size: 0.86rem;
  color: var(--mist);
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.card-meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
  padding-top: 0.75rem;
  border-top: 1px solid var(--line-subtle);
  margin-top: auto;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}
.card-tag {
  font-size: 0.7rem;
  font-weight: 500;
  padding: 0.1rem 0.45rem;
  border-radius: var(--radius-full);
  background: var(--soft-surface);
  color: var(--mist);
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
.card-mini-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 6px;
  background: transparent;
  border: 1px solid transparent;
  color: var(--mist);
  cursor: pointer;
  padding: 0;
  transition: all 0.15s ease;
  text-decoration: none;
}
.card-mini-btn:hover {
  background: var(--wash-strong);
  color: var(--ink);
  border-color: var(--line);
}
.card-mini-btn svg {
  width: 13px;
  height: 13px;
}

/* ================= 搜索弹窗 (Command Palette) ================= */
.search-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 4.5rem 1rem 1rem;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
}
.search-backdrop.open {
  opacity: 1;
  pointer-events: auto;
}

.search-palette {
  width: 100%;
  max-width: 580px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 50px -10px rgba(0, 0, 0, 0.35);
  overflow: hidden;
  transform: translateY(-8px);
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  flex-direction: column;
  max-height: 72vh;
}
.search-backdrop.open .search-palette {
  transform: translateY(0);
}

.palette-input-wrap {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1.15rem;
  border-bottom: 1px solid var(--line);
}
.palette-input-wrap svg {
  color: var(--fog);
  flex-shrink: 0;
}
.palette-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 1rem;
  font-family: inherit;
  color: var(--ink);
}
.palette-input::placeholder {
  color: var(--fog);
}
.palette-close-btn {
  background: var(--wash);
  border: none;
  color: var(--mist);
  border-radius: 6px;
  padding: 0.2rem 0.5rem;
  font-size: 0.75rem;
  cursor: pointer;
  font-family: var(--font-mono);
}

.palette-results {
  overflow-y: auto;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.palette-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.15s ease;
  text-decoration: none;
  color: inherit;
}
.palette-item:hover, .palette-item.active {
  background: var(--soft-surface);
}
.palette-item-left {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  min-width: 0;
}
.palette-item-title {
  font-weight: 600;
  font-size: 0.92rem;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.palette-item-desc {
  font-size: 0.8rem;
  color: var(--mist);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ================= 小窗预览模态框 (Live Browser Modal) ================= */
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
  padding: 1.25rem;
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
  max-width: 960px;
  height: 84vh;
  max-height: 800px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.4);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transform: scale(0.96) translateY(10px);
  transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}
.preview-backdrop.open .preview-window {
  transform: scale(1) translateY(0);
}

.window-titlebar {
  height: 46px;
  background: var(--soft-surface);
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  gap: 1rem;
  user-select: none;
  flex-shrink: 0;
}
.window-dots {
  display: flex;
  align-items: center;
  gap: 7px;
  width: 58px;
}
.window-dot {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: var(--line);
}
.dot-close { background: #ff5f56; cursor: pointer; }
.dot-min { background: #ffbd2e; }
.dot-max { background: #27c93f; }

.window-address-bar {
  flex: 1;
  max-width: 520px;
  height: 28px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  padding: 0 0.85rem;
  font-size: 0.78rem;
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
  gap: 0.45rem;
}
.window-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--mist);
  padding: 0.22rem 0.6rem;
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
  background: #111113;
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
  gap: 0.75rem;
  color: var(--mist);
  font-size: 0.86rem;
  transition: opacity 0.2s ease;
}
.preview-loading-overlay.hidden {
  opacity: 0;
  pointer-events: none;
}
.spinner {
  width: 26px;
  height: 26px;
  border: 2.5px solid var(--line);
  border-top-color: var(--signal);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ================= Toast ================= */
.toast-notice {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 130;
  background: var(--ink);
  color: var(--paper);
  padding: 0.6rem 1.1rem;
  border-radius: var(--radius-md);
  font-size: 0.84rem;
  font-weight: 500;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  gap: 0.5rem;
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
  padding: 3rem 1.25rem 3.5rem;
  margin-top: auto;
}
.footer-inner {
  max-width: 1140px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1rem;
}
.footer-quote {
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}
.footer-links {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-wrap: wrap;
  font-size: 0.84rem;
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
  font-size: 0.78rem;
  color: var(--fog);
}

@media (max-width: 768px) {
  .page-intro { flex-direction: column; align-items: flex-start; gap: 0.75rem; }
  .sites-grid { grid-template-columns: 1fr; }
  .window-address-bar { display: none; }
  .toast-notice { bottom: 1.5rem; right: 1.5rem; left: 1.5rem; justify-content: center; }
}
</style>
</head>
<body>

<!-- 顶栏：高度集成全部功能 -->
<header class="site-header">
  <div class="header-inner">
    <a href="./" class="brand" aria-label="一人一站 首页">
      <span class="brand-pulse"></span>
      <span>一人一站</span>
      <span class="brand-sub">One Person, One Site</span>
    </a>

    <div class="header-actions">
      <!-- 搜索触发按钮 -->
      <button id="btn-search-trigger" class="header-btn" title="搜索 (/)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
        </svg>
        <span>搜索</span>
      </button>

      <!-- 随机漫游按钮 -->
      <button id="btn-shuffle" class="header-btn" title="随机探索">
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
      <button id="btn-theme" class="icon-btn" title="切换主题" aria-label="切换主题">
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
  <!-- 紧凑标题 + 排序分段控制器 -->
  <section class="page-intro">
    <div class="intro-left">
      <h1 class="page-title">一人一站</h1>
      <p class="page-desc">收集值得关注的独立博客、数字花园与个人空间</p>
    </div>
    <div class="intro-right">
      <div class="segmented-control" role="tablist" aria-label="排序选项">
        <button type="button" class="segment-btn active" data-sort="default">推荐</button>
        <button type="button" class="segment-btn" data-sort="name">字母序</button>
        <button type="button" class="segment-btn" data-sort="random">探索</button>
      </div>
    </div>
  </section>

  <!-- 标签胶囊栏 -->
  <div class="tags-bar-row">
    <div id="tags-bar" style="display:flex;gap:0.4rem;flex-wrap:wrap;"></div>
    <div id="active-search-chip" class="search-filter-chip" style="display:none;" title="点击清除搜索">
      <span id="active-search-text"></span>
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
    </div>
  </div>

  <!-- 正经内容：卡片网格首屏直达 -->
  <div id="sites-grid" class="sites-grid"></div>

  <!-- 空状态 -->
  <div id="empty-state" class="empty-state" style="text-align:center;padding:3rem 1rem;display:none;">
    <p style="color:var(--mist);margin:0 0 1rem;">未找到匹配站点</p>
    <button id="btn-reset-filters" class="header-btn">重置筛选</button>
  </div>
</main>

<!-- 搜索弹窗 (Command Palette) -->
<div id="search-modal" class="search-backdrop" role="dialog" aria-modal="true" aria-label="全局搜索">
  <div class="search-palette">
    <div class="palette-input-wrap">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
      </svg>
      <input id="palette-search-input" class="palette-input" placeholder="搜索站点名称、作者、简介或标签…" autocomplete="off">
      <button id="palette-close-btn" class="palette-close-btn">ESC</button>
    </div>
    <div id="palette-results" class="palette-results"></div>
  </div>
</div>

<!-- 小窗实时预览系统 (Live Browser Modal) -->
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
        <a id="modal-external-link" href="#" target="_blank" rel="noopener noreferrer" class="window-btn" title="在新窗口打开">
          <span>在新窗口打开</span>
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
        <span style="font-size:0.78rem;color:var(--fog);">若站点设置了防内嵌保护，可直接点击右上角在新窗口打开</span>
      </div>
    </div>
  </div>
</div>

<!-- 浮动 Toast 提示 -->
<div id="toast" class="toast-notice" role="status" aria-live="polite">
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
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
      <a href="./DIRECTORY.md" target="_blank" rel="noopener">完整目录</a>
      <span>·</span>
      <a href="https://github.com/realchendahuang/one-person-one-site/blob/main/LICENSE" target="_blank" rel="noopener">MIT License</a>
    </div>
    <div class="footer-meta">
      由社区共同构建维护 · 纯静态架构 · 零第三方追踪
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

  /* 2. 数据解析与状态 */
  var rawData = JSON.parse(document.getElementById("sites-data").textContent || '{"sites":[]}');
  var sites = rawData.sites || [];

  var tagsBar = document.getElementById("tags-bar");
  var grid = document.getElementById("sites-grid");
  var emptyState = document.getElementById("empty-state");
  var btnReset = document.getElementById("btn-reset-filters");
  var segmentBtns = document.querySelectorAll(".segment-btn");
  var btnShuffle = document.getElementById("btn-shuffle");
  var toast = document.getElementById("toast");
  var toastText = document.getElementById("toast-text");
  var activeSearchChip = document.getElementById("active-search-chip");
  var activeSearchText = document.getElementById("active-search-text");

  // 搜索弹窗 DOM
  var searchModal = document.getElementById("search-modal");
  var btnSearchTrigger = document.getElementById("btn-search-trigger");
  var paletteInput = document.getElementById("palette-search-input");
  var paletteCloseBtn = document.getElementById("palette-close-btn");
  var paletteResults = document.getElementById("palette-results");

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
    }, 4000);
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

  /* 4. 搜索弹窗逻辑 */
  function openSearch() {
    if (!searchModal) return;
    searchModal.classList.add("open");
    paletteInput.value = searchQuery;
    renderPaletteResults(searchQuery);
    setTimeout(function() { paletteInput.focus(); }, 60);
  }

  function closeSearch() {
    if (!searchModal) return;
    searchModal.classList.remove("open");
  }

  if (btnSearchTrigger) btnSearchTrigger.addEventListener("click", openSearch);
  if (paletteCloseBtn) paletteCloseBtn.addEventListener("click", closeSearch);
  if (searchModal) {
    searchModal.addEventListener("click", function(e) {
      if (e.target === searchModal) closeSearch();
    });
  }

  function renderPaletteResults(q) {
    q = (q || "").trim().toLowerCase();
    paletteResults.textContent = "";

    var matches = sites.filter(function(s) {
      if (!q) return true;
      var textPool = [s.name, s.owner, s.description, (s.tags || []).join(" "), s.region, s.url].join(" ").toLowerCase();
      return textPool.indexOf(q) !== -1;
    });

    if (matches.length === 0) {
      var noItem = document.createElement("div");
      noItem.style.padding = "1.5rem 1rem";
      noItem.style.textAlign = "center";
      noItem.style.color = "var(--fog)";
      noItem.style.fontSize = "0.88rem";
      noItem.textContent = "无匹配站点";
      paletteResults.appendChild(noItem);
      return;
    }

    matches.slice(0, 10).forEach(function(s) {
      var row = document.createElement("div");
      row.className = "palette-item";
      var domain = extractDomain(s.url);
      row.innerHTML = '<div class="palette-item-left">' +
        '<div><div class="palette-item-title">' + escapeHtml(s.name) + '</div>' +
        '<div class="palette-item-desc">' + escapeHtml(s.owner || domain) + ' · ' + escapeHtml(s.description) + '</div></div>' +
        '</div>' +
        '<span style="font-size:0.75rem;color:var(--signal);font-weight:600;">预览 ↗</span>';

      row.addEventListener("click", function() {
        closeSearch();
        openPreview(s);
      });
      paletteResults.appendChild(row);
    });
  }

  if (paletteInput) {
    paletteInput.addEventListener("input", function() {
      searchQuery = paletteInput.value.trim();
      renderPaletteResults(searchQuery);
      updateActiveSearchChip();
      render();
    });
  }

  function updateActiveSearchChip() {
    if (searchQuery) {
      activeSearchChip.style.display = "inline-flex";
      activeSearchText.textContent = "搜索: " + searchQuery;
    } else {
      activeSearchChip.style.display = "none";
    }
  }

  if (activeSearchChip) {
    activeSearchChip.addEventListener("click", function() {
      searchQuery = "";
      if (paletteInput) paletteInput.value = "";
      updateActiveSearchChip();
      render();
    });
  }

  /* 5. 标签胶囊统计与渲染 */
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

  /* 6. 辅助函数 */
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

  /* 7. 生成站点卡片 */
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

    // 预览按钮
    var previewBtn = document.createElement("button");
    previewBtn.type = "button";
    previewBtn.className = "card-preview-btn";
    previewBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg><span>预览</span>';
    previewBtn.title = "在小窗中预览";
    previewBtn.addEventListener("click", function(e) {
      e.stopPropagation();
      openPreview(site);
    });

    topRow.appendChild(brandGroup);
    topRow.appendChild(previewBtn);

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

    // RSS Feed
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
    copyBtn.title = "复制网址";
    copyBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>';
    copyBtn.addEventListener("click", function(e) {
      e.stopPropagation();
      navigator.clipboard.writeText(site.url).then(function() {
        showToast("已复制站点网址");
      });
    });
    actionsWrap.appendChild(copyBtn);

    // 直达外部链接
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
      var textPool = [s.name, s.owner, s.description, (s.tags || []).join(" "), s.region, s.url].join(" ").toLowerCase();
      return textPool.indexOf(q) !== -1;
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

  /* 10. 全局事件绑定 */
  if (btnReset) {
    btnReset.addEventListener("click", function() {
      searchQuery = "";
      activeTag = null;
      sortMode = "default";
      updateActiveSearchChip();
      segmentBtns.forEach(function(b) {
        b.classList.toggle("active", b.getAttribute("data-sort") === "default");
      });
      renderTagsBar();
      render();
    });
  }

  segmentBtns.forEach(function(btn) {
    btn.addEventListener("click", function() {
      segmentBtns.forEach(function(b) { b.classList.remove("active"); });
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