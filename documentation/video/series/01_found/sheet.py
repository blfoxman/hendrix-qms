import sys, glob, os
from PIL import Image
os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/work/probe')
pre = sys.argv[1]; fs = sorted(glob.glob(pre + '_*.png'), key=os.path.getmtime)
ims = [Image.open(f).resize((720, 405)) for f in fs]
W = Image.new('RGB', (1440, 405 * ((len(ims) + 1) // 2)))
for i, im in enumerate(ims): W.paste(im, ((i % 2) * 720, (i // 2) * 405))
W.save('sheet_' + pre + '.png'); print(fs)
