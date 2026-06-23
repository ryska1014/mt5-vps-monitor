import os
import json
from datetime import datetime
import time

# --- KONFIGURACJA ---
# Ścieżka do katalogu Common dla MetaQuotes (dostosuj dla swojego systemu)
# Dla Windowsa Administratora domyślnie: r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files"
DIRECTORY_PATH = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files"

# Aktualna wersja generatora MQL5, którą powinieneś mieć na terminalach
LATEST_VERSION = "4.55"

# Plik wynikowy
OUTPUT_HTML_FILE = "dashboard.html"


def read_json_safely(filepath):
    """
    Bezpieczny odczyt pliku JSON z obsługą wyjątków.
    Jeśli plik jest akurat zapisywany przez MT5, funkcja spróbuje go odczytać ponownie.
    """
    for _ in range(3):  # Maksymalnie 3 próby w razie zablokowania pliku
        try:
            with open(filepath, 'r', encoding='ansi') as f:
                return json.load(f)
        except (json.JSONDecodeError, PermissionError):
            time.sleep(0.05)  # Odczekaj 50ms przed kolejną próbą
        except Exception as e:
            print(f"Błąd krytyczny odczytu pliku {filepath}: {e}")
            break
    return None


def load_all_accounts():
    accounts_data = {}
    
    if not os.path.exists(DIRECTORY_PATH):
        print(f"BŁĄD: Ścieżka {DIRECTORY_PATH} nie istnieje!")
        return {}
        
    files = os.listdir(DIRECTORY_PATH)
    
    # 1. Najpierw ładujemy dane bieżące (today_*.json)
    for file in files:
        if file.startswith("today_") and file.endswith(".json"):
            account_id = file.replace("today_", "").replace(".json", "")
            filepath = os.path.join(DIRECTORY_PATH, file)
            
            today_content = read_json_safely(filepath)
            if today_content:
                accounts_data[account_id] = {
                    "account": account_id,
                    "today": today_content,
                    "stats": None  # Miejsce na statystyki długoterminowe
                }

    # 2. Następnie parsujemy i dołączamy statystyki okresowe (stats_*.json)
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
    
    # Grupowanie kont według serwera/brokera dla lepszej czytelności przy 16 kontach
    grouped_accounts = {}
    for acc_id, data in accounts.items():
        server = data["today"].get("server", "Nieznany Serwer")
        broker = data["today"].get("broker", "Nieznany Broker")
        group_key = f"{broker} ({server})"
        
        if group_key not in grouped_accounts:
            grouped_accounts[group_key] = []
        grouped_accounts[group_key].append(data)

    # Początek dokumentu HTML (Dark Mode, nowoczesny layout)
    html = f"""<!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="30"> <title>PROP MONITOR Dashboard</title>
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
                margin-bottom: 30px;
            }}
            h1 {{ color: #38bdf8; margin-bottom: 5px; font-size: 26px; }}
            .time {{ color: #64748b; font-size: 14px; }}
            
            .server-group {{
                margin-bottom: 35px;
                background-color: #1e293b;
                border-radius: 8px;
                padding: 15px;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);
            }}
            .server-title {{
                font-size: 18px;
                color: #38bdf8;
                font-weight: bold;
                margin-bottom: 15px;
                border-bottom: 1px solid #334155;
                padding-bottom: 5px;
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
                padding: 10px;
            }}
            td {{
                padding: 12px 10px;
                border-bottom: 1px solid #334155;
                font-size: 14px;
            }}
            
            .main-row {{ cursor: pointer; transition: background 0.2s; }}
            .main-row:hover {{ background-color: #334155; }}
            
            .details-row {{ display: none; background-color: #0f172a; }}
            .details-box {{
                padding: 15px;
                text-align: left;
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 15px;
            }}
            .sub-card {{
                background: #1e293b;
                padding: 10px;
                border-radius: 6px;
                font-size: 12px;
                border-left: 3px solid #38bdf8;
            }}
            .sub-card h4 {{ margin: 0 0 5px 0; color: #64748b; }}
            
            /* Style statusów i wersji */
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
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0% {{ opacity: 0.6; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.6; }}
            }}
            
            .badge-on {{ background: #15803d; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; }}
            .badge-off {{ background: #991b1b; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; }}
        </style>
        <script>
            function toggleRow(acc) {{
                var el = document.getElementById('details-' + acc);
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
            <h1>MULTI-TERMINAL VPS MONITOR</h1>
            <div class="time">Ostatnie odświeżenie dashboardu: {now_str}</div>
        </div>
    """

    if not grouped_accounts:
        html += "<div style='text-align:center; color:#64748b; margin-top:50px;'>Brak danych JSON w katalogu monitora. Sprawdź czy MT5 poprawnie generują pliki.</div>"

    # Generowanie tabel dla każdej grupy serwerów osobno
    for group_name, accounts_list in grouped_accounts.items():
        html += f"""
        <div class="server-group">
            <div class="server-title">{group_name}</div>
            <table>
                <thead>
                    <tr>
                        <th>Konto</th>
                        <th>Zaktualizowano</th>
                        <th>Balance</th>
                        <th>Equity</th>
                        <th>Niezamknięte PnL</th>
                        <th>Wynik Dziś</th>
                        <th>Tydzień (W0)</th>
                        <th>Miesiąc (M0)</th>
                        <th>Pozycje (Symbole)</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for item in accounts_list:
            acc = item["account"]
            today = item["today"]
            stats = item["stats"]
            
            # Wyliczanie podstawowych parametrów live
            balance = today.get("balance", 0.0)
            equity = today.get("equity", 0.0)
            pnl_open = round(equity - balance, 2)
            today_net = today.get("today_net", 0.0)
            
            pnl_class = "pos" if pnl_open > 0 else ("neg" if pnl_open < 0 else "neutral")
            today_class = "pos" if today_net > 0 else ("neg" if today_net < 0 else "neutral")
            
            # Weryfikacja wersji MQL5
            v_app = today.get("version", "stara")
            v_class = "version-tag"
            v_title = ""
            if v_app != LATEST_VERSION:
                v_class += " version-alert"
                v_title = f"Zaktualizuj generator! Wykryto wersję {v_app}, wymagana {LATEST_VERSION}"
                
            # Wyciąganie statystyk okresowych (jeśli plik stats_* istnieje)
            w0 = stats["weeks"]["W0"] if stats and "weeks" in stats else 0.0
            m0 = stats["months"]["M0"] if stats and "months" in stats else 0.0
            w0_class = "pos" if w0 > 0 else ("neg" if w0 < 0 else "neutral")
            m0_class = "pos" if m0 > 0 else ("neg" if m0 < 0 else "neutral")
            
            open_pos = today.get("open_positions_count", 0)
            open_sym = today.get("open_symbols", "none")
            status_badge = f'<span class="badge-on">LIVE</span>' if open_pos > 0 else '<span class="badge-off">IDLE</span>'
            
            # Główny wiersz tabeli
            html += f"""
            <tr class="main-row" onclick="toggleRow('{acc}')">
                <td>
                    <strong>{acc}</strong> 
                    <span class="{v_class}" title="{v_title}">v{v_app}</span>
                </td>
                <td style="font-size:11px; color:#64748b;">{today.get("last_update_time", "")[11:]}</td>
                <td>{balance:,.2f}</td>
                <td>{equity:,.2f}</td>
                <td class="{pnl_class}">{pnl_open:+.2f}</td>
                <td class="{today_class}">{today_net:+.2f}</td>
                <td class="{w0_class}">{w0:+.2f}</td>
                <td class="{m0_class}">{m0:+.2f}</td>
                <td>{open_pos} <span style="font-size:11px; color:#64748b;">({open_sym})</span></td>
                <td>{status_badge}</td>
            </tr>
            """
            
            # Ukryty wiersz szczegółów (Accordion) rozwijany po kliknięciu
            if stats:
                weeks_str = ", ".join([f"W{i}: {stats['weeks'].get(f'W{i}',0):+.2f}" for i in range(1, 5)])
                months_str = ", ".join([f"M{i}: {stats['months'].get(f'M{i}',0):+.2f}" for i in range(1, 4)])
                html += f"""
                <tr class="details-row" id="details-{acc}">
                    <td colspan="10">
                        <div class="details-box">
                            <div class="sub-card">
                                <h4>Historia Tygodniowa (W1 - W4)</h4>
                                <span style="color:#cbd5e1;">{weeks_str}</span>
                            </div>
                            <div class="sub-card">
                                <h4>Historia Miesięczna (M1 - M3)</h4>
                                <span style="color:#cbd5e1;">{months_str}</span>
                            </div>
                            <div class="sub-card" style="border-left-color: #a855f7;">
                                <h4>Bieżący rok (Y0) oraz ubiegły (Y1)</h4>
                                <span>Y0: <strong class="{'pos' if stats['years'].get('Y0',0)>=0 else 'neg'}">{stats['years'].get('Y0',0):+.2f}</strong> | 
                                      Y1: <strong class="{'pos' if stats['years'].get('Y1',0)>=0 else 'neg'}">{stats['years'].get('Y1',0):+.2f}</strong></span>
                            </div>
                        </div>
                    </td>
                </tr>
                """
            else:
                html += f"""
                <tr class="details-row" id="details-{acc}">
                    <td colspan="10" style="color:#64748b; padding:10px; font-size:12px;">Oczekiwanie na dobowe wygenerowanie statystyk (Brak pliku stats_{acc}.json).</td>
                </tr>
                """
                
        html += """
                </tbody>
            </table>
        </div>
        """

    html += """
    </body>
    </html>
    """
    
    # Zapis gotowego szablonu do pliku HTML
    with open(OUTPUT_HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    print(f"Uruchomiono pętlę generatora. Pliki będą sprawdzane w: {DIRECTORY_PATH}")
    while True:
        try:
            generate_html()
        except Exception as e:
            print(f"Błąd w pętli głównej: {e}")
        
        # Generuj stronę ponownie co 5 sekund (częstotliwość odświeżania na dysku)
        time.sleep(5)