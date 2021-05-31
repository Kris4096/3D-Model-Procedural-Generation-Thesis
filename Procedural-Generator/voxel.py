
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import subprocess
import random
import multiprocessing
import time
import math as m

class VoxelColor:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
    def combine(self, other):
        new_r = (self.r + other.r) / 2
        new_g = (self.r + other.r) / 2
        new_b = (self.r + other.r) / 2
        return VoxelColor(new_r, new_g, new_b)

class VoxelModel:
    def __init__(self, width, height, depth):
        self.width = width;
        self.height = height;
        self.depth = depth;
        self.shape = (width,height,depth);
        self.voxels = [None]*width*height*depth;
        self.pallete = [];
    def copy(self):
        copy = VoxelModel(self.width,self.height,self.depth)
        copy.pallete = self.pallete.copy()
        copy.voxels = [x for x in self.voxels]
        return copy;
    def load_from_dataarray(self, data, offset = 50):
        offset = float(offset)/100.0
        #print(data[0][15][15])
        data = np.array(data).reshape((32*32*32),order='F')
        for i in range(32*32*32):
            if int(m.floor(data[i]+offset)) == 0:
                self.voxels[i] = None
            else:
                self.voxels[i] = 1
    def load_from_colored_dataarray(self, data, offset = 50):
        data, colors = data
        offset = float(offset)/100.0
        data = np.array(data).reshape((32*32*32),order='F')
        colors = np.array(colors).reshape((32*32*32),order='F')
        for i in range(32*32*32):
            if int(m.floor(data[i]+offset)) == 0:
                self.voxels[i] = None
            else:
                decoded_color = int(colors[i] * float(len(self.pallete)))
                if decoded_color == len(self.pallete):
                    decoded_color -= 1
                self.voxels[i] = decoded_color
    def set_voxel(self,x,y,z,color):
        index = x+self.width*y+self.width*self.height*z;
        if index >= len(self.voxels):
            print("Voxel out of range!");
        else:
            self.voxels[index] = color;
    def get_voxel(self,x,y,z):
        if x < 0 or x >= self.width or y < 0 or y >= self.height or z < 0 or z >= self.depth:
            return -1;
        index = x+self.width*y+self.width*self.height*z;
        return self.voxels[index];
    def get_voxel_chunk(self,x1,x2,y1,y2,z1,z2):
        chunk = [];
        for x in range(x1,x2):
            for y in range(y1,y2):
                for z in range(z1, z2):
                    chunk.append(self.get_voxel(y,z,x))
        return chunk
    def set_voxel_chunk(self,chunk,x0,y0,z0,n):
        for x in range(n):
            for y in range(n):
                for z in range(n):
                    index_global = (z0+z)*self.width*self.height + (y0+y)*self.width + (x0+x)
                    index_local = z*n*n + y*n + x
                    #print("{} {} {} {} {}".format(n,z,z*n*n, y*n, x))
                    #print("{} {} {}".format(len(chunk),index_global,index_local))
                    self.voxels[index_global] = chunk[index_local]
    def get_voxel_chunk_ignoring_source(self,x1,x2,y1,y2,z1,z2,sx,sy,sz):
        chunk = [];
        for x in range(x1,x2):
            for y in range(y1,y2):
                for z in range(z1, z2):
                    if x != sx or y != sy or z != sz:
                        chunk.append(self.get_voxel(x,y,z))
        return chunk;
    def export_xraw(self,file_path):
        file = open(file_path,'w+b');
        file.write(bytearray([88,82,65,87]));
        file.write(bytearray([0])); # 1b color channel type (0 = unsigned int)
        file.write(bytearray([4])); # 1b color channel count (3 = RGB)
        file.write(bytearray([8])); # 1b bits per channel (8,16,32)
        file.write(bytearray([16])); # 1b bits per index (16 must be used)
        file.write(self.width.to_bytes(4,byteorder = 'little', signed=False)); # 4b width x
        file.write(self.height.to_bytes(4,byteorder = 'little', signed=False)); # 4b height y
        file.write(self.depth.to_bytes(4,byteorder = 'little', signed=False)); # 4b depth z
        temp_num = 32768;
        file.write(temp_num.to_bytes(4,byteorder = 'little',signed=False)); # 4b num of pallette colors 32768
        buffer = [];
        for voxel in self.voxels:
            if voxel == None:
                buffer.append(255);
                buffer.append(255);
            else:
                #buffer.append(voxel.to_bytes(4,byteorder='little'));
                for b in voxel.to_bytes(2,byteorder='little',signed=False):
                    buffer.append(int(b));
        for i in range(0,32768):
            if i < len(self.pallete):
                buffer.append(self.pallete[i].r);
                buffer.append(self.pallete[i].g);
                buffer.append(self.pallete[i].b);
                buffer.append(255);
            else:
                buffer.append(75);
                buffer.append(75);
                buffer.append(75);
                buffer.append(255);
        file.write(bytearray(buffer));
        file.close();
    def export_obj(self,file_path):
        file = open(file_path,'w');
        vertices = []
        triangles = []
        # calc triangles
        for x in range(self.width):
            for y in range(self.width):
                for z in range(self.width):
                    i = z*32*32 + y*32 + x
                    vertices.append([x+1,y+1,z+1])
                    vertices.append([x+1,y+1,z-1])
                    vertices.append([x+1,y-1,z+1])
                    vertices.append([x+1,y-1,z-1])
                    vertices.append([x-1,y+1,z+1])
                    vertices.append([x-1,y+1,z-1])
                    vertices.append([x-1,y-1,z+1])
                    vertices.append([x-1,y-1,z-1])

        file.close();
    def export_off(self,file_path):
        file = open(file_path,'w');
        file.write("OFF")
        file.close();
    def get_color(self,index):
        if index == None:
            return "#FF0000"
        if index >= len(self.pallete):
            print("Index {} exceeds pallete {}".format(index, len(self.pallete)))
        #print("{} {}".format(index, len(self.pallete)))
        color = self.pallete[index]
        rgb = [color.r / 255.0, color.g / 255.0, color.b / 255.0]
        return matplotlib.colors.to_hex(rgb)
    def plot_voxels(self):
        print("{} {} {}".format(self.width, self.height, self.depth));
        n_voxels = np.array([x!=None for x in self.voxels]).reshape(32,32,32,order='F');
        figure = plt.figure();
        subplot = figure.add_subplot(projection='3d');
        colors = np.array([self.get_color(x) for x in self.voxels]).reshape(32,32,32,order='F');
        print("Pallete size {}".format(len(self.pallete)))
        #print(colors)
        subplot.voxels(n_voxels,facecolors=colors)
        figure.show();
    def as_colorless_array(self):
        result = np.zeros((self.width,self.height,self.depth), dtype=np.float32,order='F');
        for x in range(0,self.width):
            for y in range(0,self.height):
                for z in range(0,self.depth):
                    v = self.get_voxel(x,y,z);
                    if v != None:
                        result[x,y,z] = 1;
                    else:
                        result[x,y,z] = 0;
        return result;
    def as_colored_array(self):
        result = np.zeros((self.width,self.height,self.depth), dtype=np.float32,order='F');
        colors = np.zeros((self.width,self.height,self.depth), dtype=np.float32,order='F');
        max_colors = float(len(self.pallete)) if len(self.pallete) > 0 else 1.0;
        #print("Max colors: {}".format(max_colors))
        for x in range(0,self.width):
            for y in range(0,self.height):
                for z in range(0,self.depth):
                    v = self.get_voxel(x,y,z);
                    if v != None:
                        result[x,y,z] = 1.0;
                        colors[x,y,z] = (float(v) / max_colors) + (1.0 / (max_colors*2.0));
                    else:
                        result[x,y,z] = 0.0;
                        colors[x,y,z] = 0.0;
        #print("R {}".format(result[0][0]))
        return (result, colors);

def load_from_xraw(file_path):
    file = open(file_path,'r+b');
    if file.read(4) != bytearray([88,82,65,87]):
        print("File is not of XRAW type!");
        return None;
    
    color_channel_type = int.from_bytes(file.read(1), byteorder='little', signed=False);
    color_channel_count = int.from_bytes(file.read(1), byteorder='little', signed=False);
    bits_per_channel = int.from_bytes(file.read(1), byteorder='little', signed=False);
    bits_per_index = int.from_bytes(file.read(1), byteorder='little', signed=False);
    model_width = int.from_bytes(file.read(4), byteorder='little', signed=False);
    model_height = int.from_bytes(file.read(4), byteorder='little', signed=False);
    model_depth = int.from_bytes(file.read(4), byteorder='little', signed=False);
    num_of_pallete_colors = int.from_bytes(file.read(4), byteorder='little', signed=False);

    pallete_0_is_empty = False
    if num_of_pallete_colors == 256:
        pallete_0_is_empty = True

    result_model = VoxelModel(model_width, model_height, model_depth);
    
    for i in range(0,model_width*model_height*model_depth):
        result_model.voxels[i] = int.from_bytes(file.read(int(bits_per_index/8)), byteorder='little', signed=False);
        #print(result_model.voxels[i])
        if not pallete_0_is_empty and result_model.voxels[i] == (1<<bits_per_index)-1:
            result_model.voxels[i] = None

    for i in range(0, num_of_pallete_colors):
        barray = file.read(4);
        if barray[3] == 0:
            #print("Transparent found")
            for vi in range(0,model_width*model_height*model_depth):
                if result_model.voxels[vi] == i:
                    result_model.voxels[vi] = None
        result_model.pallete.append(VoxelColor(barray[0],barray[1],barray[2]));

    # remove unused pallete colors
    used_colors = []
    for vi in range(0,model_width*model_height*model_depth):
        if result_model.voxels[vi] != None:
            used_colors.append(result_model.voxels[vi])
    used_colors = list(dict.fromkeys(used_colors))
    #print("Used colors {}".format(len(used_colors)))
    #print(used_colors)

    used_colors.sort()

    new_pallete = []
    for color in used_colors:
        new_pallete.append(result_model.pallete[color])
    #print("Colors in new pallete {}".format(len(new_pallete)))

    # replace indexes

    new_voxels = []
    for vi in range(0, len(result_model.voxels)):
        color = result_model.voxels[vi]
        if color != None:
            for i in range(0, len(used_colors)):
                if color == used_colors[i]:
                    color = i;
                    break
        new_voxels.append(color)

    result_model.pallete = new_pallete;
    result_model.voxels = new_voxels;

    file.close();
    return result_model;

VOXELIZER_BIN = 'bin/voxelizer.exe';
VOXELIZER_RESOLUTION = 32;

def load_from_path(file_path):
    split_path = os.path.splitext(file_path);
    extension = split_path[1].lower();
    file_name = split_path[0].split('/')[-1];
    #print(split_path)
    if extension == ".xraw":
        return load_from_xraw(file_path);
    else:
        # Attempt to voxelize
        subprocess.call([VOXELIZER_BIN, file_path, str(VOXELIZER_RESOLUTION)]);
        return load_from_xraw("output/{}.xraw".format(file_name));