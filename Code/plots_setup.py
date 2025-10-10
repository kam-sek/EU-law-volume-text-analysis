# In your plots_setup.py or equivalent script
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os
import shutil
import matplotlib


def setup_style(colors=["Red",  'Light Blue',  'Yellow', 'Light Purple', 'Light Green'], custom_font_path=None, apply_custom_font=False):
    
    sns.set_theme(style="whitegrid", font_scale=1.5)

    color_dict = {
        "Red": "#a21636",
        "Yellow": "#e7bc59",
        "Medium Blue": "#0080c7",
        "Orange": "#e67425",
        "Light Purple": "#6b64ad",
        "Light Green": "#58a944",
        "Pink": "#ac2ff2",
        "Dark Green": "#417e3c",
        "Black": "#000000",
        "Light Blue": "#60bbce",
        "Dark Blue": "#30368B",
        "Dark Purple": "#65499d",
    }

    # Start with the user-specified colors, if any
    palette = [color_dict[color] for color in colors if color in color_dict]
    # Add the remaining colors from the dictionary to ensure we have a full palette
    for color_name, color_hex in color_dict.items():
        if color_hex not in palette:
            palette.append(color_hex)

    sns.set_palette(palette)
    
    # Apply global despine
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.bottom'] = True
    plt.rcParams['axes.spines.left'] = True

    # Global grid settings
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['grid.alpha'] = 0.7
    plt.rcParams['axes.edgecolor'] = 'black'


# Set up the custom font
    script_dir = os.path.dirname(os.path.abspath(__file__))
    custom_font_path = os.path.join(script_dir, 'Conduit ITC Regular.otf')
    set_custom_font(custom_font_path)

def set_custom_font(custom_font_path):
    """
    Loads custom font, copies it into matplotlib folder and sets it as default font.
    """
    # Use shutil to copy the custom font to Matplotlib's font directory
    original_cwd = os.getcwd()
    matplotlib_font_dir = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
    shutil.copy(custom_font_path, matplotlib_font_dir)
 
    # Clear the font cache
    font_cache_dir = matplotlib.get_cachedir()
    font_cache_files = [f for f in os.listdir(font_cache_dir) if f.startswith('fontList')]
    for font_cache_file in font_cache_files:
        os.remove(os.path.join(font_cache_dir, font_cache_file))
   
    # Reload the font manager
    font_manager.fontManager.addfont(custom_font_path)
    font_manager._load_fontmanager()
 
    # Reset working directory to the original directory
    os.chdir(original_cwd)
 
    # Set the custom font as the default font
    prop = font_manager.FontProperties(fname=custom_font_path)
    plt.rcParams['font.family'] = prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False  # To support minus sign with custom fonts

    x = 7

    # Directly set the font sizes
    plt.rcParams['font.size'] = 16 + x   # Base font size
    plt.rcParams['axes.titlesize'] = 18 + x   # Title font size
    plt.rcParams['axes.labelsize'] = 16 + x # Axes label font size
    plt.rcParams['xtick.labelsize'] = 14 + x  # X-tick label font size
    plt.rcParams['ytick.labelsize'] = 14 + x # Y-tick label font size
    plt.rcParams['legend.fontsize'] = 14 + x # Legend font size
    plt.rcParams['figure.titlesize'] = 20 + x # Figure title font size
    plt.rcParams['font.weight'] = 'normal'  # Make all fonts bold