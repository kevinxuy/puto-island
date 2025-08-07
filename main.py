from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.clock import Clock
import random

class PutoIslandGame(Widget):
    def __init__(self, **kwargs):
        super(PutoIslandGame, self).__init__(**kwargs)
        
        # Game state
        self.money = 1000
        self.population = 10
        self.buildings = []
        
        # Create UI
        self.setup_ui()
        
        # Update game every second
        Clock.schedule_interval(self.update_game, 1.0)
    
    def setup_ui(self):
        # Background
        with self.canvas:
            Color(0.2, 0.6, 0.8)  # Light blue background
            self.bg = Rectangle(pos=self.pos, size=self.size)
        
        # Bind size changes
        self.bind(size=self.update_bg, pos=self.update_bg)
        
        # Create UI layout
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Status display
        self.status_label = Label(
            text=f'Money: ${self.money} | Population: {self.population}',
            size_hint=(1, 0.1),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(self.status_label)
        
        # Game area
        game_area = FloatLayout(size_hint=(1, 0.8))
        
        # Buildings
        self.add_sample_buildings(game_area)
        
        layout.add_widget(game_area)
        
        # Control buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=5)
        
        hotel_btn = Button(text='Build Hotel ($200)', on_press=self.build_hotel)
        restaurant_btn = Button(text='Build Restaurant ($150)', on_press=self.build_restaurant)
        temple_btn = Button(text='Build Temple ($100)', on_press=self.build_temple)
        
        button_layout.add_widget(hotel_btn)
        button_layout.add_widget(restaurant_btn)
        button_layout.add_widget(temple_btn)
        
        layout.add_widget(button_layout)
        
        self.add_widget(layout)
    
    def add_sample_buildings(self, parent):
        # Add some initial buildings
        buildings_data = [
            {'name': 'Hotel', 'pos': (100, 200), 'color': (0.8, 0.4, 0.2)},
            {'name': 'Restaurant', 'pos': (250, 150), 'color': (0.2, 0.8, 0.4)},
            {'name': 'Temple', 'pos': (150, 300), 'color': (0.6, 0.2, 0.8)}
        ]
        
        for building in buildings_data:
            building_widget = Widget(size=(80, 60))
            building_widget.pos = building['pos']
            
            with building_widget.canvas:
                Color(*building['color'])
                Rectangle(pos=building_widget.pos, size=building_widget.size)
            
            label = Label(
                text=building['name'],
                pos=building_widget.pos,
                size=building_widget.size,
                color=(1, 1, 1, 1)
            )
            
            parent.add_widget(building_widget)
            parent.add_widget(label)
    
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def build_hotel(self, instance):
        if self.money >= 200:
            self.money -= 200
            self.population += 5
            self.update_status()
            print("Built a hotel!")
    
    def build_restaurant(self, instance):
        if self.money >= 150:
            self.money -= 150
            self.population += 3
            self.update_status()
            print("Built a restaurant!")
    
    def build_temple(self, instance):
        if self.money >= 100:
            self.money -= 100
            self.population += 2
            self.update_status()
            print("Built a temple!")
    
    def update_game(self, dt):
        # Generate income based on population
        income = self.population * 2
        self.money += income
        self.update_status()
    
    def update_status(self):
        self.status_label.text = f'Money: ${self.money} | Population: {self.population}'

class PutoIslandApp(App):
    def build(self):
        return PutoIslandGame()

if __name__ == '__main__':
    PutoIslandApp().run()