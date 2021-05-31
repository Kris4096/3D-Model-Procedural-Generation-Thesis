import numpy as np
import matplotlib.pyplot as plt

import voxel
import gui

# def voxel_load(file_name,resolution):
#     subprocess.call([VOXELIZER_BIN, "models/{}.obj".format(file_name), str(resolution-1)]);
#     return voxel.load_from_xraw("output/{}.xraw".format(file_name));

if __name__ == "__main__":
    gui.init_gui();