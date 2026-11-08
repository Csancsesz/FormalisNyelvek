import os
import sys
from project.problem import Problem

class Hazi3Problem(Problem):
    def initialize_parser(self, parser):
        # A --mini flag hozzáadása
        parser.add_argument('--mini', action='store_true', help='Determinisztikus véges automata minimalizálása')

    def is_chosen_problem(self, args):
        # Csak akkor fut le ez a modul, ha a --mini ott van a kiadott parancssorban
        return '--mini' in sys.argv

    def run(self, args):
        # Kimeneti fájl azonnali létrehozása 
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

        try:
            # Bemenet beolvasása és validálása
            with open(args.input, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]

            if len(lines) < 4:
                return

            original_states = sorted(lines[0].split(), key=lambda x: int(x[1:]) if x[1:].isdigit() else x)
            alphabet = sorted(lines[1].split())
            start_state = lines[2]
            accept_states = set(lines[3].split())

            # Validáció
            if start_state not in original_states:
                return

            transitions = {}
            for line in lines[4:]:
                parts = line.split()
                if len(parts) >= 3:
                    src, sym, dst = parts[0], parts[1], parts[2]
                    if src not in original_states or dst not in original_states or sym not in alphabet:
                        return
                    transitions[(src, sym)] = dst

            # Elérhetetlen állapotok kiszűrése 
            reachable = set()
            queue = [start_state]
            reachable.add(start_state)

            while queue:
                curr = queue.pop(0)
                for sym in alphabet:
                    if (curr, sym) in transitions:
                        nxt = transitions[(curr, sym)]
                        if nxt not in reachable:
                            reachable.add(nxt)
                            queue.append(nxt)

            active_states = [q for q in original_states if q in reachable]

            # Hopcroft-féle ekvivalencia-partícionálás (Minimalizálás)
            # Kezdő partíciók: elfogadó és nem elfogadó állapotok
            F = set(q for q in active_states if q in accept_states)
            non_F = set(q for q in active_states if q not in accept_states)

            P = []
            if F:
                P.append(F)
            if non_F:
                P.append(non_F)

            changed = True
            while changed:
                changed = False
                new_P = []

                for group in P:
                    if len(group) <= 1:
                        new_P.append(group)
                        continue

                    # Csoport felbontása a kimenő átmenetek cél-csoportjai alapján
                    subgroups = {}
                    for state in group:
                        # Megkeressük minden szimbólumra, hogy melyik P-beli csoportba vezet az átmenet
                        signature = []
                        for sym in alphabet:
                            target = transitions.get((state, sym))
                            target_group_idx = None
                            if target:
                                for idx, g in enumerate(P):
                                    if target in g:
                                        target_group_idx = idx
                                        break
                            signature.append(target_group_idx)
                        
                        sig_tuple = tuple(signature)
                        if sig_tuple not in subgroups:
                            subgroups[sig_tuple] = set()
                        subgroups[sig_tuple].add(state)

                    split_groups = list(subgroups.values())
                    if len(split_groups) > 1:
                        changed = True
                    new_P.extend(split_groups)

                P = new_P

            # Új állapotnevek hozzárendelése (s0, s1, ...)
            # A szabály szerint az összevont állapot az elemei közül a legkisebb indexűt képviseli
            group_representatives = []
            for group in P:
                # Eredeti sorrend szerint a legkisebb elem
                rep = sorted(list(group), key=lambda x: int(x[1:]) if x[1:].isdigit() else x)[0]
                group_representatives.append((rep, group))

            # A képviselők száma szerinti sorrend határozza meg az új 's' indexet
            group_representatives.sort(key=lambda x: int(x[0][1:]) if x[0][1:].isdigit() else x[0])

            state_map = {}
            new_states = []
            new_accept_states = set()

            for i, (rep, group) in enumerate(group_representatives):
                new_name = f"s{i}"
                new_states.append(new_name)
                for q in group:
                    state_map[q] = new_name
                
                # Ha a csoport tartalmazott végállapotot, az új állapot is az lesz
                if group.intersection(accept_states):
                    new_accept_states.add(new_name)

            # Új átmenetek generálása
            new_transitions = set()
            for (src, sym), dst in transitions.items():
                if src in state_map and dst in state_map:
                    new_src = state_map[src]
                    new_dst = state_map[dst]
                    new_transitions.add((new_src, sym, new_dst))

            # Átmenetek rendezése: forrásállapot indexe, szimbólum, célállapot indexe
            sorted_transitions = sorted(
                list(new_transitions),
                key=lambda x: (int(x[0][1:]), x[1], int(x[2][1:]))
            )

            sorted_accept_states = sorted(
                list(new_accept_states),
                key=lambda x: int(x[1:])
            )

            # Kimenet írása
            if hasattr(args, 'output') and args.output:
                with open(args.output, 'w', encoding='utf-8') as out_file:
                    out_file.write(" ".join(new_states) + "\n")
                    out_file.write(" ".join(alphabet) + "\n")
                    out_file.write(state_map[start_state] + "\n")
                    out_file.write(" ".join(sorted_accept_states) + "\n")
                    
                    for src, sym, dst in sorted_transitions:
                        out_file.write(f"{src} {sym} {dst}\n")

        except Exception:
            pass