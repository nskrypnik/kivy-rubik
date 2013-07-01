

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from cube import LogicalCube

class MainFrame(Widget):
    
    def __init__(self, *larg, **kw):
        
        super(MainFrame, self).__init__(*larg, **kw)
        self.cube = None
        self.create_inner_menu()
    
    def create_cube(self, cell_in_row):
        self.cube = LogicalCube(cell_in_row=cell_in_row)
        self.add_widget(self.cube.widget)
        self.cube.widget.update_scene()
        button = Button(text="Shake", size_hint=(None, None),\
                        size=("150dp", "75dp"), pos=(0,0), font_size="40dp")
        button.bind(on_release=lambda inst: ())
        self.add_widget(button)
        
        
    def create_inner_menu(self):
        popup = Popup(title="Choose the size of the cube", size_hint=(0.5, 0.5), auto_dismiss=False)
        layout = BoxLayout(orientation="vertical")
        label = Label(text="", font_size="20dp")
        layout.add_widget(label)
        
        textinput = TextInput(multyline=False, font_size="30dp")
        layout.add_widget(textinput)
        button = Button(text="Begin!")
        
        def _create_cube(inst):
            print textinput.text
            try:
                cube_size = int(textinput.text)
            except:
                label.text = "Error. Enter proper value."
                return
            if cube_size > 8 or cube_size < 2:
                label.text = "Cube size should be between 2 and 8"
                return
            self.create_cube(cube_size)
            textinput.focus = False
            popup.dismiss()
            
        button.bind(on_release=_create_cube)
        layout.add_widget(button)
        popup.content = layout
        popup.open()
        popup.pos = popup.pos[0], Window.height / 2.
    
    def on_pause(self):
        return True

class RubiksApp(App):
    
    def build(self):
        root = MainFrame()
        return root
    

if __name__ == '__main__':
    RubiksApp().run()