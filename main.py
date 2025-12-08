#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                    SYMULACJA PROBLEMU JAGODZIŃSKIEGO
                    System Symulacji Ruchu Drogowego
═══════════════════════════════════════════════════════════════════════════════

Główny interfejs CLI do interakcji z systemem symulacji.
Obsługuje tryb interaktywny (menu) oraz argumenty linii poleceń.

Użycie:
    python main.py                  # Tryb interaktywny (menu)
    python main.py simulate         # Uruchom symulację
    python main.py analyze          # Uruchom analizę danych
    python main.py test             # Uruchom testy przypadków trywialnych
    python main.py --help           # Wyświetl pomoc
"""

import argparse
import subprocess
import sys
import os
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════════
# STAŁE I KONFIGURACJA
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    'reset': '\033[0m',
    'bold': '\033[1m',
    'dim': '\033[2m',
    'cyan': '\033[36m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'red': '\033[31m',
    'magenta': '\033[35m',
    'blue': '\033[34m',
    'white': '\033[97m',
}

# Wyłącz kolory jeśli terminal ich nie obsługuje
if not sys.stdout.isatty():
    COLORS = {k: '' for k in COLORS}


def c(text: str, *styles: str) -> str:
    """Kolorowanie tekstu"""
    prefix = ''.join(COLORS.get(s, '') for s in styles)
    return f"{prefix}{text}{COLORS['reset']}" if prefix else text


# ═══════════════════════════════════════════════════════════════════════════════
# INTERFEJS UŻYTKOWNIKA
# ═══════════════════════════════════════════════════════════════════════════════

HEADER = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ███████╗██╗   ██╗███╗   ███╗██╗   ██╗██╗      █████╗  ██████╗     ██╗ █████╗║
║   ██╔════╝╚██╗ ██╔╝████╗ ████║██║   ██║██║     ██╔══██╗██╔════╝     ██║██╔══██║
║   ███████╗ ╚████╔╝ ██╔████╔██║██║   ██║██║     ███████║██║          ██║███████║
║   ╚════██║  ╚██╔╝  ██║╚██╔╝██║██║   ██║██║     ██╔══██║██║     ██   ██║██╔══██║
║   ███████║   ██║   ██║ ╚═╝ ██║╚██████╔╝███████╗██║  ██║╚██████╗╚█████╔╝██║  ██║
║   ╚══════╝   ╚═╝   ╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚════╝ ╚═╝  ╚═╝
║                                                                               ║
║                           PROBLEM JAGODZIŃSKI                                 ║
║                    System Symulacji Ruchu Drogowego                           ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

MENU_OPTIONS = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MENU GŁÓWNE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   {s} Uruchom symulację ruchu                                     │
│      Generuje dane symulacyjne dla różnych wariantów infrastruktury         │
│                                                                             │
│   {a} Uruchom analizę danych                                      │
│      Analizuje i wizualizuje zebrane dane symulacyjne                       │
│                                                                             │
│   {t} Uruchom testy przypadków trywialnych                        │
│      Testuje scenariusze z 100% autobusów i przypadki brzegowe              │
│                                                                             │
│   {h} Wyświetl pomoc                                              │
│      Szczegółowy opis działania programu i dostępnych opcji                 │
│                                                                             │
│   {q} Zakończ program                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
"""

HELP_TEXT = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  POMOC                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  OPIS SYSTEMU:                                                              │
│  System symulacji ruchu drogowego "Problem Jagodziński" bada wpływ       │
│  wprowadzenia buspasa na płynność ruchu drogowego w mieście.                │
│                                                                             │
│  DOSTĘPNE WARIANTY SYMULACJI:                                               │
│    • Wariant A: 3 pasy ruchu, bez buspasa (scenariusz bazowy)               │
│    • Wariant B: 2 pasy + buspas (redukcja pasów na rzecz buspasa)           │
│    • Wariant C: Konfiguracja zoptymalizowana                                │
│    • Wariant D: Wysokie natężenie ruchu (test stresu)                       │
│    • Niestandardowy: Własne parametry symulacji                             │
│                                                                             │
│  PRZEPŁYW PRACY:                                                            │
│    1. Uruchom symulację (opcja 1) - generuje dane do katalogu simulation_data│
│    2. Uruchom analizę (opcja 2) - przetwarza i wizualizuje dane             │
│                                                                             │
│  UŻYCIE Z LINII POLECEŃ:                                                    │
│    python main.py                    # Tryb interaktywny                    │
│    python main.py simulate           # Bezpośrednie uruchomienie symulacji  │
│    python main.py analyze            # Bezpośrednie uruchomienie analizy    │
│    python main.py test               # Uruchomienie testów trywialnych      │
│    python main.py simulate -v A      # Symulacja tylko wariantu A           │
│    python main.py simulate -v A B    # Symulacja wariantów A i B            │
│    python main.py simulate --all     # Wszystkie warianty + niestandardowy  │
│                                                                             │
│  PLIKI WYJŚCIOWE:                                                           │
│    • simulation_data/*.csv - surowe dane symulacji                          │
│    • analysis_results/*.png - wykresy i wizualizacje                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
"""


def print_header():
    """Wyświetla nagłówek programu"""
    print(c(HEADER, 'cyan', 'bold'))


def print_menu():
    """Wyświetla menu główne"""
    formatted_menu = MENU_OPTIONS.format(
        s=c('[1]', 'green', 'bold'),
        a=c('[2]', 'green', 'bold'),
        t=c('[3]', 'green', 'bold'),
        h=c('[H]', 'yellow', 'bold'),
        q=c('[Q]', 'red', 'bold'),
    )
    print(formatted_menu)


def print_help():
    """Wyświetla pomoc"""
    print(c(HELP_TEXT, 'white'))


def print_separator(char: str = '─', length: int = 77):
    """Wyświetla separator"""
    print(c(char * length, 'dim'))


def print_status(message: str, status: str = 'info'):
    """Wyświetla komunikat statusu"""
    icons = {
        'info': ('ℹ', 'cyan'),
        'success': ('✓', 'green'),
        'warning': ('⚠', 'yellow'),
        'error': ('✗', 'red'),
        'running': ('⟳', 'magenta'),
    }
    icon, color = icons.get(status, ('•', 'white'))
    print(f"  {c(icon, color, 'bold')} {message}")


# ═══════════════════════════════════════════════════════════════════════════════
# AKCJE
# ═══════════════════════════════════════════════════════════════════════════════

def ask_for_reruns() -> int:
    """Pyta użytkownika o liczbę powtórzeń symulacji"""
    print()
    print(c("  KONFIGURACJA SYMULACJI", 'yellow', 'bold'))
    print_separator('─')
    print()
    print("  Ile powtórzeń symulacji wykonać dla każdego scenariusza?")
    print(c("  (więcej powtórzeń = bardziej wiarygodne wyniki statystyczne)", 'dim'))
    print()
    
    try:
        reruns_input = input(f"  {c('Liczba powtórzeń', 'bold')} (1-50, Enter = 1): ").strip()
        
        if not reruns_input:
            reruns = 1
        else:
            reruns = int(reruns_input)
            reruns = max(1, min(50, reruns))
        
        if reruns > 1:
            print_status(f"Ustawiono {reruns} powtórzeń dla każdego scenariusza", 'success')
        else:
            print_status("Pojedyncze uruchomienie każdego scenariusza", 'info')
        
        return reruns
        
    except (ValueError, EOFError):
        print_status("Używam domyślnej wartości: 1 powtórzenie", 'info')
        return 1


def run_simulation(variants: Optional[list] = None, include_custom: bool = False, reruns: Optional[int] = None):
    """
    Uruchamia symulację ruchu
    
    Args:
        variants: lista wariantów do uruchomienia (None = wszystkie predefiniowane)
        include_custom: czy dołączyć scenariusz niestandardowy
        reruns: liczba powtórzeń symulacji (None = pytaj interaktywnie)
    """
    print()
    print_separator('═')
    print(c("  URUCHAMIANIE SYMULACJI", 'cyan', 'bold'))
    print_separator('═')
    
    script_path = os.path.join(os.path.dirname(__file__), 'simulation_main.py')
    
    if not os.path.exists(script_path):
        print_status("Nie znaleziono pliku simulation_main.py!", 'error')
        return 1
    
    # Pytaj o liczbę powtórzeń jeśli nie podano
    if reruns is None:
        reruns = ask_for_reruns()
    
    print()
    print_status("Uruchamianie modułu symulacji...", 'running')
    print()
    
    # Buduj argumenty dla simulation_main.py
    cmd = [sys.executable, script_path, '-r', str(reruns)]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=os.path.dirname(__file__) or '.'
        )
        
        if result.returncode == 0:
            print()
            print_status("Symulacja zakończona pomyślnie!", 'success')
        else:
            print()
            print_status(f"Symulacja zakończona z kodem: {result.returncode}", 'warning')
        
        return result.returncode
        
    except KeyboardInterrupt:
        print()
        print_status("Symulacja przerwana przez użytkownika", 'warning')
        return 130
    except Exception as e:
        print_status(f"Błąd: {e}", 'error')
        return 1


def run_analysis():
    """Uruchamia analizę danych symulacji"""
    print()
    print_separator('═')
    print(c("  URUCHAMIANIE ANALIZY DANYCH", 'cyan', 'bold'))
    print_separator('═')
    print()
    
    script_path = os.path.join(os.path.dirname(__file__), 'analysis_main.py')
    
    if not os.path.exists(script_path):
        print_status("Nie znaleziono pliku analysis_main.py!", 'error')
        return 1
    
    # Sprawdź czy są dane do analizy
    data_dir = os.path.join(os.path.dirname(__file__) or '.', 'simulation_data')
    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        print_status("Brak danych do analizy!", 'warning')
        print_status("Najpierw uruchom symulację (opcja 1)", 'info')
        return 1
    
    print_status("Uruchamianie modułu analizy...", 'running')
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=os.path.dirname(__file__) or '.'
        )
        
        if result.returncode == 0:
            print()
            print_status("Analiza zakończona pomyślnie!", 'success')
        else:
            print()
            print_status(f"Analiza zakończona z kodem: {result.returncode}", 'warning')
        
        return result.returncode
        
    except KeyboardInterrupt:
        print()
        print_status("Analiza przerwana przez użytkownika", 'warning')
        return 130
    except Exception as e:
        print_status(f"Błąd: {e}", 'error')
        return 1


def run_trivial_tests():
    """Uruchamia testy przypadków trywialnych"""
    print()
    print_separator('═')
    print(c("  URUCHAMIANIE TESTÓW TRYWIALNYCH", 'cyan', 'bold'))
    print_separator('═')
    print()
    
    script_path = os.path.join(os.path.dirname(__file__), 'trivial_cases_tester.py')
    
    if not os.path.exists(script_path):
        print_status("Nie znaleziono pliku trivial_cases_tester.py!", 'error')
        return 1
    
    print_status("Uruchamianie testów scenariuszy z 100% autobusów...", 'running')
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=os.path.dirname(__file__) or '.'
        )
        
        if result.returncode == 0:
            print()
            print_status("Testy zakończone pomyślnie!", 'success')
        else:
            print()
            print_status(f"Testy zakończone z kodem: {result.returncode}", 'warning')
        
        return result.returncode
        
    except KeyboardInterrupt:
        print()
        print_status("Testy przerwane przez użytkownika", 'warning')
        return 130
    except Exception as e:
        print_status(f"Błąd: {e}", 'error')
        return 1


# ═══════════════════════════════════════════════════════════════════════════════
# TRYB INTERAKTYWNY
# ═══════════════════════════════════════════════════════════════════════════════

def interactive_mode():
    """Uruchamia tryb interaktywny (menu)"""
    print_header()
    
    while True:
        print_menu()
        
        try:
            choice = input(f"  {c('Wybierz opcję', 'bold')}: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            print_status("Do widzenia!", 'info')
            return 0
        
        if choice in ['1', 's', 'simulate', 'symulacja']:
            run_simulation()
        elif choice in ['2', 'a', 'analyze', 'analiza']:
            run_analysis()
        elif choice in ['3', 't', 'test', 'testy']:
            run_trivial_tests()
        elif choice in ['h', 'help', 'pomoc', '?']:
            print_help()
        elif choice in ['q', 'quit', 'exit', 'wyjście', 'wyjscie', '0']:
            print()
            print_status("Do widzenia!", 'info')
            print()
            return 0
        elif choice == '':
            continue
        else:
            print_status(f"Nieznana opcja: '{choice}'", 'warning')
            print_status("Wpisz H aby wyświetlić pomoc", 'info')
        
        print()


# ═══════════════════════════════════════════════════════════════════════════════
# PARSER ARGUMENTÓW CLI
# ═══════════════════════════════════════════════════════════════════════════════

def create_parser() -> argparse.ArgumentParser:
    """Tworzy parser argumentów linii poleceń"""
    parser = argparse.ArgumentParser(
        prog='python main.py',
        description='System Symulacji Problemu Jagodzińskiego - analiza wpływu buspasa na ruch drogowy',
        epilog='Bez argumentów uruchamia tryb interaktywny (menu)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Dostępne komendy')
    
    # Komenda: simulate
    sim_parser = subparsers.add_parser(
        'simulate', 
        aliases=['sim', 's'],
        help='Uruchom symulację ruchu drogowego'
    )
    sim_parser.add_argument(
        '-v', '--variants',
        nargs='+',
        choices=['A', 'B', 'C', 'D', 'a', 'b', 'c', 'd'],
        help='Warianty do uruchomienia (np. -v A B C)'
    )
    sim_parser.add_argument(
        '--all',
        action='store_true',
        help='Uruchom wszystkie warianty + scenariusz niestandardowy'
    )
    sim_parser.add_argument(
        '-r', '--reruns',
        type=int,
        default=None,
        help='Liczba powtórzeń symulacji dla każdego scenariusza (1-50)'
    )
    
    # Komenda: analyze
    subparsers.add_parser(
        'analyze',
        aliases=['analysis', 'a'],
        help='Uruchom analizę danych symulacji'
    )
    
    # Komenda: test
    subparsers.add_parser(
        'test',
        aliases=['t'],
        help='Uruchom testy przypadków trywialnych (100% autobusów)'
    )
    
    return parser


# ═══════════════════════════════════════════════════════════════════════════════
# PUNKT WEJŚCIA
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Główna funkcja programu"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Jeśli nie podano komendy, uruchom tryb interaktywny
    if args.command is None:
        return interactive_mode()
    
    # Obsługa komend
    if args.command in ['simulate', 'sim', 's']:
        return run_simulation(
            variants=args.variants,
            include_custom=args.all if hasattr(args, 'all') else False,
            reruns=args.reruns if hasattr(args, 'reruns') else None
        )
    elif args.command in ['analyze', 'analysis', 'a']:
        return run_analysis()
    elif args.command in ['test', 't']:
        return run_trivial_tests()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
