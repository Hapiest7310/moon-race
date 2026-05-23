import os
import pygame
from src import config
from src.shaders.shader_surface import ShaderSurface


# ── OpenGL availability cache ────────────────────────────────────────

_HAS_PYOPENGL = None

def _check_pyopengl():
    global _HAS_PYOPENGL
    if _HAS_PYOPENGL is not None:
        return _HAS_PYOPENGL
    if not config.ENABLE_GLSL:
        _HAS_PYOPENGL = False
        return False
    try:
        import OpenGL.GL
        _HAS_PYOPENGL = True
    except ImportError:
        _HAS_PYOPENGL = False
    return _HAS_PYOPENGL


# ── Pre-built shader sources (defaults if no files are provided) ─────

_DEFAULT_VERT_SOURCE = """
#version 120
void main() {
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    gl_TexCoord[0] = gl_MultiTexCoord0;
    gl_FrontColor = gl_Color;
}
"""

_DEFAULT_FRAG_SOURCE = """
#version 120
uniform sampler2D texture;
void main() {
    gl_FragColor = texture2D(texture, gl_TexCoord[0].st) * gl_Color;
}
"""


# ── Simulated shader passes (software fallback) ──────────────────────

_SIMULATED_PASSES = {}

def _register_pass(name, func):
    _SIMULATED_PASSES[name] = func


def _brightness(src, params):
    factor = params.get("factor", 1.0)
    out = ShaderSurface(src.get_width(), src.get_height())
    out.surface.blit(src, (0, 0))
    px = pygame.PixelArray(out.surface)
    for y in range(px.shape[1]):
        for x in range(px.shape[0]):
            r = (px[x][y] >> 16) & 0xFF
            g = (px[x][y] >> 8) & 0xFF
            b = px[x][y] & 0xFF
            a = (px[x][y] >> 24) & 0xFF
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            px[x][y] = (r << 16) | (g << 8) | b | (a << 24)
    del px
    return out

_register_pass("brightness", _brightness)


# ── ShaderProgram: handles both GLSL and software modes ──────────────

class ShaderProgram:
    """A compiled and linked GLSL shader program (or software simulation).

    Usage:
        prog = ShaderProgram("effects/my_shader", vert="shader.vert", frag="shader.frag")
        result = prog.render(source_surface)
    """

    def __init__(self, name, vert=None, frag=None):
        self._name = name
        self._gl_program = None
        self._uniforms = {}

        # Load sources from files or default
        self._vert_src = _read_source(vert) if vert else _DEFAULT_VERT_SOURCE
        self._frag_src = _read_source(frag) if frag else _DEFAULT_FRAG_SOURCE

        # Try real GLSL compilation
        if _check_pyopengl():
            self._compile_glsl(name)
        elif bool(pygame.display.get_surface()):
            pass

    def _compile_glsl(self, name):
        import OpenGL.GL as GL
        try:
            v = GL.glCreateShader(GL.GL_VERTEX_SHADER)
            GL.glShaderSource(v, self._vert_src)
            GL.glCompileShader(v)
            if not GL.glGetShaderiv(v, GL.GL_COMPILE_STATUS):
                raise RuntimeError(GL.glGetShaderInfoLog(v).decode())

            f = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
            GL.glShaderSource(f, self._frag_src)
            GL.glCompileShader(f)
            if not GL.glGetShaderiv(f, GL.GL_COMPILE_STATUS):
                raise RuntimeError(GL.glGetShaderInfoLog(f).decode())

            self._gl_program = GL.glCreateProgram()
            GL.glAttachShader(self._gl_program, v)
            GL.glAttachShader(self._gl_program, f)
            GL.glLinkProgram(self._gl_program)
            if not GL.glGetProgramiv(self._gl_program, GL.GL_LINK_STATUS):
                raise RuntimeError(GL.glGetProgramInfoLog(self._gl_program).decode())

            GL.glDeleteShader(v)
            GL.glDeleteShader(f)
        except Exception as e:
            if config.debug:
                print(f"[SHADER] GLSL compilation failed for '{name}': {e}")
            self._gl_program = None

    def set_uniform(self, name, value):
        self._uniforms[name] = value
        if self._gl_program is not None and _check_pyopengl():
            import OpenGL.GL as GL
            loc = GL.glGetUniformLocation(self._gl_program, name)
            if loc == -1:
                return
            if isinstance(value, (int, bool)):
                GL.glUniform1i(loc, value)
            elif isinstance(value, float):
                GL.glUniform1f(loc, value)
            elif isinstance(value, (tuple, list)):
                if len(value) == 2:
                    GL.glUniform2f(loc, *value)
                elif len(value) == 3:
                    GL.glUniform3f(loc, *value)
                elif len(value) == 4:
                    GL.glUniform4f(loc, *value)

    def render(self, source_surface, target_surface=None):
        """Apply the shader to *source_surface*, return the result.

        In GLSL mode the source is uploaded as a texture and the result
        is rendered to *target_surface* (or a new surface of the same size).
        In software mode a ShaderSurface-based simulation is used.
        """
        if target_surface is None:
            target_surface = pygame.Surface(
                source_surface.get_size(), pygame.SRCALPHA,
            )

        if self._gl_program is not None and _check_pyopengl():
            self._render_glsl(source_surface, target_surface)
        else:
            self._render_software(source_surface, target_surface)

        return target_surface

    def _render_glsl(self, source, target):
        import OpenGL.GL as GL
        import numpy as np
        w, h = source.get_size()
        data = pygame.image.tostring(source, "RGBA", True)
        tex = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, tex)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, w, h, 0,
                        GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, data)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glUseProgram(self._gl_program)

        # Apply uniforms
        for name, value in self._uniforms.items():
            loc = GL.glGetUniformLocation(self._gl_program, name)
            if loc == -1:
                continue
            if isinstance(value, (int, bool)):
                GL.glUniform1i(loc, value)
            elif isinstance(value, float):
                GL.glUniform1f(loc, value)
            elif isinstance(value, (tuple, list)):
                {2: GL.glUniform2f, 3: GL.glUniform3f, 4: GL.glUniform4f}[len(value)](loc, *value)

        GL.glBegin(GL.GL_QUADS)
        GL.glTexCoord2f(0, 0); GL.glVertex2f(-1, -1)
        GL.glTexCoord2f(1, 0); GL.glVertex2f(1, -1)
        GL.glTexCoord2f(1, 1); GL.glVertex2f(1, 1)
        GL.glTexCoord2f(0, 1); GL.glVertex2f(-1, 1)
        GL.glEnd()
        GL.glUseProgram(0)
        GL.glDeleteTextures([tex])
        GL.glReadBuffer(GL.GL_BACK)
        GL.glReadPixels(0, 0, w, h, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)
        # This requires a proper OpenGL context — in practice a separate
        # FBO would be used. For now this is a stub showing intent.
        GL.glReadBuffer(GL.GL_BACK)

    def _render_software(self, source, target):
        pass_name = self._name.replace("/", "_").replace("\\", "_")
        if pass_name in _SIMULATED_PASSES:
            simulated = _SIMULATED_PASSES[pass_name](source, self._uniforms)
            target.blit(simulated.surface, (0, 0))
        else:
            target.blit(source, (0, 0))


# ── Helpers ──────────────────────────────────────────────────────────

def _read_source(path):
    with open(path) as f:
        return f.read()


# ── GLShader (simple alias / convenience class) ─────────────────────

class GLShader:
    """Load, compile and apply GLSL shaders from file paths.

    Attributes:
        vertex_path / fragment_path -- original file paths.
        programs -- dict of named ShaderProgram instances.
    """

    def __init__(self, vertex_path=None, fragment_path=None):
        self.vertex_path = vertex_path
        self.fragment_path = fragment_path
        self.programs = {}

        name = "default"
        vert_name = os.path.splitext(os.path.basename(vertex_path))[0] if vertex_path else None
        frag_name = os.path.splitext(os.path.basename(fragment_path))[0] if fragment_path else None
        if vert_name and vert_name == frag_name:
            name = vert_name

        self.programs[name] = ShaderProgram(
            name, vert=vertex_path, frag=fragment_path,
        )

    def add_program(self, name, vert_path=None, frag_path=None):
        self.programs[name] = ShaderProgram(name, vert=vert_path, frag=frag_path)
        return self.programs[name]

    def get_program(self, name="default"):
        return self.programs.get(name)

    def render(self, source, target=None, program_name="default"):
        prog = self.programs.get(program_name)
        if prog is None:
            if target is None:
                return source
            target.blit(source, (0, 0))
            return target
        return prog.render(source, target)

    @staticmethod
    def is_supported():
        return _check_pyopengl()
