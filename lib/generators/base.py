import random

# Use double braces {{ }} here because we call .format() on this string
TEMPLATE_HEADER = """/* ANALYSIS
{analysis}
*/

void mainImage( out vec4 fragColor, in vec2 fragCoord ) {{
    // 1. Setup normalized UV (0,0 is center)
    vec2 uv = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
    
    // 2. Define Base Color
    vec3 col = vec3(0.0); // Black background
    
    // 3. Shape Logic
"""

# Use single brace } here because we just concatenate this string (no .format call)
TEMPLATE_FOOTER = """
    fragColor = vec4(col, 1.0);
}"""

def random_vec3():
    """Generates a random GLSL vec3 color string."""
    r = round(random.random(), 2)
    g = round(random.random(), 2)
    b = round(random.random(), 2)
    return f"vec3({r}, {g}, {b})"

def construct_shader(analysis_lines, code_lines):
    """Assembles the full shader string."""
    analysis_text = "\n".join(analysis_lines)
    glsl_body = "\n".join(code_lines)
    
    # Header gets formatted ({{ -> {), Footer is just added as-is
    full_code = TEMPLATE_HEADER.format(analysis=analysis_text) + glsl_body + TEMPLATE_FOOTER
    return full_code, analysis_text