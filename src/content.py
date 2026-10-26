"""Redaktion, Quellen und unveränderliche Bildschirmtexte."""

SOURCES = {
    'title': 'Sworn, an explainer video about filtering the WhitelistCurator participants with the registry\'s hasTrait.',
    'game': 'WhitelistCurator was a 66-hour deposit game on Ethereum mainnet (contract 0xcb0b0531e86a9ac36fa865ca8e3dbccf047fda91, settled 2026-08-19) with 19,522 participating wallets.',
    'author': 'Its author wrote on 2026-08-16 that participation is a sign of live wallets and that sybil cleaning is for later, offchain.',
    'attempt': 'A first attempt at that cleaning (sybilkit clusters, an eligibility policy called E9, one Merkle root, a record NFT, a 30-day dispute window) never shipped.',
    'registry': 'Sworn is an ownerless registry of facts about wallets on Ethereum mainnet (Registry 0x0da2679000ea5380d1361cc3cca7d4e8c881f766, built and deployed by the IMD swarm); any contract reads hasTrait(wallet, id).',
    'traits': 'Direct traits (ids 101 to 503) are computed live from the settled game; oracle traits such as Pretrained (1301, account nonce of at least 20 at the launch block) and Uptime (701, deposited again in hours 24 to 65) are verified by IMD oracle panels when a wallet claims them for 0.5 IMD.',
    'date': 'The numbers below were measured on 2026-10-26.',
    'method': 'Wie die Liste entstand: direkte Traits (101 bis 503) für jede Wallet live aus dem Composer per Multicall, 79 Aufrufe; Chain-Proven-Fakten aus dem auditierten Snapshot der Seite; Pretrained exakt per eth_getTransactionCount im Launch-Block für alle 19.522; sybilkit-Status aus der veröffentlichten Analyse; E0/E3/E9-Zahlen aus der clustermap-API.',
    'header': 'Die Zahlen, die zählen (Filter | Wallets | davon sybilkit clean/review | deckt E0 ab):',
    'e9': 'sybilkit E9 (nie eingefroren) | 7.504 | – | –',
    'pre': 'Pretrained, Nonce >= 20 (1301) | 4.747 | 91,2 % | 60,9 %',
    'uptime': 'Pretrained und Uptime (701) | 1.194 | 98,7 % | 16,6 %',
    'bench': 'Benchmarked >= 1.000 Punkte (501) | 7.914 | 25,6 % | 28,5 %',
    'fresh': '12.291 Teilnehmer hatten im Launch-Block Nonce 0.',
    'marked': '96,6 % dessen, was sybilkit markiert, war beim Launch eine frische Wallet.',
    'loss': 'Pretrained verliert dafür 2.635 Wallets, die sybilkit für sauber hält, obwohl sie neu waren.',
    'farms': 'Punktegewichtete Filter wählen die Farmen aus: Benchmarked hält 82 % aller Punkte, drei Viertel dieser Wallets sind markiert.',
    'meaning': 'Was das heißt: hasTrait ersetzt Root, Einspruchsfrist und Herausgeber durch Regeln im Vertrag, pro Wallet lesbar für jeden Contract.',
    'direct': 'Die direkten Traits sind sofort und kostenlos wahr für alle, die die Regel erfüllen.',
    'claim': 'Pretrained ist der eine onchain claimbare Fakt, der wie ein Sybil-Filter wirkt, und sein Zielbild ist jetzt bekannt: genau diese 4.747 Wallets, jede müsste einmal 0,5 IMD claimen.',
    'limit': 'Was hasTrait nicht kann, bleibt Cluster-Erkennung über Funding- und Betragsmuster; das braucht die ganze Population auf einmal.',
}

# Sekunden sind Produktionsdaten und erscheinen niemals im Bild.
SCENES = [
    dict(key='title', duration=3, chapter='Sworn', source='title', theme='dark'),
    dict(key='game', duration=8, chapter='WhitelistCurator', source='game', theme='light'),
    dict(key='author', duration=7, chapter='WhitelistCurator', source='game', theme='light'),
    dict(key='attempt', duration=7, chapter='WhitelistCurator', source='game', theme='dark'),
    dict(key='registry', duration=9, chapter='Sworn', source='registry', theme='light'),
    dict(key='traits', duration=8, chapter='Sworn', source='registry', theme='dark'),
    dict(key='oracle', duration=8, chapter='Sworn', source='registry', theme='dark'),
    dict(key='method_a', duration=13, chapter='Wie die Liste entstand', source='method', theme='light'),
    dict(key='method_b', duration=6, chapter='Wie die Liste entstand', source='method', theme='light'),
    dict(key='table', duration=18, chapter='Die Zahlen, die zählen', source='header', theme='dark'),
    dict(key='fresh', duration=9, chapter='Die Zahlen, die zählen', source='header', theme='light'),
    dict(key='loss', duration=7, chapter='Die Zahlen, die zählen', source='header', theme='light'),
    dict(key='farms', duration=9, chapter='Die Zahlen, die zählen', source='header', theme='dark'),
    dict(key='meaning', duration=10, chapter='Was das heißt', source='meaning', theme='light'),
    dict(key='direct', duration=7, chapter='Was das heißt', source='meaning', theme='light'),
    dict(key='claim', duration=12, chapter='Was das heißt', source='meaning', theme='dark'),
    dict(key='limit', duration=8, chapter='Was das heißt', source='meaning', theme='dark'),
]

FPS = 30
WIDTH, HEIGHT = 1920, 1080
DURATION = sum(s['duration'] for s in SCENES)
