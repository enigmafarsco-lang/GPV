from pathlib import Path
import json, html

def write_html_report(r, cfg, path):
    rows = ''.join(
        '<tr><td>%d</td><td>%.3f</td><td>%.3f</td><td>%s</td><td>%s</td><td>%.2f</td></tr>' %
        (d.id, d.x_m, d.depth_m, d.classification, d.material_hint, d.confidence)
        for d in r.detections
    )
    txt = """<!doctype html><html><head><meta charset='utf-8'><title>GPR report</title>
<style>body{font-family:Arial;max-width:1100px;margin:auto}img{max-width:100%%}table{border-collapse:collapse}td,th{border:1px solid #aaa;padding:5px}</style></head><body>
<h1>GPR Processing Report</h1><h2>Diagnostics</h2><pre>%s</pre>
<h2>Migrated image</h2><img src='migration_2d.png'><h2>B-scan</h2><img src='bscan_range.png'>
<h2>Detections</h2><table><tr><th>ID</th><th>x</th><th>depth</th><th>class</th><th>material hint</th><th>confidence</th></tr>%s</table>
<p>Specific material subtype is only emitted by a validated trained classifier. Default operation reports generic conductor/geometry classes.</p></body></html>""" % (html.escape(json.dumps(r.diagnostics, indent=2)), rows)
    Path(path).write_text(txt, encoding='utf-8')
