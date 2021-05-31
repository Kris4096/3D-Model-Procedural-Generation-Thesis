from pathlib import Path
import tensorflow as tf
import voxel
import terrain_gen
import terrain_tex
import flora_gen
import flora_tex
import struct_gen
import struct_tex
import classificator
import numpy as np

XRAW_PATTERN = "*.xraw";
CATEGORIES = ["Flora", "Terrain", "Structure"]
MODEL_NAMES = ["Flora", "FloraTex", "Terrain", "TerrainTex", "Struct", "StructTex", "Class"]


def get_change_matrix(size,factor, a, b, c):
    div_factor = 1.0 if c == 0 else float(c)*10.0
    max_val = float(b)/div_factor
    min_val = -float(a)/div_factor
    factor = float(factor)/100.0
    #print("{} {} {} {}".format(div_factor, max_val, min_val, factor))
    uniform = factor*tf.random.uniform(shape=size,minval=min_val, maxval=max_val)
    return uniform

def is_category_pretrained(category):
    path = Path("tensordata/{}".format(category));
    return path.exists();

def pretrain_model(category):
    if category == "Flora":
        return flora_gen.train_flora_gen()
    elif category == "FloraTex":
        return flora_tex.train_flora_tex_gen()
    elif category == "Terrain":
        return terrain_gen.train_terrain_gen()
    elif category == "TerrainTex":
        return terrain_tex.train_terrain_tex_gen()
    elif category == "Struct":
        return struct_gen.train_struct_gen()
    elif category == "StructTex":
        return struct_tex.train_struct_tex_gen()
    elif category == "Class":
        return classificator.train_classificator()

def load_model(category):
    if category == "Flora":
        return flora_gen.load_flora_gen()
    elif category == "FloraTex":
        return flora_tex.load_flora_tex_gen()
    elif category == "Terrain":
        return terrain_gen.load_terrain_gen()
    elif category == "TerrainTex":
        return terrain_tex.load_terrain_tex_gen()
    elif category == "Struct":
        return struct_gen.load_struct_gen()
    elif category == "StructTex":
        return struct_tex.load_struct_tex_gen()
    elif category == "Class":
        return classificator.load_classifier()

def glob_categories():
    categories = []
    for itm in Path("dataset").iterdir():
        categories.append(itm);
    return categories;

def glob_data(path, t_set, t_cat, category):
    for itm in Path(path).rglob(XRAW_PATTERN):
        vox_model = voxel.load_from_xraw(itm);
        t_set.append(vox_model.as_colorless_array().reshape((32,32,32,1),order='F'));
        t_cat.append(category);
    return (t_set, t_cat);

def glob_only_data(path, t_set):
    for itm in Path(path).rglob(XRAW_PATTERN):
        vox_model = voxel.load_from_xraw(itm);
        t_set.append(vox_model.as_colorless_array().reshape((32,32,32,1),order='F'));
    return t_set;

def get_paths(path):
    paths = []
    for itm in Path(path).rglob(XRAW_PATTERN):
        paths.append(itm)
    return paths;

def glob_only_colored_data(path, t_set, t_col):
    for itm in Path(path).rglob(XRAW_PATTERN):
        vox_model = voxel.load_from_xraw(itm);
        data = vox_model.as_colored_array();
        #print(data)
        t_set.append(data[0].reshape((32,32,32,1),order='F'));
        t_col.append(data[1].reshape((32,32,32,1),order='F'))
    return (t_set, t_col);

def as_point_cloud(data):
    data = np.array(data).reshape((32*32*32))
    cloud = []
    for x in range(32):
        for y in range(32):
            for z in range(32):
                index = z*32*32 + y*32 + x
                if data[index] >= 0.5:
                    cloud.append([x,y,z])
    return [cloud]
