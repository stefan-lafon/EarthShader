import moderngl
import numpy as np
from PIL import Image
import os

class ShaderRenderer:
    def __init__(self, width=512, height=512):
        self.width = width
        self.height = height
        # Create headless context
        self.ctx = moderngl.create_context(standalone=True, backend='egl')        
        # Standard vertex shader (Full screen quad)
        self.vert_shader = '''
        #version 330
        in vec2 in_vert;
        out vec2 uv;
        void main() {
            uv = in_vert;
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }
        '''
        
        # Load Standard Library
        self.common_lib = ""
        # Assumes this file is in lib/ and common.glsl is in root/
        common_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'common.glsl')
        if os.path.exists(common_path):
            with open(common_path, 'r') as f:
                self.common_lib = f.read()
        else:
            print(f"Warning: common.glsl not found at {common_path}")

    def render(self, fragment_code, output_path):
        """
        Compiles the fragment code, renders it, and saves to output_path.
        Returns True if successful, False if compilation error.
        """
        
        # Wrap the user's mainImage logic into a full shader
        # We enforce the standard Shadertoy-style mainImage signature
        full_frag_shader = f'''
        #version 330
        uniform vec2 iResolution;
        out vec4 fragColor;
        
        {self.common_lib}
        
        {fragment_code}
        
        void main() {{
            vec4 color;
            mainImage(color, gl_FragCoord.xy);
            fragColor = color;
        }}
        '''

        try:
            # Create program
            prog = self.ctx.program(
                vertex_shader=self.vert_shader,
                fragment_shader=full_frag_shader,
            )
            
            # Set Uniforms
            if 'iResolution' in prog:
                prog['iResolution'].value = (self.width, self.height)

            # Create Vertex Buffer (Quad covers -1 to 1)
            vertices = np.array([-1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0], dtype='f4')
            vbo = self.ctx.buffer(vertices)
            vao = self.ctx.simple_vertex_array(prog, vbo, 'in_vert')
            
            # Render to Framebuffer
            fbo = self.ctx.simple_framebuffer((self.width, self.height))
            fbo.use()
            fbo.clear(0.0, 0.0, 0.0, 1.0)
            vao.render(moderngl.TRIANGLE_STRIP)
            
            # Read pixels
            data = fbo.read(components=3)
            image = Image.frombytes('RGB', fbo.size, data)
            
            # Flip Y (OpenGL is bottom-left origin, Images are top-left)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            image.save(output_path)
            
            # Cleanup
            fbo.release()
            vbo.release()
            vao.release()
            prog.release()
            
            return True

        except Exception as e:
            # Catch compilation errors so we don't crash the training loop
            print(f"Shader Compilation Failed: {e}")
            return False

    def __del__(self):
        try:
            self.ctx.release()
        except:
            pass