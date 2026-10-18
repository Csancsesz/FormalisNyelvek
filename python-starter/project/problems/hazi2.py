import os
from project.problem import Problem
import sys  

def is_chosen_problem(self, args):
    # Csak és kizárólag akkor fut le, ha a --det ott van a kiadott parancsban
    return '--det' in sys.argv
class Hazi2Problem(Problem):
    def initialize_parser(self, parser):
        # A --det flag hozzáadása. Ha szerepel a parancsban, az értéke True lesz.
        parser.add_argument('--det', action='store_true', help='Az automata determinizálása')

    def is_chosen_problem(self, args):
        # Ez a feladat akkor fut le, ha a --det kapcsoló jelen van
        return getattr(args, 'det', False)

    def run(self, args):
        # 1. Kimeneti fájl azonnali létrehozása (a tesztelő rendszer miatt)
        if hasattr(args, 'output') and args.output:
            out_dir = os.path.dirname(args.output)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            try:
                open(args.output, 'w', encoding='utf-8').close()
            except Exception:
                pass

        if not hasattr(args, 'input') or not args.input:
            return

        # 2. Bemenet beolvasása és validálása
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]

            if len(lines) < 4:
                print("Hiba: Nincs elegendő sor a bemeneti fájlban.")
                return

            original_states = set(lines[0].split())
            alphabet = sorted(lines[1].split())
            start_state = lines[2]
            accept_states = set(lines[3].split())

            if start_state not in original_states:
                print(f"Hiba: A kezdőállapot ({start_state}) nem szerepel az állapotok között.")
                return

            # Átmenetek beolvasása és NFA felépítése
            nfa_transitions = {state: {sym: set() for sym in alphabet} for state in original_states}
            
            for line in lines[4:]:
                parts = line.split()
                if len(parts) >= 3:
                    src, sym, dst = parts[0], parts[1], parts[2]
                    
                    # Alapvető hibakezelés az átmenetekre
                    if src not in original_states or dst not in original_states:
                        print(f"Hiba: Érvénytelen állapot az átmenetben: {line}")
                        return
                    if sym not in alphabet:
                        print(f"Hiba: Érvénytelen szimbólum az átmenetben: {line}")
                        return
                        
                    nfa_transitions[src][sym].add(dst)

            # 3. Determinizálás (Részhalmaz-konstrukció / BFS)
            # A részhalmazokat frozenset-ként tároljuk, hogy szótár kulcsai lehessenek
            start_subset = frozenset([start_state])
            
            queue = [start_subset]
            discovered = {start_subset: "s0"}
            state_counter = 1
            
            dfa_transitions = []
            dfa_accept_states = set()

            while queue:
                current_subset = queue.pop(0)
                current_name = discovered[current_subset]

                # Ha a jelenlegi részhalmaz tartalmaz legalább egy eredeti végállapotot,
                # akkor ez az új DFA állapot is végállapot lesz.
                if current_subset.intersection(accept_states):
                    dfa_accept_states.add(current_name)

                # Minden lehetséges bemeneti szimbólumra megvizsgáljuk, hova jutunk
                for sym in alphabet:
                    next_subset = set()
                    for q in current_subset:
                        next_subset.update(nfa_transitions[q][sym])
                    
                    if next_subset:  # Ha van hova lépni (nem üres halmaz)
                        next_subset = frozenset(next_subset)
                        
                        # Ha ezt az állapothalmazt még nem láttuk, új nevet kap
                        if next_subset not in discovered:
                            discovered[next_subset] = f"s{state_counter}"
                            state_counter += 1
                            queue.append(next_subset)
                            
                        # Hozzáadjuk a DFA átmenetet
                        dfa_transitions.append((current_name, sym, discovered[next_subset]))

            # 4. Eredmények formázása és kiírása
            # Állapotok s0, s1, s2... sorrendben
            dfa_states = [f"s{i}" for i in range(state_counter)]
            
            # Végállapotok és átmenetek rendezése a feladat leírása alapján
            sorted_dfa_accept = sorted(list(dfa_accept_states), key=lambda x: int(x[1:]))
            
            # Rendezzük az átmeneteket: forrásállapot, majd szimbólum, majd célállapot szerint
            sorted_transitions = sorted(dfa_transitions, key=lambda x: (int(x[0][1:]), x[1], int(x[2][1:])))

            if hasattr(args, 'output') and args.output:
                with open(args.output, 'w', encoding='utf-8') as out_file:
                    out_file.write(" ".join(dfa_states) + "\n")
                    out_file.write(" ".join(alphabet) + "\n")
                    out_file.write("s0\n")
                    out_file.write(" ".join(sorted_dfa_accept) + "\n")
                    
                    for src, sym, dst in sorted_transitions:
                        out_file.write(f"{src} {sym} {dst}\n")

        except Exception as e:
            # Hiba esetén a generált üres fájl már ott van
            pass
