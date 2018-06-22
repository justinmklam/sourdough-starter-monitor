import os
import glob
import pandas as pd
import imageio

import matplotlib
import matplotlib.pyplot as plt

from skimage import io
from skimage.filters import threshold_yen, threshold_otsu
from skimage.measure import label, regionprops
from skimage.transform import rotate

def load_image(fname, crop_area=[0, 1000, 650, 1100], show_img=False):
    img = io.imread(fname, as_grey=True)

    img_cropped = img[crop_area[0]:crop_area[1], crop_area[2]:crop_area[3]]

    thresh = threshold_otsu(img_cropped)
    binary = img_cropped < thresh
    
    if show_img:
        fig, ax = plt.subplots(1, 3)
        ax[0].imshow(img, cmap='gray')
        ax[1].imshow(img_cropped, cmap='gray')
        ax[2].imshow(binary, cmap='gray')
        ax[1].set_title(fname)
         
        plt.show()
    
    return binary

def get_height(binary_img, min_area=20000, show_plot=False):
    
    height = None
    
    label_img = label(binary_img)
    regions = regionprops(label_img)

    if show_plot:
        fig, ax = plt.subplots()
        ax.imshow(binary_img, cmap=plt.cm.gray)

    for props in regions:
        y0, x0 = props.centroid
        orientation = props.orientation

        minr, minc, maxr, maxc = props.bbox
        bx = (minc, maxc)
        by = (minr, minr)

        area = (maxc-minc)*(maxr-minr)

        if area >= min_area:
            if show_plot:
                ax.plot(bx, by, '-r', linewidth=2.5)
                # ax.plot(x0, y0, 'ro')
            height = minr

    # ax.axis((0, 600, 600, 0))
    if show_plot:
        plt.show()
        
    return height

def analyze_image(img_folder, crop_area=[0, 1000, 650, 1100], min_area=30000):
    export_name = img_folder + '.json'
    img_files = glob.glob(os.path.join(img_folder, '*.jpg'))
    img_files = sorted(img_files)
    
    times = []
    heights = []
    fnames = []
    
    time_interval = 5   # img taken every 5 min
    
    if not os.path.isfile(export_name):
        for i, img_name in enumerate(img_files):
            img_binary = load_image(img_name, crop_area)
            height = get_height(img_binary, min_area, False)
            heights.append(height)
            times.append(i*time_interval)
            fnames.append(img_name)

        d = {'Time': times, 'Height': heights, 'File': fnames}
        df = pd.DataFrame(data=d)

        start_size = abs(img_binary.shape[0] - df['Height'][0])
        current_sizes = abs(img_binary.shape[0] - df['Height'])
        df['Height Normalized'] = (current_sizes - start_size) / start_size
        print(start_size, img_binary.shape[0])
        # df.to_json(export_name, orient='columns')
        
    else:
        df = pd.read_json(export_name, orient='columns')
        df.sort_index(inplace=True)
        print(export_name + ' loaded.')
    
    fig, ax = plt.subplots(1)
    
    ax.plot(df['Time']/60, df['Height Normalized']*100)
    ax.set_ylabel('Normalized Growth (%)')
    ax.set_xlabel('Time (hours)')
    ax.set_title(img_folder)
    return df

def test_image(fname, crop_area, min_area=30000):
    height = None

    img = io.imread(fname, as_grey=True)

    img_cropped = img[crop_area[0]:crop_area[1], crop_area[2]:crop_area[3]]

    thresh = threshold_otsu(img_cropped)
    binary = img_cropped < thresh
    
    fig, ax = plt.subplots(1, 3)
    ax[0].imshow(img, cmap='gray')
    ax[1].imshow(img_cropped, cmap='gray')
    ax[2].imshow(binary, cmap='gray')

    label_img = label(binary)
    regions = regionprops(label_img)

    for props in regions:
        y0, x0 = props.centroid

        minr, minc, maxr, maxc = props.bbox
        bx = (minc, maxc)
        by = (minr, minr)

        area = (maxc-minc)*(maxr-minr)

        if area >= min_area:
            ax[2].plot(bx, by, '-r', linewidth=2.5)
            # ax[2].plot(x0, y0, 'ro')
            height = minr

    for i in range(1,3):
        ax[i].set_yticklabels([])
        ax[i].set_xticklabels([])
        
    ax[1].set_title(fname)

    print('Height: ', height)
    print(binary.shape[0], binary.shape[1])

    return fig, ax

def create_gif(directory, crop_area, min_area, df):
    fnames = glob.glob(os.path.join(directory, '*.jpg'))
    fnames = sorted(fnames)

    gif_imgs = []

    out_path = directory + ' (gif)'
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    for i, f in enumerate(fnames):
        img_out_fpath = os.path.join(out_path, '%d.png'%i)

        if os.path.isfile(img_out_fpath):
            gif_imgs.append(imageio.imread(img_out_fpath))
            continue

        fig, ax = plt.subplots(1, 4, figsize=(12,4))

        ax[3].plot(df['Time']/60, df['Height Normalized']*100)
        ax[3].set_ylabel('Normalized Growth (%)')
        ax[3].set_xlabel('Time (hours)')
        ax[3].plot(df['Time'][i]/60, df['Height Normalized'][i]*100, 'ro')

        height = None

        img = io.imread(f, as_grey=True)

        img_cropped = img[crop_area[0]:crop_area[1], crop_area[2]:crop_area[3]]

        thresh = threshold_otsu(img_cropped)
        binary = img_cropped < thresh
        
        ax[0].imshow(img, cmap='gray')
        ax[1].imshow(img_cropped, cmap='gray')
        ax[2].imshow(binary, cmap='gray')

        label_img = label(binary)
        regions = regionprops(label_img)

        for props in regions:
            y0, x0 = props.centroid

            minr, minc, maxr, maxc = props.bbox
            bx = (minc, maxc)
            by = (minr, minr)

            area = (maxc-minc)*(maxr-minr)

            if area >= min_area:
                ax[2].plot(bx, by, '-r', linewidth=2.5)
                # ax[2].plot(x0, y0, 'ro')
                height = minr

        for j in range(1,3):
            ax[j].set_yticklabels([])
            ax[j].set_xticklabels([])
            
        ax[0].set_title('Original')
        ax[1].set_title('Cropped')
        ax[2].set_title('Parsed')
        ax[3].set_title('Graphed')
        fig.suptitle(f.strip('.jpg'))
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        fig.savefig(img_out_fpath)

        gif_imgs.append(imageio.imread(img_out_fpath))
        plt.close(fig)

    imageio.mimsave(os.path.join(out_path,directory + '.gif'), gif_imgs, duration = 0.25)


