# ===== main_multi_zones.py =====
"""
Multi-world simulation with MULTIPLE SHARED ZONES
- TAB: Switch between 3 territories
- B: NPC Inspector (current territory)
- S: Statistics (current territory)
- C: Combined View (all 3 territories + shared zones)
- P: Shared PANTHEON view
- N: Shared SCIENCE view
- T: Shared TRADE view
- 0-5: Filter inspector by zone
- ESC: Quit
"""

import pygame
import yaml
import random
from typing import Dict, List

from npc import NPC, DoctrineType, NPCArchetype
from rendering import (
    draw_npc_with_doctrine,
    draw_npc_inspector,
    draw_statistics_dashboard,
    draw_corner_stats,
    draw_color_legend,
    COLORS as RENDER_COLORS,
)
from shared_zones import (
    SharedZoneTracker,
    draw_shared_zones_view,
    draw_specific_shared_zone,
)

# ===== CONFIG LOADER =====

def load_config(path: str = "int5.yaml") -> Dict:
    """Load YAML configuration"""
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {
            "display": {"width": 1200, "height": 900, "fps": 90},
            "fonts": {"header": 38, "large": 55, "small": 27, "tiny": 21},
            "coherence": {"inertia": 0.8},
            "shift": {"duration": 300, "travel_ratio": 0.25},
            "zone_travel_costs": {
                "SCIENCE": {"energy_cost_per_tick": 0.15, "money_cost_per_tick": 0.05},
                "TRADE": {"energy_cost_per_tick": 0.10, "money_cost_per_tick": 0.03},
                "DEVELOPMENT": {"energy_cost_per_tick": 0.20, "money_cost_per_tick": 0.08},
                "FLEX": {"energy_cost_per_tick": 0.05, "money_cost_per_tick": 0.02},
                "PANTHEON": {"energy_cost_per_tick": 0.05, "money_cost_per_tick": 0.00},
            },
            "anchors": {
                "HOME": {"norm": [0.5, 0.5]},
                "PANTHEON": {"norm": [0.5, 0.65]},
                "SCIENCE": {"norm": [0.25, 0.1]},
                "TRADE": {"norm": [0.75, 0.1]},
                "DEVELOPMENT": {"norm": [0.9, 0.55]},
                "FLEX": {"norm": [0.1, 0.55]},
            },
            "colors": {
                "BLACK": [0, 0, 0],
                "WHITE": [255, 255, 255],
                "GOLD": [255, 215, 0],
                "RED_TEXT": [200, 50, 50],
                "YELLOW_TEXT": [220, 200, 100],
                "LIME": [100, 255, 100],
            }
        }

# ===== WORLD CLASS =====

class World:
    """Single territory world"""
    
    def __init__(self, name: str, territory_num: int, config: Dict, num_npcs: int = 50):
        self.name = name
        self.territory_num = territory_num
        self.config = config
        self.npcs: List[NPC] = []
        self.tick = 0
        self.active_events = []
        
        self.anchors = self._build_anchors()
        
        # Create NPCs
        for i in range(num_npcs):
            npc = NPC(
                x=self.anchors["HOME"][0],
                y=self.anchors["HOME"][1],
                money=random.uniform(100, 250),
                energy=random.uniform(70, 100),
                coherence=random.uniform(0.5, 0.9),
                stress_endured=random.uniform(10, 50)
            )
            self.npcs.append(npc)
    
    def _build_anchors(self) -> Dict:
        """Build pixel anchors from config"""
        anchors = {}
        width = self.config["display"]["width"]
        height = self.config["display"]["height"]
        
        for anchor_name, anchor_cfg in self.config["anchors"].items():
            norm_x, norm_y = anchor_cfg["norm"]
            anchors[anchor_name] = (norm_x * width, norm_y * height)
        
        return anchors
    
    def step(self, tick: int):
        """Update all NPCs"""
        self.tick = tick
        
        for npc in self.npcs:
            npc.act(self.anchors, self.config, tick)
    
    def get_stats(self) -> Dict:
        """Get world statistics"""
        indoctrinated = {}
        for npc in self.npcs:
            if npc.doctrine_profile:
                doc = npc.doctrine_profile.doctrine_type
                indoctrinated[doc] = indoctrinated.get(doc, 0) + 1
        
        return {
            "total_npcs": len(self.npcs),
            "indoctrinated_total": sum(indoctrinated.values()),
            "indoctrinated_by_doctrine": indoctrinated,
            "avg_coherence": sum(n.coherence for n in self.npcs) / len(self.npcs) if self.npcs else 0,
            "avg_stress": sum(n.stress_endured for n in self.npcs) / len(self.npcs) if self.npcs else 0,
            "total_wealth": sum(n.money for n in self.npcs),
            "gurus": sum(1 for n in self.npcs if n.is_guru),
            "collapsed": sum(1 for n in self.npcs if n.is_collapsing),
        }

# ===== COLORS =====

COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'GOLD': (255, 215, 0),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 128, 255),
    'PURPLE': (128, 0, 128),
    'SILVER': (192, 192, 192),
    'CYAN': (0, 255, 255),
    'YELLOW_TEXT': (220, 200, 100),
    'GREEN_TEXT': (0, 170, 0),
    'RED_TEXT': (200, 50, 50),
}

ZONE_COLORS = {
    "PANTHEON": COLORS['GOLD'],
    "SCIENCE": (100, 200, 255),
    "TRADE": (200, 180, 100),
    "DEVELOPMENT": (100, 150, 200),
    "FLEX": (200, 100, 100),
}

# ===== MAIN GAME LOOP =====

def main():
    """Main multi-world simulation with shared zones"""
    
    config = load_config()
    
    pygame.init()
    width = config["display"]["width"]
    height = config["display"]["height"]
    fps = config["display"]["fps"]
    
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Multi-Territory Coherence System - Shared Zones")
    clock = pygame.time.Clock()
    
    fonts = {
        'header': pygame.font.Font(None, config["fonts"]["header"]),
        'large': pygame.font.Font(None, config["fonts"]["large"]),
        'small': pygame.font.Font(None, config["fonts"]["small"]),
        'tiny': pygame.font.Font(None, config["fonts"]["tiny"]),
    }
    
    # Create 3 territories
    worlds = [
        World("Territory 1", 1, config, num_npcs=50),
        World("Territory 2", 2, config, num_npcs=50),
        World("Territory 3", 3, config, num_npcs=50),
    ]

    # Shared zone tracker
    shared_zones = SharedZoneTracker()

    print("🚀 Multi-Territory Coherence System")
    print("=" * 50)
    print(f"✓ Created 3 territories with 50 NPCs each")
    print("\nControls:")
    print("  TAB: Switch territory (1/2/3)")
    print("  B: NPC Inspector (current territory)")
    print("  S: Statistics (current territory)")
    print("  C: Combined View (all territories)")
    print("  P: Shared PANTHEON (cross-territory)")
    print("  N: Shared SCIENCE (cross-territory)")
    print("  T: Shared TRADE (cross-territory)")
    print("  0-5: Filter inspector by zone")
    print("  SPACE: Pause/Resume")
    print("  ESC: Quit\n")

    # UI State
    current_world_idx = 0
    show_inspector = False
    show_statistics = False
    show_combined_view = False
    show_shared_zone_view = False
    shown_shared_zone = None
    inspector_zone_idx = None
    global_tick = 0
    paused = False
    running = True
    
    while running:
        # ===== EVENT HANDLING =====
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                # Territory switching
                if event.key == pygame.K_TAB:
                    current_world_idx = (current_world_idx + 1) % len(worlds)
                    print(f"🌍 Switched to: {worlds[current_world_idx].name}")
                
                # Inspector toggle
                elif event.key == pygame.K_b:
                    show_inspector = not show_inspector
                    show_statistics = False
                    show_combined_view = False
                    show_shared_zone_view = False
                    print(f"🔍 Inspector: {'ON' if show_inspector else 'OFF'}")
                
                # Statistics toggle
                elif event.key == pygame.K_s:
                    show_statistics = not show_statistics
                    show_inspector = False
                    show_combined_view = False
                    show_shared_zone_view = False
                    print(f"📊 Statistics: {'ON' if show_statistics else 'OFF'}")
                
                # Combined view toggle
                elif event.key == pygame.K_c:
                    show_combined_view = not show_combined_view
                    show_inspector = False
                    show_statistics = False
                    show_shared_zone_view = False
                    print(f"🌐 Combined View: {'ON' if show_combined_view else 'OFF'}")
                
                # Shared PANTHEON view
                elif event.key == pygame.K_p:
                    show_shared_zone_view = not show_shared_zone_view
                    shown_shared_zone = "PANTHEON" if show_shared_zone_view else None
                    show_inspector = False
                    show_statistics = False
                    show_combined_view = False
                    print(f"🏛️ Shared PANTHEON: {'ON' if show_shared_zone_view else 'OFF'}")
                
                # Shared SCIENCE view
                elif event.key == pygame.K_n:
                    show_shared_zone_view = not show_shared_zone_view
                    shown_shared_zone = "SCIENCE" if show_shared_zone_view else None
                    show_inspector = False
                    show_statistics = False
                    show_combined_view = False
                    print(f"🔬 Shared SCIENCE: {'ON' if show_shared_zone_view else 'OFF'}")
                
                # Shared TRADE view
                elif event.key == pygame.K_t:
                    show_shared_zone_view = not show_shared_zone_view
                    shown_shared_zone = "TRADE" if show_shared_zone_view else None
                    show_inspector = False
                    show_statistics = False
                    show_combined_view = False
                    print(f"💰 Shared TRADE: {'ON' if show_shared_zone_view else 'OFF'}")
                
                # Inspector zone filter
                elif event.key == pygame.K_0:
                    inspector_zone_idx = None
                    print("Inspector: All zones")
                elif event.key == pygame.K_1:
                    inspector_zone_idx = 0
                    print("Inspector: SCIENCE")
                elif event.key == pygame.K_2:
                    inspector_zone_idx = 1
                    print("Inspector: TRADE")
                elif event.key == pygame.K_3:
                    inspector_zone_idx = 2
                    print("Inspector: DEVELOPMENT")
                elif event.key == pygame.K_4:
                    inspector_zone_idx = 3
                    print("Inspector: FLEX")
                elif event.key == pygame.K_5:
                    inspector_zone_idx = 4
                    print("Inspector: PANTHEON")
                
                # Pause
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    print(f"⏸️  {'PAUSED' if paused else 'RESUMED'}")
                
                # Quit
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        # ===== SIMULATION STEP =====
        if not paused:
            for world in worlds:
                world.step(global_tick)
            
            global_tick += 1
            
            # Log shared zone activity
            for world in worlds:
                for npc in world.npcs:
                    if npc.zone in shared_zones.shared_zones:
                        shared_zones.npc_enters_shared_zone(npc.id, npc.zone, world.territory_num, global_tick)
            
            # Print status
            if global_tick % 500 == 0:
                print(f"\n[Tick {global_tick}]")
                for i, world in enumerate(worlds):
                    stats = world.get_stats()
                    print(f"  {world.name}: {stats['indoctrinated_total']} indoctrinated | Coherence: {stats['avg_coherence']:.2f}")
                shared_zones.print_all_shared_zones()
        
        # ===== RENDERING =====
        current_world = worlds[current_world_idx]
        
        if show_shared_zone_view and shown_shared_zone:
            draw_specific_shared_zone(screen, shared_zones, shown_shared_zone, fonts, width, height)
        
        elif show_combined_view:
            draw_shared_zones_view(screen, shared_zones, fonts, width, height)
        
        elif show_statistics:
            # Statistics view for current territory
            screen.fill(COLORS['BLACK'])
            draw_statistics_dashboard(screen, current_world, current_world.active_events, fonts, width, height)
        
        elif show_inspector:
            # Inspector view for current territory
            screen.fill(COLORS['BLACK'])
            draw_npc_inspector(screen, current_world, inspector_zone_idx, fonts, width, height)
        
        else:
            # Normal territory view
            screen.fill(COLORS['BLACK'])
            
            # Draw zone anchors
            for anchor_name, (ax, ay) in current_world.anchors.items():
                color = ZONE_COLORS.get(anchor_name, COLORS['WHITE'])
                pygame.draw.circle(screen, color, (int(ax), int(ay)), 12)
                pygame.draw.circle(screen, COLORS['WHITE'], (int(ax), int(ay)), 15, 2)
                
                # Zone label
                label = fonts['tiny'].render(anchor_name, True, COLORS['WHITE'])
                screen.blit(label, (int(ax) - label.get_width() // 2, int(ay) + 20))
            
            # Draw NPCs with doctrine visualization
            for npc in current_world.npcs:
                if npc.zone in current_world.anchors:
                    pos = current_world.anchors[npc.zone]
                elif npc.state == "TRAVELING":
                    pos = (npc.x, npc.y)
                else:
                    pos = current_world.anchors["HOME"]
                
                draw_npc_with_doctrine(screen, npc, pos, global_tick)
            
            # ===== CORNER PANELS =====
            draw_corner_stats(screen, current_world, global_tick, fonts, width, height)
            
            # Color legend (bottom-left)
            draw_color_legend(screen, 0, height - 240, 240, fonts)
            
            # Title
            title = fonts['header'].render(f"{current_world.name} - Tick {global_tick}", True, COLORS['GOLD'])
            screen.blit(title, (width // 2 - title.get_width() // 2, 20))
            
            # Pause indicator
            if paused:
                pause_text = fonts['large'].render("[PAUSED]", True, COLORS['RED'])
                screen.blit(pause_text, (width // 2 - pause_text.get_width() // 2, height // 2))
        
        pygame.display.flip()
        clock.tick(fps)
    
    pygame.quit()
    print("\n✓ Simulation ended")
    shared_zones.print_all_shared_zones()

if __name__ == "__main__":
    main()