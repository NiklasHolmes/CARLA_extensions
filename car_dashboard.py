"""
Generates a separate dashboard showing information about velocity and fuel level. 

"""

import carla
import pygame
import math
import os
import threading
import sys
import time
import argparse

class CarDashboard(threading.Thread):

    def __init__(self, world, width=960, height=540):
        """Initialize dashboard in separate thread.
        
        Args:
            world: CARLA world object to get hero vehicle from
            width: Dashboard window width (default 960)
            height: Dashboard window height (default 540)
        """
        # use threading to run dashboard in separate thread and avoid blocking main CARLA loop
        threading.Thread.__init__(self)
        self.daemon = True  # Run as daemon thread
        
        self.world = world
        self.width = width
        self.height = height
        
        # Fuel bars: 0-5 bars filled (0 = empty, 5 = full)
        self.fuel_level = 5
        
        # Thread control
        self.running = True
        self._display = None
        self._font_large = None
        self._font_small = None
        self._fuel_image = None
        
    def run(self):
        """Main dashboard thread loop."""
        try:
            pygame.init()
            self._display = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Car Dashboard")
            
            # Scale fonts (based on window height)
            font_large_size = max(40, int(self.height * 0.25))
            font_small_size = max(20, int(self.height * 0.08))
            self._font_large = pygame.font.Font(None, font_large_size)
            self._font_small = pygame.font.Font(None, font_small_size)
            
            # Load and scale fuel image
            fuel_image_path = os.path.join(os.path.dirname(__file__), 'images', 'fuel_test.jpg')
            try:
                img_size = max(80, int(self.height * 0.15))
                self._fuel_image = pygame.image.load(fuel_image_path)
                self._fuel_image = pygame.transform.scale(self._fuel_image, (img_size, img_size))
            except:
                self._fuel_image = None
            
            clock = pygame.time.Clock()
            
            # Main dashboard loop
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                
                velocity_kmh = self._get_velocity()
                self._render(velocity_kmh)
                clock.tick(30)  # 30 FPS
                
        except Exception as e:
            print(f"Dashboard error: {e}")
        finally:
            if self._display is not None:
                pygame.quit()
    
    def _get_velocity(self):
        """ Get hero vehicle velocity in km/h """
        try:
            if self.world and self.world.player:
                v = self.world.player.get_velocity()
                return 3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)
        except:
            pass
        return 0.0
    
    def _render(self, velocity_kmh):
        """ Render dashboard """
        # black background
        self._display.fill((0, 0, 0))
        
        # Left: velocity
        velocity_text = self._font_large.render(f"{int(velocity_kmh)}", True, (255, 255, 255))
        velocity_x = self.width // 4
        velocity_y = self.height // 2 - int(self.height * 0.1)
        velocity_rect = velocity_text.get_rect(center=(velocity_x, velocity_y))
        self._display.blit(velocity_text, velocity_rect)
        
        # "km/h" label below velocity
        unit_text = self._font_small.render("km/h", True, (255, 255, 255))
        unit_y = velocity_y + int(self.height * 0.15)
        unit_rect = unit_text.get_rect(center=(velocity_x, unit_y))
        self._display.blit(unit_text, unit_rect)
        
        # Right: fuel bars (horizontal)
        bar_height = max(15, int(self.height * 0.08))
        bar_width = max(150, int(self.width * 0.25))
        bar_spacing = int(bar_height * 0.2)
        
        total_bar_height = 5 * bar_height + 4 * bar_spacing
        
        # Get fuel position
        fuel_area_x = int(self.width * 0.62)
        fuel_area_y = self.height // 2 - total_bar_height // 2
        
        # Draw bars
        for i in range(5):
            bar_y = fuel_area_y + i * (bar_height + bar_spacing)
            
            if i < (5 - self.fuel_level):
                color = (128, 128, 128)  # Grey (empty)
            else:
                color = (255, 255, 255)  # White (filled)
            
            pygame.draw.rect(self._display, color, 
                           (fuel_area_x, bar_y, bar_width, bar_height))
        
        # Add fuel image
        if self._fuel_image:
            image_x = fuel_area_x - int(self.width * 0.15)
            image_y = fuel_area_y + (total_bar_height - self._fuel_image.get_height()) // 2
            self._display.blit(self._fuel_image, (image_x, image_y))
        
        pygame.display.flip()
    
    def set_fuel_level(self, level):
        """ Set fuel level (0-5 bars) """
        self.fuel_level = max(0, min(5, level))
    
    def close(self):
        """ Close the dashboard window """
        self.running = False
        self.join(timeout=2)


def find_hero_vehicle(world):
    """ Find the hero vehicle in the CARLA world """
    for actor in world.get_actors():
        if actor.attributes.get('role_name') == 'hero':
            return actor
    return None

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='CARLA Car Dashboard')
    argparser.add_argument(
        '--host', metavar='H', default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port', metavar='P', default=2000, type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '--res', metavar='WIDTHxHEIGHT', default='960x540',
        help='window resolution (default: 960x540)')
    args = argparser.parse_args()
    args.width, args.height = [int(x) for x in args.res.split('x')]
    dashboard = None
    
    try:
        # Connect to CARLA
        client = carla.Client(args.host, args.port)
        client.set_timeout(10.0)
        world = client.get_world()
        print(f"[Dashboard] Connected to CARLA at {args.host}:{args.port}")
        
        # Find hero vehicle
        hero = find_hero_vehicle(world)
        if hero is None:
            print("[Dashboard] ERROR: Hero vehicle not found! Start manual_control.py first.")
            sys.exit(1)
        
        print(f"[Dashboard] Found hero: {hero.type_id}")
        
        # Minimal wrapper for world.player reference
        class WorldWrapper:
            def __init__(self, player):
                self.player = player
        
        # Start dashboard
        dashboard = CarDashboard(WorldWrapper(hero), width=args.width, height=args.height)
        dashboard.start()
        print(f"[Dashboard] Started ({args.res}). Press Ctrl+C to exit.")
        
        while dashboard.running:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n[Dashboard] Shutting down...")
    except Exception as e:
        print(f"[Dashboard] ERROR: {e}")
    finally:
        if dashboard is not None:
            dashboard.close()
        print("[Dashboard] Closed.")

