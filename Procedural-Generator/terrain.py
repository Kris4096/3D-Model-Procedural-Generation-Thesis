from opensimplex import OpenSimplex
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math as m
import voxel
from bresenham import bresenham
import random
import enum
from PIL import Image

def form_terrain(scale=7.0):
    simplex = OpenSimplex()
    terrain = [None] * (32*32)
    scale_factor = 7.0;
    for x in range(32):
        for y in range(32):
            terrain[y*32+x] = (simplex.noise2d(x/scale_factor,y/scale_factor) + 1.0);
    return terrain

def plot_terrain(heightmap):
    img = Image.new(mode="RGB", size=(32,32))
    for i in range(32):
        for j in range(32):
            color = int((heightmap[j*32+i]+1.0)/2.0*255)
            img.putpixel((i,j),(color,color,color,255))
    img.show()

def filter_mask(heightmap, n = 1):
    result = [0] * (32*32)
    for y in range(32):
        for x in range(32):
            i_count = 0
            for ix in range(-n,n+1):
                for iy in range(-n,n+1):
                    i = (y+iy)*32+(x+ix)
                    if x+ix < 0 or x+ix >= 32:
                        continue;
                    if y+iy < 0 or y+iy >= 32:
                        continue;
                    i_count += 1
                    result[(y)*32+(x)] += heightmap[i]
            if i_count != 0:
                result[(y)*32+(x)] /= float(i_count)
    return result

def bleed_mask(mask,max_chance=1.0):
    for y in range(32):
        for x in range(32):
            if mask[y*32+x] == 0:
                n = 0 if (y==0 or mask[(y-1)*32+x] == 0) else 1
                s = 0 if (y==31 or mask[(y+1)*32+x] == 0) else 1
                w = 0 if (x==0 or mask[y*32+x-1] == 0) else 1
                e = 0 if (x==31 or mask[y*32+x+1] == 0) else 1
                val = n+s+w+e
                if val != 0 and random.random() <= (max_chance/4.0)*val:
                    mask[y*32+x] = 1

def add_ravine(heightmap,ravine_range=10,falloff=0.9):
    mask = [0] * (32*32)
    for p in bresenham(random.randint(0,31),random.randint(0,31),random.randint(0,31),random.randint(0,31)):
        mask[p[1]*32+p[0]] = 1
    for _ in range(ravine_range):
        for y in range(32):
            for x in range(32):
                if mask[y*32+x] == 1:
                    heightmap[y*32+x] = heightmap[y*32+x]*falloff
        bleed_mask(mask)

class ColorType(enum.Enum):
    MEADOW = 1
    MESA = 2
    SNOWY = 3
    LAST = 4

def get_random_low_color(ctype):
    if ctype == ColorType.MEADOW.value:
        return voxel.VoxelColor(38+random.randint(-10,10),53+random.randint(-10,10),46+random.randint(-10,10))
    elif ctype == ColorType.SNOWY.value:
        return voxel.VoxelColor(158+random.randint(-5,5),158+random.randint(-5,5),158+random.randint(-5,10))
    else:
        return voxel.VoxelColor(79+random.randint(-10,10),51+random.randint(-10,10),47+random.randint(-10,10))

def get_random_middle_color(ctype):
    if ctype == ColorType.MEADOW.value:
        return voxel.VoxelColor(44+random.randint(-10,10),71+random.randint(-10,10),58+random.randint(-10,10))
    elif ctype == ColorType.SNOWY.value:
        return voxel.VoxelColor(181+random.randint(-5,5),217+random.randint(-5,5),224+random.randint(-5,10))
    else:
        return voxel.VoxelColor(155+random.randint(-10,10),62+random.randint(-10,10),49+random.randint(-10,10))

def get_random_top_color(ctype):
    if ctype == ColorType.MEADOW.value:
        return voxel.VoxelColor(73+random.randint(-10,10),94+random.randint(-10,10),84+random.randint(-10,10))
    elif ctype == ColorType.SNOWY.value:
        return voxel.VoxelColor(220+random.randint(-5,5),232+random.randint(-5,5),226+random.randint(-5,10))
    else:
        return voxel.VoxelColor(170+random.randint(-10,10),83+random.randint(-10,10),71+random.randint(-10,10))

def generate_terrain_pallete(amp,ctype):
    pallete = [None] * 4
    if ctype != ColorType.MESA.value and amp > 10.0 and random.random() >= 0.5:
        #snowy
        pallete[0] = voxel.VoxelColor(220,232,226)
    else:
        pallete[0] = get_random_top_color(ctype)
    pallete[1] = get_random_middle_color(ctype)
    pallete[2] = get_random_low_color(ctype)
    pallete[3] = voxel.VoxelColor(132,132,132)
    return pallete;

def get_color(height,amp,rnd):
    sector = (10.0+amp) / 3.0;
    height += rnd
    if height < sector:
        return 2;
    elif height < 2*sector:
        return 1;
    else:
        if height < 2.5*sector and amp > 10.0:
            return 3;
        else:
            return 0;


def create_voxel_model_from_heightmap(heightmap):
    simplex = OpenSimplex()
    color_map = [None] * (32*32)
    scale_factor = 7.0;
    color_type = random.randint(1,ColorType.LAST.value-1)
    for x in range(32):
        for y in range(32):
            color_map[y*32+x] = (simplex.noise2d(x/scale_factor,y/scale_factor)) * 8;

    model = voxel.VoxelModel(32,32,32)
    amp = float(random.randint(4,15))
    model.pallete = generate_terrain_pallete(amp,color_type)
    for x in range(32):
        for y in range(32):
            i = y*32+x
            max_z = 16 + int((heightmap[i]-1.0) * amp)
            for z in range(max_z+1):
                model.set_voxel(x,y,z,get_color(z,amp,color_map[y*32+x]))
    return model

for ti in range(360):
    terrain = form_terrain(scale=float(4+random.randint(0,18)))
    terrain = filter_mask(terrain,n=random.randint(1,3))
    add_ravine(terrain,falloff=(float(random.randint(5,9))/10.0))
    terrain = filter_mask(terrain,n=1)
    model = create_voxel_model_from_heightmap(terrain)
    model.export_xraw("output/terrain_voxel_model_{}.xraw".format(ti))