import os
import shutil
import sys

# --- KONFIGURACJA DOMYŚLNA ---
# Jeśli nie podasz trzeciego parametru w konsoli, skrypt użyje tej ścieżki:
DEFAULT_ROOT = r"C:\MT5"

def deploy_ea():
    # Sprawdzenie podstawowego parametru (nazwa pliku)
    if len(sys.argv) < 2:
        print("❌ Błąd: Nie podano nazwy pliku .ex5!")
        print("💡 Użycie: python copy_ea.py NazwaPliku.ex5 [Opcjonalna_Sciezka_Do_Szukania]")
        return

    source_file = sys.argv[1]
    
    # --- DYNAMICZNE SPRAWDZANIE PARAMETRU ŚCIEŻKI ---
    # Jeśli użytkownik podał 3. parametr (indeks 2 w sys.argv), użyj go. W przeciwnym razie użyj DEFAULT_ROOT.
    if len(sys.argv) >= 3:
        search_root = sys.argv[2]
    else:
        search_root = DEFAULT_ROOT

    if not os.path.exists(source_file):
        print(f"❌ Błąd: Plik źródłowy '{source_file}' nie istnieje w bieżącym katalogu!")
        return

    print(f"🚀 Rozpoczynam wdrażanie pliku: {source_file}")
    print(f"📂 Przeszukuję katalog: {search_root}")

    if not os.path.exists(search_root):
        print(f"❌ Błąd: Katalog docelowy '{search_root}' nie istnieje na tym dysku!")
        return

    success_count = 0
    
    # Przeszukiwanie struktury folderów
    for root, dirs, files in os.walk(search_root):
        # Szukamy folderów, które kończą się na MQL5
        if os.path.basename(root).upper() == "MQL5":
            experts_path = os.path.join(root, "Experts")
            
            # Jeśli folder Experts nie istnieje, stwórz go
            if not os.path.exists(experts_path):
                os.makedirs(experts_path)
                
            try:
                dest_file = os.path.join(experts_path, source_file)
                shutil.copy2(source_file, dest_file)
                
                # Ładne przycięcie ścieżki do wyświetlania w konsoli (pokazuje tylko nazwę instancji i dalszą ścieżkę)
                display_path = root.replace(search_root, "")
                if display_path.startswith(os.sep):
                    display_path = display_path[1:]
                
                print(f"✅ Skopiowano do: ...\\{display_path}\\Experts")
                success_count += 1
            except Exception as e:
                print(f"❌ Problem z kopiowaniem do {experts_path}: {e}")

    print("\n" + "="*50)
    print(f"🎉 Gotowe! Plik został wdrożony do {success_count} terminali.")
    print("="*50)

if __name__ == "__main__":
    deploy_ea()