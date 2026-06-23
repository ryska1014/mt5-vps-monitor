# MT5 Multi-Terminal VPS Monitor (Python Dashboard)

Nowoczesny, lekki i bezpieczny system monitoringu wielu terminali MetaTrader 5 (MT5) uruchomionych na jednym serwerze VPS. Skrypt w Pythonie agreguje rozproszone dane z pamięci wspólnej terminali (`Common/Files`) i generuje scentralizowany dashboard HTML z funkcją dynamicznego sortowania i alertów.

## 🚀 Główne Funkcje

* **Globalna Lista Kont:** Agregacja danych z 16+ terminali w jedną, spójną tabelę zamiast rozbitych sekcji.
* **Dynamiczne Sortowanie (JS):** Możliwość sortowania po każdej kolumnie (rosnąco/malejąco) bezpośrednio w przeglądarce za pomocą jednego kliknięcia w nagłówek.
* **Priorytet Drawdownu (Domyślne Sortowanie):** Po załadowaniu lub odświeżeniu strony system automatycznie sortuje konta według kolumny `Niezamknięte PnL` (od największego minusu), aby natychmiast wskazać pozycje wymagające uwagi.
* **System Alerty Wersji:** Wizualne oznaczanie kont (pulsujący pomarańczowy tag), które korzystają z nieaktualnej wersji generatora MQL5.
* **Optymalizacja Zasobów VPS:** Skrypt działa w jednej instancji, nie obciążając procesora VPS ciągłym czytaniem historii wewnątrz MT5. Podział na stream live (`today_*.json`) oraz statystyki dobowe (`stats_*.json`).

## 🛠️ Parametry Konfiguracyjne (w skrypcie Python)

Wewnątrz pliku `dashboard_generator.py` możesz dostosować działanie aplikacji za pomocą następujących stałych:

| Parametr | Domyślna wartość | Opis |
| :--- | :--- | :--- |
| `DIRECTORY_PATH` | `r"C:\Users\Administrator\..."` | Ścieżka do katalogu `Common/Files` dla wszystkich MetaQuotes Terminali na danym VPS. |
| `LATEST_VERSION` | `"4.55"` | Aktualna, stabilna wersja kodu MQL5. Starsze wersje wywołają alert wizualny. |
| `OUTPUT_HTML_FILE` | `"dashboard.html"` | Nazwa wyjściowego pliku panelu, który należy otworzyć w przeglądarce. |
| `time.sleep(5)` | `5` | Częstotliwość (w sekundach) z jaką Python odświeża plik HTML na dysku. |

## 📦 Struktura Plików JSON (Dane wejściowe)

Skrypt do poprawnego działania wymaga dwóch typów plików generowanych przez autorski program EA w MQL5:

1.  **`today_{ACCOUNT_ID}.json`** (Strumień Live - generowany na każdym tiku/timerze):
    * Zawiera bieżący bilans, equity, wynik z dzisiaj, liczbę otwartych pozycji oraz nazwy brokera i serwera.
2.  **`stats_{ACCOUNT_ID}.json`** (Statystyki okresowe - generowane raz na dobę):
    * Zawiera tablice historycznych wyników netto podzielone na tygodnie (`W0`-`W12`), miesiące (`M0`-`M12`) oraz lata.

## 🏁 Instrukcja Wdrożenia i Pierwszego Uruchomienia

1.  Upewnij się, że na każdym terminalu MT5 działa EA w wersji minimum **4.55**.
2.  Pobierz repozytorium do katalogu na VPS (np. `C:\mt5-vps-monitor`).
3.  Uruchom skrypt generujący w tle za pomocą konsoli (CMD/PowerShell) lub dodaj go do Harmonogramu Zadań Windows:
    ```bash
    python dashboard_generator.py
    ```
4.  Otwórz wygenerowany plik `dashboard.html` w dowolnej przeglądarce (Chrome/Edge). Strona posiada wbudowany mechanizm auto-odświeżania co 30 sekund.

## 📄 Licencja
Projekt autorski na potrzeby monitoringu własnych kont Prop Tradingowych.