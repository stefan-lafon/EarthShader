import random
from .base import random_vec3, construct_shader

def generate_primitive(index=0):
    """
    Generates a single geometric primitive (Circle, Square, Ring).
    Returns: (full_glsl_code, analysis_text)
    """
    shape_type = random.choice(['circle', 'square', 'ring'])
    
    # 1. Randomize Parameters
    pos_x = round(random.uniform(-0.3, 0.3), 2)
    pos_y = round(random.uniform(-0.3, 0.3), 2)
    size = round(random.uniform(0.1, 0.4), 2)
    blur = round(random.uniform(0.001, 0.05), 3)
    color_vec = random_vec3()
    
    analysis_lines = [
        f"// Shape: {shape_type.capitalize()}",
        f"// Position: Offset by ({pos_x}, {pos_y})",
        f"// Size: {size}",                               # <--- NEW: Explicit Size
        f"// Color: Custom RGB {color_vec}"
    ]
    
    code_lines = []
    
    # 2. Build Code Block
    if shape_type == 'circle':
        analysis_lines.append("// Edge: Smoothstep radial distance")
        code_lines.append(f"    // Distance Field for Circle")
        code_lines.append(f"    float d = length(uv - vec2({pos_x}, {pos_y}));")
        code_lines.append(f"    float mask = smoothstep({size}, {size} - {blur}, d);")
        
    elif shape_type == 'square':
        analysis_lines.append("// Edge: Smoothstep box distance")
        code_lines.append(f"    // Distance Field for Box")
        code_lines.append(f"    vec2 p = abs(uv - vec2({pos_x}, {pos_y}));")
        code_lines.append(f"    float d = max(p.x, p.y);")
        code_lines.append(f"    float mask = smoothstep({size}, {size} - {blur}, d);")
        
    elif shape_type == 'ring':
        thickness = round(random.uniform(0.02, 0.1), 2)
        analysis_lines.append("// Edge: Annular distance")
        code_lines.append(f"    // Distance Field for Ring")
        code_lines.append(f"    float d = abs(length(uv - vec2({pos_x}, {pos_y})) - {size});")
        code_lines.append(f"    float mask = smoothstep({thickness}, {thickness} - {blur}, d);")

    # 3. Composition
    code_lines.append(f"    // Composite")
    code_lines.append(f"    col = mix(col, {color_vec}, mask);")
    
    return construct_shader(analysis_lines, code_lines)