# OLED display initialization using MicroPython's display library
from machine import Pin, I2C
import sh1106
from utime import sleep, ticks_ms
from random import randrange

def initialize_display():
    sleep(1)
    i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
    global display
    display = sh1106.SH1106_I2C(128, 64, i2c, Pin(2), 0x3c)

#  GPIO setup code
def setup_gpio():
    pass
    global buttonRight, buttonLeft, buttonUp, buttonDown, buttonStart
    
    buttonRight = Pin(10, Pin.IN, Pin.PULL_UP)
    buttonLeft = Pin(13, Pin.IN, Pin.PULL_UP)
    buttonDown = Pin(12, Pin.IN, Pin.PULL_UP)
    buttonUp = Pin(11, Pin.IN, Pin.PULL_UP)
    
    buttonStart = Pin(14, Pin.IN, Pin.PULL_UP)

def read_joystick():
   
    if buttonRight.value()==False:
        return 'R'
    if buttonLeft.value()==False:
        return 'L'
    if buttonUp.value()==False:
        return 'U'
    if buttonDown.value()==False:
        return 'D'

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Deque(list):  # deque implementation using Python list
    def push_front(self, item):
        self.insert(0, item)

    def pop_back(self):
        return self.pop()

    def clear(self):
        del self[:]

class Snake:
    def __init__(self):
        self.body = Deque([Vector2(3, 5), Vector2(4, 5), Vector2(5, 5)])
        self.direction = Vector2(1, 0)
        self.add_segment = False

        
    def eat_food(self):
        # When the snake eats food, set the flag to add a new segment
        self.add_segment = True

    def draw(self):
        display.fill(0)  # Clear the display
        # Draw each segment of the snake
        for segment in self.body:

            x = min(max(segment.x * 4, 0), display.width - 4)
            y = min(max(segment.y * 4, 0), display.height - 4)
            display.fill_rect(x, y, 4, 4, 1)  # Draw a larger square for each segment
        display.show()  # Update the display

    def update(self):
        self.body.push_front(Vector2(self.body[0].x + self.direction.x, self.body[0].y + self.direction.y))
        if not self.add_segment:
            self.body.pop_back()
        else:
            self.add_segment = False

class Food:
    def __init__(self):
        self.position = self.set_new_position()

    def draw(self):
        display.fill(0)  # Clear the display

        x = min(max(self.position.x * 4, 0), display.width - 4)
        y = min(max(self.position.y * 4, 0), display.height - 4)
        display.fill_rect(x, y, 4, 4, 1) 
        display.show()  # Update the display

    def generate_random_cell(self):
        max_x = (display.width // 4) - 1  # Calculate maximum x position
        max_y = (display.height // 4) - 1  # Calculate maximum y position
        random_x = randrange(max_x + 1)  # Generate random x within bounds
        random_y = randrange(max_y + 1)  # Generate random y within bounds
        return Vector2(random_x, random_y)

    def set_new_position(self):
        new_position = self.generate_random_cell()
        
        return new_position

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.running = True
        self.score = 0
        self.screen = 0

    def draw(self):
        if self.running:
            self.snake.draw()
            self.food.draw()

    def update(self):
        if self.running:
            self.snake.update()
            
        # Check for collision between snake and food
        if self.snake.body[0].x == self.food.position.x and self.snake.body[0].y == self.food.position.y:
            self.snake.eat_food()
            self.food.position = self.food.set_new_position()  # Reset food position


    def handle_input(self):
        # Read joystick input and update snake direction accordingly
        input_key = read_joystick() 
        if input_key:
            self.snake.direction = self.handle_key_press(input_key)

    def handle_key_press(self, key):
        # Handle joystick key press and return updated direction
        new_direction = self.snake.direction  # Default to current direction
       
        
        if key == 'U' and new_direction.y != 1:
            return Vector2(0, -1)  # Up
        elif key == 'D' and new_direction.y != -1:
            return Vector2(0, 1)   # Down
        elif key == 'L' and new_direction.x != 1:
            return Vector2(-1, 0)  # Left
        elif key == 'R' and new_direction.x != -1:
            return Vector2(1, 0)   # Right
        return new_direction


initialize_display()
setup_gpio()
game = Game()

# Set up timers
snake_timer = ticks_ms()  # snake movement speed
refresh_timer = ticks_ms()  #  screen refresh rate

# Constants for controlling timing
SNAKE_SPEED = 200  # Snake speed in milliseconds 
REFRESH_RATE = 50 # Screen refresh rate in milliseconds 

# Main game loop
while True:
    # Check if it's time to update the snake movement based on its speed
    if ticks_ms() - snake_timer > SNAKE_SPEED:
        game.handle_input()  # Check for input
        game.update()  # Update game state
        snake_timer = ticks_ms()  # Reset snake timer

    # Check if it's time to refresh the screen at a fixed rate
    if ticks_ms() - refresh_timer > REFRESH_RATE:
        game.draw()  # Redraw the screen
        refresh_timer = ticks_ms()  # Reset screen refresh timer

    # Add a small delay to control the loop execution speed
    sleep(0.01)  # Adjust this value as needed

