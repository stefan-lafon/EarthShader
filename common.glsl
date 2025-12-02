// EARTHSHADER STANDARD LIBRARY (v1.0)
// Injected automatically at the top of every generated shader.
// Do not generate these functions. Call them directly.

#define PI 3.14159265359
#define TWO_PI 6.28318530718

// --- UTILITIES ---

// Convert HSV color space to RGB
vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

// 2D Rotation matrix
mat2 rotate2d(float angle) {
    return mat2(cos(angle), -sin(angle), sin(angle), cos(angle));
}

// --- RANDOMNESS & NOISE ---

// Hash function (1D -> 1D)
float hash11(float p) {
    p = fract(p * .1031);
    p *= p + 33.33;
    p *= p + p;
    return fract(p);
}

// Hash function (2D -> 1D)
float hash12(vec2 p) {
    vec3 p3  = fract(vec3(p.xyx) * .1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

// Hash function (2D -> 2D)
vec2 hash22(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * vec3(.1031, .1030, .0973));
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.xx+p3.yz)*p3.zy);
}

// Value Noise (Smooth, organic)
float noise(vec2 st) {
    vec2 i = floor(st);
    vec2 f = fract(st);
    float a = hash12(i);
    float b = hash12(i + vec2(1.0, 0.0));
    float c = hash12(i + vec2(0.0, 1.0));
    float d = hash12(i + vec2(1.0, 1.0));
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(a, b, u.x) + (c - a)* u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

// Voronoi Noise (Cells, cracks, bubbles)
// Returns vec3(min_dist, cell_id_x, cell_id_y)
vec3 voronoi(vec2 x) {
    vec2 n = floor(x);
    vec2 f = fract(x);
    vec2 mg, mr;
    float md = 8.0;
    for(int j=-1; j<=1; j++)
    for(int i=-1; i<=1; i++) {
        vec2 g = vec2(float(i),float(j));
        vec2 o = hash22(n + g);
        o = 0.5 + 0.5*sin(6.2831*o); // Animate or offset
        vec2 r = g + o - f;
        float d = dot(r,r);
        if(d<md) {
            md = d;
            mr = r;
            mg = g;
        }
    }
    return vec3(md, n + mg);
}

// FBM (Fractal Brownian Motion) - The basis of most textures
// octaves: usually 4-6
float fbm(vec2 st, int octaves) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 0.0;
    
    for (int i = 0; i < 6; i++) { // GLSL loops often need const bounds
        if (i >= octaves) break;
        value += amplitude * noise(st);
        st *= 2.0;
        amplitude *= 0.5;
    }
    return value;
}