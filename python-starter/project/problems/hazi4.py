import os
import re
import sys
from collections import Counter
from project.problem import Problem

class Hazi4Problem(Problem):
    def initialize_parser(self, parser):
        parser.add_argument('--rgx', type=int, help='A regex feladat sorszáma (1-5)')

    def is_chosen_problem(self, args):
        return '--rgx' in sys.argv

    def run(self, args):
        # 1. Kimeneti fájl azonnali létrehozása
        if hasattr(args, 'output') and args.output:
            out_dir = os.path.dirname(args.output)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            try:
                open(args.output, 'w', encoding='utf-8').close()
            except Exception:
                pass

        if not hasattr(args, 'input') or not args.input or getattr(args, 'rgx', None) is None:
            return

        try:
            with open(args.input, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.read().splitlines()

            task = args.rgx
            results = []

            if task == 1:
                # 10 alpont reguláris kifejezései
                patterns = [
                    # 1. összes sor, amelyik 10. hónap 15-én jött létre
                    re.compile(r'^10-15\b'),
                    # 2. összes sor, amelyik 10. hónap 15-én 10 óra 18 perc és 51 másodperckor jött létre
                    re.compile(r'^10-15 10:18:51\b'),
                    # 3. összes sor, amelyik 51 másodperckor jött létre (mindegy a perc)
                    re.compile(r'^\d{2}-\d{2} \d{2}:\d{2}:51\b'),
                    # 4. összes lowmemorykiller taget tartalmazó sor
                    re.compile(r'^\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\s+\d+\s+\d+\s+[IDVEFAW]\s+lowmemorykiller\s*:'),
                    # 5. összes 10:18:51 kor keletkező 221-es process id-jú sor
                    re.compile(r'^\d{2}-\d{2} 10:18:51\.\d+\s+221\b'),
                    # 6. összes hibát tartalmazó sor (E)
                    re.compile(r'^\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\s+\d+\s+\d+\s+E\b'),
                    # 7. összes warning (W) amit a PackageManager küld
                    re.compile(r'^\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\s+\d+\s+\d+\s+W\s+PackageManager\s*:'),
                    # 8. összes ExoPlayer-es debug (D) infó
                    re.compile(r'^\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\s+\d+\s+\d+\s+D\s+.*ExoPlayer.*?:'),
                    # 9. összes java állomány pozíciót tartalmazó hiba és warning (EW .java:)
                    re.compile(r'^\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\s+\d+\s+\d+\s+[EW]\s+.*?:.*\.java:\d+'),
                    # 10. összes olyan sor, ami tartalmazza a Thread szót a message részben (nem a tagben)
                    re.compile(r'^\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\s+\d+\s+\d+\s+[IDVEFAW]\s+[^:]+:\s*.*\bThread\b')
                ]

                for pat in patterns:
                    count = sum(1 for line in lines if pat.search(line))
                    results.append(str(count))

            elif task == 2:
                # Összes hiba (E sorok) származási helye (stack trace: pl. HashMap.java)
                pat = re.compile(r'^\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\s+\d+\s+\d+\s+E\s+[^:]+:.*?\(([A-Za-z0-9_$]+\.java):\d+\)')
                for line in lines:
                    for match in pat.finditer(line):
                        results.append(match.group(1))

            elif task == 3:
                # Összes különböző process id megjelenési sorrendben
                pat = re.compile(r'^[0-9-]+ [0-9:.]+\s+([0-9]+)\s+[0-9]+\s+[IDVEFAW]\s+[^:]+:')
                seen_pids = set()
                for line in lines:
                    match = pat.search(line)
                    if match:
                        pid = match.group(1)
                        if pid not in seen_pids:
                            seen_pids.add(pid)
                            results.append(pid)

            elif task == 4:
                # A legtöbb errort tartalmazó process: PID=xx (xx errors)
                pat = re.compile(r'^[0-9-]+ [0-9:.]+\s+([0-9]+)\s+[0-9]+\s+E\s+[^:]+:')
                pid_counts = Counter()
                for line in lines:
                    match = pat.search(line)
                    if match:
                        pid_counts[match.group(1)] += 1
                
                if pid_counts:
                    top_pid, top_count = pid_counts.most_common(1)[0]
                    results.append(f"PID={top_pid} ({top_count} errors)")

            elif task == 5:
                # A fő szálon történt hibák (E) száma (PID == TID)
                pat = re.compile(r'^[0-9-]+ [0-9:.]+\s+([0-9]+)\s+\1\s+E\s+[^:]+:')
                count = sum(1 for line in lines if pat.search(line))
                results.append(str(count))

            # Eredmények kiírása
            if hasattr(args, 'output') and args.output:
                with open(args.output, 'w', encoding='utf-8') as out_file:
                    if results:
                        out_file.write('\n'.join(results) + '\n')

        except Exception as e:
            print(f"HIBA TÖRTÉNT: {e}")