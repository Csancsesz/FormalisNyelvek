import argparse
import sys

class DFA:
    def __init__(self):
        self.states = set()
        self.alphabet = set()
        self.start_state = None
        self.accept_states = set()
        self.transitions = {}

    def load_from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            # Csak a nem üres sorokat olvassuk be, eltávolítva a felesleges szóközöket/sortöréseket
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) < 4:
            raise ValueError("A bemeneti fájl nem tartalmaz elég sort a DFA definiálásához.")

        # 1. sor: Állapotok
        self.states = set(lines[0].split())
        # 2. sor: Bemeneti ábécé
        self.alphabet = set(lines[1].split())
        # 3. sor: Kezdőállapot
        self.start_state = lines[2]
        # 4. sor: Végállapotok
        self.accept_states = set(lines[3].split())

        # Következő sorok: Átmenetek
        for line in lines[4:]:
            parts = line.split()
            if len(parts) == 3:
                src_state, symbol, dst_state = parts
                self.transitions[(src_state, symbol)] = dst_state

    def accepts(self, word):
        current_state = self.start_state
        
        for symbol in word:
            # Ha nincs definiált átmenet az adott állapotból ezzel a szimbólummal, elutasítjuk
            if (current_state, symbol) in self.transitions:
                current_state = self.transitions[(current_state, symbol)]
            else:
                return False
                
        # Ha a szó végére értünk, elfogadjuk-e az aktuális állapotot?
        return current_state in self.accept_states

def main():
    parser = argparse.ArgumentParser(description="Determinisztikus Véges Automata (DFA) Szimulátor")
    parser.add_argument("--input", required=True, help="A bemeneti fájl, amely tartalmazza az automata adatait.")
    parser.add_argument("--output", required=True, help="A fájl, amelybe az eredményeket kiírja.")
    parser.add_argument("--check", required=True, help="Vesszővel elválasztott szavak listája (pl. a,ab,abc).")

    args = parser.parse_args()

    dfa = DFA()
    
    # 1. Automata betöltése
    try:
        dfa.load_from_file(args.input)
    except FileNotFoundError:
        print(f"Hiba: A '{args.input}' fájl nem található.")
        sys.exit(1)
    except Exception as e:
        print(f"Hiba az automata betöltésekor: {e}")
        sys.exit(1)

    # 2. Szavak feldolgozása
    # A szavakat vessző mentén szétválasztjuk.
    words_to_check = args.check.split(',')
    results = []

    for word in words_to_check:
        # Üres szó (epszilon) kezelése: ha a split után üres sztring maradt
        if dfa.accepts(word):
            results.append("IGEN")
        else:
            results.append("NEM")

    # 3. Eredmények kiírása fájlba
    try:
        with open(args.output, 'w', encoding='utf-8') as out_file:
            # Minden eredmény új sorba kerül
            out_file.write('\n'.join(results) + '\n')
    except Exception as e:
        print(f"Hiba a kimeneti fájl írásakor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()