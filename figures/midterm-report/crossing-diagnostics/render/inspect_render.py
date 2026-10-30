"""Inspect crossing-case rendering without altering published animations.

Run from any directory with the existing project Python environment.
Controls reuse the actual animation source and stored initial states.
"""
from pathlib import Path
import importlib.util
import json
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "notation" / "generate_lab_animations.py"
SELECTED = [0, 2, 3, 5, 8, 10]
HERE.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("lab_diagnostic", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Execute the current plotting function with selected physical frame indices.
# Remove its export tail so no existing artifacts can be overwritten.
src = SOURCE.read_text(encoding="utf-8")
src = src[src.index("def animation(real):"):src.index("\nif __name__")]
src = src[:src.index("    durations=")]
src = src.replace("dpi=120", "dpi=DIAGNOSTIC_DPI")
src = src.replace("    frames=[];checks=[]", "    frames=[];checks=[];rgb_frames=[]")
src = src.replace(
    "for index,t in enumerate(np.linspace(0,180,61)):",
    "for index,t in [(i,3.0*i) for i in SELECTED]:",
)
src = src.replace(
    "        if index in [0,30,60]:Image.fromarray(pixels.copy()).save(OUT/f'{key}-frame{index:02d}.png')",
    "        rgb_frames.append(Image.fromarray(pixels.copy()))",
)
src += """
    boxes = [list(ax.get_window_extent().bounds) for ax in axs]
    module_plt = plt
    module_plt.close(fig)
    return rgb_frames, frames, boxes
"""


def run_control(dpi):
    ns = dict(module.__dict__)
    ns.update(DIAGNOSTIC_DPI=dpi, SELECTED=SELECTED)
    exec(compile(src, str(SOURCE) + ":diagnostic", "exec"), ns)
    return ns["animation"](True)


def box_pixels(box, height):
    x, y, w, h = box
    return (int(round(x)), int(round(height-y-h)),
            int(round(x+w)), int(round(height-y)))


rgb120, pal120, boxes120 = run_control(120)
rgb360, pal360, boxes360 = run_control(360)
original = Image.open(ROOT / "notation" / "g15_lab_real_animation.gif")
rows = []
panels = []
for idx, a, p, b in zip(SELECTED, rgb120, pal120, rgb360):
    original.seek(idx)
    orig = original.convert("RGB")
    ar = np.asarray(a, dtype=float)
    pr = np.asarray(p.convert("RGB"), dtype=float)
    orr = np.asarray(orig, dtype=float)
    cbox = box_pixels(boxes120[2], a.height)
    bbox = box_pixels(boxes360[2], b.height)
    x0,y0,x1,y1 = cbox
    # Exclude inset, axes, and labels; use the lower two-thirds of C's plot.
    cy0 = int(y0 + .48 * (y1-y0))
    roi = (slice(cy0,y1-3), slice(x0+3,x1-3))
    center = module.data["C_eta1"]["track"]["cx"][idx]
    # Fixed physical square of half-width 18a centered on the packet.
    px = x0 + (center + 35) * (x1-x0) / 260
    py = y1 - (center + 35) * (y1-y0) / 260
    rr = 18 * (x1-x0) / 260
    packet = (slice(round(py-rr),round(py+rr)),
              slice(round(px-rr),round(px+rr)))
    bx0,by0,bx1,by1 = bbox
    bpx = bx0 + (center+35)*(bx1-bx0)/260
    bpy = by1 - (center+35)*(by1-by0)/260
    brr = 18*(bx1-bx0)/260
    packet_hi = (slice(round(bpy-brr),round(bpy+brr)),
                 slice(round(bpx-brr),round(bpx+brr)))
    br = np.asarray(b, dtype=float)
    chroma = lambda v: float(np.mean(np.max(v,axis=-1)-np.min(v,axis=-1)))
    rows.append(dict(
        frame=idx,t=3*idx,
        reconstructed_gif_original_max_abs_rgb_error=float(np.max(abs(pr-orr))),
        palette_full_max_abs_rgb_error=float(np.max(abs(pr-ar))),
        palette_full_mean_abs_rgb_error=float(np.mean(abs(pr-ar))),
        palette_c_lower_mean_abs_rgb_error=float(np.mean(abs(pr[roi]-ar[roi]))),
        palette_packet_mean_abs_rgb_error=float(np.mean(abs(pr[packet]-ar[packet]))),
        packet_rgb_mean_chroma_255=chroma(ar[packet]),
        packet_palette_mean_chroma_255=chroma(pr[packet]),
        packet_highres_mean_chroma_255=chroma(br[packet_hi]),
        c_main_box_pixels=cbox,
    ))
    orig.crop(cbox).save(HERE / f"original_C_frame{idx:02d}.png")
    a.crop(cbox).save(HERE / f"rgb_C_frame{idx:02d}.png")
    b.crop(bbox).save(HERE / f"highres_C_frame{idx:02d}.png")
    # Original C main plot and its enlarged inset remain visible as saved.
    panels.append((idx,orig.crop(cbox),a.crop(cbox),b.crop(bbox)))

w = 440
h = 440
sheet = Image.new("RGB",(3*w,len(panels)*(h+32)), "white")
draw = ImageDraw.Draw(sheet)
for row,(idx,orig,a,b) in enumerate(panels):
    for col,(label,img) in enumerate([
        ("Original GIF",orig),("True-color RGB",a),("3x raster, fitted",b)
    ]):
        yy=row*(h+32)
        draw.text((col*w+8,yy+8),f"{label} | frame {idx}, t={idx*3}",fill="black")
        # Comparison fit only. Full native high-resolution crops are separate.
        img=img.resize((w,h),resample=Image.Resampling.LANCZOS)
        sheet.paste(img,(col*w,yy+32))
sheet.save(HERE/"render_contact.png")

# Extract the old comoving movie too, so the observation is not tied only to
# the fixed-laboratory version. No rescaling of its numerical color values.
old=Image.open(ROOT/"notation"/"g13_real_animation.gif")
for idx in SELECTED:
    old.seek(idx)
    old.convert("RGB").save(HERE/f"comoving_full_frame{idx:02d}.png")

result=dict(
    source=str(SOURCE),
    original_movie=str(ROOT/"notation"/"g15_lab_real_animation.gif"),
    original_size=list(original.size),
    main_panel_width_pixels=boxes120[2][2],
    main_panel_range_lattice_constants=260,
    main_pixels_per_site=boxes120[2][2]/260,
    carrier_period_sites=4,
    carrier_pixels_per_period=4*boxes120[2][2]/260,
    frame_spacing_dimensionless_time=3,
    frames=rows,
)
(HERE/"render_metrics.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps(result,indent=2))
