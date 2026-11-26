from pathlib import Path
import base64,json
root=Path(__file__).resolve().parent
E=json.loads((root/'environment.json').read_text());E['models']=[p.stem for p in (root/'assets').glob('*.gltf')];E.pop('placements');img=base64.b64encode((root/'screenshots/01-environment.jpg').read_bytes()).decode();(root/'environment.js').write_text('window.ENVIRONMENT='+json.dumps(E,separators=(',',':'))+';window.ENV_DATA="data:image/jpeg;base64,'+img+'";')
s=(root/'index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(root/'style.css').read_text()+'</style>')
for n in ['environment.js','map.js','layout.js','engine.js']:s=s.replace(f'<script src="{n}"></script>','<script>'+(root/n).read_text()+'</script>')
(root/'kingdom-quest-environment.html').write_text(s)
