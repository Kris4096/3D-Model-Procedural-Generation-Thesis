
mod model;
mod math;
mod voxel;
mod ott_loader;

use std::{env, fs, path::{self, Path}, str, thread::panicking};

use model::Model;

use crate::{voxel::voxelize_model};

fn parse_model_by_extension(model_path: &path::Path, randomize_color: bool) -> Option<Model> {
    let extension = model_path.extension().expect("Model file must have extension!").to_str().unwrap();
    match extension {
        "obj" => {
            Some(Model::load_from_obj_file(model_path.to_str().unwrap()))
        }
        "off" => {
            Some(Model::load_from_off_file(model_path.to_str().unwrap(), randomize_color))
        }
        _ => {
            None
        }
    }
}

fn load_all_from_folder(path: &str) -> Vec<String> {
    let mut result = Vec::new();
    let path = Path::new(path);
    for entry in fs::read_dir(path).unwrap() {
        let entry = entry.unwrap();
        let sub_path = entry.path();
        if sub_path.is_dir() {
            let children = load_all_from_folder(&sub_path.to_str().unwrap());
            for c in children {
                result.push(c);
            }
        }else{
            let model_extension = sub_path.extension().unwrap().to_str().unwrap();
            if model_extension == "off" || model_extension == "obj" {
                result.push(sub_path.to_str().unwrap().to_string());
            }
        }
    }
    result
}

fn main() {
    let args : Vec<String> = env::args().collect();
    if args.len() < 3 {
        println!("Please specify model path and resolution!");
        return;
    }
    let resolution: u32 = args[2].parse().unwrap();
    let model_path = &args[1];
    let mut randomize_color = false;

    if args.len() > 3 {
        let option: String = args[3].parse().unwrap();
        if option == "color" {
            println!("Material color will be randomized!");
            randomize_color = true;
        }
    }

    println!("Voxelizing model at {} with resolution {}...", model_path, resolution);

    let path = path::Path::new(model_path);

    let models_to_load = {
        if path.is_dir() {
            load_all_from_folder(path.to_str().unwrap())
        }else{
            vec![path.to_str().unwrap().to_string()]
        }
    };

    for model_path in models_to_load {
        let path = Path::new(&model_path);
        let model = parse_model_by_extension(path,randomize_color);
        if !model.is_some() {
            println!("Could not parse model!");
            return;
        }
        //println!("P: {:?}", &get_folder_of_item(&path));
        let model = model.unwrap();
        let vox_model = voxelize_model(&get_folder_of_item(&path), &model, resolution);
        let file_name= path.file_stem().unwrap();
        vox_model.export_xraw(file_name.to_str().unwrap());
    }
    println!("Model voxelization complete!");
}

fn get_folder_of_item(path: &Path) -> String {
    //println!("Seperating {:?}", path);
    let mut ancestors = path.ancestors();
    ancestors.next();
    let item = ancestors.next().unwrap();
    item.to_str().unwrap().to_string()
}