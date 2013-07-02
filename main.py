

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
        self.cube = LogicalCube(cell_in_row=cell_in_row, win_cb=self.show_win)
        self.add_widget(self.cube.widget)
        self.cube.widget.update_scene()
        shake_button = Button(text="Shake", size_hint=(None, None),\
                        size=("150dp", "75dp"), pos=(0,0), font_size="40dp")
        shake_button.bind(on_release=lambda inst: self.cube.widget.shake())
        self.add_widget(shake_button)
        help_button = Button(text="Help", size_hint=(None, None),\
                        size=("150dp", "75dp"), font_size="40dp")
        self.add_widget(help_button)
        help_button.pos = (Window.width - help_button.width, 0)
        help_button.bind(on_release=self.show_help) 
    
    def show_help(self, btn):
        help_text = "To start the game touch Shake button to get cube shaken.\n\n"\
                    "To rotate the a surface of the cube tap on some cell and hold\n"\
                    "for a jiffy then move the finger in the side you want to rotate\n"\
                    "the cube\n\n"\
                    "Scale the cube with two fingers."
        content = Label(text=help_text, font_size="20dp")
        Popup(content=content, title="Game help", size_hint=(0.75, 0.75)).open()
        
    def show_win(self):
        content = Label(text="Congratulations, you win!", font_size="20dp")
        Popup(content=content, title="Game info", size_hint=(0.5, 0.5)).open()
        
    def create_inner_menu(self):
        popup = Popup(title="Choose the size of the cube", size_hint=(0.5, 0.5), auto_dismiss=False)
        layout = BoxLayout(orientation="vertical")
        label = Label(text="", font_size="20dp")
        layout.add_widget(label)
        
        textinput = TextInput(multiline=False, font_size="30dp")
        layout.add_widget(textinput)
        button = Button(text="Begin!", font_size="30dp")
        
        def _create_cube(inst):
            try:
                cube_size = int(textinput.text)
            except:
                label.text = "Error. Enter proper value."
                return
            if cube_size > 6 or cube_size < 2:
                label.text = "Cube size should be between 2 and 6"
                return
            self.create_cube(cube_size)
            textinput.focus = False
            popup.dismiss()
            
        button.bind(on_release=_create_cube)
        layout.add_widget(button)
        popup.content = layout
        popup.open()
        popup.pos = popup.pos[0], Window.height / 2.


class RubiksApp(App):
    
    def build(self):
        root = MainFrame()
        return root

    def on_pause(self):
        return True    

if __name__ == '__main__':
    RubiksApp().run()