"""Mechanically extract existing source formulas and plot content for the deck.

This script never redraws source figures. Formula clips are PDF-point rectangles;
figure clips are pixel rectangles chosen from the published source layout.
"""
from pathlib import Path
import hashlib
import json
import argparse

import pymupdf
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "build" / "assets"
PDF = ROOT / "Note" / "single_magnon_derivation" / "main.pdf"

# page (one-based), equation, (left, top, right, bottom) in source PDF points.
FORMULAS = {
    "direct_exchange": (1, "2-3", (168, 290, 427, 351)),
    "coulomb_matrix": (2, "11", (201, 284, 394, 358)),
    "eigenstates": (2, "14", (221, 553, 375, 617)),
    "spin_matrix": (3, "17", (222, 94, 375, 182)),
    "heisenberg_pair": (3, "20", (215, 319, 380, 356)),
    "lattice_H": (3, "22", (172, 512, 423, 547)),
    "ground_energy": (3, "25", (242, 745, 354, 779)),
    "oneflip_state": (4, "26", (223, 143, 372, 162)),
    "bond_action": (4, "28", (221, 326, 375, 359)),
    "oneflip_action": (4, "29", (186, 400, 409, 445)),
    "lattice_eom": (5, "35", (183, 162, 413, 215)),
    "plane_wave": (5, "36", (221, 287, 375, 315)),
    "neighbors": (5, "37", (168, 373, 427, 396)),
    "dispersion_derivation": (5, "38", (149, 424, 446, 473)),
    "dispersion": (5, "39", (185, 504, 411, 526)),
    "fermi_exchange": (2, "9", (212, 165, 384, 190)),
    "spin_components": (2, "15", (144, 678, 452, 718)),
    "ferro_state": (3, "23", (247, 610, 351, 631)),
    "ground_energy_general": (3, "24", (204, 663, 394, 700)),
    "bond_matrix_action": (4, "27", (189, 231, 406, 302)),
    "state_expansion": (4, "30", (163, 525, 430, 558)),
    "general_eom": (5, "34", (215, 89, 382, 130)),
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def formula_assets():
    out = OUT / "formula"
    out.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(PDF)
    source_hash = digest(PDF)
    result = {}
    for key, (page, equation, bbox) in FORMULAS.items():
        path = out / f"{key}.png"
        pix = doc[page-1].get_pixmap(matrix=pymupdf.Matrix(5,5), clip=pymupdf.Rect(bbox), alpha=False)
        pix.save(path)
        result[key] = {"path":str(path), "source":str(PDF), "source_sha256":source_hash,
            "page":page, "equation":equation, "bbox_pdf_points":list(bbox),
            "width":pix.width, "height":pix.height, "dpi":360,
            "operation":"PDF clip rasterized on white; equation number excluded"}
    return result

def contact_sheet(entries, path, columns=3, thumb=(600,210)):
    rows = (len(entries)+columns-1)//columns
    sheet = Image.new("RGB", (columns*thumb[0],rows*(thumb[1]+28)), "#e8edf1")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf",16)
    for idx,(key,item) in enumerate(entries.items()):
        row,col=divmod(idx,columns)
        x,y=col*thumb[0],row*(thumb[1]+28)
        draw.text((x+10,y+5),key,fill="black",font=font)
        im=Image.open(item["path"]).convert("RGB")
        im.thumbnail((thumb[0]-20,thumb[1]-10),Image.Resampling.LANCZOS)
        sheet.paste(im,(x+(thumb[0]-im.width)//2,y+28+(thumb[1]-im.height)//2))
    sheet.save(path)

def figure_assets():
    out=OUT/"figures"
    out.mkdir(parents=True,exist_ok=True)
    base=ROOT/"figures"/"midterm-report"
    result={}
    for group in "abc":
        manifest=base/f"manifest_{group}.json"
        items=json.loads(manifest.read_text(encoding="utf-8"))["items"]
        for item in items:
            if "png" not in item["files"]:
                continue
            source=base/item["files"]["png"]
            im=Image.open(source).convert("RGB")
            w,h=im.size
            arr=np.asarray(im)
            # Heading/subtitle are blue-grey; plot headings and axes are black.
            # Locate the first dark plot pixel below the source subtitle band.
            first=int(.165*h)
            last=int(.91*h)
            ink=(arr[first:last].max(axis=2)<78)
            occupied=np.where(ink.any(axis=1))[0]
            dark_top=int(occupied[0])+first
            top=max(first,dark_top-6)
            # Large formula descenders in the grey subtitle occasionally reach
            # the six-pixel padding. Remove those residual rows mechanically.
            rgb=arr.astype(np.int16)
            grey=((rgb[:,:,2]>rgb[:,:,0]+10)&(rgb[:,:,1]>rgb[:,:,0]+5)
                  &(rgb[:,:,0]>60)&(rgb[:,:,0]<200))
            stray_rows=np.where(grey[top:dark_top].any(axis=1))[0]
            if len(stray_rows):
                top=top+int(stray_rows[-1])+1
            foot_start=int(.88*h)
            foot_rows=np.where(grey[foot_start:last].any(axis=1))[0]
            if len(foot_rows):
                last=foot_start+int(foot_rows[0])-2
            content=arr[top:last]
            nonwhite=content.min(axis=2)<245
            ys,xs=np.where(nonwhite)
            left=max(0,int(xs.min())-14)
            right=min(w,int(xs.max())+15)
            bottom=min(last,top+int(ys.max())+15)
            bbox=(left,top,right,bottom)
            cropped=ImageOps.expand(im.crop(bbox),border=(0,12,0,12),fill="white")
            path=out/(item["id"]+".png")
            cropped.save(path)
            result[item["id"]]={"path":str(path),"source":str(source),
                "source_sha256":digest(source),"source_size":[w,h],
                "bbox_pixels":list(bbox),"width":cropped.width,"height":cropped.height,
                "padding_pixels":[0,12,0,12],
                "title":item["title"],"caption":item["caption"],
                "operation":"Mechanical crop of original PNG; total heading and footer omitted",
                "manifest_source":str(manifest)}
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--formulas-only",action="store_true")
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    result={"formula":formula_assets(),"figures":{},"dimensions":{}}
    contact_sheet(result["formula"],OUT/"formula-contact.png")
    if not args.formulas_only:
        result["figures"]=figure_assets()
        for group in "abc":
            selected={k:v for k,v in result["figures"].items() if k.startswith(group)}
            contact_sheet(selected,OUT/f"figures-{group}-contact.png",columns=2,thumb=(880,430))
    for kind in ("formula","figures"):
        result["dimensions"].update({k:[v["width"],v["height"]] for k,v in result[kind].items()})
    (HERE/"assets.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"formulas":len(result["formula"]),"figures":len(result["figures"]),"manifest":str(HERE/"assets.json")}))

if __name__ == "__main__":
    main()
