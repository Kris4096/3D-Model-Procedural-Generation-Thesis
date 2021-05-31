
use std::{fmt::format, fs::File, usize};
use std::io::prelude::*;
use std::{cmp::max};
use image::io::Reader;

use crate::math::{Vector3};
use crate::{math::{BoundingBox3D}, model::{Model}};

#[derive(Debug,Clone, Copy)]
pub struct VoxelColor {
    pub r: u8,
    pub g: u8,
    pub b: u8,
}

impl VoxelColor {
    pub fn new(r: u8, g: u8, b: u8) -> Self {
        Self {r,g,b}
    }
}

#[derive(Debug, Clone)]
pub struct VoxelModel {
    pub width: u32,
    pub height: u32,
    pub depth: u32,
    pub voxels: Vec<Option<u16>>,
    pub pallette: Vec<VoxelColor>,
}

impl VoxelModel {
    pub fn new(width: u32, height: u32, depth: u32) -> Self {
        let mut voxels = Vec::new();
        voxels.reserve((width*height*depth) as usize);
        for _ in 0..(width*height*depth) {
            voxels.push(None)
        }
        Self {
            width: width,
            height: height,
            depth: depth,
            voxels: voxels,
            pallette: Vec::new()
        }
    }
    pub fn set_voxel(&mut self, x: u32, y: u32, z:u32, color_index: u16) {
        let i = (x+self.width*y+self.width*self.height*z) as usize;
        if i >= self.voxels.len() {
            panic!("Voxel out of range! {} {} {} is outside of model range {} {} {}", x, y, z, self.width, self.height, self.depth);
        }
        if self.pallette.get((color_index) as usize).is_none() {
            panic!("Model does not contain the required color in its pallette!");
        }
        self.voxels[i] = Some(color_index);
    }
    pub fn export_xraw(&self, file_name: &str) {
        println!("Exporting model {} with {} colors.", file_name, self.pallette.len());
        if self.pallette.len() == 0 {
            panic!("Model has no colors. Is this an error?");
        }
        let mut file = File::create(format!("output/{}.xraw",file_name)).unwrap();
        file.write_all(&[88,82,65,87]).unwrap(); // XRAW
        file.write_all(&[0]).unwrap(); // 1b color channel type (0 = unsigned int)
        file.write_all(&[4]).unwrap(); // 1b color channel count (3 = RGB)
        file.write_all(&[8]).unwrap(); // 1b bits per channel (8,16,32)
        file.write_all(&[16]).unwrap(); // 1b bits per index (16 must be used)
        file.write_all(&self.width.to_le_bytes()).unwrap(); // 4b width x
        file.write_all(&self.height.to_le_bytes()).unwrap(); // 4b height y
        file.write_all(&self.depth.to_le_bytes()).unwrap(); // 4b depth z
        file.write_all(&32768u32.to_le_bytes()).unwrap(); // 4b num of pallette colors 32768
    
        let mut buffer = Vec::new();
        buffer.reserve(4*256 + self.voxels.len()*2);

        // voxels
        for vox in &self.voxels {
            if vox.is_none() {
                for byte in &0xFFFFu16.to_le_bytes() {
                    buffer.push(*byte);
                }
            }else{
                for byte in &vox.unwrap().to_le_bytes() {
                    buffer.push(*byte);
                }
            }
        }

        for i in 0..32768 {
            if i < self.pallette.len() {
                let c = &self.pallette[i as usize];
                buffer.push(c.r);
                buffer.push(c.g);
                buffer.push(c.b);
                buffer.push(255);
            }else{
                buffer.push(75);
                buffer.push(75);
                buffer.push(75);
                buffer.push(255);
            }
        }

        file.write_all(&buffer).unwrap();
    }
    pub fn rotation_fixed(&self) -> VoxelModel {
        let mut fixed_model = VoxelModel::new(self.depth, self.width, self.height);
        for pallette in &self.pallette {
            fixed_model.pallette.push(*pallette);
        }
        for x in 0..self.width {
            for y in 0..self.height {
                for z in 0..self.depth {
                    let i = (x+self.width*y+self.width*self.height*z) as usize;
                    if self.voxels[i].is_some() {
                        fixed_model.set_voxel(
                            z, 
                            x, 
                            y, 
                            self.voxels[i].unwrap()
                        );
                    }
                }
            }
        }
        fixed_model
    }
}

pub fn points_in_line(x0: i32, y0: i32, z0:i32, x1: i32, y1: i32, z1:i32) -> Vec<Vector3> {
    let mut result = Vec::new();
    result.push(Vector3::new(x0 as f32, y0 as f32, z0 as f32));
    let dx = (x1 - x0).abs();
    let dy = (y1 - y0).abs();
    let dz = (z1 - z0).abs();
    let xs = {
        if x1 > x0 {
            1
        }else{
            -1
        }
    };
    let ys = {
        if y1 > y0 {
            1
        }else{
            -1
        }
    };
    let zs = {
        if z1 > z0 {
            1
        }else{
            -1
        }
    };

    let mut cx = x0;
    let mut cy = y0;
    let mut cz = z0;

    if dx >= dy && dx >= dz {
        let mut p1 = 2 * dy - dx;
        let mut p2 = 2 * dz - dx;
        while cx != x1 {
            cx += xs;
            if p1 >= 0 {
                cy += ys;
                p1 -= 2*dx;
            }
            if p2 >= 0 {
                cz += zs;
                p2 -= 2*dx;
            }
            p1 += 2*dy;
            p2 += 2*dz;
            result.push(Vector3::new(cx as f32, cy as f32, cz as f32));
        }
    } else if dy >= dx && dy >= dz {
        let mut p1 = 2 * dx - dy;
        let mut p2 = 2 * dz - dy;
        while cy != y1 {
            cy += ys;
            if p1 >= 0 {
                cx += xs;
                p1 -= 2*dy;
            }
            if p2 >= 0 {
                cz += zs;
                p2 -= 2*dy;
            }
            p1 += 2*dx;
            p2 += 2*dz;
            result.push(Vector3::new(cx as f32, cy as f32, cz as f32));
        }
    } else {
        let mut p1 = 2 * dy - dz;
        let mut p2 = 2 * dx - dz;
        while cz != z1 {
            cz += zs;
            if p1 >= 0 {
                cy += ys;
                p1 -= 2*dz;
            }
            if p2 >= 0 {
                cx += xs;
                p2 -= 2*dz;
            }
            p1 += 2*dy;
            p2 += 2*dx;
            result.push(Vector3::new(cx as f32, cy as f32, cz as f32));
        }
    }
    result
}


pub fn voxelize_model(material_path: &str, obj_model: &Model, resolution: u32) -> VoxelModel {
    let bounds = obj_model.calculate_bounds();
    let largest_axis = bounds.size.x.max(bounds.size.y).max(bounds.size.z);
    let mut aspect = Vector3::new(1f32,1f32, 1f32);
    if (largest_axis - bounds.size.x).abs() < f32::EPSILON {
        // x ir largest. x = 32
        aspect.y = bounds.size.y/bounds.size.x;
        aspect.z = bounds.size.z/bounds.size.x;
    }else if (largest_axis - bounds.size.y).abs() < f32::EPSILON {
        // y ir largest. y = 32
        aspect.x = bounds.size.x/bounds.size.y;
        aspect.z = bounds.size.z/bounds.size.y;
    }else{
        // z ir largest. z = 32
        aspect.x = bounds.size.x/bounds.size.z;
        aspect.y = bounds.size.y/bounds.size.z;
    }

    //let mut aspect = Vector3::new(1f32,1f32, 1f32);

    //let aspect = ((resolution as f32) / bounds.size.x, (resolution as f32) / bounds.size.y, (resolution as f32) / bounds.size.z);
    //let aspect = Vector3::new(aspect.0, aspect.1, aspect.2);

    let mut vox_model = VoxelModel::new(
        resolution,
        resolution,
        resolution,
    );

    for mat in &obj_model.materials {
        let path = format!("{}/{}",&material_path,&mat.diffuse_texture);
        if mat.diffuse_texture.is_empty() {
            let color = VoxelColor::new((mat.diffuse[0]*255f32) as u8, (mat.diffuse[1]*255f32) as u8, (mat.diffuse[2]*255f32) as u8);
            vox_model.pallette.push(color);
        }else{
            let img = Reader::open(path).unwrap();
            let img_decode = img.decode().unwrap();
            let img_buffer = img_decode.as_rgba8().unwrap();
            let mut color = Vector3::new(0f32, 0f32, 0f32);
            let pixel_count = img_buffer.pixels().len() as f32;
            for p in img_buffer.pixels() {
                if p.0[3] > 100 {
                    let r = p.0[0];
                    let g = p.0[1];
                    let b = p.0[2];
                    color = color.add(&Vector3::new(r as f32 / pixel_count, g as f32 / pixel_count, b as f32 / pixel_count));
                }
            }
            let color = VoxelColor::new(color.x as u8, color.y as u8, color.z as u8);
            vox_model.pallette.push(color);
        }
        //println!("Texture: {:?}", mat);
    }

    let t_size = Vector3::new((vox_model.width as f32 *aspect.x-1f32) as f32,(vox_model.height as f32 *aspect.y-1f32) as f32,(vox_model.depth as f32 *aspect.z-1f32) as f32);

    for face in &obj_model.faces {
        let v0 = face.vertices[0].vertex.sub(&bounds.position).div(&bounds.size).mul(&t_size);
        let v1 = face.vertices[1].vertex.sub(&bounds.position).div(&bounds.size).mul(&t_size);
        let v2 = face.vertices[2].vertex.sub(&bounds.position).div(&bounds.size).mul(&t_size);

        let c_index = face.material_id.unwrap() as u16;

        for p0 in points_in_line(v0.x as i32, v0.y as i32, v0.z as i32, v1.x as i32, v1.y as i32, v1.z as i32) {
            for p in points_in_line(p0.x as i32, p0.y as i32, p0.z as i32, v2.x as i32, v2.y as i32, v2.z as i32) {
                vox_model.set_voxel(p.x as u32, p.y as u32, p.z as u32, c_index);
            }
        }

        for p0 in points_in_line(v1.x as i32, v1.y as i32, v1.z as i32, v2.x as i32, v2.y as i32, v2.z as i32) {
            for p in points_in_line(p0.x as i32, p0.y as i32, p0.z as i32, v0.x as i32, v0.y as i32, v0.z as i32) {
                vox_model.set_voxel(p.x as u32, p.y as u32, p.z as u32, c_index);
            }
        }

        for p0 in points_in_line(v2.x as i32, v2.y as i32, v2.z as i32, v0.x as i32, v0.y as i32, v0.z as i32) {
            for p in points_in_line(p0.x as i32, p0.y as i32, p0.z as i32, v1.x as i32, v1.y as i32, v1.z as i32) {
                vox_model.set_voxel(p.x as u32, p.y as u32, p.z as u32, c_index);
            }
        }
    }

    vox_model.rotation_fixed()
}

// assume x = 1f32
pub fn get_aspect_ratios(bounds: &BoundingBox3D) -> (f32,f32) {
    (bounds.size.y/bounds.size.x,bounds.size.z/bounds.size.x)
}