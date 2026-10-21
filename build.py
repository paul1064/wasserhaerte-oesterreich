#!/usr/bin/env python3
"""Baut die statische Seite nach ./docs (GitHub Pages: Branch main, Ordner /docs).
Neue Seite = neue Datei data/orte/<slug>.json anlegen, dann `python3 build.py`."""
import json, glob, os, html, shutil
TAG = "DEINTAG-21"   # Amazon-PartnerNet-Tag hier eintragen
SITE = "Wasserhärte Österreich"
OUT = "docs"
e = html.escape
BL = ["Burgenland","Kärnten","Niederösterreich","Oberösterreich","Salzburg","Steiermark","Tirol","Vorarlberg","Wien"]

def amz(q): return f"https://www.amazon.de/s?k={q.replace(' ','+')}&tag={TAG}"

CSS = """*{box-sizing:border-box}body{margin:0;font:17px/1.6 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#1b2b34;background:#f6f9fb}
header{background:#0b5f8a;color:#fff;padding:.8rem 1rem}header a{color:#fff;text-decoration:none;font-weight:700}nav a{margin-left:1rem;font-weight:400;font-size:.95rem}
main{max-width:820px;margin:0 auto;padding:1rem}h1{line-height:1.25;font-size:1.8rem}a{color:#0b5f8a}
.card{background:#fff;border-radius:10px;padding:1rem 1.2rem;margin:1rem 0;box-shadow:0 1px 3px #0001}
table{width:100%;border-collapse:collapse;font-size:.95rem}th,td{text-align:left;padding:.45rem;border-bottom:1px solid #e3eaef}th{background:#eef4f8}
.big{font-size:2rem;font-weight:800;color:#0b5f8a}.badge{display:inline-block;padding:.1rem .6rem;border-radius:99px;font-size:.85rem;color:#fff}
.weich{background:#2e9d5b}.mittel{background:#d39b12}.hart{background:#c2412d}.src{font-size:.85rem;color:#556}
.aff{border:2px dashed #0b5f8a33}.btn{display:inline-block;background:#ff9900;color:#111;padding:.4rem .8rem;border-radius:6px;text-decoration:none;margin:.2rem .3rem .2rem 0;font-weight:600}
footer{max-width:820px;margin:2rem auto;padding:1rem;font-size:.85rem;color:#556}ul.orte{columns:2}@media(max-width:600px){ul.orte{columns:1}h1{font-size:1.5rem}}"""

def stufe(dh):
    if dh is None: return None
    return "weich" if dh < 10 else ("mittel" if dh <= 16 else "hart")
LABEL = {"weich":"Härtestufe I – weich (<10 °dH)","mittel":"Härtestufe II – mittel (10–16 °dH)","hart":"Härtestufe III – hart (>16 °dH)"}
TIPS = {
 "weich":["Waschmittel nach der Dosierung für <b>weiches Wasser</b> sparsam verwenden.","Entkalken selten nötig – Wasserkocher/Kaffeemaschine etwa alle paar Monate kontrollieren.","Geschirrspüler auf die niedrigste Härtestufe stellen; Regeneriersalz wird kaum verbraucht."],
 "mittel":["Waschmittel nach der Dosierung für <b>mittelhartes Wasser</b> verwenden.","Wasserkocher und Kaffeemaschine ca. monatlich entkalken (Zitronen- oder Amidosulfonsäure).","Geschirrspüler auf Ihren °dH-Wert einstellen und Regeneriersalz nachfüllen."],
 "hart":["Waschmittel nach der Dosierung für <b>hartes Wasser</b> verwenden; ab 60 °C ggf. separaten Enthärter zugeben.","Wasserkocher, Kaffeemaschine und Duschkopf regelmäßig (alle 2–4 Wochen) entkalken.","Warmwasser nicht unnötig über 60 °C heizen – darüber fällt deutlich mehr Kalk aus.","Geschirrspüler unbedingt auf den °dH-Wert einstellen, Salz regelmäßig nachfüllen."]}

def page(path, title, desc, body, depth):
    r = "../"*depth
    doc = f"""<!doctype html><html lang="de-AT"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="stylesheet" href="{r}style.css"></head><body>
<header><a href="{r}index.html">💧 {SITE}</a><nav><a href="{r}wasserhaerte-erklaert.html">°dH erklärt</a><a href="{r}geschirrspueler-einstellen.html">Geschirrspüler</a></nav></header>
<main>{body}</main><footer><p><b>Hinweis:</b> Alle Werte stammen aus den verlinkten Veröffentlichungen der Wasserversorger bzw. Gemeinden. Die Härte kann schwanken; verbindlich ist die Auskunft Ihres Versorgers.</p>
<p><b>Werbehinweis:</b> Links mit „Amazon“ sind Affiliate-Links. Als Amazon-Partner verdienen wir an qualifizierten Verkäufen – für Sie entstehen keine Mehrkosten.</p>
<p><a href="{r}impressum.html">Impressum &amp; Datenschutz</a></p></footer></body></html>"""
    os.makedirs(os.path.dirname(os.path.join(OUT,path)) or OUT, exist_ok=True)
    open(os.path.join(OUT,path),"w").write(doc)

AFF = f"""<div class="card aff"><h2>Passende Produkte</h2><p>Gegen Kalk im Alltag:</p>
<a class="btn" rel="sponsored nofollow" href="{amz('Entkalker Zitronensäure')}">Entkalker auf Amazon</a>
<a class="btn" rel="sponsored nofollow" href="{amz('Duschfilter Kalk')}">Duschfilter auf Amazon</a>
<a class="btn" rel="sponsored nofollow" href="{amz('Wasserhärte Teststreifen')}">Härte-Teststreifen auf Amazon</a>
<p class="src">Werbung / Affiliate-Links.</p></div>"""

def ort(o):
    lo, hi = o["min_dh"], o["max_dh"]
    st = stufe(hi); rows = ""
    for z in o["zonen"]:
        rows += f"<tr><td>{e(z['zone'])}</td><td>{e(z['dh'])}</td>" + (f"<td>{e(z['mmol'])}</td>" if "mmol" in z else "") + (f"<td>{e(z['stufe'])}</td>" if "stufe" in z else "") + "</tr>"
    h = "<th>Gebiet</th><th>Gesamthärte °dH</th>" + ("<th>mmol/l</th>" if "mmol" in o["zonen"][0] else "") + ("<th>Härtestufe</th>" if "stufe" in o["zonen"][0] else "")
    stufen = sorted({stufe(lo), stufe(hi)}, key=["weich","mittel","hart"].index)
    tips = "".join(f"<h3><span class='badge {s}'>{LABEL[s]}</span></h3><ul>"+"".join(f"<li>{t}</li>" for t in TIPS[s])+"</ul>" for s in stufen)
    fmt = lambda x: str(x).replace(".",",")
    src = f"<a href='{e(o['quelle'])}' rel='nofollow'>{e(o['quelle_titel'])}</a>" + (f" · <a href='{e(o['quelle2'])}' rel='nofollow'>weitere Quelle</a>" if o.get("quelle2") else "")
    body = f"""<p class="src"><a href="../index.html">Start</a> › {e(o['bundesland'])} › {e(o['name'])}</p>
<h1>Wasserhärte in {e(o['name'])}</h1>
<div class="card"><div class="big">{fmt(lo)}–{fmt(hi)} °dH</div><p>{e(o['zusammenfassung'])}</p>
<p class="src">Versorger: {e(o['versorger'])}<br>Quelle: {src}<br>Abgerufen am {o['abgerufen']}</p></div>
<div class="card"><h2>Wasserhärte nach Gebiet</h2><div style="overflow-x:auto"><table><tr>{h}</tr>{rows}</table></div><p class="src">{e(o.get('hinweis',''))}</p></div>
<div class="card"><h2>Tipps für Ihren Härtebereich</h2>{tips}<p>Mehr dazu: <a href="../geschirrspueler-einstellen.html">Geschirrspüler richtig einstellen</a> · <a href="../wasserhaerte-erklaert.html">Was bedeutet °dH?</a></p></div>{AFF}"""
    page(f"orte/{o['slug']}.html", f"Wasserhärte {o['name']}: {fmt(lo)}–{fmt(hi)} °dH nach Gebiet ({o['bundesland']})",
         f"Aktuelle Wasserhärte in {o['name']} laut {o['versorger']}: {fmt(lo)} bis {fmt(hi)} °dH. Werte je Gebiet, Quelle & Tipps zu Entkalken und Waschmittel.", body, 1)

def main():
    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
    open(f"{OUT}/style.css","w").write(CSS); open(f"{OUT}/.nojekyll","w").write("")
    orte = [json.load(open(f)) for f in sorted(glob.glob("data/orte/*.json"))]
    for o in orte: ort(o)
    idx = "<h1>Wasserhärte in Österreich – nach Gemeinde und Bezirk</h1><p>Wie hart ist Ihr Leitungswasser? Hier finden Sie die Gesamthärte in °dH direkt aus den Veröffentlichungen der Wasserversorger – mit Quelle und Datum.</p>"
    for b in BL:
        lst = [o for o in orte if o["bundesland"] == b]
        if lst: idx += f"<div class='card'><h2>{b}</h2><ul class='orte'>" + "".join(f"<li><a href='orte/{o['slug']}.html'>{e(o['name'])}</a> – {str(o['min_dh']).replace('.',',')}–{str(o['max_dh']).replace('.',',')} °dH</li>" for o in lst) + "</ul></div>"
    idx += "<div class='card'><h2>Ratgeber</h2><ul><li><a href='wasserhaerte-erklaert.html'>°dH und Härtebereiche erklärt</a></li><li><a href='geschirrspueler-einstellen.html'>Geschirrspüler nach Wasserhärte einstellen</a></li></ul></div>"
    page("index.html", "Wasserhärte Österreich – Werte nach Gemeinde & Bezirk (°dH)", "Wasserhärte in Wien, Tirol, Salzburg, Linz & mehr: offizielle °dH-Werte der Wasserversorger mit Quelle, plus Tipps für Geschirrspüler und Waschmittel.", idx, 0)
    page("wasserhaerte-erklaert.html","Wasserhärte erklärt: °dH, mmol/l und Härtebereiche in Österreich","Was bedeutet °dH? Härtestufen I–III nach ÖVGW, Härtebereiche für Waschmittel und Umrechnung in mmol/l – einfach erklärt.", """<h1>Wasserhärte erklärt: °dH und Härtebereiche</h1>
<div class="card"><p>Die <b>Gesamthärte</b> gibt an, wie viel gelöstes Calcium und Magnesium im Wasser ist. In Österreich wird sie meist in <b>Grad deutscher Härte (°dH)</b> angegeben. Umrechnung: <b>1 mmol/l = 5,6 °dH</b>; 1 °dH ≈ 1,78 °fH.</p>
<p>Die <b>Carbonathärte</b> ist der Anteil, der an Kohlensäure gebunden ist – sie fällt beim Erhitzen als Kalk aus.</p></div>
<div class="card"><h2>Härtestufen in Österreich (ÖVGW)</h2><table><tr><th>Stufe</th><th>°dH</th><th>Bezeichnung</th></tr><tr><td>I</td><td>0–10</td><td>weich</td></tr><tr><td>II</td><td>10–16</td><td>mittel</td></tr><tr><td>III</td><td>über 16</td><td>hart</td></tr></table>
<p class="src">So verwenden es z. B. Wiener Wasser, IKB und LINZ AG (laut LINZ AG „lt. ÖVGW“). Quellen: <a href="https://www.wien.gv.at/umwelt/trinkwasser-wasserhaerte">wien.gv.at</a>, <a href="https://www.linzag.at/media/dokumente/wasser_2/trinkwasseruntersuchungen/wasserguete-maerz-april2026.pdf">LINZ AG</a>, abgerufen 2026-10-21.</p></div>
<div class="card"><h2>Härtebereiche für Waschmittel (deutsches Waschmittelgesetz)</h2><table><tr><th>Bereich</th><th>°dH</th><th>mmol/l</th></tr><tr><td>weich</td><td>unter 8,4</td><td>unter 1,5</td></tr><tr><td>mittel</td><td>8,4–14</td><td>1,5–2,5</td></tr><tr><td>hart</td><td>über 14</td><td>über 2,5</td></tr></table>
<p>Auf Waschmittelpackungen in Österreich steht meist diese Einteilung. Sie ist <b>nicht identisch</b> mit den ÖVGW-Stufen – ein Wert von 15 °dH ist z. B. ÖVGW „mittel“, beim Waschmittel aber schon „hart“.</p><p class="src">Diese Einteilung nutzen z. B. die Stadtwerke Schwaz (<a href="https://www.stadtwerkeschwaz.at/pdfs/Flyer%20Qualit%C3%A4t%20des%20Schwazer%20Trinkwassers.pdf">Flyer</a>).</p></div>"""+AFF, 0)
    page("geschirrspueler-einstellen.html","Geschirrspüler richtig einstellen nach Wasserhärte – Anleitung","So stellen Sie den Enthärter Ihres Geschirrspülers auf die Wasserhärte Ihrer Gemeinde ein: °dH finden, Stufe wählen, Salz nachfüllen.", """<h1>Geschirrspüler richtig einstellen nach Wasserhärte</h1>
<div class="card"><p>Jeder Geschirrspüler hat einen eingebauten Enthärter (Ionenaustauscher), der mit Regeneriersalz arbeitet. Ist er zu niedrig eingestellt, gibt es Kalkflecken und Ablagerungen; zu hoch kostet unnötig Salz.</p>
<ol><li><b>Härte herausfinden:</b> Suchen Sie Ihre Gemeinde in unserem <a href="index.html">Verzeichnis</a> oder fragen Sie Ihren Wasserversorger. Bei einer Spanne den höheren Wert nehmen.</li>
<li><b>Einheit prüfen:</b> Manche Hersteller verwenden mmol/l statt °dH (1 mmol/l = 5,6 °dH).</li>
<li><b>Stufe einstellen:</b> Im Menü (oft „H“ oder „Wasserhärte“, Tastenkombination laut Bedienungsanleitung) die Stufe wählen, die Ihrem °dH-Bereich entspricht. Die Zuordnung Stufe ↔ °dH ist <b>herstellerspezifisch</b> – sie steht in der Anleitung.</li>
<li><b>Salz nachfüllen</b>, sobald die Salzanzeige leuchtet. Bei sehr weichem Wasser kann der Enthärter teilweise ganz abgeschaltet werden (laut Anleitung).</li>
<li><b>Tabs mit „Salzfunktion“</b> ersetzen den Enthärter meist nur bei weichem bis mittlerem Wasser – bei hartem Wasser trotzdem Salz verwenden.</li></ol>
<p>Tipp aus Wien: Wiener Wasser empfiehlt für Haushaltsgeräte generell die Einstellung &lt;10 °dH (<a href="https://www.wien.gv.at/umwelt/trinkwasser-wasserhaerte">Quelle</a>, abgerufen 2026-10-21).</p></div>"""+AFF.replace("Entkalker auf Amazon","Entkalker auf Amazon").replace(amz('Duschfilter Kalk'),amz('Regeneriersalz Geschirrspüler')).replace("Duschfilter auf Amazon","Regeneriersalz auf Amazon"), 0)
    page("impressum.html","Impressum","Impressum und Datenschutz","""<h1>Impressum</h1><div class="card"><p><b>[PLATZHALTER – vor Veröffentlichung ausfüllen, Offenlegung nach § 25 MedienG / § 5 ECG]</b></p><p>Medieninhaber: [Name]<br>Anschrift: [Adresse]<br>E-Mail: [E-Mail]</p><h2>Datenschutz</h2><p>[PLATZHALTER] Diese Seite setzt keine Cookies und kein Tracking. Beim Klick auf Amazon-Links gelten die Datenschutzbestimmungen von Amazon.</p></div>""",0)
    urls = ["index.html","wasserhaerte-erklaert.html","geschirrspueler-einstellen.html"]+[f"orte/{o['slug']}.html" for o in orte]
    open(f"{OUT}/sitemap.txt","w").write("\n".join("https://BENUTZERNAME.github.io/REPO/"+u for u in urls)+"\n")
    print(f"{len(orte)} Ortsseiten, {len(urls)} Seiten gesamt -> {OUT}/")
if __name__ == "__main__": main()
