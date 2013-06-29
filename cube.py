
import math
import utils
from kivy.graphics import *
from renderer import Renderer
from copy import copy
from itertools import imap
from kivy.graphics.opengl import *
from kivy.clock import Clock
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
        
        _rotors = {'x': (1, 0, 0),
                   'y': (0, 1, 0),
                   'z': (0, 0, 1),
                   }
        
        self.vertices = vertices
        self.color = color
        
        indices = [0, 1, 2, 3, 0, 2] # allways the same
        _vertices = self._calculate_vertices()
        PushMatrix()
        self.rotors = {}
        for k, axis in _rotors.items():
            self.rotors[k] = Rotate(0, *axis)
        
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
    
    TOUCH_DELAY = 0.15
    ROTATE_SPEED = 0.125
    MAX_SCALE = 1.3
    MIN_SCALE = 0.3
     
    def __init__(self, *largs, **kw):
        kw['shader_file'] = 'shaders.glsl'
        self.cube_size = kw.pop('size', 3)
        self.surfaces = kw.pop('surfaces', [])
        self.cell_in_row = kw.pop('cell_in_row', 3)
        self.cell_spacing = kw.pop('cell_spacing', 0.025)
        self.cell_in_surface = self.cell_in_row^2
        self.color_to_cell = {}
        self.create_cubelets()
        self.is_animated = False # whetger the cube is in animation state
        self.in_turn_process = False
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
    
    def get_touched_cell(self, touch):
        pypixels = glReadPixels(touch.x, touch.y, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE)
        r, g, b, a = [ord(i) for i in pypixels]
        cell = self.color_to_cell.get((r, g, b))
        if cell:
            print cell.orient, cell.cubelet.pos
            print cell.g_cells[0].rotors['x'].angle, cell.g_cells[0].rotors['y'].angle, cell.g_cells[0].rotors['z'].angle 
            return cell
        else:
            return None
        
    def get_rotate_direction(self, orient, z_index, turn_direct):
        
        axis_rotate_indices = {(0, 0, 1): {'x': (-1, -1), 'y': (1, 1)},
                               (0, 1, 0): {'x': (1, -1), 'z': (-1, 1)},
                               (1, 0, 0): {'y': (-1, 1), 'z': (1, 1)},
                               (0, 0, -1): {'x': (-1, -1), 'y': (1, 1)},
                               (0, -1, 0): {'x': (1, -1), 'z': (-1, 1)},
                               (-1, 0, 0): {'y': (-1, 1), 'z': (1, 1)},
                               }
        
        rot_axis = {0:'x', 1:'y', 2:'z'}[z_index]
        self._graphical_rotate = axis_rotate_indices[tuple(orient)][rot_axis][0]
        self._cell_surface_rotate = axis_rotate_indices[tuple(orient)][rot_axis][1]
        for x in orient:
            if x:
                turn_direct *= x
        return rot_axis, turn_direct
    
    def make_cube_turn(self, touch):
        if self.in_turn_process:
            return
        cell = self.get_touched_cell(touch)
        if not cell:
            return
        cubelet = cell.cubelet
        if len(self._slided_cubelets) == 0:
            self._slided_cubelets.append(cubelet)
        else:
            cubelet0 = self._slided_cubelets[0]
            if cubelet0 == cubelet:
                # do nothing here
                pass
            else:
                # do here turn logic
                # define surface of turn first (as two coordinates)
                self.in_turn_process = True
                for i in xrange(3): # for 3 dimension :-)
                    turn_direct = cubelet0.pos[i] - cubelet.pos[i]
                    if turn_direct:
                        x_index = i
                        break
                        
                for i in xrange(3):
                    if cell.orient[i]:
                        y_index = i
                        break
                z_index = 3 - y_index - x_index
                try:
                    z_value = cubelet.pos[z_index]
                except IndexError:
                    import ipdb; ipdb.set_trace()
                print "turn_direct original", turn_direct
                self._rotate_direction = self.get_rotate_direction(cell.orient, z_index, turn_direct)
                self.rotate_cubelets_surface((x_index, y_index, z_index), z_value)
                self.start_animation()
    
    def rotate_cubelets_surface(self, coord_indices, z_value):
        # first get matrix of 
        x_index, y_index, z_index = coord_indices
        rot_axis, turn_direct = self._rotate_direction
        cubelets_matrix = []
        for x in xrange(self.cell_in_row):
            cubelets_matrix.append([])
            for y in xrange(self.cell_in_row):
                coord = [0, 0, 0]
                coord[x_index] = x
                coord[y_index] = y
                coord[z_index] = z_value
                cubelet = self.cubelets[tuple(coord)]
                cubelets_matrix[x].append(cubelet)
        print "Turn matrix to %s" % turn_direct    
        for i in cubelets_matrix:
            print i
        
        self.rotate_cells(cubelets_matrix, x_index, y_index)
        cubelets_matrix = utils.turn_matrix(cubelets_matrix, self.cell_in_row, turn_direct)
        
        print
        for i in cubelets_matrix:
            print i
        
        for x in xrange(self.cell_in_row):
            for y in xrange(self.cell_in_row):
                coord = [0, 0, 0]
                coord[x_index] = x
                coord[y_index] = y
                coord[z_index] = z_value
                cubelet = cubelets_matrix[x][y]
                cubelet.pos = coord 
                self.cubelets[tuple(coord)] = cubelet
                
    def rotate_cells(self, cubelets_matrix, x_index, y_index):
        _axis = {'x': 1, 'y':-1, 'z': -1}
        self._cells_to_rotate = []
        #z_index = 3 - x_index - y_index
        #rot_axis = {0:'x', 1:'y', 2:'z'}[z_index]
        #if rot_axis in ('x', 'z'):
        #    turn_direct *= -1
        rot_axis, turn_direct = self._rotate_direction
        print self._rotate_direction 
        for row in cubelets_matrix:
            for cubelet in row:
                for cell in cubelet.cells:
                    self._cells_to_rotate.append(cell)
        # change orientation of the cell
        for cell in self._cells_to_rotate:
            if cell.orient[x_index] and not cell.orient[y_index]:
                tmp = cell.orient[x_index]
                cell.orient[x_index] = 0
                cell.orient[y_index] = tmp*turn_direct*_axis[rot_axis]*self._cell_surface_rotate
            elif not cell.orient[x_index] and cell.orient[y_index]:
                tmp = cell.orient[y_index]
                cell.orient[y_index] = 0
                cell.orient[x_index] = -1*tmp*turn_direct*_axis[rot_axis]*self._cell_surface_rotate

    def on_touch_down(self, touch):
        self.touch_time = time()
        self.move_delta = 0
        self._slided_cubelets = []
        super(GraphicalCube, self).on_touch_down(touch)
        self.get_touched_cell(touch)
    
    def on_touch_move(self, touch):
        if time() - self.touch_time < self.TOUCH_DELAY or \
                len(self._touches) > 1 or self.move_delta>50 or self.is_animated:
            # here is the rotate mode of the rubik's cube
            super(GraphicalCube, self).on_touch_move(touch)
            self.move_delta += math.fabs(touch.dx) + math.fabs(touch.dy)
            self.touch_time = time()
        else:
            # this is the mode of side rotation
            self.make_cube_turn(touch)
    
    def on_touch_up(self, touch):
        if self.in_turn_process:
            self.is_animated = True
            self.in_turn_process = False
        self.move_delta = 0
        super(GraphicalCube, self).on_touch_up(touch)
    
    # Animation functions here
    def start_animation(self):
        self._ticks = 0
        Clock.schedule_interval(self._do_animation, 1 / 20.)
    
    def _do_animation(self, dt):
        
        def _change_axis():
            # Change here rotation axis of the cell, e.g.
            # if we rotate cell around y we should change
            # axis z an x
            axis, direct = self._rotate_direction
            _axis = ['x', 'y', 'z']
            _axis.remove(axis)
            for cell in self._cells_to_rotate:
                for g_cell in cell.g_cells:
                    tmp = g_cell.rotors[_axis[0]]
                    g_cell.rotors[_axis[0]] = g_cell.rotors[_axis[1]]
                    g_cell.rotors[_axis[1]] = tmp
        
        axis, direct = self._rotate_direction
        for cell in self._cells_to_rotate:
            for g_cell in cell.g_cells:
                rot = g_cell.rotors[axis]
                rot.angle += self._graphical_rotate*direct*9
        self._ticks += 1
        if self._ticks == 10:
            Clock.unschedule(self._do_animation)
            self.is_animated = False
            #_change_axis()

class LogicalCell(object):
    """ Logical representation of the cube cell """
    def __init__(self, pos, orient):
        self.id = pos
        self.orient = list(orient)
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
        
    def __repr__(self):
        return "<Cubelet %s>" % (self.pos, )


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
        if cell_in_row > 8:
            raise Exception('It doesn\'t support more than 8 cells in row')
        self.cell_in_row = cell_in_row
        self.create_surfaces()
        self.create_cells()
        self.widget = GraphicalCube(cell_in_row=cell_in_row, surfaces=self.surfaces)
         