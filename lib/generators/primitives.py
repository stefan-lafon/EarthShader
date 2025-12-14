import random
from .base import random_vec3_values, construct_shader

# =============================================================================
# STAGE 1: PRIMITIVES - CANONICAL SYNTAX
# =============================================================================
# Refactor Note:
# We have removed code-level syntactic diversity (inline vs verbose vs alternative).
# We now enforce a SINGLE "Canonical" way to write every shape.
# Diversity is maintained solely in the Analysis/Comments to teach reasoning.
# =============================================================================

def generate_primitive(index=0):
    """
    Generates primitive samples with strict GLSL syntax but diverse analysis.
    """
    if random.random() < 0.7:
        return generate_single_shape()
    else:
        return generate_double_shape()

def generate_single_shape():
    shape_type = random.choice(['circle', 'square', 'ring'])
    
    # Generate geometric parameters
    params = generate_shape_params(shape_type)
    
    # Generate diverse analysis (reasoning), but STRICT code
    if shape_type == 'circle':
        return generate_circle_canonical(params)
    elif shape_type == 'square':
        return generate_square_canonical(params)
    else:  # ring
        return generate_ring_canonical(params)

def generate_double_shape():
    shape1 = random.choice(['circle', 'square', 'ring'])
    shape2 = random.choice(['circle', 'square', 'ring'])
    
    params1 = generate_shape_params(shape1, size_range=(0.1, 0.25))
    params2 = generate_shape_params(shape2, size_range=(0.1, 0.25))
    
    # Offset logic to ensure shapes don't perfectly overlap
    offset_x = random.uniform(0.15, 0.3) * random.choice([-1, 1])
    offset_y = random.uniform(0.15, 0.3) * random.choice([-1, 1])
    
    params2['pos_x'] = round(params1['pos_x'] + offset_x, 2)
    params2['pos_y'] = round(params1['pos_y'] + offset_y, 2)
    
    # Clamp to screen bounds
    params2['pos_x'] = round(max(-0.35, min(0.35, params2['pos_x'])), 2)
    params2['pos_y'] = round(max(-0.35, min(0.35, params2['pos_y'])), 2)
    
    # Get Canonical Code Blocks
    code1, mask_var1 = get_shape_code_canonical(shape1, params1, suffix='1')
    code2, mask_var2 = get_shape_code_canonical(shape2, params2, suffix='2')
    
    # Analysis is still verbose/reasoned
    analysis_lines = [
        f"// Composition: Two shapes ({shape1} + {shape2})",
        f"// Shape 1: {shape1.capitalize()} at ({params1['pos_x']}, {params1['pos_y']})",
        f"// Shape 2: {shape2.capitalize()} at ({params2['pos_x']}, {params2['pos_y']})",
        f"// Blending: Sequential mix operations using masks",
    ]
    
    code_lines = []
    code_lines.extend(code1)
    code_lines.append(f"    col = mix(col, vec3({params1['r']}, {params1['g']}, {params1['b']}), {mask_var1});")
    code_lines.append("")
    code_lines.extend(code2)
    code_lines.append(f"    col = mix(col, vec3({params2['r']}, {params2['g']}, {params2['b']}), {mask_var2});")
    
    return construct_shader(analysis_lines, code_lines)

def generate_shape_params(shape_type, size_range=(0.15, 0.35)):
    size = round(random.uniform(*size_range), 2)
    thickness = round(random.uniform(0.02, 0.08), 2) if shape_type == 'ring' else 0.0
    
    outer_radius = size + thickness
    margin = 0.05
    max_offset = 0.5 - outer_radius - margin
    max_offset = max(0.0, max_offset)
    
    pos_x = round(random.uniform(-max_offset, max_offset), 2)
    pos_y = round(random.uniform(-max_offset, max_offset), 2)
    blur = round(random.uniform(0.005, 0.04), 3)
    
    r, g, b = random_vec3_values()
    
    return {
        'size': size, 'thickness': thickness,
        'pos_x': pos_x, 'pos_y': pos_y,
        'blur': blur, 'r': r, 'g': g, 'b': b
    }

# =============================================================================
# CANONICAL IMPLEMENTATIONS
# =============================================================================

def get_analysis_comment(shape_type, p):
    """
    Returns a diverse analysis comment to prevent template collapse in the Vision Encoder,
    even though the code generation is strict/canonical.
    """
    templates = []
    
    if shape_type == 'circle':
        templates = [
            [
                f"// Shape: Circle",
                f"// Center: ({p['pos_x']}, {p['pos_y']}), Radius: {p['size']}",
                f"// Concept: Euclidean distance field"
            ],
            [
                f"// Geometry: Circle centered at ({p['pos_x']}, {p['pos_y']})",
                f"// Edge: Soft transition (blur {p['blur']})",
                f"// Math: length(uv - center)"
            ],
            [
                f"// Feature: Radial gradient mask",
                f"// Location: vec2({p['pos_x']}, {p['pos_y']})",
                f"// Size: {p['size']}"
            ]
        ]
    elif shape_type == 'square':
        templates = [
            [
                f"// Shape: Square",
                f"// Center: ({p['pos_x']}, {p['pos_y']}), Size: {p['size']}",
                f"// Concept: Chebyshev distance (max of absolute x/y)"
            ],
            [
                f"// Geometry: Box/Square",
                f"// Dimensions: {p['size']} radius (half-width)",
                f"// Math: max(abs(p.x), abs(p.y))"
            ]
        ]
    elif shape_type == 'ring':
        templates = [
            [
                f"// Shape: Ring (Annulus)",
                f"// Center: ({p['pos_x']}, {p['pos_y']}), Radius: {p['size']}",
                f"// Thickness: {p['thickness']}"
            ],
            [
                f"// Geometry: Ring",
                f"// Math: abs(distance - radius)",
                f"// Profile: Stroked circle with thickness {p['thickness']}"
            ]
        ]

    return random.choice(templates)

def generate_circle_canonical(p):
    inner_edge = round(p['size'] - p['blur'], 3)
    
    analysis_lines = get_analysis_comment('circle', p)
    
    code_lines = [
        f"    // Circle: Canonical Implementation",
        f"    vec2 center = vec2({p['pos_x']}, {p['pos_y']});",
        f"    float d = length(uv - center);",
        f"    float mask = smoothstep({p['size']}, {inner_edge}, d);",
        f"    col = mix(col, vec3({p['r']}, {p['g']}, {p['b']}), mask);"
    ]
    return construct_shader(analysis_lines, code_lines)

def generate_square_canonical(p):
    inner_edge = round(p['size'] - p['blur'], 3)
    
    analysis_lines = get_analysis_comment('square', p)
    
    code_lines = [
        f"    // Square: Canonical Implementation",
        f"    vec2 p = abs(uv - vec2({p['pos_x']}, {p['pos_y']}));",
        f"    float d = max(p.x, p.y);",
        f"    float mask = smoothstep({p['size']}, {inner_edge}, d);",
        f"    col = mix(col, vec3({p['r']}, {p['g']}, {p['b']}), mask);"
    ]
    return construct_shader(analysis_lines, code_lines)

def generate_ring_canonical(p):
    inner_thickness = round(p['thickness'] - p['blur'], 3)
    
    analysis_lines = get_analysis_comment('ring', p)
    
    code_lines = [
        f"    // Ring: Canonical Implementation",
        f"    vec2 center = vec2({p['pos_x']}, {p['pos_y']});",
        f"    float d = abs(length(uv - center) - {p['size']});",
        f"    float mask = smoothstep({p['thickness']}, {inner_thickness}, d);",
        f"    col = mix(col, vec3({p['r']}, {p['g']}, {p['b']}), mask);"
    ]
    return construct_shader(analysis_lines, code_lines)

# Used for composition (Double Shape)
def get_shape_code_canonical(shape_type, p, suffix=''):
    mask_var = f"mask{suffix}"
    code_lines = []
    
    if shape_type == 'circle':
        inner_edge = round(p['size'] - p['blur'], 3)
        code_lines = [
            f"    // Circle {suffix}",
            f"    float d{suffix} = length(uv - vec2({p['pos_x']}, {p['pos_y']}));",
            f"    float {mask_var} = smoothstep({p['size']}, {inner_edge}, d{suffix});"
        ]
    elif shape_type == 'square':
        inner_edge = round(p['size'] - p['blur'], 3)
        code_lines = [
            f"    // Square {suffix}",
            f"    vec2 p{suffix} = abs(uv - vec2({p['pos_x']}, {p['pos_y']}));",
            f"    float d{suffix} = max(p{suffix}.x, p{suffix}.y);",
            f"    float {mask_var} = smoothstep({p['size']}, {inner_edge}, d{suffix});"
        ]
    elif shape_type == 'ring':
        inner_thickness = round(p['thickness'] - p['blur'], 3)
        code_lines = [
            f"    // Ring {suffix}",
            f"    float d{suffix} = abs(length(uv - vec2({p['pos_x']}, {p['pos_y']})) - {p['size']});",
            f"    float {mask_var} = smoothstep({p['thickness']}, {inner_thickness}, d{suffix});"
        ]
        
    return code_lines, mask_var