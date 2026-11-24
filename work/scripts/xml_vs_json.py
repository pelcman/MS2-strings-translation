# XML_sample/string/jp と json_weblate/jp を突き合わせ、Weblate 管理外の XML を洗い出す
#   PYTHONIOENCODING=utf-8 python work/scripts/xml_vs_json.py
#
# XML はゲームに組み込まれる最終形。json_weblate は Weblate が管理する翻訳データ。
# XML にしか存在しないファイルは「翻訳枠がそもそも無い」= 未訳が放置されている可能性がある。
import glob, os, re, html

XML = "XML_sample/string/jp"
JSON = "json_weblate/jp"

HAN = re.compile(r"[가-힣]")
JPC = re.compile(r"[ぁ-んァ-ヶ]")
CN_ONLY = re.compile(r"[一-鿿]")
# name= / value= など、翻訳対象になりうる属性
ATTR = re.compile(r'\b(?:name|value|desc|text|tooltipDescription|guideDescription|'
                  r'manual|complete|uiDescription|feature)="([^"]*)"')
PH = re.compile(r"^[A-Z0-9$]+(_+[A-Z0-9$]+)+(:\[F\].*)?$")

jsons = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(JSON, "*.json"))}
rows = []
for p in sorted(glob.glob(os.path.join(XML, "*.xml"))):
    fn = os.path.basename(p)[:-4]
    if fn in jsons:
        continue
    raw = open(p, encoding="utf-8", errors="replace").read()
    keys = raw.count("<key ") + raw.count("<quest ") + raw.count("<env ")
    vals = [html.unescape(m) for m in ATTR.findall(raw)]
    vals = [v for v in vals if v.strip()]
    ph = sum(1 for v in vals if PH.match(v.strip()))
    han = sum(1 for v in vals if HAN.search(v))
    jp = sum(1 for v in vals if JPC.search(v))
    cn = sum(1 for v in vals if CN_ONLY.search(v) and not JPC.search(v) and not HAN.search(v))
    size = os.path.getsize(p)
    rows.append((fn, keys, len(vals), ph, han, jp, cn, size))

rows.sort(key=lambda r: (-(r[3] + r[4]), -r[1]))
print("XML にしか存在しないファイル: %d 件\n" % len(rows))
print("%-40s %7s %8s %8s %8s %8s %8s" %
      ("ファイル", "key数", "属性値", "PH", "ハングル", "日本語", "漢字のみ"))
print("-" * 92)
for fn, keys, n, ph, han, jp, cn, size in rows:
    print("%-40s %7d %8d %8d %8d %8d %8d" % (fn, keys, n, ph, han, jp, cn))
print("-" * 92)
print("%-40s %7d %8d %8d %8d %8d %8d" %
      ("合計", sum(r[1] for r in rows), sum(r[2] for r in rows), sum(r[3] for r in rows),
       sum(r[4] for r in rows), sum(r[5] for r in rows), sum(r[6] for r in rows)))
print("\nPH = プレースホルダー形式(未翻訳の目印) / ハングル = 韓国語が残っている値")
