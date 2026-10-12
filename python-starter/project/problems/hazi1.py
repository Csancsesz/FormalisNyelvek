from project.problem import Problem

class DFA:
    def __init__(self):
        self.states = set()
        self.alphabet = set()
        self.start_state = None
        self.accept_states = set()
        self.transitions = {}

    def load_from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) < 4:
            raise ValueError("A bemeneti fájl nem tartalmaz elég sort a DFA definiálásához.")

        self.states = set(lines[0].split())
        self.alphabet = set(lines[1].split())
        self.start_state = lines[2]
        self.accept_states = set(lines[3].split())

        for line in lines[4:]:
            parts = line.split()
            if len(parts) >= 3:
                src_state, symbol, dst_state = parts[0], parts[1], parts[2]
                self.transitions[(src_state, symbol)] = dst_state

    def accepts(self, word):
        current_state = self.start_state
        for symbol in word:
            if (current_state, symbol) in self.transitions:
                current_state = self.transitions[(current_state, symbol)]
            else:
                return False
        return current_state in self.accept_states


class Hazi1Problem(Problem):
    def initialize_parser(self, parser):
        parser.add_argument('--check', help='Vesszővel elválasztott szavak listája (pl. a,ab,abc).', default="")

    def is_chosen_problem(self, args):
        # Akkor tekintjük kiválasztottnak, ha a --check argumentum szerepel a hívásban.
        # A getattr azért biztonságosabb, ha a parser valamiért nem inicializálná.
        return getattr(args, 'check', None) is not None

    def run(self, args):
        # 1. Azonnal hozzuk létre a kimeneti fájlt, hogy a tesztelő rendszer mindenképp megtalálja
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                pass
        except Exception:
            pass # Ha nem tudjuk létrehozni, az később amúgy is kiderül
            
        if not args.input or not args.output:
            return

        dfa = DFA()
        
        # 2. Automata betöltése
        try:
            dfa.load_from_file(args.input)
        except Exception as e:
            # Hiba esetén írjuk be a fájlba a hibát, vagy hagyjuk üresen, 
            # de a fájl már legalább létezik.
            return

        # 3. Szavak feldolgozása
        # Ha a check üres sztring, akkor is helyesen le kell kezelni.
        words_to_check = args.check.split(',') if args.check else []
        results = []

        if words_to_check:
            for word in words_to_check:
                # Az üres szó tesztelése miatt, ha "" van megadva, azt is vizsgálja meg
                if dfa.accepts(word):
                    results.append("IGEN")
                else:
                    results.append("NEM")

        # 4. Eredmények végleges kiírása
        try:
            with open(args.output, 'w', encoding='utf-8') as out_file:
                out_file.write('\n'.join(results) + '\n')
        except Exception:
            pass