#!/usr/bin/env python3
"""从 data/sites.json 生成 GitHub Pages 静态网站（单文件 index.html）。

零第三方依赖：数据以内嵌 JSON 注入页面，搜索/过滤全部在浏览器端完成。
站点卡片由 JS 用 textContent 渲染，贡献数据中的特殊字符不会被当作 HTML 执行。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sites.json"
OUT = ROOT / "site"

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>一人一站 · One Person, One Site</title>
<meta name="description" content="收集值得关注的个人网站、独立博客与数字花园。发现那些在平台之外，认真经营自己互联网家园的人。">
<style>
:root {
  --bg: #faf9f6; --fg: #2b2822; --muted: #8a8577; --line: #e5e1d8;
  --card: #ffffff; --accent: #2f6f4f; --accent-soft: #e8f0ea;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1e1c18; --fg: #e8e4da; --muted: #9a9484; --line: #38352e;
    --card: #28251f; --accent: #7db894; --accent-soft: #2c3a31;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--fg);
  font-family: -apple-system, "PingFang SC", "Noto Sans SC", "Segoe UI", sans-serif;
  line-height: 1.6;
}
main { max-width: 960px; margin: 0 auto; padding: 2rem 1.25rem 4rem; }
header h1 { margin: 0 0 .25rem; font-size: 1.9rem; }
header p.tagline { margin: 0 0 .25rem; color: var(--muted); }
header p.links { margin: 0 0 1.5rem; font-size: .9rem; }
header p.links a { color: var(--accent); text-decoration: none; margin-right: 1rem; }
#search {
  width: 100%; padding: .65rem .9rem; font-size: 1rem;
  border: 1px solid var(--line); border-radius: 8px;
  background: var(--card); color: var(--fg);
}
#search:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
#stats { color: var(--muted); font-size: .85rem; margin: .6rem 0 1.25rem; }
#tags { display: flex; flex-wrap: wrap; gap: .4rem; margin-bottom: 1.5rem; }
.tag-btn {
  border: 1px solid var(--line); background: var(--card); color: var(--muted);
  border-radius: 999px; padding: .15rem .7rem; font-size: .8rem; cursor: pointer;
}
.tag-btn.active { background: var(--accent-soft); color: var(--accent); border-color: var(--accent); }
#grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 1rem; }
.card {
  display: flex; flex-direction: column; gap: .45rem;
  background: var(--card); border: 1px solid var(--line); border-radius: 10px;
  padding: 1rem 1.1rem; text-decoration: none; color: inherit;
}
.card:hover { border-color: var(--accent); }
.card h3 { margin: 0; font-size: 1.05rem; color: var(--accent); }
.card .owner { color: var(--muted); font-size: .85rem; }
.card .desc { margin: 0; font-size: .9rem; }
.card .meta { display: flex; flex-wrap: wrap; gap: .35rem; margin-top: auto; padding-top: .3rem; }
.card .meta span {
  background: var(--accent-soft); color: var(--accent);
  border-radius: 999px; padding: .05rem .55rem; font-size: .72rem;
}
.empty { color: var(--muted); text-align: center; padding: 3rem 0; }
footer { text-align: center; color: var(--muted); font-size: .85rem; padding: 2rem 0 3rem; }
footer a { color: var(--accent); }
</style>
</head>
<body>
<main>
  <header>
    <h1>一人一站 <span style="color:var(--muted);font-weight:400">· One Person, One Site</span></h1>
    <p class="tagline">收集值得关注的个人网站、独立博客与数字花园。</p>
    <p class="links">
      <a href="https://github.com/realchendahuang/one-person-one-site">GitHub 仓库</a>
      <a href="https://github.com/realchendahuang/one-person-one-site/issues/new?template=submit-site.yml">提交网站</a>
      <a href="./DIRECTORY.md">Markdown 目录</a>
    </p>
  </header>
  <input id="search" type="search" placeholder="搜索名称、站长、简介、标签…" autocomplete="off" aria-label="搜索站点">
  <p id="stats"></p>
  <div id="tags"></div>
  <div id="grid"></div>
  <div id="empty" class="empty" hidden>没有匹配的站点，换个关键词试试。</div>
  <footer>
    <p>每个人，都应该在互联网上拥有一个真正属于自己的地方。</p>
    <p><a href="https://github.com/realchendahuang/one-person-one-site/pulls">欢迎提交你的网站</a> · MIT License</p>
  </footer>
</main>
<script id="sites-data" type="application/json">__SITES_DATA__</script>
<script>
(function () {
  var DATA = JSON.parse(document.getElementById("sites-data").textContent);
  var sites = DATA.sites;

  var searchInput = document.getElementById("search");
  var tagsBox = document.getElementById("tags");
  var grid = document.getElementById("grid");
  var stats = document.getElementById("stats");
  var emptyTip = document.getElementById("empty");

  var activeTag = null;

  var tagCounts = {};
  sites.forEach(function (s) {
    (s.tags || []).forEach(function (t) {
      tagCounts[t] = (tagCounts[t] || 0) + 1;
    });
  });
  var tags = Object.keys(tagCounts).sort();

  tags.forEach(function (t) {
    var btn = document.createElement("button");
    btn.className = "tag-btn";
    btn.textContent = t + " (" + tagCounts[t] + ")";
    btn.addEventListener("click", function () {
      activeTag = activeTag === t ? null : t;
      renderTagBar();
      render();
    });
    tagsBox.appendChild(btn);
  });

  function renderTagBar() {
    Array.prototype.forEach.call(tagsBox.children, function (btn) {
      var tag = btn.textContent.replace(/ \\(\\d+\\)$/, "");
      btn.classList.toggle("active", tag === activeTag);
    });
  }

  function card(site) {
    var a = document.createElement("a");
    a.className = "card";
    a.href = site.url;
    a.rel = "noopener";
    var h3 = document.createElement("h3");
    h3.textContent = site.name;
    var owner = document.createElement("div");
    owner.className = "owner";
    owner.textContent = site.owner;
    var desc = document.createElement("p");
    desc.className = "desc";
    desc.textContent = site.description;
    var meta = document.createElement("div");
    meta.className = "meta";
    (site.tags || []).slice(0, 8).forEach(function (t) {
      var sp = document.createElement("span");
      sp.textContent = t;
      meta.appendChild(sp);
    });
    a.appendChild(h3); a.appendChild(owner); a.appendChild(desc); a.appendChild(meta);
    return a;
  }

  function render() {
    var q = searchInput.value.trim().toLowerCase();
    var shown = sites.filter(function (s) {
      if (activeTag && (s.tags || []).indexOf(activeTag) === -1) return false;
      if (!q) return true;
      var hay = [s.name, s.owner, s.description, (s.tags || []).join(" "),
                 s.languages.join(" "), s.region].join(" ").toLowerCase();
      return hay.indexOf(q) !== -1;
    });
    grid.textContent = "";
    shown.forEach(function (s) { grid.appendChild(card(s)); });
    emptyTip.hidden = shown.length > 0;
    stats.textContent = "共收录 " + sites.length + " 个站点，当前显示 " + shown.length + " 个。";
  }

  searchInput.addEventListener("input", render);
  render();
})();
</script>
</body>
</html>
"""


def main() -> None:
    sites = json.loads(DATA.read_text(encoding="utf-8"))
    payload = json.dumps({"sites": sites}, ensure_ascii=False, separators=(",", ":"))
    # </script> 出现在数据里会提前终止内嵌脚本标签，必须转义
    payload = payload.replace("</", "<\\/")
    html = HTML.replace("__SITES_DATA__", payload)
    out_dir = ROOT / "site"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    # DIRECTORY.md 直接作为静态资源提供，供 GitHub Pages 上下载阅读
    directory = ROOT / "DIRECTORY.md"
    if directory.exists():
        (out_dir / "DIRECTORY.md").write_text(directory.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Generated site/index.html with {len(sites)} site(s)")


if __name__ == "__main__":
    main()