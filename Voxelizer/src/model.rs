use tobj::Material;
use crate::{math::*, ott_loader::load_off_file};

pub struct Model {
    pub materials: Vec<Material>,
    pub faces: Vec<ModelTriangle>,
}

#[derive(Debug)]
pub struct ModelTriangle {
    pub vertices: [MeshVertex;3],
    pub material_id: Option<usize>,
}

#[derive(Debug,Clone, Copy)]
pub struct MeshVertex {
    pub vertex: Vector3,
    pub normal: Option<Vector3>,
    pub uv: Option<Vector2>
}

impl Model {
    pub fn load_from_obj_file(file_name: &str) -> Self {
        let (models, materials) = tobj::load_obj(&file_name, true).expect("Failed to load file");
        let mut mesh_triangles = Vec::new();
        for model in models {
            let mesh = model.mesh;
            let mut mesh_vertices = Vec::new();

            let has_texture = mesh.texcoords.len() != 0;
            let has_normals = mesh.normals.len() != 0;

            if has_normals && has_texture {
                for i in &mesh.indices {
                    let i = *i as usize;
                    let pos = [mesh.positions[i * 3], mesh.positions[i * 3 + 1], mesh.positions[i * 3 + 2]];
                    let normal = [mesh.normals[i * 3], mesh.normals[i * 3 + 1], mesh.normals[i * 3 + 2]];
                    let texcoord = [mesh.texcoords[i * 2], mesh.texcoords[i * 2 + 1]];
                    mesh_vertices.push(MeshVertex {vertex: Vector3::from_array(&pos), normal: Some(Vector3::from_array(&normal)), uv: Some(Vector2::from_array(&texcoord))})
                }
            }else if has_texture {
                for i in &mesh.indices {
                    let i = *i as usize;
                    let pos = [mesh.positions[i * 3], mesh.positions[i * 3 + 1], mesh.positions[i * 3 + 2]];
                    let texcoord = [mesh.texcoords[i * 2], mesh.texcoords[i * 2 + 1]];
                    mesh_vertices.push(MeshVertex {vertex: Vector3::from_array(&pos), normal: None, uv: Some(Vector2::from_array(&texcoord))})
                }
            }else if has_normals {
                for i in &mesh.indices {
                    let i = *i as usize;
                    let pos = [mesh.positions[i * 3], mesh.positions[i * 3 + 1], mesh.positions[i * 3 + 2]];
                    let normal = [mesh.normals[i * 3], mesh.normals[i * 3 + 1], mesh.normals[i * 3 + 2]];
                    mesh_vertices.push(MeshVertex {vertex: Vector3::from_array(&pos), normal: Some(Vector3::from_array(&normal)), uv: None})
                }
            }else{
                for i in &mesh.indices {
                    let i = *i as usize;
                    let pos = [mesh.positions[i * 3], mesh.positions[i * 3 + 1], mesh.positions[i * 3 + 2]];
                    mesh_vertices.push(MeshVertex {vertex: Vector3::from_array(&pos), normal: None, uv: None})
                }
            }
            for i in mesh_vertices.chunks(3) {
                mesh_triangles.push(ModelTriangle {
                    vertices: [i[0],i[1],i[2]],
                    material_id: mesh.material_id
                })
            }
        }
        Model {
            materials: materials,
            faces: mesh_triangles
        }
    }
    pub fn load_from_off_file(file_name: &str, randomize_color: bool) -> Self {
        let result = load_off_file(file_name, randomize_color);
        result.unwrap()
    }
    pub fn calculate_bounds(&self) -> BoundingBox3D {
        let mut min_x = self.faces[0].vertices[0].vertex.x;
        let mut max_x = min_x;
        let mut min_y = self.faces[0].vertices[0].vertex.y;
        let mut max_y = min_y;
        let mut min_z = self.faces[0].vertices[0].vertex.z;
        let mut max_z = min_z;
        for face in &self.faces {
            let triangle = face.vertices;
            for i in 0..3 {
                let pos = triangle[i].vertex;
                if pos.x > max_x { max_x = pos.x; }
                if pos.x < min_x { min_x = pos.x; }
                if pos.y > max_y { max_y = pos.y; }
                if pos.y < min_y { min_y = pos.y; }
                if pos.z > max_z { max_z = pos.z; }
                if pos.z < min_z { min_z = pos.z; }
            }
        }
        let bounding_box_position = Vector3::new(min_x, min_y, min_z);
        let bounding_box_size = Vector3::new(max_x-min_x, max_y-min_y, max_z-min_z);
        BoundingBox3D {position: bounding_box_position, size: bounding_box_size}
    }
}