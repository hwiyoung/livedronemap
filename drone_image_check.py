from ldm_client import livedronemap
import time
import glob

img_fname_list = glob.glob('example_krihs/*.jpg')

ldm = livedronemap('http://127.0.0.1:5000/')
ldm.create_project('test_ti')
ldm.set_current_project('test_ti')

for img_fname in img_fname_list:
    eo_fname = img_fname.split('.')[0] + '.txt'
    result = ldm.ldm_upload(img_fname, eo_fname)
    print('Image: %s, EO: %s, Result: %s' % (img_fname, eo_fname, result))
    time.sleep(3)