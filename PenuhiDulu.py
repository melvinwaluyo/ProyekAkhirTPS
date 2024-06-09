import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
ELEVATOR_CAPACITY = 10
ELEVATOR_WAIT_TIME = 180  # seconds
PERSON_SIZE = 10

# User-controlled spawn rate (people per minute)
SPAWN_RATE = 45  # Example: 60 people per minute

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Elevator Queue Simulation")

# Elevator Class
class Elevator:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.capacity = ELEVATOR_CAPACITY
        self.people = 0
        self.full = False
        self.timer = 0

    def update(self, dt):
        if self.full:
            self.timer += dt
            if self.timer >= ELEVATOR_WAIT_TIME:
                self.people = 0
                self.full = False
                self.timer = 0

    def draw(self):
        color = RED if self.full else BLUE
        pygame.draw.rect(screen, color, (self.x, self.y, 50, 50))
        font = pygame.font.SysFont(None, 24)
        if self.full:
            img = font.render(f'Full', True, WHITE)
            screen.blit(img, (self.x + 5, self.y + 15))
            countdown_img = font.render(f'{int(ELEVATOR_WAIT_TIME - self.timer)}s', True, BLACK)
            screen.blit(countdown_img, (self.x + 60, self.y + 15))
        else:
            img = font.render(f'{self.people}/{ELEVATOR_CAPACITY}', True, WHITE)
            screen.blit(img, (self.x + 5, self.y + 15))

    def add_person(self):
        if not self.full:
            self.people += 1
            if self.people == ELEVATOR_CAPACITY:
                self.full = True

# Person Class
class Person:
    def __init__(self, x, y, elevators, entry_point):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.elevators = elevators
        self.target_elevator = elevators[current_elevator_index]
        self.waiting = False
        self.in_elevator = False
        self.stop_x = self.x
        self.stop_y = self.y
        self.entry_point = entry_point
        self.state = 'moving_vertical'  # States: moving_vertical, moving_horizontal, moving_to_elevator

    def update(self):
        if not self.in_elevator:
            if self.target_elevator.full:
                self.update_target_elevator()
            if not self.all_elevators_full():
                self.move()

    def update_target_elevator(self):
        available_elevators = [e for e in self.elevators if not e.full]
        if available_elevators:
            self.target_elevator = available_elevators[0]
            self.waiting = False
        else:
            self.waiting = True
            self.stop_x = self.x
            self.stop_y = self.y

    def all_elevators_full(self):
        return all(elevator.full for elevator in self.elevators)

    def move(self):
        if self.state == 'moving_vertical':
            if self.entry_point == 'North1':
                if self.y < 300:
                    self.y += 1
                else:
                    self.state = 'moving_horizontal'
            elif self.entry_point == 'North2':
                if self.y < 300:
                    self.y += 1
                else:
                    self.state = 'moving_horizontal'
            elif self.entry_point == 'South1':
                if self.y > 300:
                    self.y -= 1
                else:
                    self.state = 'moving_horizontal'
            elif self.entry_point == 'South2':
                if self.y > 300:
                    self.y -= 1
                else:
                    self.state = 'moving_horizontal'
        elif self.state == 'moving_horizontal':
            if self.entry_point == 'North1' or self.entry_point == 'South1':
                if self.x < 375:
                    self.x += 1
                else:
                    self.state = 'moving_to_elevator'
            elif self.entry_point == 'North2' or self.entry_point == 'South2':
                if self.x > 425:
                    self.x -= 1
                else:
                    self.state = 'moving_to_elevator'
        elif self.state == 'moving_to_elevator':
            if self.x < self.target_elevator.x + 25:
                self.x += 1
            elif self.x > self.target_elevator.x + 25:
                self.x -= 1
            if self.y < self.target_elevator.y + 25:
                self.y += 1
            elif self.y > self.target_elevator.y + 25:
                self.y -= 1
            if self.x == self.target_elevator.x + 25 and self.y == self.target_elevator.y + 25:
                self.target_elevator.add_person()
                self.in_elevator = True
                global total_people
                total_people += 1

    def draw(self):
        if not self.in_elevator:
            pygame.draw.circle(screen, GREEN, (self.x, self.y), PERSON_SIZE)

# Create elevators
elevators = [
    Elevator(250, 250),  # Elevator A
    Elevator(250, 350),  # Elevator B
    Elevator(500, 250),  # Elevator C
    Elevator(500, 350)   # Elevator D
]

# Create people
people = []

# Simulation variables
running = True
clock = pygame.time.Clock()
start_time = time.time()
total_people = 0
spawn_interval = 60 / SPAWN_RATE  # Time in seconds between spawns
last_spawn_time = time.time()

# Global index to keep track of the current elevator to be filled
current_elevator_index = 0

# Main loop
while running:
    dt = clock.tick(30) / 1000  # Time in seconds since last frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Add a new person at user-controlled intervals
    if time.time() - last_spawn_time > spawn_interval:
        entry_point = random.choice(['North1', 'North2', 'South1', 'South2'])
        if entry_point == 'North1':
            person = Person(375, 0, elevators, entry_point)
        elif entry_point == 'North2':
            person = Person(425, 0, elevators, entry_point)
        elif entry_point == 'South1':
            person = Person(375, SCREEN_HEIGHT, elevators, entry_point)
        elif entry_point == 'South2':
            person = Person(425, SCREEN_HEIGHT, elevators, entry_point)
        people.append(person)
        last_spawn_time = time.time()

    # Update elevators
    for i, elevator in enumerate(elevators):
        elevator.update(dt)
        if elevator.full and i == current_elevator_index:
            current_elevator_index = (current_elevator_index + 1) % len(elevators)

    # Update people
    for person in people:
        person.update()

    # Draw everything
    screen.fill(WHITE)

    # Draw roads (narrower, two lanes)
    pygame.draw.line(screen, BLACK, (350, 0), (350, SCREEN_HEIGHT), 2)  # Lane separator 1
    pygame.draw.line(screen, BLACK, (450, 0), (450, SCREEN_HEIGHT), 2)  # Lane separator 2
    pygame.draw.line(screen, BLACK, (400, 0), (400, SCREEN_HEIGHT), 1)  # Central separator line

    for elevator in elevators:
        elevator.draw()
    for person in people:
        person.draw()

    # Display elapsed time and total people
    elapsed_time = int(time.time() - start_time)
    font = pygame.font.SysFont(None, 24)
    time_img = font.render(f'Time: {elapsed_time}s', True, BLACK)
    people_img = font.render(f'Total People: {total_people}', True, BLACK)
    screen.blit(time_img, (650, 10))
    screen.blit(people_img, (650, 40))

    pygame.display.flip()

pygame.quit()
