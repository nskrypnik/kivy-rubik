
import math
from kivy.graphics import *
from renderer import Renderer
from copy import copy
from itertools import imap
from kivy.graphics.opengl import *
from time import time

class CubeCell(object):
    """ This is the cube cell class which is graphical
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
        
        indices = [0, 1, 2, 3, 0, 2] # allways the same
        _vertices = self._calculate_vertices()
        PushMatrix()
        ChangeState(
                    Kd=self.color,
                    Ka=self.color,
                    Ks=(.3, .3, .3),
                    Tr=1., Ns=1.,
                    intensity=1.,
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


class GraphicalCube(Renderer):
    """ Graphical representation of the cube """
    
    TOUCH_DELAY = 0.25
     
    def __init__(self, *largs, **kw):
        kw['shader_file'] = 'shaders.glsl'
        self.cube_size = kw.pop('size', 3)
        self.surfaces = kw.pop('surfaces', [])
        self.cell_in_row = kw.pop('cell_in_row', 3)
        self.cell_spacing = kw.pop('cell_spacing', 0.01)
        self.cell_in_surface = self.cell_in_row^2
        self.color_to_cell = {}
        self.create_cubelets()
        super(GraphicalCube, self).__init__(*largs, **kw)
        
    def create_cubelets(self):
        self.cubelets = {}
        self.center_to_cubelets = {} 
        # define here position of center of top cubelet
        cubelet_size = float(self.cube_size) / self.cell_in_row  
        if self.cell_in_row % 2:
            cubelets_to_corner = (self.cell_in_row - 1) / 2
            zero_cubelet_center = [cubelets_to_corner*cubelet_size for i in xrange(3)]
        else:
            cubelets_to_corner = self.cell_in_row  / 2
            zero_cubelet_center = [cubelets_to_corner*cubelet_size - cubelet_size / 2. for i in xrange(3)]
        for x in xrange(self.cell_in_row):
            for y in xrange(self.cell_in_row):
                for z in xrange(self.cell_in_row):
                    cubelet_center = (
                                      zero_cubelet_center[0] - x*cubelet_size,
                                      zero_cubelet_center[1] - y*cubelet_size,
                                      zero_cubelet_center[2] - z*cubelet_size
                                      )
                    cubelet = Cubelet((x, y, z), cubelet_center)
                    self.cubelets[x, y, z] = cubelet
                    self.center_to_cubelets[cubelet_center] = cubelet
        
    def draw_surface(self, surface):
        vertices = self.get_surface_vertices(surface)
        CubeCell(vertices, surface.inner_color)
        
    def get_cell_vertices(self, surface):
        """ This function returns vertices for cells in surface """
        
        _quadrat = ((-1, -1), (-1, 1), (1, 1), (1, -1))
        
        cube_diameter = self.cube_size / 2. # float
        cell_diameter = cube_diameter / self.cell_in_row
        cell_size = cell_diameter * 2
        # define center of the surface
        surface_center = [i*cube_diameter for i in surface.pos]
        
        surface_index = reduce(lambda x, y: x+y, surface.pos)
        # Now define the center of left-top corner
        if self.cell_in_row % 2:
            cells_to_corner = (self.cell_in_row - 1) / 2
            left_top_corner = [cells_to_corner *cell_size for i in xrange(2)]
        else:
            cells_to_corner = self.cell_in_row / 2
            left_top_corner = [cells_to_corner *cell_size - cell_diameter for i in xrange(2)]
        
        left_top_corner = map(lambda x: surface_index*x, left_top_corner)
        
        # Now get position of centers of all cells
        cell_centers = {}
        for cell_y in xrange(self.cell_in_row):
            for cell_x in xrange(self.cell_in_row):
                cell_center_pos = copy(surface_center)
                is_x_now = True
                for i in xrange(len(cell_center_pos)):
                    if  cell_center_pos[i] == 0:
                        if is_x_now:
                            cell_center_pos[i] = left_top_corner[0] - cell_x * cell_size*surface_index
                            is_x_now = False
                        else:
                            cell_center_pos[i] = left_top_corner[1] - cell_y * cell_size*surface_index
                cell_centers[cell_x, cell_y] = cell_center_pos
        
        # now get vertexes for each cell
        cell_vertices = {}
        normal_surface_vertices = self.get_normal_vertices(surface_center, cell_diameter, spacing=self.cell_spacing)
        for pos, cell in cell_centers.iteritems():
            vertices = []
            for v in normal_surface_vertices:
                vertices.append(list(imap(lambda a, b: a+b, cell, v)))
            cell_vertices[pos] = vertices
            
        return cell_vertices, cell_centers
    
    def get_back_cell_vertices(self, cell_centers, surface):
        
        cube_diameter = self.cube_size / 2. # float
        cell_diameter = cube_diameter / self.cell_in_row
        cell_size = cell_diameter * 2
        # define center of the surface
        surface_center = [i*cube_diameter for i in surface.pos]
        
        cell_vertices = {}
        normal_surface_vertices = self.get_normal_vertices(surface_center, cell_diameter, z_shift=-0.001)
        for pos, cell in cell_centers.iteritems():
            vertices = []
            for v in normal_surface_vertices:
                vertices.append(list(imap(lambda a, b: a+b, cell, v)))
            cell_vertices[pos] = vertices
        return cell_vertices
    
    def get_normal_vertices(self, center, size, spacing=0, z_shift=0):
        _quadrat = ((-1, -1), (-1, 1), (1, 1), (1, -1))
        
        vertices = []
        for _q in _quadrat:
            vertex = []
            _ql = list(_q)
            for coor in center:
                if coor:
                    if coor > 0: 
                        vertex.append(z_shift)
                    else:
                        vertex.append(-1*z_shift)
                else:
                    vertex.append(_ql[0] * size - _ql[0]*spacing)
                    _ql.remove(_ql[0])
            vertices.append(vertex)
        return vertices
    
    def draw(self):

        for surface in self.surfaces.values():
            cell_vertices, cell_centers = self.get_cell_vertices(surface)
            back_cell_vertices = self.get_back_cell_vertices(cell_centers, surface)
            inner_color = map(lambda x: x+self.cell_in_row if x < self.cell_in_row else x, surface.inner_color)
            # draw color cell section
            for cell_pos, vertices in cell_vertices.iteritems():
                color = inner_color[0] - cell_pos[0], inner_color[1] - cell_pos[1], inner_color[2]
                cell = surface.cells[cell_pos]
                r, g, b = color
                self.color_to_cell[r, g, b] = cell
                cell.color = color # set color for surface
                color = map(lambda x: x / 255., color)
                cell.g_cells.append(CubeCell(vertices, color))
            # draw background black section
            for cell_pos, vertices in back_cell_vertices.iteritems():
                surface.cells[cell_pos].g_cells.append(CubeCell(vertices, (0., 0., 0.)))
            # bind cells to cubelets
            for cell_pos, cell_center in cell_centers.iteritems():
                res = self.bind_to_cubelet(cell_pos, cell_center, surface)
                if not res:
                    raise Exception('Can\'t bind cell')
    
    def bind_to_cubelet(self, cell_pos, cell_center, surface):
        cell_diameter = self.cube_size / float(self.cell_in_row) / 2.
        center_shift = map(lambda x: x*cell_diameter, surface.pos)
        cell_cube_center = list(imap(lambda x, y: x-y, cell_center, center_shift))

        for k in self.center_to_cubelets:
            cell_belongs_to = True
            for u, v in zip(k, cell_cube_center):
                if not math.fabs(u-v) < 0.000000001:
                    cell_belongs_to = False
            if cell_belongs_to:
                # do some stuff to bind cells
                cell = surface.cells[cell_pos]
                cubelet = self.center_to_cubelets[k]
                cubelet.bind(cell)
                return True
        # no appropriate cubelet found
        return False
                
    def on_touch_down(self, touch):
        self.touch_time = time()
        pypixels = glReadPixels(touch.x, touch.y, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE)
        r, g, b, a = [ord(i) for i in pypixels]
        cell = self.color_to_cell.get((r, g, b))
        if cell:
            print cell.cubelet.pos, cell.orient
        super(GraphicalCube, self).on_touch_down(touch)
    
    def on_touch_move(self, touch):
        super(GraphicalCube, self).on_touch_move(touch)
    
    def on_touch_up(self, touch):
        super(GraphicalCube, self).on_touch_up(touch)


class LogicalCell(object):
    """ Logical representation of the cube cell """
    def __init__(self, pos, orient):
        self.id = pos
        self.orient = orient
        self.color = () # color identifier
        self.cubelet = None
        self.g_cells = []


class LogicalSurface(object):
    
    def __init__(self, _id, pos, inner_color=(0, 0, 0)):
        self.cells = {}
        self.pos = pos
        self.id = _id
        self.inner_color = inner_color


class Cubelet(object):
    
    def __init__(self, pos, center):
        self.pos = pos
        self.center = center
        self.cells = [] # bound cells
    
    def bind(self, cell):
        self.cells.append(cell)
        cell.cubelet = self


class LogicalCube(object):
    
    SURFACE_COLOR_MAP = {0: (255, 255, 255), # white
                         1: (255, 255, 0.), # yellow
                         2: (255, 0, 0), # red
                         3: (0, 255, 0), # green
                         4: (0, 0, 255), # blue
                         5: (255, 127, 0) # orange
                         }
    
    # surface map in format of three coordinates 
    SURFACE_MAP = {
                   0: (0, 1, 0),
                   1: (0, 0, 1),
                   2: (-1, 0, 0),
                   3: (0, 0, -1),
                   4: (1, 0, 0),
                   5: (0, -1, 0),
                }

    def create_surfaces(self):
        self.surfaces = {}
        for surface_id in xrange(6):
            color = self.SURFACE_COLOR_MAP[surface_id]
            pos =  self.SURFACE_MAP[surface_id]
            surface = LogicalSurface(surface_id, pos, color)
            self.surfaces[pos] = surface
    
    def create_cells(self):
        for surface in self.surfaces.values():
            for x in xrange(self.cell_in_row):
                for y in xrange(self.cell_in_row):
                    surface.cells[x, y] = LogicalCell((x, y), surface.pos)
        
    def __init__(self, cell_in_row=3):
        self.cell_in_row = cell_in_row
        self.create_surfaces()
        self.create_cells()
        self.widget = GraphicalCube(cell_in_row=cell_in_row, surfaces=self.surfaces)
         