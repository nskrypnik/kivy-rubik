

from kivy.app import App
from kivy.uix.widget import Widget

from cube import LogicalCube

class MainFrame(Widget):
    
    def __init__(self, *larg, **kw):
        
        super(MainFrame, self).__init__(*larg, **kw)
        self.cube = LogicalCube()
        self.add_widget(self.cube.widget)
        self.cube.widget.update_scene()
        

class RubiksApp(App):
    
    def build(self):
        root = MainFrame()
        return root
    

if __name__ == '__main__':
    RubiksApp().run()