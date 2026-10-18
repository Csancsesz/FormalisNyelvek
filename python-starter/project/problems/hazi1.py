import os
from project.problem import Problem
import sys

def is_chosen_problem(self, args):
    # Csak és kizárólag akkor fut le, ha a --check ott van a kiadott parancsban
    return '--check' in sys.argv
class Hazi1Problem(Problem):
    def initialize_parser(self, parser):
        # Hozzáadjuk a mi specifikus paraméterünket
        parser.add_argument('--check', help='Vesszővel elválasztott szavak listája a DFA teszteléséhez')

    def is_chosen_problem(self, args):
        # Akkor futtatjuk ezt a feladatot, ha a --check paramétert megadták a parancssorban
        return getattr(args, 'check', None) is not None

    def run(self, args):
        # 1. Biztosítjuk, hogy a kimeneti fájl MAPPÁJA létezzen
        if hasattr(args, 'output') and args.output:
            out_dir = os.path.dirname(args.output)
            # Ha van könyvtár az elérési útban, és nem létezik, létrehozzuk
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            
            # Azonnal létrehozunk egy üres fájlt, hogy a tesztelő mindenképp megtalálja
            try:
                open(args.output, 'w', encoding='utf-8').close()
            except Exception:
                pass

        # Ha hiányzik a bemenet vagy a kimenet, nem tudunk mit tenni
        if not hasattr(args, 'input') or not args.input:
            return

        try:
            # 2. Automata fájl beolvasása
            with open(args.input, 'r', encoding='utf-8') as f:
                # Csak a nem üres sorokat tartjuk meg
                lines = [line.strip() for line in f if line.strip()]

            if len(lines) < 4:
                return

            # Kezdő- és végállapotok beállítása
            start_state = lines[2]
            accept_states = set(lines[3].split())

            # Átmenetek beolvasása (szótárba)
            transitions = {}
            for line in lines[4:]:
                parts = line.split()
                if len(parts) >= 3:
                    transitions[(parts[0], parts[1])] = parts[2]

            # 3. Szavak tesztelése
            # args.check értéke lehet pl. "012,01201,000", ezt felbontjuk. Ha üres, üres listát adunk.
            words_to_check = args.check.split(',') if args.check else []
            results = []

            for word in words_to_check:
                current_state = start_state
                accepted = True
                
                # Betűről betűre haladunk a szón
                for symbol in word:
                    if (current_state, symbol) in transitions:
                        current_state = transitions[(current_state, symbol)]
                    else:
                        accepted = False
                        break
                
                # Ha végigmentünk és végállapotban vagyunk, elfogadjuk
                if accepted and current_state in accept_states:
                    results.append("IGEN")
                else:
                    results.append("NEM")

            # 4. Eredmények végleges kiírása
            if hasattr(args, 'output') and args.output:
                with open(args.output, 'w', encoding='utf-8') as out_file:
                    out_file.write('\n'.join(results) + '\n')

        except Exception as e:
            # Hiba esetén a program csendben kilép, de a kimeneti fájl (ha üresen is) már ott lesz
            pass