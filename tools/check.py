"""Prüft die ausgelieferten Bytes und erstellt die technischen Begleitnotizen."""
from pathlib import Path
import hashlib
import json
import re
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'src'))
from bootstrap import setup, SCRATCH
from content import SCENES, SOURCES, DURATION, FPS
FFMPEG, FFPROBE = setup()
from PIL import Image
from render import Scene

def run(args, **kwargs):
    result = subprocess.run([str(x) for x in args], cwd=ROOT, capture_output=True, **kwargs)
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf-8', errors='replace'))
    return result

def mp4_atoms(path):
    atoms = []
    with path.open('rb') as f:
        size = path.stat().st_size
        while f.tell() < size:
            start = f.tell()
            length, kind = struct.unpack('>I4s', f.read(8))
            if length == 1:
                length = struct.unpack('>Q', f.read(8))[0]
            if length == 0:
                length = size-start
            assert length >= 8
            atoms.append(kind.decode('ascii'))
            f.seek(start+length)
    return atoms

def check():
    output = ROOT / 'artifacts'
    video = output / 'video.mp4'
    probe_cmd = [FFPROBE, '-v', 'error', '-count_frames', '-show_entries',
        'format=format_name,duration,size,bit_rate:stream=index,codec_name,codec_type,profile,width,height,pix_fmt,r_frame_rate,avg_frame_rate,duration,nb_frames,nb_read_frames,sample_rate,channels,channel_layout:stream_tags=language',
        '-of', 'json', 'artifacts/video.mp4']
    result = run(probe_cmd)
    probe = json.loads(result.stdout)
    (SCRATCH / 'ffprobe.json').write_bytes(result.stdout)
    streams = probe['streams']
    v = next(s for s in streams if s['codec_type'] == 'video')
    a = next(s for s in streams if s['codec_type'] == 'audio')
    assert len(streams) == 2, streams
    assert v['codec_name'] == 'h264' and v['pix_fmt'] == 'yuv420p'
    assert (v['width'], v['height']) == (1920, 1080)
    assert v['avg_frame_rate'] == v['r_frame_rate'] == '30/1'
    assert int(v['nb_read_frames']) == DURATION*FPS == 4470
    assert float(probe['format']['duration']) == DURATION == 149
    assert a['codec_name'] == 'aac' and a['sample_rate'] == '48000' and a['channels'] == 2
    atoms = mp4_atoms(video)
    assert atoms.index('moov') < atoms.index('mdat'), atoms
    assert video.stat().st_size <= 64*1024*1024
    print('Codec, Bildrate, Laufzeit, Bildzahl, Audio und Faststart geprüft.', flush=True)

    # Vollständige Dekodierung beider Streams; -xerror macht einen Fehler fatal.
    decoded = run([FFMPEG, '-hide_banner', '-v', 'error', '-xerror', '-i',
        'artifacts/video.mp4', '-map', '0:v:0', '-map', '0:a:0', '-f', 'null', '-'])
    assert not decoded.stderr.strip(), decoded.stderr
    (SCRATCH / 'decode.log').write_bytes(decoded.stderr)
    print('Beide Streams vollständig und fehlerfrei dekodiert.', flush=True)

    # Ein tatsächliches, fertig komprimiertes Videobild, kein erneutes Rendering.
    poster_args = [FFMPEG, '-hide_banner', '-v', 'error', '-y', '-i', 'artifacts/video.mp4',
        '-vf', 'select=eq(n\\,2460)', '-frames:v', '1', '-fps_mode', 'vfr', 'artifacts/poster.png']
    run(poster_args)
    with Image.open(output / 'poster.png') as poster:
        assert poster.size == (1920, 1080) and poster.format == 'PNG'
        poster_pixels = poster.convert('RGB').tobytes()
    # Unabhängige zweite Dekodierung desselben Frames in rohe RGB-Bytes.
    decoded_frame = run([FFMPEG, '-hide_banner', '-v', 'error', '-ss', '82',
        '-i', 'artifacts/video.mp4', '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    assert hashlib.sha256(poster_pixels).digest() == hashlib.sha256(decoded_frame.stdout).digest()
    print('Poster ist pixelgleich zu Videoframe 2460 bei 82 Sekunden.', flush=True)

    audio = run([FFMPEG, '-hide_banner', '-v', 'info', '-i', 'artifacts/video.mp4',
        '-vn', '-af', 'astats=metadata=0:reset=0', '-f', 'null', '-'])
    stats = audio.stderr.decode('utf-8')
    assert 'Peak level dB: -inf' in stats and 'RMS level dB: -inf' in stats
    (SCRATCH / 'audio.log').write_text(stats)

    # Alle Quellenzuordnungen, sichtbaren Ziffern und Pflichtzeilen prüfen.
    onscreen = [dict(scene=spec['key'], lines=Scene(spec, i).lines)
                for i, spec in enumerate(SCENES)]
    assert len(onscreen) == len(SCENES)
    allowed = ['0xcb0b0531e86a9ac36fa865ca8e3dbccf047fda91',
        '0x0da2679000ea5380d1361cc3cca7d4e8c881f766',
        '101 bis 503', '79', '19.522', 'E0/E3/E9', 'E0', 'E3', 'E9',
        '7.504', '4.747', '91,2 %', '60,9 %', '1.194', '98,7 %', '16,6 %',
        '7.914', '25,6 %', '28,5 %', '12.291', '96,6 %', '2.635', '82 %',
        '0,5 IMD', '20', '1.000', '24 bis 65', '30 Tage', '1301', '701', '501',
        '66', '2026-08-16', '2026-08-19', '2026-10-26']
    script = (output / 'script.md').read_text()
    all_text = []
    for scene in onscreen:
        for line in scene['lines']:
            assert line['source'] in SOURCES
            assert '**Bild:** '+line['text'] in script
            assert '**Quelle:** '+SOURCES[line['source']] in script
            rest = line['text']
            for token in sorted(allowed, key=len, reverse=True):
                rest = rest.replace(token, '')
            assert not re.search(r'\d', rest), (scene['scene'], line['text'], rest)
            all_text.append(line['text'])
    joined = '\n'.join(all_text)
    by_scene = {s['scene']: s for s in onscreen}
    table = by_scene['table']['lines']
    expected_rows = {
        'e9': ['sybilkit E9', '(nie eingefroren)', '7.504', '–', '–'],
        'pre': ['Pretrained, Nonce >= 20 (1301)', '4.747', '91,2 %', '60,9 %'],
        'uptime': ['Pretrained und Uptime (701)', '1.194', '98,7 %', '16,6 %'],
        'bench': ['Benchmarked >= 1.000 Punkte (501)', '7.914', '25,6 %', '28,5 %'],
    }
    for source, expected in expected_rows.items():
        assert [line['text'] for line in table if line['source'] == source] == expected
    for source, key in [('loss', 'loss'), ('farms', 'farms'), ('direct', 'direct'), ('claim', 'claim'), ('limit', 'limit')]:
        visible = ' '.join(line['text'] for line in by_scene[key]['lines'] if line['source'] == source)
        assert SOURCES[source] in visible, (source, visible)
    method = []
    for key in ('method_a', 'method_b'):
        for line in by_scene[key]['lines']:
            if line['source'] == 'method' and not line['text'].startswith('Wie die Liste entstand'):
                method.append(line['text'])
    assert ' '.join(method) == SOURCES['method'].removeprefix('Wie die Liste entstand: ')
    visible = ' '.join(line['text'] for line in by_scene['fresh']['lines'] if line['source'] == 'marked')
    assert visible == SOURCES['marked']
    for text in ('sybilkit E9', 'Pretrained, Nonce >= 20 (1301)',
        'Pretrained und Uptime (701)', 'Benchmarked >= 1.000 Punkte (501)',
        'Was hasTrait nicht kann,', 'bleibt Cluster-Erkennung über',
        'Funding- und Betragsmuster;', 'das braucht die ganze Population auf einmal.'):
        assert text in joined, text
    assert sum(p.stat().st_size for p in output.iterdir() if p.is_file()) <= 128*1024*1024
    print('Zahlenliste, Quellennachweise und Pflichtaussagen geprüft.', flush=True)

    version_ffmpeg = run([FFMPEG, '-version']).stdout.decode().splitlines()[0]
    version_ffprobe = run([FFPROBE, '-version']).stdout.decode().splitlines()[0]
    notes = f'''# Sworn – Videodokumentation

## Gelieferte Fassung

- Datei: `artifacts/video.mp4`, MP4, H.264 High, YUV 4:2:0, 1920 × 1080, konstant 30 fps.
- Laufzeit: 149 Sekunden; 4.470 vollständig dekodierte Videoframes.
- Audio: AAC-LC, Stereo, 48 kHz. Absichtlich digitale Stille: keine Narration, keine Musik, keine Geräusche. Peak und RMS wurden als `-inf` bestätigt.
- Browserwiedergabe: H.264/AAC und vorangestelltes `moov`-Atom (`+faststart`).
- Videogröße: {video.stat().st_size:,} Bytes ({video.stat().st_size/1024/1024:.2f} MiB).
- Poster: PNG, 1920 × 1080, unverändertes dekodiertes Videoframe 2460 bei 82 Sekunden. Ein zweiter RGB-Export war pixelgleich.
- Bildschirmmanuskript: `artifacts/script.md`; jede sichtbare Zeile mit dem zugehörigen Satz der Aufgabenquelle. Es gibt keine gesprochenen Sätze.

## Gestaltung und Inhalt

Ruhige typografische Erklärung in Deutsch mit abstrakten Linien, Knoten und proportionalen Balken. Die Kennzahlen springen nicht durch Zwischenwerte. Alle Filterzeilen bleiben während der gesamten Tabelle sichtbar. Die Balken in der Wallets-Spalte teilen dieselbe lineare Skala; Prozentbalken zeigen jeweils den ausdrücklich daneben genannten Anteil. Dekorative Knoten bilden keine gemessenen Populationen ab.

Die Inhalte und Messwerte stammen vollständig aus dem Auftrag, Stand 2026-10-26. Es wurden keine neuen Daten abgefragt oder ergänzt. Kontextaussagen wurden ins Deutsche übersetzt; Fachnamen und die vorgegebenen Tabellenbezeichnungen bleiben erhalten. Keine Screenshots, fremden Logos, echten oder nachgeahmten Karten, Archivbilder oder generativ erzeugten Bildinhalte.

## Einschränkungen

Der Auftrag schreibt im Quellsatz „Nonce 0“, lässt die einzelne Ziffer 0 aber in seiner abschließenden Liste erlaubter Bildschirmzahlen aus. Im Film steht deshalb „Nonce null“. Dies ist die einzige bewusste Abweichung vom Wortlaut des deutschen Fließtexts; die Aussage bleibt dieselbe. Im Manuskript steht direkt darunter der unveränderte Quellsatz.

Die Fassung hat keine Sprecherstimme. Sämtliche Informationen sind ohne Ton verständlich; Untertitel als separate Spur sind nicht enthalten, weil der Text Teil des Bildes ist. Die gelieferten Fakten wurden nicht unabhängig auf der Blockchain überprüft.

## Werkzeuge und Reproduktion

- Python 3.12 und Pillow 11.3.0: Satz, Vektorelemente, Animation und RGB-Bildsequenz.
- {version_ffmpeg}
- {version_ffprobe}
- Das ursprüngliche Rendering erfolgte mit FFmpeg 7.0.2-static; die erneuten Datei- und Dekodierprüfungen verwenden die kompakte mitgelieferte Fassung derselben FFmpeg-Version. Der MP4-Bildinhalt wurde bei der Verkleinerung des Quellpakets nicht geändert.
- FFmpeg: `libx264`, CRF 19, Preset medium, YUV420p, 30 fps; AAC-Stereospur, `+faststart`.
- Schriften: IBM Plex Sans und Instrument Serif, mitgelieferte SIL-OFL-Lizenzen in `tools/fonts/`.
- Die benötigten Laufzeitdateien sind als normale Dateien in `tools/vendor/` und `tools/fonts/` enthalten. Die kompakten Archive enthalten Pillow mit den benötigten Bild-/Schriftbibliotheken sowie eigens für diesen Film gebautes FFmpeg/ffprobe. Herkunft, Umfang und Prüfsummen stehen in `tools/vendor/`. Keine Netzwerkverbindung zur Reproduktion erforderlich. Zielplattform: Linux x86_64, CPython 3.12 mit den üblichen Systembibliotheken (glibc und zlib).

Vom Repository-Hauptverzeichnis:

```sh
python3 src/render.py
python3 tools/check.py
```

Die Werkzeugarchive werden bei Bedarf nach `test/scratch/` entpackt. Dieser Ordner darf vor dem Build vollständig gelöscht werden. Das Rendern erstellt Video und Manuskript; die Prüfung kann auch direkt auf dem gelieferten Video ausgeführt werden, extrahiert das Poster und aktualisiert diese Dokumentation. Für Standbildvorschauen: `python3 src/render.py --previews`.

## Ausgeführte Prüfungen

- Vollständige Dekodierung des Video- und Audiostreams mit `ffmpeg -v error -xerror`: ohne Fehlermeldung, Exit-Code 0.
- Codec, Auflösung, konstante Bildrate, Bildzahl, Laufzeit, Audioprofil und Atomreihenfolge geprüft.
- Tatsächliches Posterframe pixelweise mit einer zweiten Dekodierung verglichen.
- Stille der gesamten AAC-Spur mit `astats` bestätigt.
- Alle Bildschirmzeilen auf erlaubte Ziffernfolgen und vorhandene Quellenzuordnung geprüft; vier Tabellenzeilen und vollständige Schlussaussage zur Cluster-Erkennung geprüft.
- Die unveränderte Renderpipeline wurde zusätzlich mit einem kurzen Testclip und frisch entpackter kompakter Laufzeit geprüft: H.264/AAC, Full HD und 30 fps erfolgreich.
- Gestaltung aller Einstellungen anhand von Vorschauen und dekodierten Videoframes visuell geprüft.

## ffprobe-Zusammenfassung

Aufruf mit dem mitgelieferten `ffprobe`:

```sh
ffprobe -v error -count_frames -show_entries format=format_name,duration,size,bit_rate:stream=index,codec_name,codec_type,profile,width,height,pix_fmt,r_frame_rate,avg_frame_rate,duration,nb_frames,nb_read_frames,sample_rate,channels,channel_layout:stream_tags=language -of json artifacts/video.mp4
```

```json
{json.dumps(probe, ensure_ascii=False, indent=2)}
```
'''
    (output / 'VIDEO.md').write_text(notes, encoding='utf-8')
    print('Alle Prüfungen bestanden; artifacts/VIDEO.md geschrieben.', flush=True)

if __name__ == '__main__':
    check()
