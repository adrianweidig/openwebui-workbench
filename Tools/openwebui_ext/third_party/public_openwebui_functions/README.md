# Public OpenWebUI Function Exports

Diese JSON-Dateien sind unveränderte öffentliche OpenWebUI-Function-Exports aus `C:\Users\adrian.TOP\Downloads\öffentliche functions`.

Die produktiven Kopien liegen unter `Tools/openwebui_ext/filters/` oder künftig unter passenden Function-Unterordnern und wurden für Air-Gap-Betrieb geprüft.

- `markdown_normalizer.json` -> `Tools/openwebui_ext/filters/markdown_normalizer.py`

Der Original-Export deklariert `type: action`, enthält aber eine `Filter`-Klasse mit `outlet`-Hook. Die produktive Repo-Version wird deshalb als Filter behandelt.
