"""
EARTHSHADER SHARED LIBRARY
--------------------------
Core utilities for GLSL shader sanitization, headless rendering, and image generation.

DEPENDENCIES:
This library requires the following modules to be installed:
    pip install moderngl numpy pillow

SYSTEM REQUIREMENTS (For Rendering):
    apt-get install libegl1-mesa libgl1-mesa-dri libxcb-xfixes0-dev mesa-vulkan-drivers
"""

import os
import re
import json
import hashlib
import numpy as np
import moderngl
import signal
from PIL import Image

# --- CONFIGURATION & CONSTANTS ---

SAFE_LICENSES = [
    "MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause",
    "CC0-1.0", "Unlicense", "ISC", "BlueOak-1.0.0"
]

SHADER_HEADER = """
#version 330
uniform vec3      iResolution;
uniform float     iTime;
uniform float     iTimeDelta;
uniform float     iFrame;
uniform vec4      iMouse;
uniform vec4      iDate;
out vec4 fragColor;
"""

SHADER_FOOTER = """
void main() {
    mainImage(fragColor, gl_FragCoord.xy);
}
"""

VERTEX_SHADER = """
#version 330
in vec2 in_vert;
void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
"""

# --- UTILITY FUNCTIONS ---

def get_content_hash(code):
    """Generates a SHA-256 hash of the code (ignoring whitespace)."""
    normalized = "".join(code.split())
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

def extract_code_from_json(text):
    """Attempts to parse JSON dumps and extract the 'code' field."""
    text = text.strip()
    if text.startswith("{") and text.endswith("}") and '"code":' in text:
        try:
            data = json.loads(text)
            return data.get("code", text)
        except:
            return text
    return text

def strip_comments(code):
    """Removes C-style comments (// and /* */)."""
    code = re.sub(r'/\*[\s\S]*?\*/', '', code)
    code = re.sub(r'//.*', '', code)
    return code

def remove_function_block(code, func_name):
    """Surgically removes a function block by tracking braces."""
    pattern = r"void\s+" + func_name + r"\s*\("
    match = re.search(pattern, code)
    if not match: return code 

    start_pos = match.start()
    open_brace_pos = code.find("{", start_pos)
    if open_brace_pos == -1: return code

    balance = 1
    current_pos = open_brace_pos + 1
    while balance > 0 and current_pos < len(code):
        char = code[current_pos]
        if char == "{": balance += 1
        elif char == "}": balance -= 1
        current_pos += 1

    if balance == 0:
        return code[:start_pos] + "\n" + code[current_pos:]
    return code

def collapse_newlines(code):
    lines = [line.rstrip() for line in code.splitlines()]
    clean_lines = []
    empty_count = 0
    for line in lines:
        if not line:
            empty_count += 1
            if empty_count <= 1: clean_lines.append(line)
        else:
            clean_lines.append(line)
            empty_count = 0
    return "\n".join(clean_lines)

# --- CORE SANITIZATION ---

def clean_shader_code(code):
    """
    Scorched Earth Cleaning Pipeline:
    Removes directives, sound logic, and ALL Shadertoy built-in declarations
    to prevent conflicts with our injected header.
    """
    if not code: return ""

    # 1. Basic cleanup
    code = extract_code_from_json(code)
    code = code.replace("\\n", "\n").replace("\\t", "\t")
    code = strip_comments(code)

    # 2. Remove Directives (#version, #extension)
    code = re.sub(r'^\s*#(version|extension).*$', '', code, flags=re.MULTILINE)

    # 3. Remove Sound Logic
    code = remove_function_block(code, "mainSound")

    # 4. Scorched Earth: Remove Shadertoy Built-in Declarations
    builtins_list = [
        "iResolution", "iTime", "iTimeDelta", "iFrame", "iMouse", 
        "iDate", "iChannelTime", "iChannelResolution", "iSampleRate"
    ]
    builtins_pattern = r"(" + "|".join(builtins_list) + r")"

    # A. Remove Uniforms: "uniform float iTime;"
    code = re.sub(r"^\s*uniform\s+.*?\b" + builtins_pattern + r"\b.*?;", "", code, flags=re.MULTILINE)
    
    # B. Remove Variable Declarations: "float iTime = 0.0;" or "vec4 iMouse;"
    code = re.sub(r"^\s*[a-zA-Z0-9]+\s+\b" + builtins_pattern + r"\b.*?;", "", code, flags=re.MULTILINE)

    # 5. Remove "varying" lines
    code = re.sub(r'^\s*varying\s+.*?;', '', code, flags=re.MULTILINE)

    # 6. Rename Legacy Variables
    replacements = {
        "iGlobalTime": "iTime",
        "aTexture0": "iChannel0",
        "aTexture1": "iChannel1",
        "aTexture2": "iChannel2",
        "aTexture3": "iChannel3",
        "u_tex0": "iChannel0",
        "image.Sample": "texture"
    }
    for old, new in replacements.items():
        code = code.replace(old, new)

    # 7. Strip "void main" Wrapper (if mainImage exists)
    if "void main" in code and "mainImage" in code:
         wrapper_pattern = r'void\s+main\s*\([^)]*\)\s*\{[^}]*mainImage[^}]*\}'
         code = re.sub(wrapper_pattern, '', code, flags=re.DOTALL)

    return collapse_newlines(code.strip())

def is_strictly_shadertoy(code):
    if not code: return False
    if "void mainImage" not in code: return False
    if "#include" in code: return False
    banned_keywords = ["iChannel", "texture(", "texture2D(", "sampler2D", "texelFetch", "image.Sample"]
    if any(kw in code for kw in banned_keywords): return False
    if "fragCoord" not in code and "iResolution" not in code: return False
    return True

def is_safe_license(license_list):
    if not license_list: return False
    return any(lic in SAFE_LICENSES for lic in license_list)

# --- RENDERING ENGINE ---

# Helper for signal timeout
def _timeout_handler(signum, frame):
    raise TimeoutError("Shader rendering timed out.")

def create_headless_context():
    """Creates a ModernGL context for headless rendering."""
    try:
        return moderngl.create_context(standalone=True, backend='egl')
    except:
        return moderngl.create_context(standalone=True)

def render_shader(ctx, user_code, width=512, height=512, time_val=1.0, timeout=8):
    """
    Fast validation render. Returns statistics (Success, Msg, Entropy).
    Includes a Watchdog Timeout (default 8s) to prevent hangs.
    """
    # Register timeout handler
    signal.signal(signal.SIGALRM, _timeout_handler)
    
    try:
        full_source = f"{SHADER_HEADER}\n{user_code}\n{SHADER_FOOTER}"

        prog = ctx.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader=full_source
        )

        # Set Uniforms
        if 'iResolution' in prog: prog['iResolution'].value = (width, height, 1.0)
        if 'iTime' in prog:       prog['iTime'].value = time_val
        if 'iTimeDelta' in prog:  prog['iTimeDelta'].value = 1.0 / 60.0
        if 'iFrame' in prog:      prog['iFrame'].value = 0.0
        if 'iMouse' in prog:      prog['iMouse'].value = (0.0, 0.0, 0.0, 0.0)
        if 'iDate' in prog:       prog['iDate'].value = (2024.0, 1.0, 1.0, 0.0)

        fbo = ctx.simple_framebuffer((width, height))
        fbo.use()
        fbo.clear(0.0, 0.0, 0.0, 1.0)

        vertices = np.array([-1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0], dtype='f4')
        vbo = ctx.buffer(vertices)
        vao = ctx.simple_vertex_array(prog, vbo, 'in_vert')
        
        # --- RENDER WITH TIMEOUT ---
        signal.alarm(timeout) # Start timer
        try:
            vao.render(moderngl.TRIANGLE_STRIP)
            raw = fbo.read(components=3) # Force GPU sync
        finally:
            signal.alarm(0) # Disable timer
        # ---------------------------

        img = np.frombuffer(raw, dtype=np.uint8)

        # Basic Validation (Check for pure black/flat images)
        entropy = np.std(img)
        
        # Cleanup
        vbo.release()
        vao.release()
        prog.release()
        fbo.release()

        if entropy < 0.01:
            return False, "Rendered flat/empty image", 0.0

        return True, "Success", float(entropy)

    except TimeoutError:
        return False, "Timeout (GPU Hang)", 0.0
    except Exception as e:
        return False, str(e), 0.0

def render_image(code, width=512, height=288, time_val=1.0, timeout=8):
    """
    Production render. Returns a PIL Image object.
    Includes a Watchdog Timeout (default 8s) to prevent hangs.
    """
    ctx = None
    # Register timeout handler
    signal.signal(signal.SIGALRM, _timeout_handler)

    try:
        ctx = create_headless_context()
        full_source = f"{SHADER_HEADER}\n{code}\n{SHADER_FOOTER}"
        
        prog = ctx.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader=full_source
        )

        if 'iResolution' in prog: prog['iResolution'].value = (width, height, 1.0)
        if 'iTime' in prog:       prog['iTime'].value = time_val
        if 'iMouse' in prog:      prog['iMouse'].value = (0.0, 0.0, 0.0, 0.0)

        fbo = ctx.simple_framebuffer((width, height))
        fbo.use()
        fbo.clear(0.0, 0.0, 0.0, 1.0)

        vertices = np.array([-1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0], dtype='f4')
        vbo = ctx.buffer(vertices)
        vao = ctx.simple_vertex_array(prog, vbo, 'in_vert')
        
        # --- RENDER WITH TIMEOUT ---
        signal.alarm(timeout)
        try:
            vao.render(moderngl.TRIANGLE_STRIP)
            raw = fbo.read(components=3)
        finally:
            signal.alarm(0)
        # ---------------------------
        
        # Convert to PIL Image
        img = Image.frombytes('RGB', (width, height), raw).transpose(Image.FLIP_TOP_BOTTOM)
        
        # Cleanup
        vbo.release()
        vao.release()
        prog.release()
        fbo.release()
        ctx.release()
        
        return img

    except Exception as e:
        if ctx: ctx.release()
        return None