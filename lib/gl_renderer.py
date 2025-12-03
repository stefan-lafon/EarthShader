import moderngl
import numpy as np
from PIL import Image
import os
import gc

class ShaderRenderer:
    def __init__(self, width=512, height=512):
        self.width = width
        self.height = height
        
        # Force EGL backend for Colab (Headless)
        # This prevents the "cannot open display" error
        self.ctx = moderngl.create_context(standalone=True, backend='egl')
        
        # OPTIMIZATION 1: Create the geometry (VBO) ONCE.
        # It's just a screen quad, it never changes.
        vertices = np.array([-1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0], dtype='f4')
        self.vbo = self.ctx.buffer(vertices)
        
        # OPTIMIZATION 2: Create the Framebuffer (FBO) ONCE.
        # We can just clear it and reuse it for every image.
        self.fbo = self.ctx.simple_framebuffer((self.width, self.height))
        
        # Standard vertex shader
        self.vert_shader = '''
        #version 330
        in vec2 in_vert;
        out vec2 uv;
        void main() {
            uv = in_vert;
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }
        '''
        
        self.common_lib = ""
        # Locate common.glsl relative to this lib file
        common_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'common.glsl')
        if os.path.exists(common_path):
            with open(common_path, 'r') as f:
                self.common_lib = f.read()

    def render(self, fragment_code, output_path):
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

        prog = None
        vao = None

        try:
            # 1. Create Program (Must be new every time as code changes)
            prog = self.ctx.program(
                vertex_shader=self.vert_shader,
                fragment_shader=full_frag_shader,
            )
            
            if 'iResolution' in prog:
                prog['iResolution'].value = (self.width, self.height)

            # 2. Create VAO (Links static VBO to dynamic Program)
            vao = self.ctx.simple_vertex_array(prog, self.vbo, 'in_vert')
            
            # 3. Render to the static FBO
            self.fbo.use()
            self.fbo.clear(0.0, 0.0, 0.0, 1.0)
            vao.render(moderngl.TRIANGLE_STRIP)
            
            # 4. Read pixels
            data = self.fbo.read(components=3)
            image = Image.frombytes('RGB', self.fbo.size, data)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            image.save(output_path)
            
            return True

        except Exception as e:
            print(f"Shader Error: {e}")
            return False
            
        finally:
            # OPTIMIZATION 3: Explicit cleanup of dynamic objects only
            if vao: vao.release()
            if prog: prog.release()

    def __del__(self):
        try:
            # Release static resources on destroy
            if hasattr(self, 'fbo'): self.fbo.release()
            if hasattr(self, 'vbo'): self.vbo.release()
            if hasattr(self, 'ctx'): self.ctx.release()
        except:
            pass