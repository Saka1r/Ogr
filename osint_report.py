#!/usr/bin/env python3
"""
OSINT Report Generator + Graph
Команды: /new, /title, /add-fact, /add-link, /link, /links, /unlink, /graph, /list, /save, /load, /export, /help, /exit
"""

import os
import json
import html
import datetime
from pathlib import Path

# ─────────────────────────── ХРАНИЛИЩЕ ───────────────────────────
report = {
    "title": "Untitled OSINT Report",
    "author": "anonymous",
    "created": "",
    "modified": "",
    "facts": [],   # [{"id":1, "text":"...", "source":"...", "ts":"..."}]
    "links": [],   # [{"from":1, "to":2, "label":"..."}]
}
current_id = 1


# ─────────────────────────── УТИЛИТЫ ─────────────────────────────
def now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    print("\033[1;36m" + "=" * 56)
    print("   🔍  OSINT REPORT GENERATOR  ·  graph edition")
    print("=" * 56 + "\033[0m")
    print("  Введи \033[1;33m/help\033[0m чтобы увидеть команды\n")


def ok(msg):   print(f"  \033[1;32m✓\033[0m {msg}")
def err(msg):  print(f"  \033[1;31m✗\033[0m {msg}")
def info(msg): print(f"  \033[1;34m·\033[0m {msg}")


# ─────────────────────────── КОМАНДЫ ─────────────────────────────
def cmd_new():
    global report, current_id
    report = {
        "title": "Untitled OSINT Report",
        "author": "anonymous",
        "created": now_str(),
        "modified": now_str(),
        "facts": [],
        "links": [],
    }
    current_id = 1
    ok("Новый отчёт создан.")


def cmd_title():
    t = input("  Заголовок отчёта: ").strip()
    if not t: return err("Пусто.")
    report["title"] = t
    report["modified"] = now_str()
    ok(f"Заголовок: {t}")


def cmd_author():
    a = input("  Автор: ").strip()
    if not a: return err("Пусто.")
    report["author"] = a
    report["modified"] = now_str()
    ok(f"Автор: {a}")


def cmd_add_fact():
    global current_id
    text = input("  Факт: ").strip()
    if not text: return err("Пусто.")
    source = input("  Источник (URL или описание, можно оставить пустым): ").strip()
    report["facts"].append({
        "id": current_id,
        "text": text,
        "source": source,
        "ts": now_str(),
    })
    current_id += 1
    report["modified"] = now_str()
    ok(f"Факт #{current_id - 1} добавлен.")


def cmd_add_link():
    """Добавить ссылку без факта (например, просто ресурс)."""
    global current_id
    url = input("  URL: ").strip()
    if not url: return err("Пусто.")
    desc = input("  Описание (опционально): ").strip() or "—"
    report["facts"].append({
        "id": current_id,
        "text": f"🔗 {desc}",
        "source": url,
        "ts": now_str(),
        "kind": "link",
    })
    current_id += 1
    report["modified"] = now_str()
    ok(f"Ссылка #{current_id - 1} добавлена.")


def cmd_link():
    """Создать связь между двумя фактами."""
    try:
        id1 = int(input("  ID первого факта: ").strip())
        id2 = int(input("  ID второго факта: ").strip())
    except ValueError:
        return err("Нужны числа.")
    
    # Проверка существования
    ids = [f["id"] for f in report["facts"]]
    if id1 not in ids or id2 not in ids:
        return err("Один или оба ID не найдены.")
    if id1 == id2:
        return err("Нельзя связать факт сам с собой.")
    
    label = input("  Метка связи (опционально): ").strip() or ""
    
    report["links"].append({
        "from": id1,
        "to": id2,
        "label": label,
    })
    report["modified"] = now_str()
    ok(f"Связь #{id1} ↔ #{id2} создана.")


def cmd_links():
    """Показать все связи."""
    if not report["links"]:
        return info("Связей нет.")
    print(f"\n  \033[1;35m🔗 Связи\033[0m  ·  {len(report['links'])} шт.")
    print("  " + "-" * 52)
    for i, link in enumerate(report["links"], 1):
        label = f"  \033[2;36m[{link['label']}]\033[0m" if link.get("label") else ""
        print(f"  \033[1;33m{i:<3}\033[0m #{link['from']} ↔ #{link['to']}{label}")
    print()


def cmd_unlink():
    """Удалить связь."""
    try:
        i = int(input("  Номер связи для удаления: ").strip())
    except ValueError:
        return err("Нужно число.")
    
    if 1 <= i <= len(report["links"]):
        removed = report["links"].pop(i - 1)
        report["modified"] = now_str()
        ok(f"Связь #{removed['from']} ↔ #{removed['to']} удалена.")
    else:
        err("Неверный номер.")


def cmd_list():
    if not report["facts"]:
        return info("Отчёт пуст.")
    print(f"\n  \033[1;35m📋 {report['title']}\033[0m  ·  {len(report['facts'])} записей")
    print("  " + "-" * 52)
    for f in report["facts"]:
        src = f"  \033[2;36m→ {f['source']}\033[0m" if f.get("source") else ""
        print(f"  \033[1;33m#{f['id']:<3}\033[0m {f['text']}{src}")
    print()


def cmd_delete():
    try:
        i = int(input("  ID записи для удаления: ").strip())
    except ValueError:
        return err("Нужно число.")
    before = len(report["facts"])
    report["facts"] = [f for f in report["facts"] if f["id"] != i]
    if len(report["facts"]) < before:
        report["modified"] = now_str()
        ok(f"Запись #{i} удалена.")
    else:
        err(f"Запись #{i} не найдена.")


def cmd_save():
    fname = input("  Имя файла (по умолчанию report.json): ").strip() or "report.json"
    if not fname.endswith(".json"):
        fname += ".json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    ok(f"Сохранено: {fname}")


def cmd_load():
    global report, current_id
    fname = input("  Имя файла: ").strip() or "report.json"
    try:
        with open(fname, "r", encoding="utf-8") as f:
            report = json.load(f)
        # Миграция для старых файлов без links
        if "links" not in report:
            report["links"] = []
        current_id = max([0] + [x["id"] for x in report.get("facts", [])]) + 1
        ok(f"Загружено: {fname}  ·  {len(report['facts'])} записей  ·  {len(report['links'])} связей")
    except FileNotFoundError:
        err("Файл не найден.")
    except json.JSONDecodeError:
        err("Файл повреждён.")


# ─────────────────────────── HTML ГЕНЕРАЦИЯ ──────────────────────
def generate_html() -> str:
    facts_html = ""
    for f in report["facts"]:
        text = html.escape(f["text"])
        src = f.get("source", "")
        if src:
            if src.startswith(("http://", "https://")):
                link = f'<a href="{html.escape(src)}" target="_blank" rel="noopener">{html.escape(src)}</a>'
            else:
                link = f'<span class="src">{html.escape(src)}</span>'
            facts_html += f"""
            <div class="fact">
                <div class="fact-head">
                    <span class="num">#{f['id']:02d}</span>
                    <span class="ts">{html.escape(f['ts'])}</span>
                </div>
                <p class="text">{text}</p>
                <div class="source">{link}</div>
            </div>"""
        else:
            facts_html += f"""
            <div class="fact">
                <div class="fact-head">
                    <span class="num">#{f['id']:02d}</span>
                    <span class="ts">{html.escape(f['ts'])}</span>
                </div>
                <p class="text">{text}</p>
            </div>"""

    if not facts_html:
        facts_html = '<div class="empty">Пока нет записей. Добавь факты через <code>/add-fact</code></div>'

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(report['title'])}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg: #000000;
    --glass: rgba(255, 255, 255, 0.04);
    --glass-border: rgba(255, 255, 255, 0.08);
    --text: #e8e8ee;
    --muted: #8a8a99;
    --accent: #7c5cff;
    --accent2: #00d4ff;
  }}
  html, body {{
    min-height: 100vh;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, "SF Pro Display", "Inter", system-ui, sans-serif;
    font-size: 15px;
    line-height: 1.6;
    overflow-x: hidden;
  }}
  .wrap {{
    position: relative;
    z-index: 1;
    max-width: 900px;
    margin: 0 auto;
    padding: 60px 24px 100px;
  }}
  /* шапка */
  .header {{
    background: var(--glass);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border-radius: 20px;
    padding: 36px 40px;
    margin-bottom: 32px;
  }}
  .header h1 {{
    font-size: 32px;
    font-weight: 600;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #fff 0%, #a8a8c0 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 12px;
  }}
  .meta {{
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
    color: var(--muted);
    font-size: 13px;
  }}
  .meta span::before {{
    content: "●";
    color: var(--accent);
    margin-right: 8px;
    font-size: 8px;
    vertical-align: middle;
  }}
  /* список фактов */
  .facts {{
    display: flex;
    flex-direction: column;
    gap: 14px;
  }}
  .fact {{
    background: var(--glass);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(16px) saturate(160%);
    -webkit-backdrop-filter: blur(16px) saturate(160%);
    border-radius: 16px;
    padding: 22px 26px;
    transition: transform .2s ease, border-color .2s ease, background .2s ease;
  }}
  .fact:hover {{
    transform: translateY(-2px);
    border-color: rgba(124, 92, 255, 0.35);
    background: rgba(255, 255, 255, 0.06);
  }}
  .fact-head {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }}
  .num {{
    font-family: "JetBrains Mono", "SF Mono", monospace;
    font-size: 12px;
    color: var(--accent);
    background: rgba(124, 92, 255, 0.12);
    padding: 3px 10px;
    border-radius: 8px;
    font-weight: 600;
  }}
  .ts {{
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    color: var(--muted);
  }}
  .text {{
    font-size: 15px;
    color: var(--text);
    margin-bottom: 10px;
    white-space: pre-wrap;
    word-break: break-word;
  }}
  .source {{
    font-family: "JetBrains Mono", monospace;
    font-size: 12px;
    color: var(--accent2);
    word-break: break-all;
  }}
  .source a {{
    color: var(--accent2);
    text-decoration: none;
    border-bottom: 1px dashed rgba(0, 212, 255, 0.3);
    transition: border-color .2s;
  }}
  .source a:hover {{ border-bottom-color: var(--accent2); }}
  .empty {{
    text-align: center;
    padding: 60px 20px;
    color: var(--muted);
    background: var(--glass);
    border: 1px dashed var(--glass-border);
    border-radius: 16px;
    backdrop-filter: blur(10px);
  }}
  .empty code {{
    background: rgba(124, 92, 255, 0.15);
    padding: 2px 8px;
    border-radius: 6px;
    color: var(--accent);
  }}
  .footer {{
    margin-top: 40px;
    text-align: center;
    color: var(--muted);
    font-size: 12px;
  }}
  .footer span {{
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 600;
  }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <h1>{html.escape(report['title'])}</h1>
      <div class="meta">
        <span>Автор: {html.escape(report.get('author','anonymous'))}</span>
        <span>Создан: {html.escape(report.get('created','—'))}</span>
        <span>Изменён: {html.escape(report.get('modified','—'))}</span>
        <span>Записей: {len(report['facts'])}</span>
        <span>Связей: {len(report['links'])}</span>
      </div>
    </div>
    <div class="facts">
      {facts_html}
    </div>
    <div class="footer">
      -_- · <span>OSINT Report Generator</span> · {now_str()}
    </div>
  </div>
</body>
</html>"""


def cmd_export():
    fname = input("  Имя файла (по умолчанию report.html): ").strip() or "report.html"
    if not fname.endswith(".html"):
        fname += ".html"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(generate_html())
    ok(f"HTML экспортирован: {fname}")


# ─────────────────────────── GRAPH HTML ──────────────────────────
def generate_graph_html() -> str:
    """Генерирует HTML с графом связей используя vis-network."""
    
    # Подготовка данных для vis.js
    nodes = []
    for f in report["facts"]:
        text_short = f["text"][:50] + "..." if len(f["text"]) > 50 else f["text"]
        nodes.append({
            "id": f["id"],
            "label": f"#{f['id']}\n{html.escape(text_short)}",
            "color": {
                "background": "#1a1a1f",
                "border": "#7c5cff",
                "highlight": {
                    "background": "#2a2a3f",
                    "border": "#00d4ff"
                }
            },
            "font": {
                "color": "#e8e8ee",
                "size": 14,
                "face": "Inter, sans-serif"
            },
            "shape": "box",
            "margin": 10,
            "borderWidth": 2,
            "borderWidthSelected": 3
        })
    
    edges = []
    for i, link in enumerate(report["links"]):
        edges.append({
            "from": link["from"],
            "to": link["to"],
            "label": html.escape(link.get("label", "")),
            "color": {
                "color": "#00d4ff",
                "highlight": "#7c5cff"
            },
            "font": {
                "color": "#8a8a99",
                "size": 12,
                "align": "middle"
            },
            "arrows": "to",
            "smooth": {
                "type": "continuous"
            }
        })
    
    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)
    
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(report['title'])} · Graph</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg: #000000;
    --glass: rgba(255, 255, 255, 0.04);
    --glass-border: rgba(255, 255, 255, 0.08);
    --text: #e8e8ee;
    --muted: #8a8a99;
    --accent: #7c5cff;
    --accent2: #00d4ff;
  }}
  html, body {{
    height: 100vh;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, "SF Pro Display", "Inter", system-ui, sans-serif;
    overflow: hidden;
  }}
  .header {{
    position: fixed;
    top: 20px;
    left: 20px;
    right: 20px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border-radius: 16px;
    padding: 20px 28px;
    z-index: 100;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .header h1 {{
    font-size: 20px;
    font-weight: 600;
    background: linear-gradient(135deg, #fff 0%, #a8a8c0 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .stats {{
    display: flex;
    gap: 20px;
    color: var(--muted);
    font-size: 13px;
  }}
  .stats span::before {{
    content: "●";
    color: var(--accent);
    margin-right: 6px;
    font-size: 8px;
  }}
  #graph {{
    width: 100%;
    height: 100vh;
  }}
  .footer {{
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--glass);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(20px);
    border-radius: 12px;
    padding: 12px 24px;
    color: var(--muted);
    font-size: 12px;
    z-index: 100;
  }}
  .footer span {{
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 600;
  }}
</style>
</head>
<body>
  <div class="header">
    <h1>{html.escape(report['title'])} · Graph</h1>
    <div class="stats">
      <span>Узлов: {len(nodes)}</span>
      <span>Связей: {len(edges)}</span>
    </div>
  </div>
  <div id="graph"></div>
  <div class="footer">
    Перетаскивай узлы · Колёсико для зума · <span>OSINT Report Generator</span>
  </div>
  <script>
    const nodes = new vis.DataSet({nodes_json});
    const edges = new vis.DataSet({edges_json});
    
    const container = document.getElementById('graph');
    const data = {{ nodes, edges }};
    const options = {{
      nodes: {{
        font: {{
          multi: false
        }},
        borderWidth: 2
      }},
      edges: {{
        width: 2,
        selectionWidth: 3
      }},
      physics: {{
        enabled: true,
        barnesHut: {{
          gravitationalConstant: -3000,
          centralGravity: 0.3,
          springLength: 150,
          springConstant: 0.04,
          damping: 0.09
        }},
        stabilization: {{
          iterations: 200
        }}
      }},
      interaction: {{
        hover: true,
        tooltipDelay: 200
      }}
    }};
    
    const network = new vis.Network(container, data, options);
  </script>
</body>
</html>"""


def cmd_graph():
    fname = input("  Имя файла (по умолчанию graph.html): ").strip() or "graph.html"
    if not fname.endswith(".html"):
        fname += ".html"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(generate_graph_html())
    ok(f"Граф экспортирован: {fname}")


# ─────────────────────────── HELP ────────────────────────────────
HELP = """
  \033[1;36mКоманды:\033[0m
    /new          — создать новый отчёт
    /title        — задать заголовок
    /author       — задать автора
    /add-fact     — добавить факт (+ опционально источник)
    /add-link     — добавить просто ссылку
    /link         — создать связь между двумя фактами
    /links        — показать все связи
    /unlink       — удалить связь
    /list         — показать все записи
    /delete       — удалить запись по ID
    /save         — сохранить отчёт в JSON
    /load         — загрузить отчёт из JSON
    /export       — экспортировать в HTML (список фактов)
    /graph        — экспортировать граф связей в HTML
    /clear        — очистить экран
    /help         — эта подсказка
    /exit         — выход
"""


# ─────────────────────────── MAIN LOOP ───────────────────────────
def main():
    clear()
    banner()
    cmd_new()

    while True:
        try:
            raw = input("\n\033[1;36mosint>\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not raw:
            continue

        cmd = raw.split()[0].lower()
        if cmd in ("/help", "help", "?"):      print(HELP)
        elif cmd in ("/new", "new"):           cmd_new()
        elif cmd in ("/title", "title"):       cmd_title()
        elif cmd in ("/author", "author"):     cmd_author()
        elif cmd in ("/add-fact", "add-fact"): cmd_add_fact()
        elif cmd in ("/add-link", "add-link"): cmd_add_link()
        elif cmd in ("/link", "link"):         cmd_link()
        elif cmd in ("/links", "links"):       cmd_links()
        elif cmd in ("/unlink", "unlink"):     cmd_unlink()
        elif cmd in ("/list", "list", "ls"):   cmd_list()
        elif cmd in ("/delete", "delete", "rm"): cmd_delete()
        elif cmd in ("/save", "save"):         cmd_save()
        elif cmd in ("/load", "load"):         cmd_load()
        elif cmd in ("/export", "export", "html"): cmd_export()
        elif cmd in ("/graph", "graph"):       cmd_graph()
        elif cmd in ("/clear", "clear", "cls"): clear(); banner()
        elif cmd in ("/exit", "/quit", "exit", "quit"): break
        else: err(f"Неизвестная команда: {cmd}  (введи /help)")


if __name__ == "__main__":
    main()
