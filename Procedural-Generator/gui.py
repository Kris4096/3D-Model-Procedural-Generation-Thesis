import tkinter
from tkinter import filedialog
import voxel
import classificator as cl
import random
import utils
import tensorflow as tf
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

slider_texture_param_a = None;
slider_texture_param_b = None;
slider_texture_param_c = None;
slider_texture_param_d = None;
slider_texture_param_e = None;

slider_gen_param_a = None;
slider_gen_param_b = None;
slider_gen_param_c = None;
slider_gen_param_d = None;
slider_gen_param_e = None;

label_info = {}
loaded_model = None
generated_model = None
var_list = None

matplotlib.use("TkAgg")

model_classifier = None;
flora_generator = None;
flora_tex_generator = None;
terrain_generator = None;
terrain_tex_generator = None;
struct_generator = None;
struct_tex_generator = None;

def init_gui():
    global loaded_model;
    loaded_model = voxel.VoxelModel(32,32,32);

    utils.glob_categories();

    root = tkinter.Tk();

    # Leftmost pane for texture related options
    texturing_frame = tkinter.Frame(root);
    texturing_frame.grid(column=0,row=0,padx=5,pady=5);

    btn_randomize_texture_options = tkinter.Button(texturing_frame, text="Randomize",command = on_randomize_texture_options);
    btn_randomize_texture_options.grid(column=0,row=0,padx=5,pady=5)

    label_texture_params = tkinter.Label(texturing_frame,text="Texture Parameters:");
    label_texture_params.grid(column=0,row=1,padx=5,pady=5)

    global slider_texture_param_a;
    slider_texture_param_a = tkinter.Scale(texturing_frame, from_=0, to=100, orient=tkinter.HORIZONTAL);
    slider_texture_param_a.grid(column=0,row=2,padx=5,pady=5)

    global slider_texture_param_b;
    slider_texture_param_b = tkinter.Scale(texturing_frame, from_=0, to=100, orient=tkinter.HORIZONTAL);
    slider_texture_param_b.grid(column=0,row=3,padx=5,pady=5)

    global slider_texture_param_c;
    slider_texture_param_c = tkinter.Scale(texturing_frame, from_=0, to=100, orient=tkinter.HORIZONTAL);
    slider_texture_param_c.grid(column=0,row=4,padx=5,pady=5)

    global slider_texture_param_d;
    slider_texture_param_d = tkinter.Scale(texturing_frame, from_=0, to=100, orient=tkinter.HORIZONTAL);
    slider_texture_param_d.grid(column=0,row=5,padx=5,pady=5)

    global slider_texture_param_e;
    slider_texture_param_e = tkinter.Scale(texturing_frame, from_=0, to=100, orient=tkinter.HORIZONTAL);
    slider_texture_param_e.grid(column=0,row=6,padx=5,pady=5)

    btn_repaint_texture = tkinter.Button(texturing_frame, text="Repaint",command = on_repaint_texture);
    btn_repaint_texture.grid(column=0,row=7,padx=5,pady=5)

    # Middle pane for 3D model view
    model_frame = tkinter.Frame(root);
    model_frame.grid(column=1,row=0,padx=5,pady=5);

    btn_plot_model = tkinter.Button(model_frame, text="Plot Model",command = on_plot_model);
    btn_plot_model.grid(column=0,row=0,padx=5,pady=5)

    btn_generate_model = tkinter.Button(model_frame, text="Generate Model",command = on_generate_model);
    btn_generate_model.grid(column=0,row=1,padx=5,pady=5)

    # Rightmost pane for generation related options
    gen_frame = tkinter.Frame(root);
    gen_frame.grid(column=2,row=0,padx=5,pady=5);

    btn_retrain_model = tkinter.Button(gen_frame, text="Retrain Model",command = on_retrain_model);
    btn_retrain_model.grid(column=0,row=0,padx=5,pady=5)

    btn_load_model = tkinter.Button(gen_frame, text="Load Model",command = on_load_model);
    btn_load_model.grid(column=0,row=1,padx=5,pady=5)

    label_model_type = tkinter.Label(gen_frame,text="Model Type:");
    label_model_type.grid(column=0,row=2,padx=20,pady=5)

    global var_list;
    var_list = tkinter.StringVar(root);
    var_list.set("Flora")

    dropdown_model_type = tkinter.OptionMenu(gen_frame, var_list, *utils.CATEGORIES)
    dropdown_model_type.grid(column=0,row=3,padx=5,pady=3)

    # Rightmostest pane for generation related parameters
    gen_param_frame = tkinter.Frame(root);
    gen_param_frame.grid(column=3,row=0,padx=5,pady=5);

    label_sensitivity = tkinter.Label(gen_param_frame,text="Generator Cutoff:");
    label_sensitivity.grid(column=0,row=0,padx=20,pady=5)

    global slider_gen_param_a;
    slider_gen_param_a = tkinter.Scale(gen_param_frame, from_=0, to=100, orient=tkinter.HORIZONTAL);
    slider_gen_param_a.set(50)
    slider_gen_param_a.grid(column=0,row=1,padx=5,pady=5)

    btn_randomize_gen_options = tkinter.Button(gen_param_frame, text="Randomize",command = on_randomize_gen_options);
    btn_randomize_gen_options.grid(column=0,row=2,padx=5,pady=5)

    label_gen_params = tkinter.Label(gen_param_frame,text="Generator Parmeters:");
    label_gen_params.grid(column=0,row=3,padx=20,pady=5)

    global slider_gen_param_b;
    slider_gen_param_b = tkinter.Scale(gen_param_frame, from_=0, to=100, orient=tkinter.HORIZONTAL);
    slider_gen_param_b.set(50)
    slider_gen_param_b.grid(column=0,row=4,padx=5,pady=5)

    global slider_gen_param_c;
    slider_gen_param_c = tkinter.Scale(gen_param_frame, from_=0, to=100, orient=tkinter.HORIZONTAL);
    slider_gen_param_c.set(50)
    slider_gen_param_c.grid(column=0,row=5,padx=5,pady=5)

    global slider_gen_param_d;
    slider_gen_param_d = tkinter.Scale(gen_param_frame, from_=0, to=100, orient=tkinter.HORIZONTAL);
    slider_gen_param_d.set(50)
    slider_gen_param_d.grid(column=0,row=6,padx=5,pady=5)

    global slider_gen_param_e;
    slider_gen_param_e = tkinter.Scale(gen_param_frame, from_=0, to=100, orient=tkinter.HORIZONTAL);
    slider_gen_param_e.set(50)
    slider_gen_param_e.grid(column=0,row=7,padx=5,pady=5)

    # export pane
    export_frame = tkinter.Frame(root);
    export_frame.grid(column=4,row=0,padx=5,pady=5);

    label_gen_params = tkinter.Label(export_frame,text="Export:");
    label_gen_params.grid(column=0,row=0,padx=20,pady=5)

    btn_export_xraw = tkinter.Button(export_frame, text="XRAW",command = on_export_xraw);
    btn_export_xraw.grid(column=0,row=1,padx=5,pady=5)

    btn_export_obj = tkinter.Button(export_frame, text="OBJ",command = on_export_obj);
    btn_export_obj.grid(column=0,row=2,padx=5,pady=5)

    btn_export_off = tkinter.Button(export_frame, text="OFF",command = on_export_off);
    btn_export_off.grid(column=0,row=3,padx=5,pady=5)

    # load pretrained models

    load_existing_models();
    global generated_model;
    generated_model = voxel.VoxelModel(32,32,32)

    #global label_info;
    #label_info = tkinter.Label(root,text="");
    #label_info.grid(column=0,columnspan=2,row=2,padx=32,pady=5)

    on_randomize_texture_options();
    root.resizable(False,False);
    root.mainloop();

def on_export_off():
    fn = filedialog.asksaveasfilename(defaultextension=".xraw")
    if fn is None:
        return
    generated_model.export_off(fn)

def on_export_obj():
    fn = filedialog.asksaveasfilename(defaultextension=".xraw")
    if fn is None:
        return
    generated_model.export_obj(fn)

def on_export_xraw():
    fn = filedialog.asksaveasfilename(defaultextension=".xraw")
    if fn is None:
        return
    generated_model.export_xraw(fn)

def load_existing_models():
    global model_classifier;
    if utils.is_category_pretrained("Class"):
        print("Classifier has been pretrained!");
        model_classifier = utils.load_model("Class");
    else:
        print("Classifier has not been trained! Training...");
        model_classifier = utils.pretrain_model("Class");
    global flora_generator;
    if utils.is_category_pretrained("Flora"):
        print("Flora Model has been pretrained!");
        flora_generator = utils.load_model("Flora");
    else:
        print("Flora Model has not been trained! Training...");
        flora_generator = utils.pretrain_model("Flora");
    global terrain_generator;
    if utils.is_category_pretrained("Terrain"):
        print("Terrain Model has been pretrained!");
        terrain_generator = utils.load_model("Terrain");
    else:
        print("Terrain Model has not been trained! Training...");
        terrain_generator = utils.pretrain_model("Terrain");
    # Terrain texture
    global terrain_tex_generator;
    if utils.is_category_pretrained("TerrainTex"):
        print("Terrain Tex Model has been pretrained!");
        terrain_tex_generator = utils.load_model("TerrainTex");
    else:
        print("Terrain Tex Model has not been trained! Training...");
        terrain_tex_generator = utils.pretrain_model("TerrainTex");
    # Flora texture
    global flora_tex_generator;
    if utils.is_category_pretrained("FloraTex"):
        print("Flora Tex Model has been pretrained!");
        flora_tex_generator = utils.load_model("FloraTex");
    else:
        print("Flora Tex Model has not been trained! Training...");
        flora_tex_generator = utils.pretrain_model("FloraTex");

    global struct_generator;
    if utils.is_category_pretrained("Struct"):
        print("Struct Model has been pretrained!");
        struct_generator = utils.load_model("Struct");
    else:
        print("Struct Model has not been trained! Training...");
        struct_generator = utils.pretrain_model("Struct");
    # Terrain texture
    global struct_tex_generator;
    if utils.is_category_pretrained("StructTex"):
        print("Struct Tex Model has been pretrained!");
        struct_tex_generator = utils.load_model("StructTex");
    else:
        print("Struct Tex Model has not been trained! Training...");
        struct_tex_generator = utils.pretrain_model("StructTex");

def on_retrain_model():
    global var_list;
    if var_list.get() == "Flora":
        global flora_generator;
        global flora_tex_generator;
        flora_generator = utils.pretrain_model("Flora");
        flora_tex_generator = utils.pretrain_model("FloraTex");
    elif var_list.get() == "Terrain":
        global terrain_generator;
        global terrain_tex_generator;
        terrain_generator = utils.pretrain_model("Terrain");
        terrain_tex_generator = utils.pretrain_model("TerrainTex");
    elif var_list.get() == "Structure":
        global struct_generator;
        global struct_tex_generator;
        terrain_generator = utils.pretrain_model("Terrain");
        terrain_tex_generator = utils.pretrain_model("TerrainTex");

def on_generate_model():
    global var_list;
    global loaded_model;
    global generated_model;
    global slider_gen_param_a;
    data = loaded_model.as_colorless_array().reshape(1,32,32,32,1)
    global slider_gen_param_b;
    global slider_gen_param_c;
    global slider_gen_param_d;
    global slider_gen_param_e;
    bias = float((slider_gen_param_a.get() / 100.0))
    if var_list.get() == "Flora":
        global flora_generator;
        latent_space = flora_generator.get_layer(name='encoder')(data)
        latent_space = latent_space[2]

        change_matrix = utils.get_change_matrix(tf.shape(latent_space),slider_gen_param_b.get(), slider_gen_param_c.get(), slider_gen_param_d.get(), slider_gen_param_e.get())
        latent_space += change_matrix
        data = flora_generator.get_layer(name='decoder')(latent_space)
    elif var_list.get() == "Terrain":
        global terrain_generator;
        latent_space = terrain_generator.get_layer(name='encoder')(data)
        latent_space = latent_space[2]

        change_matrix = utils.get_change_matrix(tf.shape(latent_space),slider_gen_param_b.get(), slider_gen_param_c.get(), slider_gen_param_d.get(), slider_gen_param_e.get())
        latent_space += change_matrix
        data = terrain_generator.get_layer(name='decoder')(latent_space)
    elif var_list.get() == "Structure":
        global struct_generator;
        latent_space = struct_generator.get_layer(name='encoder')(data)
        latent_space = latent_space[2]

        change_matrix = utils.get_change_matrix(tf.shape(latent_space),slider_gen_param_b.get(), slider_gen_param_c.get(), slider_gen_param_d.get(), slider_gen_param_e.get())
        latent_space += change_matrix
        data = struct_generator.get_layer(name='decoder')(latent_space)
        print(data)
        print(type(data))
    data = data.numpy()
    data = (data.reshape((32,32,32),order='F')*bias + loaded_model.as_colorless_array().reshape((32,32,32),order='F')*(1.0-bias))
    generated_model.load_from_dataarray(data,offset=50)
    on_repaint_texture()

def on_plot_model():
    generated_model.plot_voxels();

def on_repaint_texture():
    global var_list;
    global loaded_model;
    global generated_model;
    global slider_gen_param_a;
    global slider_texture_param_a;
    global slider_texture_param_b;
    global slider_texture_param_c;
    global slider_texture_param_d;
    global slider_texture_param_e;
    color_data = loaded_model.as_colored_array()[1].reshape(32,32,32);
    if var_list.get() == "Terrain":
        global terrain_tex_generator;
        generated_model.pallete = loaded_model.pallete.copy()
        latent_space = terrain_tex_generator.get_layer(name='encoder')(generated_model.as_colorless_array().reshape(1,32,32,32,1))
        latent_space = latent_space[2]
        change_matrix = utils.get_change_matrix(tf.shape(latent_space),slider_texture_param_b.get(), slider_texture_param_c.get(), slider_texture_param_d.get(), slider_texture_param_e.get())
        latent_space += change_matrix
        color_data = terrain_tex_generator.get_layer(name='decoder')(latent_space)
        color_data = color_data.numpy()
        bias = float((slider_texture_param_a.get() / 100.0))
        color_data = (color_data.reshape((32,32,32),order='F')*bias + loaded_model.as_colored_array()[1].reshape((32,32,32),order='F')*(1.0-bias))
    elif var_list.get() == "Flora":
        global flora_tex_generator;
        generated_model.pallete = loaded_model.pallete.copy()
        latent_space = flora_tex_generator.get_layer(name='encoder')(generated_model.as_colorless_array().reshape(1,32,32,32,1))
        latent_space = latent_space[2]
        change_matrix = utils.get_change_matrix(tf.shape(latent_space),slider_texture_param_b.get(), slider_texture_param_c.get(), slider_texture_param_d.get(), slider_texture_param_e.get())
        latent_space += change_matrix
        color_data = flora_tex_generator.get_layer(name='decoder')(latent_space)
        color_data = color_data.numpy()
        bias = float((slider_texture_param_a.get() / 100.0))
        color_data = (color_data.reshape((32,32,32),order='F')*bias + loaded_model.as_colored_array()[1].reshape((32,32,32),order='F')*(1.0-bias))
    elif var_list.get() == "Structure":
        global struct_tex_generator;
        generated_model.pallete = loaded_model.pallete.copy()
        latent_space = struct_tex_generator.get_layer(name='encoder')(generated_model.as_colorless_array().reshape(1,32,32,32,1))
        latent_space = latent_space[2]
        change_matrix = utils.get_change_matrix(tf.shape(latent_space),slider_texture_param_b.get(), slider_texture_param_c.get(), slider_texture_param_d.get(), slider_texture_param_e.get())
        latent_space += change_matrix
        color_data = struct_tex_generator.get_layer(name='decoder')(latent_space)
        color_data = color_data.numpy()
        bias = float((slider_texture_param_a.get() / 100.0))
        color_data = (color_data.reshape((32,32,32),order='F')*bias + loaded_model.as_colored_array()[1].reshape((32,32,32),order='F')*(1.0-bias))
    generated_model.load_from_colored_dataarray((generated_model.as_colorless_array().reshape(32,32,32), color_data), slider_gen_param_a.get())

def on_randomize_gen_options():
    global slider_gen_param_b;
    slider_gen_param_b.set(random.randint(0, 100));
    global slider_gen_param_c;
    slider_gen_param_c.set(random.randint(0, 100));
    global slider_gen_param_d;
    slider_gen_param_d.set(random.randint(0, 100));
    global slider_gen_param_e;
    slider_gen_param_e.set(random.randint(0, 100));

def on_randomize_texture_options():
    #global slider_texture_param_a;
    #slider_texture_param_a.set(random.randint(0, 100));
    global slider_texture_param_b;
    slider_texture_param_b.set(random.randint(0, 100));
    global slider_texture_param_c;
    slider_texture_param_c.set(random.randint(0, 100));
    global slider_texture_param_d;
    slider_texture_param_d.set(random.randint(0, 100));
    global slider_texture_param_e;
    slider_texture_param_e.set(random.randint(0, 100));
    #on_repaint_texture();

def classify_model():
    global generated_model;
    mdl_class = model_classifier.predict(generated_model.as_colorless_array().reshape(1,32,32,32,1))[0]
    print(mdl_class)
    global var_list;

    if mdl_class[0] > mdl_class[1] and mdl_class[0] > mdl_class[2]:
        mdl_class = 0
    elif mdl_class[1] > mdl_class[0] and mdl_class[1] > mdl_class[2]:
        mdl_class = 1
    else:
        mdl_class = 2

    if mdl_class == 0:
        var_list.set("Structure")
    elif mdl_class == 1:
        var_list.set("Flora")
    else:
        var_list.set("Terrain")

def on_load_model():
    filename = filedialog.askopenfilename(
        initialdir = "",
        title = "Select a Model",
        filetypes = (
            ("All files","*"),
            ("OBJ Files","*.obj"),
            ("OFF Files","*.off"),
            ("XRAW Files","*.xraw")
        )
    )
    if filename != "":
        global loaded_model;
        global generated_model;
        loaded_model = voxel.load_from_path(filename)
        generated_model = loaded_model.copy()
        classify_model()
        #generated_model.pallete = loaded_model.pallete.copy()
        #generated_model.load_from_colored_dataarray(loaded_model.as_colored_array());