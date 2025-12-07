import random
from .base import random_vec3_values, construct_shader

def generate_primitive(index=0):
    """
    Generates a single geometric primitive (Circle, Square, Ring).
    Uses dynamic constraints to ensure shapes never clip the edge.
    """
    shape_type = random.choice(['circle', 'square', 'ring'])
    
    # --- 1. PARAMETER GENERATION (ORDER MATTERS) ---
    
    # A. Base Size
    size = round(random.uniform(0.1, 0.4), 2)
    
    # B. Thickness (Only relevant for Ring, but needed for bounds calculation)
    # We default to 0.0 for others so the math works universally
    thickness = 0.0
    if shape_type == 'ring':
        thickness = round(random.uniform(0.02, 0.1), 2)
        
    # C. Calculate Safe Bounds
    # For a ring, the "outer edge" is size + thickness.
    # For circle/square, it's just size.
    outer_radius = size + thickness
    
    margin = 0.03 # Slightly increased buffer for soft blur edges
    max_offset = 0.5 - outer_radius - margin
    
    # Safety clamp (in case size + thickness > 0.5, though unlikely with current ranges)
    max_offset = max(0.0, max_offset)
    
    # D. Position (Now guaranteed safe for all shapes)
    pos_x = round(random.uniform(-max_offset, max_offset), 2)
    pos_y = round(random.uniform(-max_offset, max_offset), 2)
    
    blur = round(random.uniform(0.001, 0.05), 3)
    r, g, b = random_vec3_values()
    
    # --- 2. CONSTRUCT ANALYSIS ---
    analysis_lines = [
        f"// Shape: {shape_type.capitalize()}",
        f"// Position: Offset by ({pos_x}, {pos_y})",
        f"// Size: {size}",
        f"// Color: RGB ({r}, {g}, {b})",
        f"// Blur: {blur}"
    ]
    
    if shape_type == 'ring':
        analysis_lines.append(f"// Thickness: {thickness}")
    
    code_lines = []
    glsl_color = f"vec3({r}, {g}, {b})"
    
    # --- 3. BUILD GLSL CODE ---
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
        analysis_lines.append("// Edge: Annular distance")
        code_lines.append(f"    // Distance Field for Ring")
        code_lines.append(f"    float d = abs(length(uv - vec2({pos_x}, {pos_y})) - {size});")
        code_lines.append(f"    float mask = smoothstep({thickness}, {thickness} - {blur}, d);")

    # Composition
    code_lines.append(f"    // Composite")
    code_lines.append(f"    col = mix(col, {glsl_color}, mask);")
    
    return construct_shader(analysis_lines, code_lines)