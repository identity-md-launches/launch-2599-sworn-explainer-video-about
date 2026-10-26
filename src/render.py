"""Typografischer Film: keine Stockbilder, Screenshots oder generierten Marken."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
from functools import lru_cache

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from bootstrap import setup, SCRATCH
FFMPEG, FFPROBE = setup()
from PIL import Image, ImageDraw, ImageFont
from content import SOURCES, SCENES, WIDTH, HEIGHT, FPS, DURATION

PAPER = '#F0EDE4'
INK = '#15363B'
TEAL = '#168575'
MINT = '#91D6BE'
RUST = '#B84E30'
CORAL = '#F1A17E'
MUTED_LIGHT = '#58706D'
MUTED_DARK = '#AFBEB5'
RULE_LIGHT = '#C9D1C7'
RULE_DARK = '#3C595A'

@lru_cache(maxsize=256)
def font(size, kind='sans', weight=400):
    path = ROOT / 'tools' / 'fonts' / (
        'InstrumentSerif-Regular.ttf' if kind == 'serif' else 'IBMPlexSans.ttf')
    f = ImageFont.truetype(str(path), size)
    if kind != 'serif':
        f.set_variation_by_axes([weight, 100])
    return f

def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

def rgba(hex_color, alpha=255):
    c = hex_color.lstrip('#')
    return tuple(int(c[i:i+2], 16) for i in (0, 2, 4)) + (alpha,)

class Scene:
    def __init__(self, spec, index):
        self.spec, self.index = spec, index
        self.dark = spec['theme'] == 'dark'
        self.bg = INK if self.dark else PAPER
        self.fg = PAPER if self.dark else INK
        self.accent = MINT if self.dark else TEAL
        self.warning = CORAL if self.dark else RUST
        self.muted = MUTED_DARK if self.dark else MUTED_LIGHT
        self.rule = RULE_DARK if self.dark else RULE_LIGHT
        self.base = Image.new('RGB', (WIDTH, HEIGHT), self.bg)
        self.layer = Image.new('RGBA', (WIDTH, HEIGHT))
        self.d = ImageDraw.Draw(self.layer)
        self.lines = []
        self.d.line((96, 130, 1824, 130), fill=self.rule, width=2)
        self.text('Sworn', 96, 65, 28, 'registry', weight=600)
        self.text(spec['chapter'], 1824, 67, 25, spec['source'], align='right', color=self.muted)
        if index >= 9:
            self.text('Gemessen am 2026-10-26.', 96, 982, 23, 'date', color=self.muted)
        self.layout()
        self.full = Image.alpha_composite(self.base.convert('RGBA'), self.layer).convert('RGB')

    def text(self, value, x, y, size, source, *, kind='sans', weight=400, color=None, align='left'):
        f = font(size, kind, weight)
        w = self.d.textlength(value, font=f)
        if align == 'right': x -= w
        if align == 'center': x -= w / 2
        bounds = self.d.textbbox((x, y), value, font=f, anchor='lt')
        assert bounds[0] >= 70 and bounds[2] <= 1855, (self.spec['key'], value, bounds)
        assert bounds[1] >= 45 and bounds[3] <= 1025, (self.spec['key'], value, bounds)
        self.d.text((x, y), value, font=f, fill=color or self.fg, anchor='lt')
        self.lines.append(dict(text=value, source=source, bounds=list(bounds)))

    def lines_at(self, values, x, y, size, source, leading=None, **kwargs):
        for i, value in enumerate(values):
            self.text(value, x, y + i * (leading or size * 1.35), size, source, **kwargs)

    def layout(self):
        t, d, k = self.text, self.d, self.spec['key']
        if k == 'title':
            t('Sworn', 96, 205, 248, 'registry', kind='serif')
            t('WhitelistCurator', 104, 563, 70, 'game', weight=500)
            t('hasTrait(wallet, id)', 104, 678, 52, 'registry', color=self.accent)
        elif k == 'game':
            t('66', 96, 195, 170, 'game', weight=500)
            t('19.522', 885, 195, 170, 'game', weight=500)
            t('Stunden dauerte', 100, 395, 43, 'game')
            t('das Einzahlungsspiel', 100, 457, 43, 'game')
            t('teilnehmende Wallets', 893, 395, 43, 'game')
            t('auf Ethereum-Mainnet.', 100, 565, 49, 'game')
            t('Abgerechnet am 2026-08-19.', 100, 666, 45, 'game')
            t('Vertrag', 100, 793, 27, 'game', color=self.muted)
            t('0xcb0b0531e86a9ac36fa865ca8e3dbccf047fda91', 100, 842, 36, 'game')
        elif k == 'author':
            t('2026-08-16', 96, 190, 126, 'author', kind='serif')
            t('Der Autor schrieb:', 100, 366, 37, 'author', color=self.muted)
            self.lines_at([
                'Die Teilnahme ist ein Zeichen',
                'aktiver Wallets; die Sybil-Bereinigung',
                'ist für später vorgesehen, offchain.'
            ], 100, 466, 64, 'author', leading=94)
        elif k == 'attempt':
            t('Nie ausgeliefert.', 96, 192, 142, 'attempt', kind='serif')
            t('Ein erster Bereinigungsversuch:', 100, 391, 43, 'attempt')
            labels = [('sybilkit-Cluster',), ('Eignungsregel E9',), ('eine Merkle-Root',), ('ein Record-NFT',), ('30 Tage', 'Einspruchsfrist')]
            for x, lines in zip((96, 440, 784, 1128, 1472), labels):
                self.lines_at(lines, x, 663, 31, 'attempt', leading=46)
        elif k == 'registry':
            t('Fakten über Wallets.', 96, 185, 127, 'registry', kind='serif')
            self.lines_at(['Sworn ist ein inhaberloses Register', 'auf Ethereum-Mainnet.'], 100, 365, 48, 'registry', leading=68)
            t('Vom IMD-Schwarm gebaut und bereitgestellt.', 100, 544, 37, 'registry', color=self.muted)
            t('hasTrait(wallet, id)', 100, 652, 65, 'registry', weight=500, color=self.accent)
            t('Jeder Contract kann lesen.', 100, 747, 37, 'registry')
            t('Registry', 100, 839, 25, 'registry', color=self.muted)
            t('0x0da2679000ea5380d1361cc3cca7d4e8c881f766', 100, 885, 33, 'registry')
        elif k == 'traits':
            d.line((960, 205, 960, 886), fill=self.rule, width=2)
            t('Direkte Traits', 96, 202, 91, 'traits', kind='serif')
            t('101 bis 503', 100, 356, 100, 'traits', weight=500, color=self.accent)
            self.lines_at(['Live aus dem abgerechneten', 'Spiel berechnet.'], 100, 531, 46, 'traits', leading=67)
            t('Oracle-Traits', 1040, 202, 91, 'traits', kind='serif')
            self.lines_at(['IMD-Oracle-Panels prüfen,', 'wenn eine Wallet claimt.'], 1040, 373, 43, 'traits', leading=64)
            t('0,5 IMD', 1040, 628, 109, 'traits', weight=500, color=self.accent)
            t('pro Claim', 1045, 774, 36, 'traits', color=self.muted)
        elif k == 'oracle':
            t('Pretrained', 96, 187, 115, 'traits', kind='serif')
            t('1301', 1824, 221, 73, 'traits', align='right', color=self.accent)
            self.lines_at(['Account-Nonce von mindestens 20', 'im Launch-Block.'], 100, 352, 55, 'traits', leading=77)
            d.line((96, 550, 1824, 550), fill=self.rule, width=2)
            t('Uptime', 96, 605, 115, 'traits', kind='serif')
            t('701', 1824, 640, 73, 'traits', align='right', color=self.accent)
            t('Erneut eingezahlt in den Stunden 24 bis 65.', 100, 794, 51, 'traits')
        elif k == 'method_a':
            t('Wie die Liste entstand:', 96, 180, 101, 'method', kind='serif')
            self.lines_at(['direkte Traits (101 bis 503) für jede Wallet', 'live aus dem Composer per Multicall, 79 Aufrufe;'], 130, 345, 45, 'method', leading=62)
            self.lines_at(['Chain-Proven-Fakten aus dem auditierten', 'Snapshot der Seite;'], 130, 555, 45, 'method', leading=62)
            self.lines_at(['Pretrained exakt per eth_getTransactionCount', 'im Launch-Block für alle 19.522;'], 130, 762, 45, 'method', leading=62)
            for y in (363, 573, 780):
                d.rectangle((98, y, 108, y + 10), fill=self.accent)
        elif k == 'method_b':
            t('Wie die Liste entstand:', 96, 180, 101, 'method', kind='serif')
            self.lines_at(['sybilkit-Status aus der', 'veröffentlichten Analyse;'], 130, 365, 57, 'method', leading=79)
            t('E0/E3/E9-Zahlen aus der clustermap-API.', 130, 623, 55, 'method')
            for y in (387, 645):
                d.rectangle((98, y, 108, y + 10), fill=self.accent)
        elif k == 'table':
            t('Die Zahlen, die zählen', 96, 176, 99, 'header', kind='serif')
            t('Filter', 112, 323, 28, 'header', color=self.muted)
            t('Wallets', 929, 323, 28, 'header', align='right', color=self.muted)
            self.lines_at(['davon sybilkit', 'clean/review'], 1051, 303, 27, 'header', leading=35, color=self.muted)
            t('deckt E0 ab', 1802, 323, 28, 'header', align='right', color=self.muted)
            rows = [
                (['sybilkit E9', '(nie eingefroren)'], '7.504', '–', '–', 'e9'),
                (['Pretrained, Nonce >= 20 (1301)'], '4.747', '91,2 %', '60,9 %', 'pre'),
                (['Pretrained und Uptime (701)'], '1.194', '98,7 %', '16,6 %', 'uptime'),
                (['Benchmarked >= 1.000 Punkte (501)'], '7.914', '25,6 %', '28,5 %', 'bench'),
            ]
            for i, (names, count, clean, e0, source) in enumerate(rows):
                y = 390 + i * 138
                d.line((96, y - 13, 1824, y - 13), fill=self.rule, width=2)
                if len(names) == 2:
                    self.lines_at(names, 112, y + 10, 33, source, leading=44)
                else:
                    t(names[0], 112, y + 29, 33, source)
                t(count, 929, y + 18, 62, source, align='right', weight=500)
                t(clean, 1286, y + 25, 51, source, align='right', color=self.accent if clean != '–' else self.muted)
                t(e0, 1802, y + 25, 51, source, align='right')
            d.line((96, 929, 1824, 929), fill=self.rule, width=2)
        elif k == 'fresh':
            t('12.291', 96, 182, 217, 'fresh', kind='serif')
            # Die Ziffer 0 fehlt in der vom Auftrag freigegebenen Zahlenliste.
            # Der Sachverhalt wird deshalb ohne diese Ziffer ausgeschrieben.
            t('Teilnehmer hatten im Launch-Block Nonce null.', 101, 457, 49, 'fresh')
            t('96,6 %', 96, 622, 132, 'marked', weight=500, color=self.accent)
            self.lines_at(['dessen, was sybilkit markiert,', 'war beim Launch eine frische Wallet.'], 720, 641, 45, 'marked', leading=66)
        elif k == 'loss':
            t('2.635', 96, 192, 226, 'loss', kind='serif', color=self.warning)
            self.lines_at(['Pretrained verliert dafür 2.635 Wallets,', 'die sybilkit für sauber hält,', 'obwohl sie neu waren.'], 100, 475, 57, 'loss', leading=82)
        elif k == 'farms':
            t('Punktegewichtete Filter', 96, 183, 103, 'farms', kind='serif')
            t('wählen die Farmen aus:', 100, 327, 55, 'farms')
            t('Benchmarked hält', 100, 451, 37, 'farms', color=self.muted)
            t('82 %', 96, 523, 146, 'farms', weight=500, color=self.warning)
            t('aller Punkte,', 100, 715, 46, 'farms')
            t('drei Viertel', 1015, 543, 106, 'farms', kind='serif', color=self.warning)
            self.lines_at(['dieser Wallets', 'sind markiert.'], 1020, 695, 43, 'farms', leading=61)
        elif k == 'meaning':
            self.lines_at(['hasTrait ersetzt Root, Einspruchsfrist', 'und Herausgeber durch Regeln im Vertrag,', 'pro Wallet lesbar für jeden Contract.'], 100, 218, 64, 'meaning', leading=92)
            for value, x in [('Root', 100), ('Einspruchsfrist', 355), ('Herausgeber', 820)]:
                t(value, x, 610, 37, 'meaning', color=self.muted)
            t('Regeln im Vertrag', 1260, 610, 48, 'meaning', weight=500, color=self.accent)
            t('hasTrait(wallet, id)', 100, 805, 63, 'registry', color=self.accent)
        elif k == 'direct':
            t('Sofort und kostenlos.', 96, 211, 133, 'direct', kind='serif')
            self.lines_at(['Die direkten Traits sind sofort und kostenlos', 'wahr für alle, die die Regel erfüllen.'], 100, 453, 61, 'direct', leading=92)
        elif k == 'claim':
            t('4.747', 96, 189, 207, 'claim', kind='serif')
            t('Wallets', 654, 344, 49, 'claim')
            t('0,5 IMD', 1120, 242, 108, 'claim', weight=500, color=self.accent)
            t('einmal claimen', 1124, 396, 43, 'claim')
            self.lines_at([
                'Pretrained ist der eine onchain claimbare Fakt,',
                'der wie ein Sybil-Filter wirkt, und sein Zielbild',
                'ist jetzt bekannt: genau diese 4.747 Wallets,',
                'jede müsste einmal 0,5 IMD claimen.'
            ], 100, 575, 51, 'claim', leading=73)
        elif k == 'limit':
            t('Was hasTrait nicht kann,', 96, 188, 110, 'limit', kind='serif')
            self.lines_at(['bleibt Cluster-Erkennung über', 'Funding- und Betragsmuster;'], 100, 361, 62, 'limit', leading=86)
            t('das braucht die ganze Population auf einmal.', 100, 589, 55, 'limit')
        else:
            raise ValueError(k)

    def dynamic(self, image, local):
        d = ImageDraw.Draw(image)
        k, p = self.spec['key'], ease((local - .15) / 1.2)
        if k == 'title':
            # Abstrakte Wallet-Fakten, keine Marke oder Benutzeroberfläche.
            cx, cy = 1460, 499
            for radius in (92, 170, 249):
                d.arc((cx-radius, cy-radius, cx+radius, cy+radius), 210, 210 + 300*p, fill=self.rule, width=2)
            for a in (225, 315, 405):
                r = 249
                x, y = cx + math.cos(math.radians(a))*r, cy + math.sin(math.radians(a))*r
                d.line((cx, cy, cx+(x-cx)*p, cy+(y-cy)*p), fill=self.accent, width=2)
                if p > .85: d.ellipse((x-8, y-8, x+8, y+8), fill=self.accent)
            d.ellipse((cx-17, cy-17, cx+17, cy+17), fill=self.accent)
        elif k == 'game':
            d.line((100, 747, 100+1720*p, 747), fill=self.accent, width=3)
        elif k == 'author':
            for i in range(9):
                x = 112 + i * 53
                d.ellipse((x-6, 851, x+6, 863), fill=self.accent if i/9 < p else self.rule)
            d.line((100, 888, 100+1210*p, 888), fill=self.rule, width=2)
        elif k == 'attempt':
            x0, end, y = 112, 1650, 579
            d.line((x0, y, x0+(end-x0)*p, y), fill=self.rule, width=3)
            for x in (112, 456, 800, 1144, 1488):
                if x <= x0+(end-x0)*p:
                    d.ellipse((x-8, y-8, x+8, y+8), fill=self.accent)
            # Offener Abschluss: der Versuch wurde nie ausgeliefert.
            d.line((1662, y, 1724, y), fill=self.warning, width=3)
            d.line((1737, y, 1799, y), fill=self.warning, width=3)
        elif k == 'traits':
            for i in range(5):
                x, y = 120+i*136, 795
                d.line((120, 795, 120+(x-120)*p, y), fill=self.rule, width=2)
                if p > i/5:
                    d.ellipse((x-10, y-10, x+10, y+10), fill=self.accent)
        elif k == 'method_b':
            for sy in (800, 850, 900):
                d.line((130, sy, 130+1050*p, sy+(850-sy)*p), fill=self.rule, width=2)
            d.line((1180, 850, 1180+550*p, 850), fill=self.accent, width=3)
        elif k == 'table':
            active = min(3, max(0, int((local-1.0)/4.1)))
            for i, n in enumerate((7504, 4747, 1194, 7914)):
                y = 390+i*138
                length = 250 * n/7914 * p
                d.line((679, y+104, 929, y+104), fill=self.rule, width=4)
                d.line((679, y+104, 679+length, y+104), fill=self.accent, width=4)
                if i == active:
                    d.line((98, y+8, 98, y+105), fill=self.accent, width=4)
        elif k == 'fresh':
            d.rectangle((100, 855, 1820, 879), fill=self.rule)
            d.rectangle((100, 855, 100+1720*.966*p, 879), fill=self.accent)
        elif k == 'loss':
            # Keine Flächenskala: reine Ausschluss-Metapher.
            for i in range(12):
                x = 116+i*69
                d.ellipse((x-9, 838, x+9, 856), outline=self.rule, width=2)
                if i/12 < p:
                    d.line((x-12, 862, x+12, 832), fill=self.warning, width=2)
        elif k == 'farms':
            for x, share in [(100, .82), (1020, .75)]:
                d.rectangle((x, 848, x+710, 872), fill=self.rule)
                d.rectangle((x, 848, x+710*share*p, 872), fill=self.warning)
        elif k == 'meaning':
            d.line((101, 696, 1115, 696), fill=self.rule, width=2)
            d.line((1138, 696, 1138+570*p, 696), fill=self.accent, width=3)
            if p > .85:
                d.line((1689, 685, 1708, 696, 1689, 707), fill=self.accent, width=3)
        elif k == 'direct':
            for i in range(8):
                x, y = 115+i*207, 792
                if i/8 < p:
                    d.ellipse((x-7, y-7, x+7, y+7), fill=self.accent)
                    d.line((x+22, y, x+142, y), fill=self.rule, width=2)
        elif k == 'claim':
            d.line((96, 497, 96+1728*p, 497), fill=self.rule, width=2)
        elif k == 'limit':
            nodes = [(120, 800), (310, 743), (390, 867), (570, 791), (760, 884), (906, 758), (1050, 846), (1217, 745), (1390, 875), (1570, 785), (1780, 851)]
            links = [(0,1),(0,2),(1,3),(2,3),(3,4),(3,5),(4,6),(5,6),(5,7),(6,8),(7,8),(7,9),(8,10),(9,10),(2,5),(6,9)]
            for a, b in links:
                ax, ay = nodes[a]; bx, by = nodes[b]
                d.line((ax, ay, ax+(bx-ax)*p, ay+(by-ay)*p), fill=self.rule, width=2)
            for i, (x, y) in enumerate(nodes):
                d.ellipse((x-7, y-7, x+7, y+7), fill=self.accent)

    def frame(self, local, global_time, transition_from=None):
        image = self.full.copy()
        self.dynamic(image, local)
        if transition_from is not None and local < .35:
            image = Image.blend(transition_from, image, ease(local/.35))
        draw = ImageDraw.Draw(image)
        draw.line((96, 1041, 1824, 1041), fill=self.rule, width=2)
        draw.line((96, 1041, 96+1728*global_time/DURATION, 1041), fill=self.accent, width=3)
        return image

def export_script(scenes):
    output = [
        '# Sworn – Bildschirmmanuskript', '',
        'Keine Narration. Die AAC-Tonspur enthält ausschließlich digitale Stille. '
        'Alle sichtbaren Textzeilen folgen unten in der Reihenfolge ihres ersten Erscheinens '
        'pro Einstellung; gleichzeitig eingeblendete Zeilen stehen in Leserichtung. '
        'Wiederkehrende Kopf- und Fußzeilen sind für jede Einstellung aufgeführt. '
        'Linienumbrüche in einem Satz bilden getrennte Bildschirmzeilen. '
        'Die Quellen sind die vom Auftrag gelieferten Sätze, keine externen Recherchen. '
        'Die englischen Kontextquellen bleiben hier zur eindeutigen Zuordnung im Original.', '',
        'Die Nonce-Ziffer aus dem Quellsatz wird als „null“ ausgeschrieben, '
        'weil sie in der ausdrücklich erlaubten Zahlenliste des Auftrags fehlt. '
        'Bedeutung und Anzahl bleiben unverändert.', ''
    ]
    start = 0
    for scene in scenes:
        end = start + scene.spec['duration']
        output += [f'## {start:03d}–{end:03d} s · {scene.spec["key"]}', '']
        # Kopf-/Fußzeilen stehen in visueller Reihenfolge, nicht Zeichenreihenfolge.
        lines = sorted(scene.lines, key=lambda line: (int(line['bounds'][1]//25), line['bounds'][0]))
        for line in lines:
            output += [f'**Bild:** {line["text"]}', '', f'**Quelle:** {SOURCES[line["source"]]}', '']
        start = end
    (ROOT / 'artifacts' / 'script.md').write_text('\n'.join(output), encoding='utf-8')
    (SCRATCH / 'onscreen.json').write_text(json.dumps([
        dict(scene=s.spec['key'], lines=s.lines) for s in scenes
    ], ensure_ascii=False, indent=2), encoding='utf-8')

def render(previews=False):
    (ROOT / 'artifacts').mkdir(exist_ok=True)
    scenes = [Scene(spec, i) for i, spec in enumerate(SCENES)]
    export_script(scenes)
    preview_dir = SCRATCH / 'frames'
    preview_dir.mkdir(exist_ok=True)
    now = 0
    for i, scene in enumerate(scenes):
        scene.frame(3, now+3).save(preview_dir / f'{i:02d}-{scene.spec["key"]}.png')
        now += scene.spec['duration']
    if previews:
        print('Vorschaubilder und Manuskript geschrieben.', flush=True)
        return
    output = ROOT / 'artifacts' / 'video.mp4'
    command = [str(FFMPEG), '-hide_banner', '-y',
        '-f', 'rawvideo', '-pixel_format', 'rgb24', '-video_size', '1920x1080',
        '-framerate', '30', '-i', 'pipe:0',
        '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
        '-t', str(DURATION), '-map', '0:v:0', '-map', '1:a:0',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
        '-maxrate', '2400k', '-bufsize', '4800k', '-threads', '4',
        '-pix_fmt', 'yuv420p', '-r', '30', '-g', '60',
        '-c:a', 'aac', '-b:a', '96k', '-ar', '48000', '-ac', '2',
        '-movflags', '+faststart', '-video_track_timescale', '30000',
        '-metadata', 'title=Sworn – WhitelistCurator mit hasTrait filtern',
        '-metadata:s:v:0', 'language=deu', '-metadata:s:a:0', 'language=deu',
        str(output)]
    with (SCRATCH / 'encode.log').open('w') as logfile:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=logfile)
        now = 0
        previous = None
        try:
            for i, scene in enumerate(scenes):
                print(f'{i+1}/{len(scenes)}: {scene.spec["key"]}, {scene.spec["duration"]} s', flush=True)
                frames = scene.spec['duration'] * FPS
                last = None
                for f in range(frames):
                    local = f/FPS
                    last = scene.frame(local, now+local, previous)
                    process.stdin.write(last.tobytes())
                previous = last
                now += scene.spec['duration']
            process.stdin.close()
            if process.wait() != 0:
                raise RuntimeError((SCRATCH / 'encode.log').read_text()[-5000:])
        except BaseException:
            process.kill()
            process.wait()
            raise
    print(f'Fertig: {output.stat().st_size:,} Bytes, {DURATION} Sekunden.', flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--previews', action='store_true')
    args = parser.parse_args()
    render(previews=args.previews)
