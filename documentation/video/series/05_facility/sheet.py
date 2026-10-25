import sys, glob
from PIL import Image
pre = sys.argv[1]; fs = sorted(glob.glob('work/probe/%s_*.png' % pre), key=lambda f: __import__('os').path.getmtime(f))
ims = [Image.open(f).resize((720, 405)) for f in fs]
W = Image.new('RGB', (1440, 405 * ((len(ims) + 1) // 2)))
for i, im in enumerate(ims): W.paste(im, ((i % 2) * 720, (i // 2) * 405))
W.save('work/probe/sheet_%s.png' % pre); print([f.split('/')[-1] for f in fs])
