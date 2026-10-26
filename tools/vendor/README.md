# Kompakte Offline-Laufzeit

Diese Archive sind Laufzeitdateien, keine Installationscaches. `tools/bootstrap.py`
prüft ihre SHA-256-Werte und entpackt sie mit der Python-Standardbibliothek nach
`test/scratch/`. Rendern und Prüfen benötigen weder Netzwerk noch Paketmanager.
Zielplattform: Linux x86_64, CPython 3.12, glibc und zlib.

## Pillow

`pillow-runtime.tar.xz` stammt aus dem offiziellen Pillow-11.3.0-Wheel für
CPython 3.12 / manylinux x86_64. Enthalten sind die Python-Module, `_imaging`,
`_imagingft`, deren Bibliotheken, Metadaten und sämtliche ursprünglichen
Lizenztexte. Entfernt wurden ausschließlich unbenutzte Erweiterungsmodule für
AVIF, WebP, Farbmanagement, Tk, Bildarithmetik und Morphologie sowie die nicht
benötigten AVIF-/WebP-/LCMS-Bibliotheken. PNG, RGB-Zeichnen, Alpha-Compositing,
FreeType und variable Schriften bleiben verfügbar. Es handelt sich um einen
für diesen Film zugeschnittenen Laufzeitausschnitt, nicht um ein vollständiges
Pillow-Paket für beliebige Anwendungen.

Ursprüngliches Wheel:
`pillow-11.3.0-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl`

SHA-256 des ursprünglichen Wheels:
`676b2815362456b5b3216b4fd5bd89d362100dc6f4945154ff172e206a22c024`

## FFmpeg und ffprobe

`ffmpeg-runtime.tar.xz` enthält die eigens gebauten, gestrippten Werkzeuge
FFmpeg/ffprobe 7.0.2 mit statisch eingebundenem x264 und zlib sowie deren
Lizenztexte. Die ursprüngliche allgemeine FFmpeg-Distribution mit zahlreichen
anderen Codecs, Dokumentation und Modellen wird nicht zusätzlich ausgeliefert.

Die Quell-URLs und SHA-256-Werte der beim Bau verwendeten Archive stehen in
`build-sources.json`. NASM und pkgconf dienen ausschließlich dem Werkzeugbau
und sind für Rendern und Prüfung nicht erforderlich. Der Bau verwendet GCC
und Make. zlib wird mit `--static` gebaut; x264 mit `--enable-static
--disable-cli --disable-opencl --enable-pic`.

Die FFmpeg-Auswahl aktiviert H.264/AAC, PNG/RGB, MP4, lokale Dateien und Pipes,
die stille Audioquelle, Skalierung, Frameauswahl und Audiostatistik. Netzwerk,
andere Codecs und Dokumentation sind deaktiviert. Der genaue Configure-Aufruf
ist im Archiv als `BUILD.txt` enthalten. Beide Werkzeuge werden mit `strip`
verkleinert und gemeinsam mit `tarfile` / XZ-Preset 9 archiviert.

Das Video wurde ursprünglich mit FFmpeg 7.0.2 aus der allgemeinen statischen
Distribution erstellt. Die kompakte Laufzeit dient derselben Render- und
Prüfpipeline; das mitgelieferte Video bleibt unabhängig von diesen Werkzeugen
direkt abspielbar.
