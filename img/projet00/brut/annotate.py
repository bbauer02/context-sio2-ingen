"""Annote les captures du Projet 00 : cadres, etiquettes et fleches rouges.
Usage : python -I annotate.py <dossier brut> <dossier sortie>
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

RED = (214, 40, 40)
WHITE = (255, 255, 255)
FONT = "C:/Windows/Fonts/segoeuib.ttf"

# Chaque capture : band = hauteur d'un bandeau blanc ajoute en bas (0 = aucun)
# boxes = cadres (x0, y0, x1, y1) ; tags = etiquettes (x, y, largeur max, texte, cible ou None)
SPEC = {
    "01-topologie-pt.png": dict(size=22, band=0, boxes=[], tags=[
        (660, 150, 420, "Transit VLAN 300 · G0/0 ↔ F0/7", (632, 175)),
        (110, 175, 260, "VLAN 10 · F0/4", (360, 266)),
        (40, 380, 260, "VLAN 200 · F0/1", (420, 402)),
        (860, 290, 560, "Trunk 802.1Q · câble croisé · F0/5 ↔ F0/1", (850, 392)),
        (690, 600, 230, "VLAN 30 · F0/2", (995, 628)),
        (1250, 545, 230, "VLAN 70 · F0/3", (1228, 630)),
    ]),
    "02-t1-ipconfig.png": dict(size=19, band=0, boxes=[
        (488, 196, 645, 222), (488, 271, 632, 297), (488, 296, 656, 322), (488, 396, 656, 422),
    ], tags=[
        (700, 180, 420, "Bail obtenu : 1re adresse du pool VLAN10-ADMIN", (645, 209)),
        (700, 250, 420, "Passerelle = SVI Vlan10 du cœur", (632, 284)),
        (700, 302, 420, "Serveur DHCP dans un autre VLAN (200)", (656, 309)),
        (700, 395, 420, "DNS = NUB-DC01", (656, 409)),
    ]),
    "03-t3-t8-ping.png": dict(size=20, band=0, boxes=[
        (10, 100, 672, 200), (10, 450, 696, 550),
    ], tags=[
        (780, 110, 450, "T3 : quatre réponses du serveur (VLAN 200)", (672, 150)),
        (780, 440, 460, "T8 : refusé. C'est la passerelle 10.10.10.1 qui répond « unreachable », pas le poste visé", (696, 500)),
    ]),
    "04-core-vlan-brief.png": dict(size=18, band=0, boxes=[
        (650, 104, 722, 130), (28, 255, 612, 305),
    ], tags=[
        (735, 6, 385, "F0/6 : déclaré en trunk mais sans câble, il reste affiché dans le VLAN 1", (700, 104)),
        (660, 400, 450, "VLAN 30 et 70 : aucun port d'accès, ils arrivent par le trunk F0/5, absent de la liste", (612, 290)),
    ]),
    "05-core-svi.png": dict(size=16, band=0, boxes=[
        (26, 60, 1022, 85), (26, 185, 1000, 210),
    ], tags=[
        (1040, 25, 290, "Vlan1 éteinte volontairement (shutdown)", (1022, 72)),
        (1040, 140, 290, "Vlan300 up/up : le trunk F0/5 porte aussi le VLAN 300", (1000, 197)),
    ]),
    "06-gw-ip-route.png": dict(size=19, band=0, boxes=[
        (26, 230, 466, 256), (26, 296, 562, 347), (26, 380, 856, 430),
    ], tags=[
        (520, 222, 380, "Aucune route par défaut", (466, 243)),
        (640, 285, 560, "Deux routes de retour seulement : VLAN 10 et VLAN 200. Rien vers 10.10.30.0 ni 10.10.70.0", (562, 322)),
        (900, 392, 440, "Le transit, directement connecté", (856, 405)),
    ]),
    "07-dc01-dhcp.png": dict(size=19, band=90, boxes=[
        (800, 30, 870, 52), (300, 320, 480, 377), (14, 380, 1562, 408),
    ], tags=[
        (885, 28, 300, "Service DHCP sur On", (870, 41)),
        (470, 440, 520, "Passerelle du pool = adresse de la SVI qui relaie", (390, 377)),
        (1020, 440, 520, "serverPool : étendue par défaut, non créée par la fiche", (1200, 408)),
    ]),
    "08-a17-access-lists.png": dict(size=18, band=0, boxes=[
        (803, 80, 992, 105), (748, 130, 914, 155), (748, 180, 966, 205),
        (748, 205, 914, 230), (748, 230, 914, 255), (80, 105, 737, 130),
    ], tags=[
        (1015, 150, 310, "Compteurs : relier chacun aux essais qui l'ont fait bouger", (966, 192)),
        (1015, 103, 310, "Pas de compteur", (737, 117)),
        (1015, 250, 310, "Les refus ne sont jamais comptés", None),
    ]),
    "09-a13-web.png": dict(size=20, band=0, boxes=[
        (124, 16, 272, 44), (14, 146, 1560, 192), (14, 607, 436, 640),
    ], tags=[
        (330, 8, 640, "Requête HTTP ouverte depuis AUTOMATE-N3 (VLAN 70)", (272, 30)),
        (700, 230, 520, "Page de recette laissée par le prestataire", (900, 192)),
        (520, 600, 480, "La page annonce un autre service : FTP", (436, 623)),
    ]),
    "10-a16-telnet.png": dict(size=19, band=0, boxes=[
        (10, 54, 340, 80), (10, 154, 340, 180), (10, 104, 652, 130), (10, 204, 652, 230),
    ], tags=[
        (720, 30, 520, "Connexion Telnet (TCP 23) acceptée par l'équipement…", (340, 67)),
        (720, 150, 520, "… puis refermée aussitôt. Packet Tracer n'affiche pas le message « Password required » de l'IOS réel", (652, 217)),
    ]),
}


def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def arrow(draw, start, end, width=4):
    draw.line([start, end], fill=RED, width=width)
    ang = math.atan2(end[1] - start[1], end[0] - start[0])
    size = 14
    p1 = (end[0] - size * math.cos(ang - 0.45), end[1] - size * math.sin(ang - 0.45))
    p2 = (end[0] - size * math.cos(ang + 0.45), end[1] - size * math.sin(ang + 0.45))
    draw.polygon([end, p1, p2], fill=RED)


def nearest_edge(rect, target):
    x0, y0, x1, y1 = rect
    return (min(max(target[0], x0), x1), min(max(target[1], y0), y1))


def render(src, dst, spec):
    im = Image.open(src).convert("RGB")
    if spec["band"]:
        big = Image.new("RGB", (im.width, im.height + spec["band"]), WHITE)
        big.paste(im, (0, 0))
        im = big
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT, spec["size"])
    for b in spec["boxes"]:
        draw.rectangle(b, outline=RED, width=4)
    pad = 7
    line_h = spec["size"] + 6
    for x, y, maxw, text, target in spec["tags"]:
        lines = wrap(draw, text, font, maxw - 2 * pad)
        w = max(draw.textlength(l, font=font) for l in lines) + 2 * pad
        h = len(lines) * line_h + 2 * pad - 4
        rect = (x, y, x + w, y + h)
        if target:
            arrow(draw, nearest_edge(rect, target), target)
        draw.rounded_rectangle(rect, radius=6, fill=RED)
        for i, l in enumerate(lines):
            draw.text((x + pad, y + pad - 2 + i * line_h), l, font=font, fill=WHITE)
    im.save(dst)


if __name__ == "__main__":
    src_dir, out_dir = sys.argv[1], sys.argv[2]
    for name, spec in SPEC.items():
        render(os.path.join(src_dir, name), os.path.join(out_dir, name), spec)
        print("ok", name)
