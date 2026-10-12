from project.problem import Problem

class DFA:
    """A determinisztikus véges automata logikája"""
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
            if len(parts) == 3:
                src_state, symbol, dst_state = parts
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
    """A feladatot a keretrendszerhez illesztő osztály"""
    
    def initialize_parser(self, parser):
        # A --input és --output argumentumokat a main.py már inicializálja,
        # így ide csak a mi egyedi --check argumentumunk kell.
        parser.add_argument('--check', help='Vesszővel elválasztott szavak listája (pl. a,ab,abc).')

    def is_chosen_problem(self, args):
        # Ez a probléma akkor aktív, ha a felhasználó megadta a --check argumentumot.
        return args.check is not None

    def run(self, args):
        # Ellenőrizzük, hogy a fő argumentumok (input, output) meg lettek-e adva
        if not args.input or not args.output:
            print("Hiba: Az --input és --output megadása kötelező a feladat futtatásához!")
            return

        dfa = DFA()
        
        # 1. Automata betöltése
        try:
            dfa.load_from_file(args.input)
        except FileNotFoundError:
            print(f"Hiba: A '{args.input}' fájl nem található.")
            return
        except Exception as e:
            print(f"Hiba az automata betöltésekor: {e}")
            return

        # 2. Szavak feldolgozása
        words_to_check = args.check.split(',')
        results = []

        for word in words_to_check:
            if dfa.accepts(word):
                results.append("IGEN")
            else:
                results.append("NEM")

        # 3. Eredmények kiírása
        try:
            with open(args.output, 'w', encoding='utf-8') as out_file:
                out_file.write('\n'.join(results) + '\n')
        except Exception as e:
            print(f"Hiba a kimeneti fájl írásakor: {e}")