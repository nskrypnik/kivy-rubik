
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import *
from kivy.logger import Logger
from kivy.uix.widget import Widget


class Renderer(Widget):
    def __init__(self, **kw):
        self.canvas = RenderContext(compute_normal_mat=True)
        shader_file = kw.pop('shader_file')
        self.canvas.shader.source = resource_find(shader_file)
        super(Renderer, self).__init__(**kw)
        with self.canvas:
            self.cb = Callback(self.setup_gl_context)
            PushMatrix()
            self.setup_scene()
            PopMatrix()
            self.cb = Callback(self.reset_gl_context)
        

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)

    def update_glsl(self, *largs):
        asp = float(Window.width) / Window.height
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        self.canvas['projection_mat'] = proj

    def setup_scene(self):
        
        PushMatrix()
        Translate(0, 0, 0)
        UpdateNormalMatrix()
        self.draw()
        PopMatrix()
    
    def update_scene(self, *largs):
        self.update_glsl()
        
    def draw(self):
        raise NotImplemented
    

class RendererApp(App):
    def build(self):

        return Renderer()

if __name__ == "__main__":
    RendererApp().run()
