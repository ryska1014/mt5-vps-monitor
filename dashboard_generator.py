import os
import json
from datetime import datetime
import time

# --- KONFIGURACJA i WERSJONOWANIE ---
DASHBOARD_VERSION = "1.1.0"  # Inteligentne sortowanie PnL (pozycje na górze) + ukryta gotowość na flagę AlgoTrading
DIRECTORY_PATH = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files"
OUTPUT_HTML_FILE = "dashboard.html"


def read_json_safely(filepath):
    for _ in range(3):
        try:
            with open(filepath, 'r', encoding='ansi') as f:
                return json.load(f)
        except (json.JSONDecodeError, PermissionError):
            time.sleep(0.05)
        except Exception as e:
            print(f"Błąd odczytu pliku {filepath}: {e}")
            break
    return None


def load_all_accounts():
    accounts_data = {}
    if not os.path.exists(DIRECTORY_PATH):
        return {}
        
    files = os.listdir(DIRECTORY_PATH)
    
    for file in files:
        if file.startswith("today_") and file.endswith(".json"):
            account_id = file.replace("today_", "").replace(".json", "")
            filepath = os.path.join(DIRECTORY_PATH, file)
            today_content = read_json_safely(filepath)
            if today_content:
                accounts_data[account_id] = {"account": account_id, "today": today_content, "stats": None}

    for file in files:
        if file.startswith("stats_") and file.endswith(".json"):
            account_id = file.replace("stats_", "").replace(".json", "")
            filepath = os.path.join(DIRECTORY_PATH, file)
            if account_id in accounts_data:
                stats_content = read_json_safely(filepath)
                if stats_content:
                    accounts_data[account_id]["stats"] = stats_content
                    
    return accounts_data


def parse_version(v_str):
    try:
        return tuple(map(int, v_str.strip().split('.')))
    except Exception:
        return (0, 0)


def generate_html():
    accounts = load_all_accounts()
    now = datetime.now()
    now_str = now.strftime("%Y.%m.%d %H:%M:%S")
    
    highest_version_str = "0.00"
    highest_version_tuple = (0, 0)
    
    for item in accounts.values():
        v_str = item["today"].get("version", "0.00")
        current_tuple = parse_version(v_str)
        if current_tuple > highest_version_tuple:
            highest_version_tuple = current_tuple
            highest_version_str = v_str
            
    html = f"""<!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="30">
        <title>PROP MONITOR Global Dashboard v{DASHBOARD_VERSION}</title>
        <style>
            body {{
                background-color: #0f172a;
                color: #f1f5f9;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0;
                padding: 20px;
                padding-bottom: 60px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 25px;
            }}
            h1 {{ color: #38bdf8; margin-bottom: 5px; font-size: 26px; }}
            .time {{ color: #64748b; font-size: 14px; margin-bottom: 12px; }}
            
            .badges-container {{
                display: flex;
                justify-content: center;
                gap: 10px;
            }}
            .global-badge {{
                display: inline-block;
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                background-color: #1e293b;
                padding: 4px 12px;
                border-radius: 20px;
            }}
            .badge-ea {{
                color: #38bdf8;
                border: 1px solid rgba(56, 189, 248, 0.2);
            }}
            .badge-dash {{
                color: #a855f7;
                border: 1px solid rgba(168, 85, 247, 0.2);
            }}
            
            .table-container {{
                background-color: #1e293b;
                border-radius: 8px;
                padding: 15px;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);
                overflow-x: auto;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                text-align: center;
            }}
            
            th {{
                background-color: #0f172a;
                color: #94a3b8;
                font-size: 11px;
                text-transform: uppercase;
                padding: 12px 10px;
                cursor: pointer;
                user-select: none;
                transition: background 0.2s, color 0.2s;
            }}
            th:hover {{
                background-color: #1e293b;
                color: #38bdf8;
            }}
            th.sort-asc::after {{ content: " ▲"; color: #38bdf8; font-size: 10px; }}
            th.sort-desc::after {{ content: " ▼"; color: #38bdf8; font-size: 10px; }}
            
            td {{
                padding: 12px 10px;
                border-bottom: 1px solid #334155;
                font-size: 14px;
            }}
            
            .main-row {{ cursor: pointer; transition: background 0.2s; }}
            .main-row:hover {{ background-color: #334155; }}
            
            .details-row {{ display: none; background-color: #0f172a; }}
            
            .details-box {{
                padding: 20px;
                text-align: left;
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 20px;
            }}
            
            .sub-card {{
                background: #1e293b;
                padding: 15px;
                border-radius: 6px;
                font-size: 13px;
                border-left: 4px solid #38bdf8;
            }}
            .sub-card h4 {{ margin: 0 0 12px 0; color: #94a3b8; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }}
            
            .history-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 8px 25px;
            }}
            .history-col {{
                display: flex;
                flex-direction: column;
                gap: 6px;
            }}
            .history-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px dashed #2d3748;
                padding-bottom: 4px;
                font-family: monospace;
                font-size: 13px;
            }}
            .history-label {{ color: #64748b; }}
            
            .broker-cell {{
                text-align: left;
                font-size: 13px;
                color: #cbd5e1;
            }}
            .broker-cell small {{ color: #64748b; display: block; font-size: 11px; }}
            
            .pos {{ color: #4ade80; font-weight: bold; }}
            .neg {{ color: #f87171; font-weight: bold; }}
            .neutral {{ color: #94a3b8; }}
            
            .time-ok {{ color: #4ade80; font-weight: bold; font-family: monospace; }}
            .time-warn {{ 
                color: #fb923c; 
                font-weight: bold; 
                font-family: monospace; 
                background-color: rgba(251, 146, 60, 0.12); 
                box-shadow: inset 0 0 0 1px rgba(251, 146, 60, 0.2);
            }}
            .time-alert {{ 
                color: #f87171; 
                font-weight: bold; 
                font-family: monospace; 
                background-color: rgba(248, 113, 113, 0.18); 
                box-shadow: inset 0 0 0 1px rgba(248, 113, 113, 0.3);
                animation: pulse 2s infinite; 
            }}
            
            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
                100% {{ opacity: 1; }}
            }}
            
            .version-tag {{
                font-size: 10px;
                padding: 2px 5px;
                border-radius: 4px;
                background: #334155;
                color: #94a3b8;
            }}
            .version-alert {{
                background: #7c2d12 !important;
                color: #fb923c !important;
                border: 1px solid rgba(251, 146, 60, 0.3);
                font-weight: bold;
            }}
            
            .badge-on {{ background: #15803d; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
            .badge-off {{ background: #991b1b; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
            
            .footer {{
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100%;
                background-color: #0f172a;
                border-top: 1px solid #1e293b;
                text-align: center;
                padding: 8px 0;
                font-size: 11px;
                color: #475569;
            }}
        </style>
        <script>
            function toggleRow(accId) {{
                var el = document.getElementById('details-' + accId);
                let openRows = JSON.parse(localStorage.getItem("openRows") || "[]");
                
                if(el.style.display === 'table-row') {{
                    el.style.display = 'none';
                    openRows = openRows.filter(id => id !== accId);
                }} else {{
                    el.style.display = 'table-row';
                    if(!openRows.includes(accId)) {{
                        openRows.push(accId);
                    }}
                }}
                localStorage.setItem("openRows", JSON.stringify(openRows));
            }}
        </script>
    </head>
    <body>
        <div class="header">
            <h1>GLOBAL VPS MONITOR</h1>
            <div class="time">Ostatnie odświeżenie danych: {now_str}</div>
            <div class="badges-container">
                <div class="global-badge badge-ea">Wykryty skrypt MT5: v{highest_version_str}</div>
                <div class="global-badge badge-dash">Dashboard System: v{DASHBOARD_VERSION}</div>
            </div>
        </div>

        <div class="table-container">
            <table id="accountTable">
                <thead>
                    <tr>
                        <th onclick="sortTable(0, 'str')">Konto</th>
                        <th onclick="sortTable(1, 'str')">Broker / Serwer</th>
                        <th onclick="sortTable(2, 'num')">Aktualizacja</th>
                        <th onclick="sortTable(3, 'num')">Balance</th>
                        <th onclick="sortTable(4, 'num')">Equity</th>
                        <th onclick="sortTable(5, 'num')">Niezamknięte PnL</th>
                        <th onclick="sortTable(6, 'num')">Wynik Dziś</th>
                        <th onclick="sortTable(7, 'num')">Tydzień (W0)</th>
                        <th onclick="sortTable(8, 'num')">Tydzień (W1)</th>
                        <th onclick="sortTable(9, 'num')">Miesiąc (M0)</th>
                        <th onclick="sortTable(10, 'num')">Pozycje</th>
                        <th onclick="sortTable(11, 'num')">Algo</th>
                        <th onclick="sortTable(12, 'str')">Status</th>
                    </tr>
                </thead>
                <tbody>
        """

    for acc_id, item in accounts.items():
        today = item["today"]
        stats = item["stats"]
        
        balance = today.get("balance", 0.0)
        equity = today.get("equity", 0.0)
        credit = today.get("account_credit", 0.0)
        pnl_open = round(equity - balance - credit, 2)
        
        today_net = today.get("today_net", 0.0)
        
        pnl_class = "pos" if pnl_open > 0 else ("neg" if pnl_open < 0 else "neutral")
        today_class = "pos" if today_net > 0 else ("neg" if today_net < 0 else "neutral")
        
        v_app = today.get("version", "0.00")
        is_outdated = parse_version(v_app) < highest_version_tuple
        v_class = "version-tag" + (" version-alert" if is_outdated else "")
            
        w0 = 0.0
        w1 = 0.0
        m0 = 0.0
        if stats and "weeks" in stats:
            w0 = stats["weeks"].get("W0", 0.0)
            w1 = stats["weeks"].get("W1", 0.0)
        if stats and "months" in stats:
            m0 = stats["months"].get("M0", 0.0)
            
        w0_class = "pos" if w0 > 0 else ("neg" if w0 < 0 else "neutral")
        w1_class = "pos" if w1 > 0 else ("neg" if w1 < 0 else "neutral")
        m0_class = "pos" if m0 > 0 else ("neg" if m0 < 0 else "neutral")
        
        open_pos = today.get("open_positions_count", 0)
        open_sym = today.get("open_symbols", "none")
        status_badge = f'<span class="badge-on">LIVE</span>' if open_pos > 0 else '<span class="badge-off">IDLE</span>'
        
        # BEZPIECZNA OBSŁUGA ALGO TRADINGU: Domyślnie True (ON), jeśli tagu nie ma w pliku JSON
        algo_trading_active = today.get("algo_trading", True)
        algo_val = 1 if algo_trading_active else 0
        algo_badge = f'<span class="badge-on">ON</span>' if algo_trading_active else f'<span class="badge-off">OFF</span>'
        
        broker_name = today.get("broker", "Nieznany Broker")
        server_name = today.get("server", "Nieznany Serwer")
        
        update_time_str = today.get("last_update_time", "")
        display_time = "--:--:--"
        diff_minutes = 9999
        time_css_class = "time-alert"
        
        if update_time_str:
            try:
                dt_update = datetime.strptime(update_time_str, "%Y.%m.%d %H:%M:%S")
                display_time = update_time_str[11:]
                diff_seconds = (now - dt_update).total_seconds()
                diff_minutes = int(diff_seconds / 60)
                
                if diff_minutes < 15:
                    time_css_class = "time-ok"
                elif 15 <= diff_minutes <= 60:
                    time_css_class = "time-warn"
                else:
                    time_css_class = "time-alert"
            except Exception:
                display_time = "--:--:--"
                diff_minutes = 9999
                time_css_class = "time-alert"

        html += f"""
        <tr class="main-row" onclick="toggleRow('{acc_id}')">
            <td data-val="{acc_id}">
                <strong>{acc_id}</strong> 
                <span class="{v_class}">v{v_app}</span>
            </td>
            <td class="broker-cell" data-val="{broker_name} {server_name}">
                {broker_name}
                <small>{server_name}</small>
            </td>
            <td data-val="{diff_minutes}" class="{time_css_class}">{display_time}</td>
            <td data-val="{balance}">{balance:,.2f}</td>
            <td data-val="{equity}">{equity:,.2f}</td>
            <td data-val="{pnl_open}" class="{pnl_class}">{pnl_open:+.2f}</td>
            <td data-val="{today_net}" class="{today_class}">{today_net:+.2f}</td>
            <td data-val="{w0}" class="{w0_class}">{w0:+.2f}</td>
            <td data-val="{w1}" class="{w1_class}">{w1:+.2f}</td>
            <td data-val="{m0}" class="{m0_class}">{m0:+.2f}</td>
            <td data-val="{open_pos}">{open_pos} <span style="font-size:11px; color:#64748b;">({open_sym})</span></td>
            <td data-val="{algo_val}">{algo_badge}</td>
            <td data-val="{open_pos}">{status_badge}</td>
        </tr>
        """
        
        # SEKCJA SZCZEGÓŁÓW KONTA (colspan zwiększony do 13 dla nowej kolumny)
        html += f"""
        <tr class="details-row" id="details-{acc_id}">
            <td colspan="13">
                <div class="details-box">
        """
        
        if stats:
            weeks_col1 = ""
            for i in range(1, 7):
                val = stats["weeks"].get(f"W{i}", 0.0)
                cls = "pos" if val > 0 else ("neg" if val < 0 else "neutral")
                weeks_col1 += f"""
                <div class="history-item">
                    <span class="history-label">Tydzień W{i}:</span>
                    <span class="{cls}">{val:+.2f}</span>
                </div>"""
                
            weeks_col2 = ""
            for i in range(7, 13):
                val = stats["weeks"].get(f"W{i}", 0.0)
                cls = "pos" if val > 0 else ("neg" if val < 0 else "neutral")
                weeks_col2 += f"""
                <div class="history-item">
                    <span class="history-label">Tydzień W{i}:</span>
                    <span class="{cls}">{val:+.2f}</span>
                </div>"""

            months_col1 = ""
            for i in range(1, 7):
                val = stats["months"].get(f"M{i}", 0.0)
                cls = "pos" if val > 0 else ("neg" if val < 0 else "neutral")
                months_col1 += f"""
                <div class="history-item">
                    <span class="history-label">Miesiąc M{i}:</span>
                    <span class="{cls}">{val:+.2f}</span>
                </div>"""
                
            months_col2 = ""
            for i in range(7, 13):
                val = stats["months"].get(f"M{i}", 0.0)
                cls = "pos" if val > 0 else ("neg" if val < 0 else "neutral")
                months_col2 += f"""
                <div class="history-item">
                    <span class="history-label">Miesiąc M{i}:</span>
                    <span class="{cls}">{val:+.2f}</span>
                </div>"""
                
            html += f"""
                    <div class="sub-card">
                        <h4>Historia Tygodniowa (W1 - W12)</h4>
                        <div class="history-grid">
                            <div class="history-col">{weeks_col1}</div>
                            <div class="history-col">{weeks_col2}</div>
                        </div>
                    </div>
                    
                    <div class="sub-card">
                        <h4>Historia Miesięczna (M1 - M12)</h4>
                        <div class="history-grid">
                            <div class="history-col">{months_col1}</div>
                            <div class="history-col">{months_col2}</div>
                        </div>
                    </div>
            """
        else:
            html += f"""
                    <div class="sub-card" style="border-left-color: #64748b; grid-column: span 2;">
                        <h4>Statystyki Historyczne</h4>
                        <div style="color:#64748b; padding:10px 0; font-size:13px;">
                            ⚠️ Oczekiwanie na dobowe wygenerowanie statystyk (Brak pliku stats_{acc_id}.json). Strumień live działa poprawnie.
                        </div>
                    </div>
            """

        credit_html = ""
        if credit > 0:
            credit_html = f"""
            <div style="display:flex; justify-content:space-between; border-bottom:1px dashed #334155; background-color: rgba(56, 189, 248, 0.08); padding: 4px 6px; border-radius: 4px; margin-bottom: 5px;">
                <span style="color:#38bdf8; font-weight: bold;">Zwrot za rejestrację (Credit):</span>
                <strong style="color:#38bdf8;">{credit:,.2f}</strong>
            </div>
            """

        y0_val = stats['years'].get('Y0', 0.0) if stats else 0.0
        y1_val = stats['years'].get('Y1', 0.0) if stats else 0.0

        html += f"""
                    <div class="sub-card" style="border-left-color: #a855f7;">
                        <h4>Statystyki Roczne i Finanse</h4>
                        <div style="display:flex; flex-direction:column; gap:10px; font-size:13px; margin-top:5px;">
                            {credit_html}
                            <div style="display:flex; justify-content:space-between; border-bottom:1px dashed #334155;">
                                <span style="color:#64748b;">Bieżący rok Y0:</span>
                                <strong class="{'pos' if y0_val>=0 else 'neg'}">{y0_val:+.2f}</strong>
                            </div>
                            <div style="display:flex; justify-content:space-between; border-bottom:1px dashed #334155;">
                                <span style="color:#64748b;">Ubiegły rok Y1:</span>
                                <strong class="{'pos' if y1_val>=0 else 'neg'}">{y1_val:+.2f}</strong>
                            </div>
                            <div style="margin-top:10px; font-size:11px; color:#64748b; line-height:1.4;">
                                * Dane finansowe live uwzględniają zamrożone środki typu Credit. Historia zysków ignoruje operacje wpłat/wypłat.
                            </div>
                        </div>
                    </div>
                </div>
            </td>
        </tr>
        """
            
    html += f"""
                </tbody>
            </table>
        </div>

        <div class="footer">
            PROP MONITOR Core – Dashboard System v{DASHBOARD_VERSION} © 2026
        </div>

        <script>
            function sortTable(colIndex, type, isAutomatic = false) {{
                const table = document.getElementById("accountTable");
                const tbody = table.querySelector("tbody");
                const allRows = Array.from(tbody.querySelectorAll("tr"));
                if (allRows.length === 0) return;

                const pairs = [];
                for (let i = 0; i < allRows.length; i += 2) {{
                    if (allRows[i] && allRows[i].classList.contains('main-row')) {{
                        pairs.push({{
                            main: allRows[i],
                            details: allRows[i+1]
                        }});
                    }}
                }}
                
                let savedCol = localStorage.getItem("sortCol");
                let savedAsc = localStorage.getItem("sortAsc");
                
                let isAsc = true;
                
                if (isAutomatic && savedCol !== null) {{
                    colIndex = parseInt(savedCol);
                    isAsc = (savedAsc === "true");
                    type = (colIndex === 0 || colIndex === 1 || colIndex === 12) ? 'str' : 'num';
                }} else {{
                    if (savedCol !== null && parseInt(savedCol) === colIndex) {{
                        isAsc = (savedAsc !== "true");
                    }} else {{
                        // Dla PnL (5) i Wyniku Dziś (6) domyślne kliknięcie sortuje od największych zysków
                        isAsc = (colIndex === 2) ? true : (colIndex === 5 || colIndex === 6 ? false : true);
                    }}
                    localStorage.setItem("sortCol", colIndex);
                    localStorage.setItem("sortAsc", isAsc);
                }}

                const headers = table.querySelectorAll("th");
                headers.forEach((th, idx) => {{
                    th.classList.remove("sort-asc", "sort-desc");
                    if (idx === colIndex) {{
                        th.classList.add(isAsc ? "sort-asc" : "sort-desc");
                    }}
                }});

                pairs.sort((pairA, pairB) => {{
                    let cellA = pairA.main.children[colIndex].getAttribute("data-val") || "0";
                    let cellB = pairB.main.children[colIndex].getAttribute("data-val") || "0";

                    // INTELIGENTNA LOGIKA DLA NIEZAMKNIĘTEGO PnL (Kolumna indeks 5)
                    if (colIndex === 5) {{
                        // Pobieramy liczbę pozycji z kolumny 10 (indeks 10)
                        let posA = parseInt(pairA.main.children[10].getAttribute("data-val") || "0");
                        let posB = parseInt(pairB.main.children[10].getAttribute("data-val") || "0");

                        // Wyświetlaj konta z otwartymi pozycjami zawsze na górze tabeli
                        if (posA > 0 && posB === 0) return -1;
                        if (posA === 0 && posB > 0) return 1;
                        
                        // Gdy oba konta odpoczywają (0 pozycji), ułóż je na dole po numerze konta
                        if (posA === 0 && posB === 0) {{
                            let idA = pairA.main.children[0].getAttribute("data-val") || "";
                            let idB = pairB.main.children[0].getAttribute("data-val") || "";
                            return idA.localeCompare(idB);
                        }}
                    }}

                    if (type === 'num') {{
                        let numA = parseFloat(cellA);
                        let numB = parseFloat(cellB);
                        if (isNaN(numA)) numA = 0;
                        if (isNaN(numB)) numB = 0;
                        return isAsc ? numA - numB : numB - numA;
                    }} else {{
                        return isAsc ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
                    }}
                }});

                tbody.innerHTML = "";
                pairs.forEach(pair => {{
                    tbody.appendChild(pair.main);
                    tbody.appendChild(pair.details);
                }});

                if (isAutomatic) {{
                    let openRows = JSON.parse(localStorage.getItem("openRows") || "[]");
                    openRows.forEach(accId => {{
                        let el = document.getElementById('details-' + accId);
                        if (el) {{
                            el.style.display = 'table-row';
                        }}
                    }});
                }}
            }}

            window.addEventListener('DOMContentLoaded', () => {{
                // Ustawiamy domyślne sortowanie od razu po wejściu na stronę na Niezamknięte PnL (od zysków)
                if (localStorage.getItem("sortCol") === null) {{
                    localStorage.setItem("sortCol", 5);
                    localStorage.setItem("sortAsc", false);
                }}
                sortTable(0, 'str', true);
            }});
        </script>
    </body>
    </html>
    """
    
    with open(OUTPUT_HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    print(f"==================================================")
    print(f" PROP MONITOR Global Dashboard v{DASHBOARD_VERSION} uruchomiony!")
    print(f" Ścieżka skanowania: {DIRECTORY_PATH}")
    print(f"==================================================")
    while True:
        try:
            generate_html()
        except Exception as e:
            print(f"Błąd pętli głównej: {e}")
        time.sleep(5)