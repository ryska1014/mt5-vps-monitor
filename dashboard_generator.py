import os
import json
from datetime import datetime
import time

# --- KONFIGURACJA ---
DIRECTORY_PATH = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files"
LATEST_VERSION = "4.55"
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


def generate_html():
    accounts = load_all_accounts()
    now_str = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    
    html = f"""<!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="30">
        <title>PROP MONITOR Global Dashboard</title>
        <style>
            body {{
                background-color: #0f172a;
                color: #f1f5f9;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0;
                padding: 20px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 25px;
            }}
            h1 {{ color: #38bdf8; margin-bottom: 5px; font-size: 26px; }}
            .time {{ color: #64748b; font-size: 14px; }}
            
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
            
            /* TRZYKOLUMNOWY UKŁAD GŁÓWNY SEKCJI SZCZEGÓŁÓW */
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
            
            /* WIELOWIERSZOWA MINI-SIATKA DLA KOLUMN MIESIĘCY I TYGODNI */
            .history-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr); /* Rozbicie danych na 2 kolumny wewnątrz karty */
                gap: 8px 15px;
            }}
            .history-item {{
                display: flex;
                justify-content: space-between;
                border-bottom: 1px dashed #334155;
                padding-bottom: 2px;
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
            
            .version-tag {{
                font-size: 10px;
                padding: 2px 5px;
                border-radius: 4px;
                background: #334155;
                color: #94a3b8;
            }}
            .version-alert {{
                background: #7c2d12 !important;
                color: #fdba74 !important;
                font-weight: bold;
            }}
            
            .badge-on {{ background: #15803d; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; }}
            .badge-off {{ background: #991b1b; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; }}
        </style>
        <script>
            function toggleRow(accId) {{
                var el = document.getElementById('details-' + accId);
                if(el.style.display === 'table-row') {{
                    el.style.display = 'none';
                }} else {{
                    el.style.display = 'table-row';
                }}
            }}
        </script>
    </head>
    <body>
        <div class="header">
            <h1>GLOBAL VPS MONITOR</h1>
            <div class="time">Ostatnie odświeżenie danych: {now_str}</div>
        </div>

        <div class="table-container">
            <table id="accountTable">
                <thead>
                    <tr>
                        <th onclick="sortTable(0, 'str')">Konto</th>
                        <th onclick="sortTable(1, 'str')">Broker / Serwer</th>
                        <th onclick="sortTable(2, 'time')">Aktualizacja</th>
                        <th onclick="sortTable(3, 'num')">Balance</th>
                        <th onclick="sortTable(4, 'num')">Equity</th>
                        <th id="pnlHeader" onclick="sortTable(5, 'num')">Niezamknięte PnL</th>
                        <th onclick="sortTable(6, 'num')">Wynik Dziś</th>
                        <th onclick="sortTable(7, 'num')">Tydzień (W0)</th>
                        <th onclick="sortTable(8, 'num')">Miesiąc (M0)</th>
                        <th onclick="sortTable(9, 'num')">Pozycje</th>
                        <th onclick="sortTable(10, 'str')">Status</th>
                    </tr>
                </thead>
                <tbody>
        """

    for acc_id, item in accounts.items():
        today = item["today"]
        stats = item["stats"]
        
        balance = today.get("balance", 0.0)
        equity = today.get("equity", 0.0)
        pnl_open = round(equity - balance, 2)
        today_net = today.get("today_net", 0.0)
        
        pnl_class = "pos" if pnl_open > 0 else ("neg" if pnl_open < 0 else "neutral")
        today_class = "pos" if today_net > 0 else ("neg" if today_net < 0 else "neutral")
        
        v_app = today.get("version", "stara")
        v_class = "version-tag" + (" version-alert" if v_app != LATEST_VERSION else "")
            
        w0 = 0.0
        m0 = 0.0
        if stats and "weeks" in stats and "W0" in stats["weeks"]:
            w0 = stats["weeks"]["W0"]
        if stats and "months" in stats and "M0" in stats["months"]:
            m0 = stats["months"]["M0"]
            
        w0_class = "pos" if w0 > 0 else ("neg" if w0 < 0 else "neutral")
        m0_class = "pos" if m0 > 0 else ("neg" if m0 < 0 else "neutral")
        
        open_pos = today.get("open_positions_count", 0)
        open_sym = today.get("open_symbols", "none")
        status_badge = f'<span class="badge-on">LIVE</span>' if open_pos > 0 else '<span class="badge-off">IDLE</span>'
        
        broker_name = today.get("broker", "Nieznany Broker")
        server_name = today.get("server", "Nieznany Serwer")
        update_time = today.get("last_update_time", "")
        if len(update_time) >= 19:
            update_time = update_time[11:]
        else:
            update_time = "--:--:--"

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
            <td data-val="{update_time}" style="font-size:12px; color:#64748b;">{update_time}</td>
            <td data-val="{balance}">{balance:,.2f}</td>
            <td data-val="{equity}">{equity:,.2f}</td>
            <td data-val="{pnl_open}" class="{pnl_class}">{pnl_open:+.2f}</td>
            <td data-val="{today_net}" class="{today_class}">{today_net:+.2f}</td>
            <td data-val="{w0}" class="{w0_class}">{w0:+.2f}</td>
            <td data-val="{m0}" class="{m0_class}">{m0:+.2f}</td>
            <td data-val="{open_pos}">{open_pos} <span style="font-size:11px; color:#64748b;">({open_sym})</span></td>
            <td data-val="{open_pos}">{status_badge}</td>
        </tr>
        """
        
        if stats:
            # DYNAMICZNA GENERACJA WIELOWIERSZOWEGO WIDOKU TYGODNI (W1 - W12)
            weeks_html = ""
            for i in range(1, 13):
                val = stats["weeks"].get(f"W{i}", 0.0)
                cls = "pos" if val > 0 else ("neg" if val < 0 else "neutral")
                weeks_html += f"""
                <div class="history-item">
                    <span class="history-label">Tydzień W{i}:</span>
                    <span class="{cls}">{val:+.2f}</span>
                </div>"""

            # DYNAMICZNA GENERACJA WIELOWIERSZOWEGO WIDOKU MIESIĘCY (M1 - M12)
            months_html = ""
            for i in range(1, 13):
                val = stats["months"].get(f"M{i}", 0.0)
                cls = "pos" if val > 0 else ("neg" if val < 0 else "neutral")
                months_html += f"""
                <div class="history-item">
                    <span class="history-label">Miesiąc M{i}:</span>
                    <span class="{cls}">{val:+.2f}</span>
                </div>"""
                
            html += f"""
            <tr class="details-row" id="details-{acc_id}">
                <td colspan="11">
                    <div class="details-box">
                        <div class="sub-card">
                            <h4>Historia Tygodniowa (W1 - W12)</h4>
                            <div class="history-grid">
                                {weeks_html}
                            </div>
                        </div>
                        
                        <div class="sub-card">
                            <h4>Historia Miesięczna (M1 - M12)</h4>
                            <div class="history-grid">
                                {months_html}
                            </div>
                        </div>
                        
                        <div class="sub-card" style="border-left-color: #a855f7;">
                            <h4>Statystyki Roczne i Zbiorcze</h4>
                            <div style="display:flex; flex-direction:column; gap:10px; font-size:13px; margin-top:5px;">
                                <div style="display:flex; justify-content:space-between; border-bottom:1px dashed #334155;">
                                    <span style="color:#64748b;">Bieżący rok Y0:</span>
                                    <strong class="{'pos' if stats['years'].get('Y0',0)>=0 else 'neg'}">{stats['years'].get('Y0',0):+.2f}</strong>
                                </div>
                                <div style="display:flex; justify-content:space-between; border-bottom:1px dashed #334155;">
                                    <span style="color:#64748b;">Ubiegły rok Y1:</span>
                                    <strong class="{'pos' if stats['years'].get('Y1',0)>=0 else 'neg'}">{stats['years'].get('Y1',0):+.2f}</strong>
                                </div>
                                <div style="margin-top:10px; font-size:11px; color:#64748b; line-height:1.4;">
                                    * Dane historyczne odświeżane są automatycznie raz na dobę po zmianie daty serwera VPS.
                                </div>
                            </div>
                        </div>
                    </div>
                </td>
            </tr>
            """
        else:
            html += f"""
            <tr class="details-row" id="details-{acc_id}">
                <td colspan="11" style="color:#64748b; padding:20px; font-size:13px; background-color: #0f172a; text-align:left;">
                    ⚠️ Oczekiwanie na dobowe wygenerowanie statystyk (Brak pliku stats_{acc_id}.json). Strumień live działa poprawnie.
                </td>
            </tr>
            """
            
    html += """
                </tbody>
            </table>
        </div>

        <script>
            let currentSortCol = -1;
            let isAsc = true;

            function sortTable(colIndex, type) {
                const table = document.getElementById("accountTable");
                const tbody = table.querySelector("tbody");
                const allRows = Array.from(tbody.querySelectorAll("tr"));
                if (allRows.length === 0) return;

                const pairs = [];
                for (let i = 0; i < allRows.length; i += 2) {
                    if (allRows[i] && allRows[i].classList.contains('main-row')) {
                        pairs.push({
                            main: allRows[i],
                            details: allRows[i+1]
                        });
                    }
                }
                
                if (currentSortCol === colIndex) {
                    isAsc = !isAsc;
                } else {
                    isAsc = true;
                    currentSortCol = colIndex;
                }

                const headers = table.querySelectorAll("th");
                headers.forEach((th, idx) => {
                    th.classList.remove("sort-asc", "sort-desc");
                    if (idx === colIndex) {
                        th.classList.add(isAsc ? "sort-asc" : "sort-desc");
                    }
                });

                pairs.sort((pairA, pairB) => {
                    let cellA = pairA.main.children[colIndex].getAttribute("data-val") || "0";
                    let cellB = pairB.main.children[colIndex].getAttribute("data-val") || "0";

                    if (type === 'num') {
                        let numA = parseFloat(cellA);
                        let numB = parseFloat(cellB);
                        if (isNaN(numA)) numA = 0;
                        if (isNaN(numB)) numB = 0;
                        return isAsc ? numA - numB : numB - numA;
                    } else {
                        return isAsc ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
                    }
                });

                tbody.innerHTML = "";
                pairs.forEach(pair => {
                    tbody.appendChild(pair.main);
                    tbody.appendChild(pair.details);
                });
            }

            window.addEventListener('DOMContentLoaded', () => {
                sortTable(5, 'num');
                sortTable(5, 'num');
            });
        </script>
    </body>
    </html>
    """
    
    with open(OUTPUT_HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    print(f"Uruchomiono globalny monitor [W1-W12 / M1-M12 GRID]. Szukam w: {DIRECTORY_PATH}")
    while True:
        try:
            generate_html()
        except Exception as e:
            print(f"Błąd pętli głównej: {e}")
        time.sleep(5)