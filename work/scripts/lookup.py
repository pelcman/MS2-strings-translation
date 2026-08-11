# -*- coding: utf-8 -*-
"""対訳コーパス検索ツール。EN/KO/JAいずれの語でも部分一致で検索できる。

使い方:
    python work/scripts/lookup.py <検索語> [最大表示件数=20]
例:
    python work/scripts/lookup.py "Reward Box"
    python work/scripts/lookup.py ブーツ
    python work/scripts/lookup.py 주문서
"""
import sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TSV = os.path.join(ROOT, "dict", "corpus", "itemname-pairs.tsv")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    term = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    hits = 0
    with open(TSV, encoding="utf-8") as f:
        header = next(f)
        for line in f:
            cols = line.rstrip("\n").split("\t")
            if any(term in c for c in cols[:3]):
                hits += 1
                if hits <= limit:
                    en, ko, ja = cols[0], cols[1], cols[2]
                    print(f"EN: {en}\nKO: {ko}\nJA: {ja}\n")
    print(f"--- {hits} 件ヒット (表示は最大 {limit} 件)")

if __name__ == "__main__":
    main()
