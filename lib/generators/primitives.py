# @title 1. Scenario generation and labeling
import random
from .base import random_vec3_values, construct_shader

# =============================================================================
# STAGE 1: PRIMITIVES - SDF REASONING FOCUS
# =============================================================================
# We use randomized variable names (d, dist, field, val) to ensure the model
# learns the mathematical relationship of the coordinate space rather than
# memorizing specific character sequences.
# =============================================================================

def generate_primitive(index=0):
    """
    Generates primitive samples focusing on signed distance field logic.
    """
    if random.random() < 0.7:
        return generate_single_shape()
    else:
        return generate_double_shape()

def generate_single_shape():
    """
    Creates a single shape with deep SDF reasoning in the comments.
    """
    shape_type = random.choice(['circle', 'square', 'ring'])
    params = generate_shape_params(shape_type)
    
    if shape_type == 'circle':
        return generate_circle_sdf(params)
    elif shape_type == 'square':
        return generate_square_sdf(params)
    else:
        return generate_ring_sdf(params)

def generate_double_shape():
    """
    Generates two shapes to demonstrate field blending logic.
    """
    shape1 = random.choice(['circle', 'square', 'ring'])
    shape2 = random.choice(['circle', 'square', 'ring'])
    
    params1 = generate_shape_params(shape1, size_range=(0.1, 0.25))
    params2 = generate_shape_params(shape2, size_range=(0.1, 0.25))
    
    offset_x = random.uniform(0.15, 0.3) * random.choice([-1, 1])
    offset_y = random.uniform(0.15, 0.3) * random.choice([-1, 1])
    
    params2['pos_x'] = round(params1['pos_x'] + offset_x, 2)
    params2['pos_y'] = round(params1['pos_y'] + offset_y, 2)
    
    # Keep shapes within the standard UV viewport.
    params2['pos_x'] = round(max(-0.35, min(0.35, params2['pos_x'])), 2)
    params2['pos_y'] = round(max(-0.35, min(0.35, params2['pos_y'])), 2)
    
    code1, mask1, v1 = get_shape_code_sdf(shape1, params1, suffix='_a')
    code2, mask2, v2 = get_shape_code_sdf(shape2, params2, suffix='_b')
    
    analysis_lines = [
        f"// Composition: Blending two distinct signed distance fields.",
        f"// Field A: {shape1.capitalize()} centered at ({params1['pos_x']}, {params1['pos_y']}).",
        f"// Field B: {shape2.capitalize()} centered at ({params2['pos_x']}, {params2['pos_y']}).",
        f"// The final color is a sequential mix based on distance mask thresholds.",
    ]
    
    code_lines = []
    code_lines.extend(code1)
    code_lines.append(f"    col = mix(col, vec3({params1['r']}, {params1['g']}, {params1['b']}), {mask1});")
    code_lines.append("")
    code_lines.extend(code2)
    code_lines.append(f"    col = mix(col, vec3({params2['r']}, {params2['g']}, {params2['b']}), {mask2});")
    
    return construct_shader(analysis_lines, code_lines)

def generate_shape_params(shape_type, size_range=(0.15, 0.35)):
    """
    Calculates geometric and visual parameters for shapes.
    """
    size = round(random.uniform(*size_range), 2)
    thickness = round(random.uniform(0.02, 0.08), 2) if shape_type == 'ring' else 0.0
    
    max_offset = max(0.0, 0.5 - (size + thickness) - 0.05)
    pos_x = round(random.uniform(-max_offset, max_offset), 2)
    pos_y = round(random.uniform(-max_offset, max_offset), 2)
    blur = round(random.uniform(0.005, 0.04), 3)
    
    r, g, b = random_vec3_values()
    return {
        'size': size, 'thickness': thickness,
        'pos_x': pos_x, 'pos_y': pos_y,
        'blur': blur, 'r': r, 'g': g, 'b': b
    }

def get_sdf_analysis(shape_type, p):
    """
    Provides diverse reasoning to prevent template collapse.
    """
    v_name = random.choice(['d', 'dist', 'field', 'sdfValue', 'res'])
    c_name = random.choice(['center', 'p0', 'origin', 'mid'])
    
    if shape_type == 'circle':
        templates = [
            [
                f"// Geometry: Circular signed distance field.",
                f"// The distance is calculated from the pixel to the center point ({p['pos_x']}, {p['pos_y']}).",
                f"// Mathematical boundary is set at radius {p['size']}.",
                f"// The smoothstep function handles the edge transition using the field value."
            ],
            [
                f"// Logic: Euclidean distance field for a sphere primitive.",
                f"// Formula: length(uv - center) - radius.",
                f"// This creates a continuous gradient where zero represents the edge.",
                f"// We use a blur of {p['blur']} for the visual falloff."
            ]
        ]
    elif shape_type == 'square':
        templates = [
            [
                f"// Geometry: Square distance field using the Chebyshev metric.",
                f"// We calculate the maximum absolute offset from the center ({p['pos_x']}, {p['pos_y']}).",
                f"// This creates a box boundary at distance {p['size']}.",
                f"// The distance field is normalized by the coordinate space."
            ],
            [
                f"// Logic: Box SDF based on absolute coordinate offsets.",
                f"// The field value {v_name} increases linearly from the center point.",
                f"// Edge transition occurs at the boundary defined by {p['size']}.",
                f"// This implementation avoids conditional branching for performance."
            ]
        ]
    else: # ring
        templates = [
            [
                f"// Geometry: Annulus field derived from a circle SDF.",
                f"// We take the absolute distance from the radius {p['size']}.",
                f"// This creates a stroke with thickness {p['thickness']}.",
                f"// Logic ensures the zero-point of the field is the ring center-line."
            ]
        ]

    return random.choice(templates), v_name, c_name

def generate_circle_sdf(p):
    """
    Generates a compilable circle using pure SDF logic.
    """
    analysis, v, c = get_sdf_analysis('circle', p)
    inner = round(p['size'] - p['blur'], 3)
    
    code_lines = [
        f"    // Circle SDF implementation.",
        f"    vec2 {c} = vec2({p['pos_x']}, {p['pos_y']});",
        f"    float {v} = length(uv - {c});",
        f"    float mask = smoothstep({p['size']}, {inner}, {v});",
        f"    col = mix(col, vec3({p['r']}, {p['g']}, {p['b']}), mask);"
    ]
    return construct_shader(analysis, code_lines)

def generate_square_sdf(p):
    """
    Generates a compilable square using pure SDF logic.
    """
    analysis, v, c = get_sdf_analysis('square', p)
    inner = round(p['size'] - p['blur'], 3)
    
    # Human-like variation: sometimes calculate center inline, sometimes as a variable.
    if random.random() > 0.5:
        coord_logic = f"abs(uv - vec2({p['pos_x']}, {p['pos_y']}))"
    else:
        coord_logic = f"abs(uv - {c})"
    
    code_lines = []
    code_lines.append(f"    // Square SDF implementation.")
    if "abs(uv - {c})" in coord_logic:
        code_lines.append(f"    vec2 {c} = vec2({p['pos_x']}, {p['pos_y']});")
    
    code_lines.extend([
        f"    vec2 p_loc = {coord_logic};",
        f"    float {v} = max(p_loc.x, p_loc.y);",
        f"    float mask = smoothstep({p['size']}, {inner}, {v});",
        f"    col = mix(col, vec3({p['r']}, {p['g']}, {p['b']}), mask);"
    ])
    return construct_shader(analysis, code_lines)

def generate_ring_sdf(p):
    """
    Generates a compilable ring using pure SDF logic.
    """
    analysis, v, c = get_sdf_analysis('ring', p)
    inner = round(p['thickness'] - p['blur'], 3)
    
    code_lines = [
        f"    // Ring SDF implementation.",
        f"    vec2 {c} = vec2({p['pos_x']}, {p['pos_y']});",
        f"    float {v} = abs(length(uv - {c}) - {p['size']});",
        f"    float mask = smoothstep({p['thickness']}, {inner}, {v});",
        f"    col = mix(col, vec3({p['r']}, {p['g']}, {p['b']}), mask);"
    ]
    return construct_shader(analysis, code_lines)

def get_shape_code_sdf(shape_type, p, suffix=''):
    """
    Returns compilable snippets for composition scenarios.
    """
    v = f"d{suffix}"
    mask = f"mask{suffix}"
    code = []
    
    if shape_type == 'circle':
        inner = round(p['size'] - p['blur'], 3)
        code = [
            f"    float {v} = length(uv - vec2({p['pos_x']}, {p['pos_y']}));",
            f"    float {mask} = smoothstep({p['size']}, {inner}, {v});"
        ]
    elif shape_type == 'square':
        inner = round(p['size'] - p['blur'], 3)
        code = [
            f"    vec2 p{suffix} = abs(uv - vec2({p['pos_x']}, {p['pos_y']}));",
            f"    float {v} = max(p{suffix}.x, p{suffix}.y);",
            f"    float {mask} = smoothstep({p['size']}, {inner}, {v});"
        ]
    elif shape_type == 'ring':
        inner = round(p['thickness'] - p['blur'], 3)
        code = [
            f"    float {v} = abs(length(uv - vec2({p['pos_x']}, {p['pos_y']})) - {p['size']});",
            f"    float {mask} = smoothstep({p['thickness']}, {inner}, {v});"
        ]
    return code, mask, v