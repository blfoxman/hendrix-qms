import sys, glob
from PIL import Image
pre, out = sys.argv[1], sys.argv[2]
fs = sorted(glob.glob('work/probe/%s_*.png' % pre)); print(fs)
ims = [Image.open(f).resize((960, 540)) for f in fs]
W = Image.new('RGB', (1920, 540 * ((len(ims) + 1) // 2)))
for i, im in enumerate(ims): W.paste(im, ((i % 2) * 960, (i // 2) * 540))
W.save(out, quality=80)
