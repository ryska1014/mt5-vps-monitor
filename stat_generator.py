import os
import json
from datetime import datetime
import time

# --- KONFIGURACJA i WERSJONOWANIE ---
DASHBOARD_VERSION = "1.4.1"  # Poprawka kodowania (UTF-16 / BOM) dla plików MT5
DIRECTORY_PATH = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files"
OUTPUT_HTML_FILE = "stats.html"  # Zmieniono nazwę pliku wynikowego


def read_json_safely(filepath):
    # Próbujemy różnych kodowań, ponieważ MT5 często zapisuje w UTF-16
    for encoding_type in ['utf-16', 'utf-8-sig', 'ansi']:
        try:
            with open(filepath, 'r', encoding=encoding_type) as f:
                return json.load(f)
        except (json.JSONDecodeError, PermissionError):
            # Jeśli to problem z blokowaniem pliku, poczekaj chwilę
            time.sleep(0.05)
            continue
        except UnicodeDecodeError:
            # Jeśli to złe kodowanie, pętla przejdzie do następnego typu
            continue
        except Exception as e:
            print(f"Błąd krytyczny odczytu pliku {filepath}: {e}")
            break
            
    print(f"❌ Nie udało się odczytać pliku {os.path.basename(filepath)} przy użyciu UTF-16/UTF-8/ANSI.")
    return None


def load_all_accounts():
    accounts_data = {}
    if not os.path.exists(DIRECTORY_PATH):
        return {}
        
    files = os.listdir(DIRECTORY_PATH)
    
    for file in files:
        if file.startswith("hist_") and file.endswith(".json") and not file.endswith("_LOG.txt"):
            account_id = file.replace("hist_", "").replace(".json", "")
            filepath = os.path.join(DIRECTORY_PATH, file)
            content = read_json_safely(filepath)
            if content:
                accounts_data[account_id] = content
                        
    return accounts_data


def build_table_rows(accounts_list, now):
    """Generuje wiersze tabeli dla listy kont opartych na nowym formacie JSON"""
    html_rows = ""
    
    totals = {
        "balance": 0.0,
        "equity": 0.0,
        "pnl_open": 0.0,
        "period_net": 0.0,
        "open_pos": 0
    }
    
    for acc_id, data in accounts_list:
        account_number = data.get("account_number", acc_id)
        balance = data.get("current_balance", 0.0)
        equity = data.get("current_equity", balance) 
        pnl_open = round(equity - balance, 2)
        period_net_profit = data.get("period_net_profit", 0.0)
        
        pnl_class = "pos" if pnl_open > 0 else ("neg" if pnl_open < 0 else "neutral")
        today_class = "pos" if period_net_profit > 0 else ("neg" if period_net_profit < 0 else "neutral")
        
        status_badge = '<span class="badge-on">LIVE</span>'
        algo_badge = '<span class="badge-on">ON</span>'
        
        totals["balance"] += balance
        totals["equity"] += equity
        totals["pnl_open"] += pnl_open
        totals["period_net"] += period_net_profit
        
        update_time_str = data.get("last_update", "")
        display_time = "--:--:--"
        diff_minutes = 9999
        time_css_class = "time-alert"
        
        if update_time_str:
            try:
                dt_update = datetime.strptime(update_time_str, "%Y.%m.%d %H:%M")
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

        html_rows += f"""
        <tr class="main-row" onclick="toggleRow('{account_number}')">
            <td data-val="{account_number}">
                <strong>{account_number}</strong> 
                <span class="version-tag">v1.44</span>
            </td>
            <td class="broker-cell" data-val="MT5 Account">
                MetaTrader 5 Account
                <small>Prop Firm Server</small>
            </td>
            <td data-val="{diff_minutes}" class="{time_css_class}">{display_time}</td>
            <td data-val="{balance}">{balance:,.2f}</td>
            <td data-val="{equity}">{equity:,.2f}</td>
            <td data-val="{pnl_open}" class="{pnl_class}">{pnl_open:+.2f}</td>
            <td data-val="{period_net_profit}" class="{today_class}">{period_net_profit:+.2f}</td>
            <td data-val="0">--</td>
            <td data-val="0">--</td>
            <td data-val="0">--</td>
            <td data-val="0">--</td>
            <td data-val="1">{algo_badge}</td>
            <td data-val="LIVE">{status_badge}</td>
        </tr>
        <tr class="details-row" id="details-{account_number}">
            <td colspan="13">
                <div class="details-box">
        """
        
        stats_symbols = data.get("stats_per_month_symbol", [])
        stats_magics = data.get("stats_per_month_magic", [])
        
        symbols_html = ""
        for stat in stats_symbols:
            val = stat.get("profit", 0.0)
            cls = "pos" if val > 0 else ("neg" if val < 0 else "neutral")
            symbols_html += f"""
            <div class="history-item">
                <span class="history-label">{stat.get('month', '')} | {stat.get('symbol', '')}:</span>
                <span class="{cls}">{val:+.2f} ({stat.get('trades', 0)} tr)</span>
            </div>"""
            
        magics_html = ""
        for stat in stats_magics:
            val = stat.get("profit", 0.0)
            cls = "pos" if val > 0 else ("neg" if val < 0 else "neutral")
            magics_html += f"""
            <div class="history-item">
                <span class="history-label">{stat.get('month', '')} | Magic: {stat.get('magic', 0)} ({stat.get('symbol', '')}):</span>
                <span class="{cls}">{val:+.2f}</span>
            </div>"""

        html_rows += f"""
                    <div class="sub-card">
                        <h4>Agregacja Miesięczna na Instrumentach</h4>
                        <div class="history-col">{symbols_html if symbols_html else 'Brak danych'}</div>
                    </div>
                    <div class="sub-card">
                        <h4>Wydajność Systemów (Magic Numbers)</h4>
                        <div class="history-col">{magics_html if magics_html else 'Brak danych'}</div>
                    </div>
                    <div class="sub-card" style="border-left-color: #a855f7;">
                        <h4>Metadane Filtru 2026</h4>
                        <div style="display:flex; flex-direction:column; gap:10px; font-size:13px; margin-top:5px;">
                            <div style="display:flex; justify-content:space-between; border-bottom:1px dashed #334155;">
                                <span style="color:#64748b;">Punkt Startu:</span>
                                <strong>{data.get('filter_start_date','')}</strong>
                            </div>
                            <div style="display:flex; justify-content:space-between; border-bottom:1px dashed #334155;">
                                <span style="color:#64748b;">Zysk netto okresu:</span>
                                <strong class="{today_class}">{period_net_profit:+.2f}</strong>
                            </div>
                        </div>
                    </div>
                </div>
            </td>
        </tr>
        """
    return html_rows, totals


def build_summary_row(totals, is_archive=False):
    pnl_cls = "pos" if totals["pnl_open"] > 0 else ("neg" if totals["pnl_open"] < 0 else "neutral")
    today_cls = "pos" if totals["period_net"] > 0 else ("neg" if totals["period_net"] < 0 else "neutral")
    
    status_label = "ARCHIWUM" if is_archive else "GLOBAL"
    
    return f"""
    <tr class="summary-row">
        <td><strong>SUMA:</strong></td>
        <td colspan="2" style="text-align: left; font-size: 11px; color: #64748b; letter-spacing: 0.5px;">🧬 {status_label} SUMMARY</td>
        <td>{totals["balance"]:,.2f}</td>
        <td>{totals["equity"]:,.2f}</td>
        <td class="{pnl_cls}">{totals["pnl_open"]:+.2f}</td>
        <td class="{today_cls}">{totals["period_net"]:+.2f}</td>
        <td>--</td>
        <td>--</td>
        <td>--</td>
        <td>{totals["open_pos"]}</td>
        <td>--</td>
        <td><span class="badge-on" style="padding: 1px 5px; font-size:10px;">SUMA</span></td>
    </tr>
    """


def generate_html():
    accounts = load_all_accounts()
    now = datetime.now()
    now_str = now.strftime("%Y.%m.%d %H:%M:%S")
    
    active_accounts = []
    for acc_id, item in accounts.items():
        active_accounts.append((acc_id, item))
            
    active_rows_html, active_totals = build_table_rows(active_accounts, now)
            
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
                padding-bottom: 80px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 25px;
            }}
            h1 {{ color: #38bdf8; margin-bottom: 5px; font-size: 26px; }}
            .time {{ color: #64748b; font-size: 14px; margin-bottom: 12px; }}
            
            .section-title {{
                color: #38bdf8;
                font-size: 16px;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin: 25px 0 10px 5px;
                font-weight: bold;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
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
            .badge-ea {{ color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.2); }}
            .badge-dash {{ color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.2); }}
            
            .table-container {{
                background-color: #1e293b;
                border-radius: 8px;
                padding: 15px;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);
                overflow-x: auto;
                margin-bottom: 20px;
            }}
            
            table {{ width: 100%; border-collapse: collapse; text-align: center; }}
            
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
            th:hover {{ background-color: #1e293b; color: #38bdf8; }}
            th.sort-asc::after {{ content: " ▲"; color: #38bdf8; font-size: 10px; }}
            th.sort-desc::after {{ content: " ▼"; color: #38bdf8; font-size: 10px; }}
            
            td {{ padding: 12px 10px; border-bottom: 1px solid #334155; font-size: 14px; }}
            
            .main-row {{ cursor: pointer; transition: background 0.2s; }}
            .main-row:hover {{ background-color: #334155; }}
            
            .summary-row {{ background-color: #0f172a; font-weight: bold; border-top: 2px solid #334155; }}
            .summary-row td {{ padding: 14px 10px; border-bottom: none; border-top: 1px solid #334155; font-size: 14px; color: #e2e8f0; }}
            
            .details-row {{ display: none; background-color: #0f172a; }}
            .details-box {{ padding: 20px; text-align: left; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }}
            
            .sub-card {{ background: #1e293b; padding: 15px; border-radius: 6px; font-size: 13px; border-left: 4px solid #38bdf8; }}
            .sub-card h4 {{ margin: 0 0 12px 0; color: #94a3b8; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }}
            
            .history-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px 25px; }}
            .history-col {{ display: flex; flex-direction: column; gap: 6px; }}
            .history-item {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed #2d3748; padding-bottom: 4px; font-family: monospace; font-size: 13px; }}
            .history-label {{ color: #64748b; }}
            
            .broker-cell {{ text-align: left; font-size: 13px; color: #cbd5e1; }}
            .broker-cell small {{ color: #64748b; display: block; font-size: 11px; }}
            
            .pos {{ color: #4ade80; font-weight: bold; }}
            .neg {{ color: #f87171; font-weight: bold; }}
            .neutral {{ color: #94a3b8; }}
            
            .time-ok {{ color: #4ade80; font-weight: bold; font-family: monospace; }}
            .time-warn {{ color: #fb923c; font-weight: bold; font-family: monospace; background-color: rgba(251, 146, 60, 0.12); }}
            .time-alert {{ color: #f87171; font-weight: bold; font-family: monospace; background-color: rgba(248, 113, 113, 0.18); animation: pulse 2s infinite; }}
            
            @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} 100% {{ opacity: 1; }} }}
            
            .version-tag {{ font-size: 10px; padding: 2px 5px; border-radius: 4px; background: #334155; color: #94a3b8; }}
            
            .badge-on {{ background: #15803d; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
            .badge-off {{ background: #991b1b; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
            
            .footer {{ position: fixed; bottom: 0; left: 0; width: 100%; background-color: #0f172a; border-top: 1px solid #1e293b; text-align: center; padding: 8px 0; font-size: 11px; color: #475569; }}
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
                <div class="global-badge badge-ea">Format Audytu: DEALS UTF-16</div>
                <div class="global-badge badge-dash">Dashboard System: v{DASHBOARD_VERSION}</div>
            </div>
        </div>

        <div class="section-title">📊 Aktywne wyzwania i statystyki kont zysku rynkowego</div>
        <div class="table-container">
            <table id="accountTable">
                <thead>
                    <tr>
                        <th>Konto</th>
                        <th>Broker / Typ</th>
                        <th>Aktualizacja</th>
                        <th>Balance</th>
                        <th>Equity</th>
                        <th>Otwarte PnL</th>
                        <th>Wynik Okresu (2026)</th>
                        <th>Tydzień (W0)</th>
                        <th>Tydzień (W1)</th>
                        <th>Miesiąc (M0)</th>
                        <th>Pozycje</th>
                        <th>Algo</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {active_rows_html}
                </tbody>
                <tfoot>
                    {build_summary_row(active_totals, is_archive=False)}
                </tfoot>
            </table>
        </div>
        
        <div class="footer">
            PROP MONITOR Core – Dashboard System v{DASHBOARD_VERSION} © 2026
        </div>
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