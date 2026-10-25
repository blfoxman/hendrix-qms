import sys, glob
from PIL import Image
fs = sorted(glob.glob('work/probe/%s_*.png' % sys.argv[1])); print(fs)
ims = [Image.open(f).resize((720, 405)) for f in fs]
W = Image.new('RGB', (1440, 405 * ((len(ims) + 1) // 2)))
for i, im in enumerate(ims): W.paste(im, ((i % 2) * 720, (i // 2) * 405))
W.save('work/probe/sheet_%s.png' % sys.argv[1])
