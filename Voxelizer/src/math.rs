#[derive(Debug, Clone, Copy)]
pub struct Vector3 {
    pub x : f32,
    pub y : f32,
    pub z : f32
}

impl Vector3 {
    pub fn new(x: f32, y: f32, z: f32) -> Self {
        Vector3 { x: x, y: y, z: z }
    }
    pub fn from_vec3(vec3: &Vector3) -> Self {
        Vector3 { x: vec3.x, y: vec3.y, z: vec3.z }
    }
    pub fn from_array(array: &[f32; 3]) -> Self {
        Vector3 { x: array[0], y: array[1], z : array[2] }
    }
    pub fn add(&self, other: &Vector3) -> Vector3 {
        Vector3::new(self.x+other.x,self.y+other.y,self.z+other.z)
    }
    pub fn sub(&self, other: &Vector3) -> Vector3 {
        Vector3::new(self.x-other.x,self.y-other.y,self.z-other.z)
    }
    pub fn div(&self, other: &Vector3) -> Vector3 {
        Vector3::new(self.x/other.x,self.y/other.y,self.z/other.z)
    }
    pub fn mul(&self, other: &Vector3) -> Vector3 {
        Vector3::new(self.x*other.x,self.y*other.y,self.z*other.z)
    }
    pub fn align_to_grid(&mut self, other: &Vector3) {
        self.x = (self.x as i32) as f32;
        self.y = (self.y as i32) as f32;
        self.z = (self.z as i32) as f32;
    }
    pub fn cross_product(&self, other: &Vector3) -> Vector3 {
        Vector3::new(
            self.y*other.z - self.z*other.y,
            self.z*other.x - self.x*other.z,
            self.x*other.y-self.y*other.x
        )
    }
    pub fn dot_product(&self, other: &Vector3) -> f32 {
        self.x*other.x + self.y*other.y + self.z*other.z
    }
}

#[derive(Debug, Clone, Copy)]
pub struct Vector2 {
    pub x : f32,
    pub y : f32,
}

impl Vector2 {
    pub fn new(x: f32, y: f32) -> Self {
        Vector2 { x: x, y: y }
    }
    pub fn from_vec3(vec3: &Vector2) -> Self {
        Vector2 { x: vec3.x, y: vec3.y }
    }
    pub fn from_array(array: &[f32; 2]) -> Self {
        Vector2 { x: array[0], y: array[1] }
    }
}

#[derive(Debug)]
pub struct BoundingBox3D {
    pub position : Vector3,
    pub size : Vector3
}

#[derive(Debug)]
pub struct BoundingBox2D {
    pub position : Vector2,
    pub size : Vector2
}

pub fn find_bounding_box_2d(positions: &Vec<Vector2>) -> BoundingBox2D {
    let mut max_x = 0f32;
    let mut min_x = 0f32;
    let mut max_y = 0f32;
    let mut min_y = 0f32;

    for pos in positions {
        let x = pos.x;
        let y = pos.y;
        if max_x < x { max_x = x; }
        if min_x > x { min_x = x; }
        if max_y < y { max_y = y; }
        if min_y > y { min_y = y; }
    }

    println!("{} {} {} {}", max_x, min_x, max_y, min_y);

    let bounding_box_position = Vector2::new(min_x, min_y);
    let bounding_box_size = Vector2::new(max_x-min_x, max_y-min_y);

    BoundingBox2D {position: bounding_box_position, size: bounding_box_size}
}

pub fn find_bounding_box_3d(positions: &Vec<Vector3>) -> BoundingBox3D {
    let mut max_x = 0f32;
    let mut min_x = 0f32;
    let mut max_y = 0f32;
    let mut min_y = 0f32;
    let mut max_z = 0f32;
    let mut min_z = 0f32;

    for pos in positions {
        let x = pos.x;
        let y = pos.x;
        let z = pos.x;
        if max_x < x { max_x = x; }
        if min_x > x { min_x = x; }
        if max_y < y { max_y = y; }
        if min_y > y { min_y = y; }
        if max_z < z { max_z = z; }
        if min_z > z { min_z = z; }
    }

    let bounding_box_position = Vector3::new(min_x, min_y, min_z);
    let bounding_box_size = Vector3::new(max_x-min_x, max_y-min_y, max_z-min_z);

    BoundingBox3D {position: bounding_box_position, size: bounding_box_size}
}

// https://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
// pub fn ray_intersects_triangle(origin: &Vector3, direction: &Vector3, triangle: &ModelTriangle) -> Option<Vector3> {
//     let v0 = triangle.vertices[0].vertex;
//     let v1 = triangle.vertices[1].vertex;
//     let v2 = triangle.vertices[2].vertex;

//     let edge1 = v1.sub(&v0);
//     let edge2 = v2.sub(&v0);
//     let h = direction.cross_product(&edge2);
//     let a = edge1.dot_product(&h);
//     if a > -f32::EPSILON && a < f32::EPSILON {
//         return None;
//     }
//     let f = 1f32 / a;
//     let s = origin.sub(&v0);
//     let u = f * s.dot_product(&h);
//     if u < 0f32 || u > 1f32 {
//         return None;
//     }
//     let q = s.cross_product(&edge1);
//     let v = f * direction.dot_product(&q);
//     if v < 0f32 || v > 1f32 {
//         return None;
//     }

//     let t = f * edge2.dot_product(&q);
//     if t > f32::EPSILON {
//         Some(origin.add(&direction.mul(&Vector3::new(t, t, t))))
//     }else{
//         None
//     }
// }