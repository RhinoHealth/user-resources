#!/usr/bin/env python
# coding: utf-8

# In[1]:


import argparse
import os
import random
from multiprocessing import Pool
import sys

import imageio
import numpy as np
import pandas as pd
import pydicom
import scipy.ndimage

# In[2]:


def read_general(dcm):
    img = dcm.pixel_array
    
    if hasattr(dcm, 'VOILUTSequence'):
        img = pydicom.pixel_data_handlers.util.apply_voi_lut(img, dcm)
    
    if hasattr(dcm, 'PixelIntensityRelationshipSign'):
        if dcm.PixelIntensityRelationshipSign == 1 and dcm.PixelIntensityRelationship == 'LIN':
            img = -img
    elif hasattr(dcm, 'PresentationLUTShape'):
        if dcm.PresentationLUTShape == 'INVERSE':
            img = -img
    
    if hasattr(dcm, 'WindowCenter') and hasattr(dcm, 'WindowWidth'):
        vmin = dcm.WindowCenter - dcm.WindowWidth / 2
        vmax = dcm.WindowCenter + dcm.WindowWidth / 2
    else:
        vmin = img.min()
        vmax = img.max()
    
    return (img - vmin) / (vmax - vmin)


# In[3]:


def read_fuji_iray(dcm):
    img = dcm.pixel_array
    
    if hasattr(dcm, 'VOILUTSequence'):
        img = pydicom.pixel_data_handlers.util.apply_voi_lut(img, dcm)
    
    if hasattr(dcm, 'WindowCenter') and hasattr(dcm, 'WindowWidth'):
        vmin = dcm.WindowCenter - dcm.WindowWidth / 2
        vmax = dcm.WindowCenter + dcm.WindowWidth / 2
    else:
        vmin = img.min()
        vmax = img.max()
    
    return 1 - (img - vmin) / (vmax - vmin)


# In[4]:


def read_swissray(dcm):
    img = dcm.pixel_array
    
    if hasattr(dcm, 'VOILUTSequence'):
        img = pydicom.pixel_data_handlers.util.apply_voi_lut(img, dcm)
    
    if hasattr(dcm, 'WindowCenter') and hasattr(dcm, 'WindowWidth'):
        vmin = dcm.WindowCenter - dcm.WindowWidth / 2
        vmax = dcm.WindowCenter + dcm.WindowWidth / 2
    else:
        vmin = img.min()
        vmax = img.max()
    
    return (img - vmin) / (vmax - vmin)


# In[5]:


def read_ge(dcm):
    '''
    Use window center, window width if possible, otherwise directly apply LUT
    '''
    img = dcm.pixel_array
    
    if hasattr(dcm, 'WindowCenter') and hasattr(dcm, 'WindowWidth'):        
        # use the soft window to be consistent with other vendors    
        if dcm.WindowWidth[2] >= (img.max() - img.min()):
            vmin = img.min()
            vmax = img.max()
        else:
            vmin = dcm.WindowCenter[2] - dcm.WindowWidth[2] / 2
            vmax = dcm.WindowCenter[2] + dcm.WindowWidth[2] / 2
        img = (img - vmin) / (vmax - vmin)
    else:
        img = pydicom.pixel_data_handlers.util.apply_voi_lut(img, dcm)
        img = (img - img.min()) / (img.max() - img.min())
    
    return img


# In[6]:


def read_by_manufacturer(dcm):
    if not hasattr(dcm, 'PixelData'):
        return None
    
    manufacturer = dcm.Manufacturer.lower()
    if 'altamont' in manufacturer or 'lexmark' in manufacturer or 'pacsgear' in manufacturer:
        # these are texts
        return None;
    elif 'ge health' in manufacturer or 'ge medical' in manufacturer:
        return read_ge(dcm)
    elif 'fuji' in manufacturer or 'iray' in manufacturer:
        return read_fuji_iray(dcm)
    elif 'swissray' in manufacturer:
        return read_swissray(dcm)
    else:
        try:
            return read_general(dcm)
        except TypeError:
            return None


# In[7]:


# parameters
parser = argparse.ArgumentParser(description = 'CXR Preprocess')

parser.add_argument('--input_dir', type=str, required=True, help="input CXR dicom directory")
parser.add_argument('--output_dir', type=str, required=True, help="output directory")
parser.add_argument('--output_folder', type=str, required=True, help="folder of output CXR png files")
parser.add_argument('--crop_black', action='store_true', help="try to crop black borders")
parser.add_argument('--crop_white', action='store_true', help="try to crop black borders")
parser.add_argument('--crop_th', type=float, default=0.5, help="threshold for cropping borders")

# In[12]:


args = parser.parse_args()
input_dir = args.input_dir
img_shape = [512, 512] # output image shape
output_dir = args.output_dir
output_folder = args.output_folder
npy_dir = os.path.join(output_dir, 'npys')
output_folder = args.output_folder
png_dir = os.path.join(output_dir,output_folder)
if not os.path.exists(npy_dir):
    os.makedirs(npy_dir)
if not os.path.exists(png_dir):
    os.makedirs(png_dir)

file_list = [
    os.path.join(dirpath, filename)
    for dirpath, dirnames, filenames in os.walk(input_dir)
    for filename in filenames
    if filename.lower().endswith('.dcm')
]


# In[8]:


# data analysis
exclusion = {'SeriesDescription': ['protocol', 'screenshot', 'fl angio']} # exclude these keywords (lower case)
fields_to_record = [
    'SeriesInstanceUID',
    'ImageType',
    'BodyPartExamined', 
    'Manufacturer', 
    'ExposureIndex',
    'PixelSpacing',
    'ProtocolName',
    'SeriesDescription', 
    'AcquisitionDeviceProcessingDescription']


# In[9]:


def read_single_file(filename, fields_to_record, exclusion):
    dcm = pydicom.dcmread(filename)
    if not hasattr(dcm, 'ImageType'):
        return None, None
    
    # extract fields
    infos = {}
    for field_name in fields_to_record:
        if hasattr(dcm, field_name):
            infos[field_name] = getattr(dcm, field_name)
        else:
            infos[field_name] = ''
    
    for field_name in exclusion:
        if hasattr(dcm, field_name):
            attr = str(getattr(dcm, field_name)).lower()
            for k in exclusion[field_name]:
                if k in attr:
                    return None, None
    
    img = read_by_manufacturer(dcm)
    if img is None:
        return None, None
    
    return img, infos


def crop_border(img, crop_black, th):
    print(f'crop image: shape={img.shape}, min={np.min(img)}, max={np.max(img)}, th={th}', )
    invalid_index = []
    for x in range(img.shape[0]):
        if crop_black:
            arr = img[x, :] < th
        else:
            arr = img[x, :] > th
        if np.sum(arr) == img.shape[1]:
            invalid_index.append(x)
    assert len(invalid_index) < img.shape[1], f'all pixels in x axis would be removed with th={th}!'
    img = np.delete(img, invalid_index, axis=0)
    print(f'crop x: removing {len(invalid_index)} pixels')

    invalid_index = []
    for y in range(img.shape[1]):
        if crop_black:
            arr = img[:, y] < th
        else:
            arr = img[:, y] > th
        if np.sum(arr) == img.shape[0]:
            invalid_index.append(y)
    assert len(invalid_index) < img.shape[0], f'all pixels in y axis would be removed with th={th}!'
    img = np.delete(img, invalid_index, axis=1)
    print(f'crop y: removing {len(invalid_index)} pixels')

    return img


def process_file(file_path, fields_to_record, exclusion, npy_dir, png_dir, img_shape,
                   crop_black=False, crop_white=False, crop_th=0.5):
    img, info = read_single_file(file_path, fields_to_record, exclusion)
    if img is None or info is None:
        return None

    # get output_filename
    output_filename_base = info['SeriesInstanceUID']
    output_filename = output_filename_base
    ind_append = 1
    while os.path.exists(os.path.join(png_dir, output_filename+'.png')):
        output_filename = output_filename_base + '_%d' % ind_append
        ind_append += 1
    # if 'POS' in os.path.dirname(foldername):
    if random.randint(0, 1):  # TODO: replace after talking with Aoxiao
        info['label'] = True
    else:
        info['label'] = False
    info['filename'] = output_filename

    # save npy
    #np.save(os.path.join(npy_dir, output_filename), img)

    if crop_black:
        img = crop_border(img, crop_black=True, th=crop_th)
    if crop_white:
        img = crop_border(img, crop_black=False, th=crop_th)

    # save image
    # apply a prefilter to the image when downsampling
    zoom = np.array(img_shape) / np.array(img.shape)
    stds = 1 / zoom / 4
    img = scipy.ndimage.filters.gaussian_filter1d(img, stds[0], axis=0)
    img = scipy.ndimage.filters.gaussian_filter1d(img, stds[1], axis=1)
    img = scipy.ndimage.interpolation.zoom(img, zoom)
    # convert to rgb
    img[img < 0] = 0
    img[img > 1] = 1
    img = np.tile(img[..., np.newaxis], (1,1,3)) * 255
    imageio.imwrite(os.path.join(png_dir, output_filename+'.png'), img.astype(np.uint8))

    return info



# In[10]:


def process_file_wrapper(file_path, crop_black=False, crop_white=False, crop_th=130):
#     print (folder_list[i])
#     print (i, end=',', flush=True)
    return process_file(file_path, fields_to_record, exclusion, npy_dir, png_dir, img_shape,
                        crop_black=args.crop_black, crop_white=args.crop_white, crop_th=args.crop_th)


# In[11]:
if __name__ == '__main__':
    if args.crop_black and args.crop_white:
        print("Either use --crop_black or --crop_white but not both together.", file=sys.stderr)
        sys.exit(1)
    if not file_list:
        print("No input files found at .", file=sys.stderr)
        sys.exit(1)

    p = Pool(20)
    # folder_list = folder_list[-20:]
    print(len(file_list))
    infos = []
    batch_size = 100
    for i in range(0, len(file_list), batch_size):
        print(i, end=',', flush=True)
        infos += p.map(process_file_wrapper, file_list[i:i+batch_size])
    print(len(file_list))


    # In[13]:


    df = pd.DataFrame()
    for info in infos:
        df = df.append(info, ignore_index=True)
    df.to_csv(os.path.join(png_dir, "manifest.csv"), index=False)


# In[98]:


# folder_investigate = [f for f in glob.glob(os.path.join(input_dir, '0283805', 'E15489750*')) 
#                       if not 'CT' in os.path.basename(f) and not 'US' in os.path.basename(f)]
# print (folder_investigate)
# filenames = glob.glob(os.path.join(folder_investigate[0], '*.dcm'))
# print (filenames)
# dcm = pydicom.dcmread(filenames[1])
# img = read_by_manufacturer(dcm)
# plt.imshow(img, 'gray', vmin=0, vmax=1)


# In[ ]:




