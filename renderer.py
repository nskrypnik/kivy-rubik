
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
    
    SCALE_FACTOR = 0.01
    MAX_SCALE = 3.0
    MIN_SCALE = 0.3
    ROTATE_SPEED = 1.
    
    def __init__(self, **kw):
        self.canvas = RenderContext(compute_normal_mat=True)
        shader_file = kw.pop('shader_file')
        self.canvas.shader.source = resource_find(shader_file)
        self._touches = []
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
        asp = float(Window.width) / Window.height / 2.
        proj = Matrix().view_clip(-asp, asp, -0.5, 0.5, 1, 100, 1)
        self.canvas['projection_mat'] = proj

    def setup_scene(self):
        
        PushMatrix()
        Translate(0, 0, -5)
        self.rotx = Rotate(0, 1, 0, 0)
        self.roty = Rotate(0, 0, 1, 0)
        self.scale = Scale(1)
        UpdateNormalMatrix()
        self.draw()
        PopMatrix()
    
    def update_scene(self, *largs):
        self.update_glsl()
        
    def draw(self):
        raise NotImplemented
    
    def define_rotate_angle(self, touch):
        x_angle = (touch.dx/self.width)*360.*self.ROTATE_SPEED
        y_angle = -1*(touch.dy/self.height)*360.*self.ROTATE_SPEED
        
        return x_angle, y_angle
    
    def do_scale(self):
        touch1, touch2 = self._touches 
        old_pos1 = (touch1.x - touch1.dx, touch1.y - touch1.dy)
        old_pos2 = (touch2.x - touch2.dx, touch2.y - touch2.dy)              
        old_dx = old_pos1[0] - old_pos2[0]
        old_dy = old_pos1[1] - old_pos2[1]
        old_distance = (old_dx*old_dx + old_dy*old_dy)

        
        new_dx = touch1.x - touch2.x
        new_dy = touch1.y - touch2.y
        
        new_distance = (new_dx*new_dx + new_dy*new_dy)
        
        if new_distance > old_distance: 
            scale = self.SCALE_FACTOR

        elif new_distance == old_distance:
            scale = 0
        else:
            scale = -1*self.SCALE_FACTOR
        
        xyz = self.scale.xyz
        if scale:
            scale = xyz[0] + scale
            if scale < self.MAX_SCALE and scale > self.MIN_SCALE:
                self.scale.xyz = (scale, scale, scale)
        
    def on_touch_down(self, touch):
        touch.grab(self)
        self._touches.append(touch)
        
    def on_touch_up(self, touch): 
        touch.ungrab(self)
        self._touches.remove(touch)
        
    def on_touch_move(self, touch): 
        #Logger.debug("dx: %s, dy: %s. Widget: (%s, %s)" % (touch.dx, touch.dy, self.width, self.height))

        if touch in self._touches and touch.grab_current == self:
            if len(self._touches) == 1:
                # here do just rotation        
                ax, ay = self.define_rotate_angle(touch)
                
                self.roty.angle += ax
                self.rotx.angle += ay

            elif len(self._touches) == 2: # scaling here
                #use two touches to determine do we need scal
                self.do_scale()
        
        self.update_scene()    


class RendererApp(App):
    def build(self):

        return Renderer()

if __name__ == "__main__":
    RendererApp().run()
