import nltk

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy import platform
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

class WindowManager(ScreenManager):
    pass

class EditScreen(Screen):
    pass

class PresentScreen(Screen):
    pass

class PresentWidget(BoxLayout):
    window_size  = Window.size
    orientation = 'vertical'
    display_notes ='sample. text.'
    parsed_notes = ['sample', '.', '\\//', 'text', '.']

    current = 0
    last_current = 0
    previous = 0
    last_previous = 0
    block = 0

    def __init__(self,*args, **kwargs):
        super().__init__(**kwargs)
        self.init_screen()
        self.parsed_notes = mainwidget.parsed_notes

        if self.is_desktop:
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)

    def init_screen(self):
        self.head_box = BoxLayout(orientation = 'horizontal', size_hint=(1,0.1))
        self.header = Label(size_hint =(0.85,1), text="SIMPLI-PREZ", markup=True)
        self.edit_text = Button(size_hint = (.15, 1), text = "Edit Script")
        self.head_box.add_widget(self.header)
        self.head_box.add_widget(self.edit_text)

        self.edit_text.bind(on_release=self.change_window)

        self.display_notes = Label(text="Sample. Text", markup = True, color=(0.5,0.5,0.5,0.9))
        self.display_notes.text_size = (self.window_size[0]*0.9,self.window_size[1]*0.9)

        self.add_widget(self.head_box)
        self.add_widget(self.display_notes)
        self.find_sentences()

    def is_desktop(self):
        if platform in ('linux', 'windows', 'macosx'):
            return True
        else:
            return False
    def change_window(self, instance):
        simpliprezapp.screen_manager.current = 'edit'
    
    def keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_keyboard_down)
        self._keyboard = None

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
            if keycode[1] == 'left':
                print(keycode)
            elif keycode[1] == 'right':
                pass
            return True

    def on_touch_down(self, touch):
        if touch.y < self.height*0.9:
            if touch.x < self.width/2:
                self.current = self.previous
                self.previous = self.previous - 1
                self.block_switch()
                self.last_sentence()
            else:
                self.previous = self.current
                self.current = self.current + 1
                self.block_switch()
                self.next_sentence()
        return super(BoxLayout, self).on_touch_down(touch)

    def next_sentence(self):
        found = False
        while not found:
            if self.current >= len(self.parsed_notes)-1:
                found = True
            elif (self.parsed_notes[self.current] == '.' or self.parsed_notes[self.current] == '?' or self.parsed_notes[self.current] == '!' or self.parsed_notes[self.current] == '//\\'): 
                found = True
            else:
                self.current = self.current + 1
        self.current = self.current + 1
        self.bold_next_sentence()

    def last_sentence(self):
        try:
            self.previous = self.previous - 1
        except:
            pass
        found = False
        while not found and self.previous > 0:
            if (self.parsed_notes[self.previous] == '.' or self.parsed_notes[self.previous] == '?' or self.parsed_notes[self.previous] == '!' or self.parsed_notes[self.previous] == '//\\'):
                found = True
            # elif self.previous <= 0:
            #     self.previous = 0
            #     found = True
            else:
                self.previous = self.previous -1
        if self.previous < 0:
            self.previous = 0
        self.bold_last_sentence()

    def bold_next_sentence(self):
        try:
            self.parsed_notes.remove('[b][color=#FFFFFF]')
            self.parsed_notes.remove('[/color][/b]')
            self.current = self.current -2
        except:
            pass
        self.parsed_notes.insert(self.previous, '[b][color=#FFFFFF]')
        self.parsed_notes.insert(self.current+1, '[/color][/b]')
        if abs(self.last_current-self.current) == 1:
            self.current = self.current +2
            self.previous = self.previous +2
            self.next_sentence()
        else:
            self.last_current = self.current
        self.string_notes()

    def bold_last_sentence(self):
        try:
            self.parsed_notes.remove('[b][color=#FFFFFF]')
            self.parsed_notes.remove('[/color][/b]')
        except:
            pass
        if self.previous == 0:
            self.parsed_notes.insert(self.previous, '[b][color=#FFFFFF]')
        else:
            self.parsed_notes.insert(self.previous+1, '[b][color=#FFFFFF]')
        self.parsed_notes.insert(self.current+1, '[/color][/b]')
        self.last_current = self.current
        self.string_notes()

    def string_notes(self):
        self.decoded_notes = ''
        for element in self.parsed_notes:
            if element == '//\\':
                self.decoded_notes = self.decoded_notes + '\n'
            elif element == '\\//':
                self.decoded_notes = self.decoded_notes + ' '
            else:
                self.decoded_notes = self.decoded_notes + element
        self.display_notes.text = self.decoded_notes
        # print(self.decoded_notes)
        print("current: " + str(self.current) + " previous: " + str(self.previous) )
    
    def find_sentences(self):
        self.sentence_ends = [i for i, x in enumerate(self.parsed_notes) if x == '.']
        print(self.sentence_ends)

    def cut_blocks(self):
        self.block_notes = []
        self.block = 0
        for i in range(0, (len(self.parsed_notes)//800)+1):
            self.block_notes.append(self.parsed_notes[self.get_block_start_index(i):self.get_block_end_index(i+1)])
            i = i+1
        self.parsed_notes = self.block_notes[self.block]
        print("the length is " + str(len(self.block_notes)))
    
    def get_block_start_index(self, i):
        if i == 0:
            return 0
        for x in range(0, len(self.sentence_ends)):
            if self.sentence_ends[x] > i*800:
                return self.sentence_ends[x-1]+1
            x = x+1
    
    def get_block_end_index(self, i):
        for sentence in self.sentence_ends:
            if sentence >= i*800:
                return sentence+1
        
    def block_switch(self):
        try:
            if self.current >= len(self.block_notes[self.block])-1 and self.block < len(self.block_notes):
                self.block = self.block + 1
                self.parsed_notes = self.block_notes[self.block]
                self.current = 0
                self.previous = 0
            if self.previous == -1:
                self.block = self.block -1 
                self.parsed_notes = self.block_notes[self.block]
                self.current = len(self.parsed_notes)-1
                self.previous = self.current
        except:
            self.block = self.block-1

#___________________________________________________________________________________________________________________________________

class MainWidget(BoxLayout):
    orientation = 'vertical'
    notes ='sample text'
    parsed_notes = ['sample', '.', '\\//', 'text', '.']

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.init_screen()

    def init_screen(self):
        self.head_box = BoxLayout(orientation = 'horizontal', size_hint=(1,0.1))
        self.header = Label(size_hint =(0.85,1), text="SIMPLI-PREZ", markup=True)
        self.submit_text = Button(size_hint = (.15,1), text = "Presenters Mode")
        self.head_box.add_widget(self.header)
        self.head_box.add_widget(self.submit_text)

        self.submit_text.bind(on_release=self.parse_text)

        self.notes = TextInput(hint_text="Write your notes here", multiline= True)
        self.add_widget(self.head_box)
        self.add_widget(self.notes)

    #LOGIC
    def parse_text(self, instance):
        encoded_notes = self.notes.text.replace("\n", " //\\ ")
        encoded_notes = encoded_notes.replace(" ", " \\// ")
        self.parsed_notes = nltk.word_tokenize(encoded_notes)
        presentwidget.parsed_notes = self.parsed_notes
        presentwidget.find_sentences()
        presentwidget.cut_blocks()
        presentwidget.string_notes()
        self.change_window()
    
    def change_window(self):
        simpliprezapp.screen_manager.current = 'present'    

class SimpliPrezApp(App):
    def build(self):
        self.screen_manager = ScreenManager()

        screen = Screen(name='edit')
        screen.add_widget(mainwidget)
        self.screen_manager.add_widget(screen)

        screen = Screen(name='present')
        screen.add_widget(presentwidget)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

if __name__ == '__main__':
    mainwidget = MainWidget()
    presentwidget = PresentWidget()
    simpliprezapp = SimpliPrezApp()
    simpliprezapp.run()
