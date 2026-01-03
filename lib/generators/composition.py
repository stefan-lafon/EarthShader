import random
from generators.primitives import generate_shape_params, get_sdf_formula, construct_full_shader

def generate_boolean_composition(index=0):
    """
    Creates a scene where two shapes interact via boolean logic (CSG).
    This leverages Stage 1 primitives as the foundational math.
    """
    random.seed(index)
    
    # 1. Reuse existing Stage 1 parameter generation.
    shape1 = random.choice(['circle', 'square', 'annulus'])
    shape2 = random.choice(['circle', 'square', 'annulus'])
    
    # We use slightly smaller ranges to ensure the intersection is visible.
    p1 = generate_shape_params(shape1, size_range=(0.15, 0.25))
    p2 = generate_shape_params(shape2, size_range=(0.15, 0.25))
    
    # 2. Force the shapes to overlap.
    # We keep the centers close so the boolean operation is meaningful.
    p2['pos_x'] = round(p1['pos_x'] + random.uniform(-0.15, 0.15), 2)
    p2['pos_y'] = round(p1['pos_y'] + random.uniform(-0.15, 0.15), 2)
    
    c = random.choice(['p', 'uv', 'st'])
    
    # 3. Choose the boolean operation.
    op_type = random.choice(['union', 'subtraction', 'intersection'])
    
    # 4. Fetch raw formulas from the existing primitives.py file.
    sdf1 = get_sdf_formula(shape1, p1, c)
    sdf2 = get_sdf_formula(shape2, p2, c)
    
    # 5. Apply the CSG mathematical wrappers.
    if op_type == 'union':
        combined_sdf = f"min({sdf1}, {sdf2})"
        op_label = "Combining shapes via union (min)"
    elif op_type == 'subtraction':
        # This effectively cuts shape A out of shape B.
        combined_sdf = f"max(-({sdf1}), {sdf2})"
        op_label = "Subtracting shape A from shape B (max/negation)"
    else: # intersection
        combined_sdf = f"max({sdf1}, {sdf2})"
        op_label = "Intersecting shapes (max)"

    # 6. Assemble the reasoning and code block.
    analysis = f"// Analysis: [CSG Operation: {op_type} | A: {shape1} | B: {shape2}]. {op_label}."
    
    code_lines = [
        f"float d = {combined_sdf};",
        f"vec3 color = mix(vec3({p2['r']}, {p2['g']}, {p2['b']}), vec3(0.0), smoothstep(0.0, 0.01, d));"
    ]
    
    # Return using the Stage 1 shader construction helper.
    return construct_full_shader(analysis, code_lines, c)