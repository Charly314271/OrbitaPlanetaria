import pygame
import math
import random
from pygame.math import Vector2

# --- Simulation Parameters ---
G = 6.674e-2
BASE_MASS = 1e6
NUM_BODIES = 10
DT = 0.005
TRAIL_LENGTH = 100
MIN_BODY_RADIUS = 3
MAX_BODY_RADIUS = 15
MASS_SCALING_POWER = 0.33
SOFTENING = 50
PREDICTION_STEPS = 50  # Pasos para la predicción de trayectoria

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 80, 80)
BLUE = (80, 80, 255)
YELLOW = (255, 255, 80)
GREEN = (80, 255, 80)
ORANGE = (255, 165, 0)
GRAY = (150, 150, 150)
CENTER_CROSS_COLOR = (100, 100, 100)
HIGHLIGHT_COLOR = (255, 255, 255)

# --- UI Settings ---
FONT_SIZE = 18
TEXT_COLOR = WHITE
WINDOW_TITLE = "N-Body Gravity Simulation with Physics Table"
info_height = 150  # Altura del panel de información

class Body:
    def __init__(self, mass, pos_x, pos_y, vel_x, vel_y, color, name=""):
        self.mass = mass
        self.position = Vector2(pos_x, pos_y)
        self.velocity = Vector2(vel_x, vel_y)
        self.force = Vector2(0, 0)
        self.force_prev = Vector2(0, 0)
        self.color = color
        self.name = name or f"Body {id(self)[-4:]}"
        self.trail = []
        self.predicted_trajectory = []

        scaled_radius = (mass / BASE_MASS)**MASS_SCALING_POWER * (MAX_BODY_RADIUS - MIN_BODY_RADIUS) + MIN_BODY_RADIUS
        self.radius = max(MIN_BODY_RADIUS, min(MAX_BODY_RADIUS, int(scaled_radius)))
        self.id = id(self)

    def calculate_force(self, other_bodies):
        self.force_prev = Vector2(self.force.x, self.force.y)
        self.force.update(0, 0)
        for other in other_bodies:
            if other is self: continue
            r_vec = other.position - self.position
            dist_sq = r_vec.length_squared() + SOFTENING
            if dist_sq == 0: continue
            force_mag = G * self.mass * other.mass / dist_sq
            force_vec = r_vec.normalize() * force_mag
            self.force += force_vec

    def update_position_verlet(self):
        if self.mass == 0: return
        accel_prev = self.force_prev / self.mass
        self.position += self.velocity * DT + 0.5 * accel_prev * DT**2

    def update_velocity_verlet(self):
        if self.mass == 0: return
        accel_prev = self.force_prev / self.mass
        accel_now = self.force / self.mass
        self.velocity += 0.5 * (accel_prev + accel_now) * DT
        self.trail.append(Vector2(self.position.x, self.position.y))
        if len(self.trail) > TRAIL_LENGTH:
            self.trail.pop(0)

    def predict_trajectory(self, bodies, steps):
        temp_pos = Vector2(self.position)
        temp_vel = Vector2(self.velocity)
        temp_force = Vector2(self.force)
        temp_force_prev = Vector2(self.force_prev)

        predicted = []
        for _ in range(steps):
            accel_prev = temp_force_prev / self.mass
            temp_pos += temp_vel * DT + 0.5 * accel_prev * DT**2

            temp_force_prev = Vector2(temp_force)
            temp_force.update(0, 0)
            for other in bodies:
                if other is self: continue
                r_vec = other.position - temp_pos
                dist_sq = r_vec.length_squared() + SOFTENING
                if dist_sq == 0: continue
                force_mag = G * self.mass * other.mass / dist_sq
                temp_force += r_vec.normalize() * force_mag

            accel_prev = temp_force_prev / self.mass
            accel_now = temp_force / self.mass
            temp_vel += 0.5 * (accel_prev + accel_now) * DT

            predicted.append(Vector2(temp_pos))

        return predicted

    def draw(self, surface, font, camera_offset, center_of_mass, draw_prediction=False):
        if draw_prediction and len(self.predicted_trajectory) > 1:
            screen_predicted = []
            for world_pos in self.predicted_trajectory:
                screen_pos_vec = world_pos - camera_offset
                screen_predicted.append((int(screen_pos_vec.x), int(screen_pos_vec.y)))
            try:
                pygame.draw.lines(surface, (*self.color[:3], 100), False, screen_predicted, 1)
            except (OverflowError, ValueError):
                pass

        screen_trail = []
        for world_pos in self.trail:
            screen_pos_vec = world_pos - camera_offset
            screen_trail.append((int(screen_pos_vec.x), int(screen_pos_vec.y)))
        if len(screen_trail) > 1:
            try:
                pygame.draw.lines(surface, self.color, False, screen_trail, 1)
            except OverflowError:
                pass

        screen_position_vec = self.position - camera_offset
        draw_pos_screen = (int(screen_position_vec.x), int(screen_position_vec.y))

        dynamic_color = self.get_velocity_color()
        pygame.draw.circle(surface, dynamic_color, draw_pos_screen, int(self.radius))

        vel_end = draw_pos_screen[0] + int(self.velocity.x), draw_pos_screen[1] + int(self.velocity.y)
        pygame.draw.line(surface, GREEN, draw_pos_screen, vel_end, 1)

        if self.force.length() > 0:
            force_scaled = self.force * (10 / self.mass)
            force_end = draw_pos_screen[0] + int(force_scaled.x), draw_pos_screen[1] + int(force_scaled.y)
            pygame.draw.line(surface, RED, draw_pos_screen, force_end, 1)

        label_surface = font.render(self.name, True, TEXT_COLOR)
        label_rect = label_surface.get_rect(center=(draw_pos_screen[0], draw_pos_screen[1] - self.radius - 10))
        surface.blit(label_surface, label_rect)

    def get_velocity_color(self):
        speed = self.velocity.length()
        max_speed = 50
        speed_ratio = min(speed / max_speed, 1.0)
        red = int(255 * speed_ratio)
        blue = int(255 * (1 - speed_ratio))
        return (red, 0, blue)

class PhysicsTable:
    def __init__(self, x, y, width, height, font):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.header_font = pygame.font.SysFont(None, FONT_SIZE, bold=True)
        self.row_height = 25
        self.column_widths = [180, 140, 140, 140, 220]  # Ajustado para mejor visualización

    def draw(self, surface, bodies, selected_body=None):
        pygame.draw.rect(surface, (20, 20, 40), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.width, self.height), 1)

        pygame.draw.rect(surface, (40, 40, 70), (self.x, self.y, self.width, self.row_height))
        headers = ["Body", "Mass", "Velocity", "Force", "Energy"]
        
        for i, header in enumerate(headers):
            x_pos = self.x + sum(self.column_widths[:i]) + 20
            text = self.header_font.render(header, True, WHITE)
            surface.blit(text, (x_pos, self.y + 4))

        pygame.draw.line(surface, GRAY, (self.x, self.y + self.row_height),
                         (self.x + self.width, self.y + self.row_height), 1)

        for i, body in enumerate(bodies):
            y_pos = self.y + self.row_height + i * self.row_height
            bg_color = (30, 30, 50) if i % 2 == 0 else (40, 40, 60)
            if body == selected_body:
                bg_color = (70, 70, 110)
            pygame.draw.rect(surface, bg_color, (self.x, y_pos, self.width, self.row_height))

            values = [
                (body.name, body.color),
                (f"{body.mass/BASE_MASS:.1f} M", WHITE),
                (f"{body.velocity.length():.1f}", GREEN),
                (f"{body.force.length():.1f}", RED),
                (f"{0.5 * body.mass * body.velocity.length_squared():.1e}", YELLOW)
            ]

            for j, (text_str, color) in enumerate(values):
                col_x = self.x + sum(self.column_widths[:j]) + 20
                text_surface = self.font.render(text_str, True, color)
                surface.blit(text_surface, (col_x, y_pos + 5))

            for j in range(1, len(self.column_widths)):
                x = self.x + sum(self.column_widths[:j])
                pygame.draw.line(surface, GRAY, (x, y_pos), (x, y_pos + self.row_height))

def calculate_center_of_mass(bodies):
    total_mass = 0.0
    weighted_position_sum = Vector2(0, 0)
    for body in bodies:
        total_mass += body.mass
        weighted_position_sum += body.position * body.mass
    if total_mass == 0: 
        return Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    else: 
        return weighted_position_sum / total_mass

def main():
    pygame.init()
    pygame.font.init()

    screen_info = pygame.display.Info()
    SCREEN_WIDTH = screen_info.current_w
    SCREEN_HEIGHT = screen_info.current_h - info_height if screen_info.current_h > 768 else screen_info.current_h

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + info_height), 
                                   pygame.FULLSCREEN if screen_info.current_h > 768 else 0)
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', FONT_SIZE)
    bold_font = pygame.font.SysFont('Arial', FONT_SIZE, bold=True)

    # Create 5 bodies
    bodies = []
    initial_offset_x = SCREEN_WIDTH // 2
    initial_offset_y = SCREEN_HEIGHT // 2
    star_mass = 500 * BASE_MASS

    # Central star
    bodies.append(Body(mass=star_mass, pos_x=initial_offset_x, pos_y=initial_offset_y,
                      vel_x=0, vel_y=0, color=YELLOW, name="Star"))

    # Create 4 orbiting bodies
    colors = [BLUE, RED, GREEN, ORANGE]
    for i in range(4):
        angle = 2 * math.pi * i / 4  # Distribute evenly around the star
        distance = 150 + i * 50  # Incremental distance
        velocity = math.sqrt(G * star_mass / distance) * (0.9 + 0.1 * i)  # Slightly varying velocities
        
        pos_x = initial_offset_x + distance * math.cos(angle)
        pos_y = initial_offset_y + distance * math.sin(angle)
        vel_x = -velocity * math.sin(angle)
        vel_y = velocity * math.cos(angle)
        
        bodies.append(Body(mass=(10 + i*5) * BASE_MASS, 
                          pos_x=pos_x, pos_y=pos_y,
                          vel_x=vel_x, vel_y=vel_y,
                          color=colors[i],
                          name=f"Planet {chr(65+i)}"))

    physics_table = PhysicsTable(10, SCREEN_HEIGHT + 10, SCREEN_WIDTH - 20, info_height - 20, font)

    # Main loop
    running = True
    draw_predictions = True
    selected_body = None
    screen_center = Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p:
                    draw_predictions = not draw_predictions
                elif event.key == pygame.K_1:
                    selected_body = bodies[0] if len(bodies) > 0 else None
                elif event.key == pygame.K_2:
                    selected_body = bodies[1] if len(bodies) > 1 else None
                elif event.key == pygame.K_3:
                    selected_body = bodies[2] if len(bodies) > 2 else None
                elif event.key == pygame.K_4:
                    selected_body = bodies[3] if len(bodies) > 3 else None
                elif event.key == pygame.K_5:
                    selected_body = bodies[4] if len(bodies) > 4 else None

        # Physics updates
        for body in bodies:
            body.calculate_force(bodies)
        for body in bodies:
            body.update_position_verlet()
        for body in bodies:
            body.calculate_force(bodies)
        for body in bodies:
            body.update_velocity_verlet()

        if draw_predictions:
            for body in bodies:
                body.predicted_trajectory = body.predict_trajectory(bodies, PREDICTION_STEPS)

        # Drawing
        screen.fill(BLACK)
        center_of_mass = calculate_center_of_mass(bodies)
        camera_offset = center_of_mass - screen_center

        for body in bodies:
            body.draw(screen, font, camera_offset, center_of_mass, draw_prediction=draw_predictions)

        physics_table.draw(screen, bodies, selected_body)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()