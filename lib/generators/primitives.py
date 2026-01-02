import random
import math

# This file handles the generation of SDF scenes for Stage 1.
# It prioritizes diverse mathematical reasoning and coordinate randomization.

def generate_primitive(index=0):
    """
    Main router for primitive generation with deterministic seeding.
    """
    random.seed(index)
    if random.random() < 0.7:
        return generate_single_shape()
    else:
        return generate_double_shape()

def generate_single_shape():
    """
    Creates a single shape with dense SDF reasoning labels.
    """
    shape_type = random.choice(['circle', 'square', 'annulus'])
    p = generate_shape_params(shape_type)
    
    # Coordinate and variable randomization.
    c = random.choice(['p', 'st', 'pos', 'uv'])
    v = random.choice(['d', 'dist', 'field', 'sdfValue'])
    
    # Dense Reasoning Block for Stage 1.
    analysis = f"// Analysis: [Type: {shape_type} | Center: {p['pos_x']}, {p['pos_y']} | Size: {p['size']}]. "
    analysis += f"Mapping field to '{v}' using '{c}' space."

    code_lines = []
    if shape_type == 'circle':
        # Standard circle SDF formula.
        code_lines.append(f"float {v} = length({c} - vec2({p['pos_x']}, {p['pos_y']})) - {p['size']};")
    elif shape_type == 'square':
        # Precise box SDF for GLSL.
        code_lines.append(f"vec2 q = abs({c} - vec2({p['pos_x']}, {p['pos_y']})) - {p['size']};")
        code_lines.append(f"float {v} = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0);")
    else: # annulus
        # Absolute distance from a radius creates a ring.
        thickness = 0.02
        code_lines.append(f"float {v} = abs(length({c} - vec2({p['pos_x']}, {p['pos_y']})) - {p['size']}) - {thickness};")

    code_lines.append(f"vec3 color = mix(vec3({p['r']}, {p['g']}, {p['b']}), vec3(0.0), smoothstep(0.0, 0.01, {v}));")
    
    return construct_full_shader(analysis, code_lines, c)

def generate_double_shape():
    """
    Generates two shapes to demonstrate field blending logic.
    """
    shape1 = random.choice(['circle', 'square', 'annulus'])
    shape2 = random.choice(['circle', 'square', 'annulus'])
    
    p1 = generate_shape_params(shape1, size_range=(0.1, 0.22))
    p2 = generate_shape_params(shape2, size_range=(0.1, 0.22))
    
    # Ensure shapes are visually distinct and offset.
    offset_x = random.uniform(0.15, 0.25) * random.choice([-1, 1])
    p2['pos_x'] = round(max(-0.35, min(0.35, p1['pos_x'] + offset_x)), 2)
    p2['pos_y'] = round(max(-0.35, min(0.35, p1['pos_y'] + random.uniform(-0.2, 0.2))), 2)
    
    c = random.choice(['p', 'uv', 'st'])
    
    analysis = f"// Analysis: [Composition: 2 Shapes | A: {shape1} | B: {shape2}]. "
    analysis += f"Blending distinct fields at ({p1['pos_x']}, {p1['pos_y']}) and ({p2['pos_x']}, {p2['pos_y']})."
    
    code_lines = []
    # Logic for shape A.
    code_lines.append(f"float d1 = {get_sdf_formula(shape1, p1, c)};")
    code_lines.append(f"vec3 col1 = vec3({p1['r']}, {p1['g']}, {p1['b']});")
    
    # Logic for shape B.
    code_lines.append(f"float d2 = {get_sdf_formula(shape2, p2, c)};")
    code_lines.append(f"vec3 col2 = vec3({p2['r']}, {p2['g']}, {p2['b']});")
    
    # Blending based on sequential mix operations.
    code_lines.append(f"vec3 color = mix(col1, vec3(0.0), smoothstep(0.0, 0.01, d1));")
    code_lines.append(f"color = mix(col2, color, smoothstep(0.0, 0.01, d2));")
    
    return construct_full_shader(analysis, code_lines, c)

def get_sdf_formula(shape_type, p, coord):
    """
    Returns the raw SDF formula string for composition.
    """
    if shape_type == 'circle':
        return f"length({coord} - vec2({p['pos_x']}, {p['pos_y']})) - {p['size']}"
    elif shape_type == 'square':
        # Condensed box SDF for inline use.
        return f"length(max(abs({coord} - vec2({p['pos_x']}, {p['pos_y']})) - {p['size']}, 0.0))"
    else: # annulus
        return f"abs(length({coord} - vec2({p['pos_x']}, {p['pos_y']})) - {p['size']}) - 0.02"

def generate_shape_params(shape_type, size_range=(0.12, 0.28)):
    """
    Calculates geometric and visual parameters for primitives.
    """
    size = round(random.uniform(*size_range), 2)
    pos_x = round(random.uniform(-0.35, 0.35), 2)
    pos_y = round(random.uniform(-0.35, 0.35), 2)
    r = round(random.random(), 2)
    g = round(random.random(), 2)
    b = round(random.random(), 2)
    return {'size': size, 'pos_x': pos_x, 'pos_y': pos_y, 'r': r, 'g': g, 'b': b}

def construct_full_shader(analysis, code_lines, coord_name):
    """
    Wraps reasoning and code into the EarthShader mainImage format.
    """
    inner_code = "\n    ".join(code_lines)
    full_shader = f"""void mainImage(out vec4 fragColor, in vec2 fragCoord) {{
    vec2 {coord_name} = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
    {inner_code}
    fragColor = vec4(color, 1.0);
}}"""
    return full_shader, analysis