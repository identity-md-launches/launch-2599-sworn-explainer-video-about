# Sworn – Erklärvideo

Ein deutsches, ohne Ton verständliches Erklärvideo über WhitelistCurator und `hasTrait`. Die vier Lieferdateien entstehen unter `artifacts/` und bleiben ungetrackt.

```sh
python3 src/render.py
python3 tools/check.py
```

Das ergibt `video.mp4`, `poster.png`, `script.md` und `VIDEO.md`. Die letzte Datei enthält das tatsächliche ffprobe-Ergebnis und die Prüfungen. Die Fassung dauert 149 Sekunden, hat Full-HD-Auflösung mit 30 fps, H.264-Bild und eine stille AAC-Tonspur. Keine Musik und keine Narration.

Die benötigten Laufzeitdateien sind mitgeliefert. Es ist keine Installation und keine Netzwerkverbindung nötig. Erforderlich ist Linux x86_64 mit CPython 3.12, glibc und zlib. Die kompakten Abhängigkeiten werden mit SHA-256 geprüft und nach `test/scratch/` entpackt; ein leerer Scratch-Ordner ist zulässig. Der Check funktioniert auch direkt auf den vorhandenen Lieferdateien, ohne vorheriges Rendern.

`src/content.py` enthält Reihenfolge, Laufzeiten und Quellen. `src/render.py` enthält Satz, Animation und Encoding. `tools/check.py` prüft die tatsächlich gelieferten Bytes, extrahiert das Poster direkt aus dem Video und schreibt die technischen Notizen.

Die Schriften liegen samt SIL-OFL-Lizenzen in `tools/fonts/`. Die verkleinerten Pillow- und FFmpeg-Laufzeitarchive enthalten ihre Lizenztexte. Herkunft und Prüfsummen stehen in `tools/vendor/manifest.json`, Umfang und Bauhinweise in `tools/vendor/README.md`. Die vollständigen ursprünglichen Installationsarchive werden nicht zusätzlich mitgeliefert.

Der Quellsatz „Nonce 0“ wird wegen der abweichenden Liste erlaubter Bildschirmzahlen als „Nonce null“ gesetzt; das Manuskript dokumentiert den unveränderten Quellsatz.
