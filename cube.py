
from kivy.graphics import *
from renderer import Renderer
from trackball import TrackBallMixin


class CubeSurface(object):
    """ This is the cube surface class which is graphical
        part of Rubik's cube. To create surface you need
        to specify it's color and 4 vertices in 3d dimension 
    """
    vertex_format = [
            ('v_pos', 3, 'float'),
            ('v_normal', 3, 'float'),
            ('v_tc0', 2, 'float')]
    
    def __init__(self, vertices, color):
        
        
        self.vertices = vertices
        self.color = color
        
        indices = [0, 1, 2, 3, 1, 2] # allways the same
        _vertices = self._calculate_vertices()
        PushMatrix()
        ChangeState(
                    Kd=self.color,
                    Ka=self.color,
                    Ks=(.3, .3, .3),
                    Tr=1., Ns=1.,
                    intensity=.5,
                )
        Mesh(
             vertices=_vertices,
             indices=indices,
             fmt=self.vertex_format,
             mode='triangles',
            )
        PopMatrix()
        
    def _calculate_vertices(self):
        vertices = []
        for vertex in self.vertices:
            vertices.extend(list(vertex))
            # FIXME: here should be calculated
            # normals but while we just get 0 instead
            vertices.extend([0. for i in xrange(5)])
        return vertices


class GraphicalCube(Renderer, TrackBallMixin):
    """ Graphical representation of the cube """
    
    
    def __init__(self, *largs, **kw):
        kw['shader_file'] = 'shaders.glsl'
        super(GraphicalCube, self).__init__(*largs, **kw)
    
    def draw(self):
        #Rotate(35, 0, 0, 1)
        vertices = [     
                   
                   (0., 0., -1.), 
                   (0., 1.0, -1.),
                   (1., 0., -1.), 
                   (1., 1.0, -1.), 
                ]
        CubeSurface(vertices, (1., 0., 0.))


class LogicalCube(object):
    
    def __init__(self):
        self.widget = GraphicalCube() 