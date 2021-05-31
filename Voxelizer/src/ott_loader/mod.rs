
use core::f32;
use std::fs::File;
use std::io::{self,BufRead};
use std::path::Path;

use rand::{Rng, prelude::ThreadRng};
use tobj::Material;

use crate::{math::Vector3, model::{MeshVertex, Model, ModelTriangle}};

pub fn foo_bar() {
    print!("ABC")
}

enum OFFReadState {
    FirstLine,
    DataLine,
    Vertices,
    Faces
}

pub fn load_off_file(file_path: &str, randomize_color: bool) -> Option<Model> {
    let mut lines = read_lines(file_path).unwrap();

    let mut vertice_count: u32 = 0;
    let mut face_count: u32 = 0;
    let mut current_count = 0;

    let mut vertice_list = Vec::new();
    let mut triangle_list: Vec<ModelTriangle> = Vec::new();

    let mut file_state = OFFReadState::FirstLine;

    let mut possible_colors = Vec::new();
    let mut material = Material::empty();
    material.diffuse = [0.7f32, 0.7f32, 0.7f32];
    possible_colors.push(material.clone());

    let mut rng = rand::thread_rng();
    let max_rand_colors = rng.gen_range(0..6);

    for line in lines {
        if let Ok(line) = line {
            if line.contains("#") {
                continue;
            }
            match file_state {
                OFFReadState::FirstLine => {
                    if line != "OFF" { return None; }
                    file_state = OFFReadState::DataLine;
                    continue;
                }
                OFFReadState::DataLine => {
                    let line_data: Vec<&str> = line.split(" ").collect();
                    vertice_count = line_data[0].parse().unwrap();
                    face_count = line_data[1].parse().unwrap();
                    file_state = OFFReadState::Vertices;
                    continue;
                }
                OFFReadState::Vertices => {
                    let line_data: Vec<&str> = line.split(" ").collect();
                    let x = line_data[0].parse().unwrap();
                    let y = line_data[1].parse().unwrap();
                    let z = line_data[2].parse().unwrap();
                    vertice_list.push(Vector3::new(x, y, z));
                    current_count += 1;
                    if current_count >= vertice_count {
                        file_state = OFFReadState::Faces;
                        current_count = 0;
                    }
                    continue;
                }
                OFFReadState::Faces => {
                    let line_data: Vec<&str> = line.split(" ").collect();
                    let v_count: u32 = line_data[0].parse().unwrap();
                    let color_index = {
                        if v_count > line_data.len() as u32 -1 {
                            // Contains color data
                            let b: u32 = line_data[line_data.len()-1].parse().unwrap();
                            let g: u32 = line_data[line_data.len()-2].parse().unwrap();
                            let r: u32 = line_data[line_data.len()-3].parse().unwrap();
                            material.diffuse = [r as f32 / 255f32, g as f32 / 255f32, b as f32 / 255f32];
                            let (color_exists, color_index) = check_if_color_already_exists(&possible_colors, &material);
                            if color_exists {
                                color_index
                            }else{
                                possible_colors.push(material.clone());
                                possible_colors.len()-1
                            }
                        }else{
                            if randomize_color {
                                if possible_colors.len() > max_rand_colors {
                                    rng.gen_range(0..possible_colors.len())
                                }else{
                                    material.diffuse = get_random_color(&mut rng);
                                    let (color_exists, color_index) = check_if_color_already_exists(&possible_colors, &material);
                                    if color_exists {
                                        //println!("{}", color_index);
                                        color_index
                                    }else{
                                        possible_colors.push(material.clone());
                                        possible_colors.len()-1
                                    }
                                }
                            }else{
                                0
                            }
                        }
                    };
                    //println!("{}", color_index);
                    match v_count {
                        3 => {
                            let v1 = vertice_list[line_data[1].parse::<usize>().unwrap()];
                            let v2 = vertice_list[line_data[2].parse::<usize>().unwrap()];
                            let v3 = vertice_list[line_data[3].parse::<usize>().unwrap()];
                            let triangle = ModelTriangle {
                                vertices: [MeshVertex {
                                    vertex: v1,
                                    normal: None,
                                    uv: None,
                                },
                                MeshVertex {
                                    vertex: v2,
                                    normal: None,
                                    uv: None,
                                },
                                MeshVertex {
                                    vertex: v3,
                                    normal: None,
                                    uv: None,
                                }],
                                material_id: Some(color_index),
                            };
                            triangle_list.push(triangle);
                        }
                        _ => {
                            panic!("Unhandled vertex count! {}", v_count);
                        }
                    }
                    current_count += 1;
                    if current_count >= face_count {
                        break;
                    }
                    continue;
                }
            }
        }
    }

    Some(Model {
        materials: possible_colors,
        faces: triangle_list,
    })
}

pub fn get_random_color(rng: &mut ThreadRng) -> [f32;3] {
    let possible_color = vec![
        [1f32, 0f32, 0f32],
        [0f32, 1f32, 0f32],
        [0f32, 0f32, 1f32],
        [0f32, 0.2f32, 0.8f32],
        [0.2f32, 0f32, 0.8f32],
        [0f32, 0.8f32, 0.2f32],
        [0.2f32, 0.8f32, 0f32],
        [0.8f32, 0.2f32, 0f32],
        [0.8f32, 0f32, 0.2f32],
        [0.1f32, 0.3f32, 0.6f32],
        [0.3f32, 0.1f32, 0.6f32],
        [0.1f32, 0.6f32, 0.3f32],
        [0.3f32, 0.6f32, 0.1f32],
        [0.6f32, 0.3f32, 0.1f32],
        [0.3f32, 0.1f32, 0.3f32],
    ];
    possible_color[rng.gen_range(0..possible_color.len())]
}

pub fn check_if_color_already_exists(pallete: &Vec<Material>, color: &Material) -> (bool,usize) {
    for (i,c) in pallete.iter().enumerate() {
        let r = c.diffuse[0];
        let g = c.diffuse[1];
        let b = c.diffuse[2];
        if r-color.diffuse[0] <= f32::EPSILON && g-color.diffuse[1] <= f32::EPSILON && b-color.diffuse[2] <= f32::EPSILON {
            return (true,i);
        }
    }
    (false,0)
}

// The output is wrapped in a Result to allow matching on errors
// Returns an Iterator to the Reader of the lines of the file.
fn read_lines<P>(filename: P) -> io::Result<io::Lines<io::BufReader<File>>>
where P: AsRef<Path>, {
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}