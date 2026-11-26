from pathlib import Path
root=Path(__file__).resolve().parent
s=(root/'index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(root/'style.css').read_text()+'</style>')
for name in ['assets.js','map.js','layout.js','engine.js']:
 s=s.replace(f'<script src="{name}"></script>','<script>'+(root/name).read_text()+'</script>')
(root/'kingdom-quest-kaykit.html').write_text(s)
