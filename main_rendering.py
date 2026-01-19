# ===== main_rendering.py =====
"""
Main simulation loop with full rendering
Integrates NPC, Doctrine, and Rendering modules
"""

import pygame
import yaml
import random
from typing import Dict, List, Optional
from npc import NPC
from doctrines_module import (
    GuruSystem, DoctrineAnalytics, DoctrineEvents,
    DoctrineType, NPCArchetype, GuruType
)
from rendering import (
    draw_npc_inspector, draw_statistics_dashboard,
    draw_npc_with_doctrine, draw_corner_stats,
    draw_color_legend, COLORS
)

# ===== CONFIG LOADER =====

def load_config(path: str = "int5.yaml") -> Dict:
    """Load YAML configuration"""
    with open(path, "r") as f:
        return yaml.safe_load(f)

# ===== WORLD CLASS =====

class World:
    """World container with NPCs and guru system"""
    
    def __init__(self, name: str, config: Dict, num_npcs: int = 50):
        self.name = name
        self.config = config
        self.npcs: List[NPC] = []
        self.tick = 0
        self.guru_system = GuruSystem()
        self.active_events = []
        
        # Create NPCs
        home_x = config["display"]["width"] / 2
        home_y = config["display"]["height"] / 2
        
        for i in range(num_npcs):
            npc = NPC(
                x=home_x,
                y=home_y,
                money=random.uniform(100, 250),
                energy=random.uniform(70, 100),
                coherence=random.uniform(0.5, 0.9),
                stress_endured=random.uniform(10, 50)
            )
            self.npcs.append(npc)
        
        # Build anchors from config
        self.anchors = self._build_anchors()
    
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
        
        # Guru influence spread
        for guru_id in self.guru_system.gurus:
            self.guru_system.spread_influence(guru_id, self.npcs, tick)
    
    def print_status(self):
        """Print current status"""
        DoctrineAnalytics.print_report(self.npcs, self.tick)

# ===== SCENARIO BUILDERS =====

class Scenarios:
    """Pre-built simulation scenarios"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    def prosperity_world(self) -> World:
        """Baseline: stable world"""
        return World("Prosperity", self.config, num_npcs=50)
    
    def merit_indoctrination(self) -> World:
        """World prone to meritocratic capture"""
        world = World("Merit Trap", self.config, num_npcs=50)
        
        # Create wealthy gurus
        for i in range(5):
            world.npcs[i].is_guru = True
            world.npcs[i].money = 500.0
            world.guru_system.register_guru(
                world.npcs[i].id,
                DoctrineType.MERITOCRATIC,
                GuruType.PROSPERITY_PREACHER
            )
        
        return world
    
    def paranoia_crisis(self) -> World:
        """High-stress world vulnerable to conspiracy"""
        world = World("Paranoia", self.config, num_npcs=50)
        
        # Trigger stress event
        for npc in world.npcs:
            npc.stress_endured = 70.0
            npc.coherence = 0.45
            npc.has_witnessed_system_failure = True
        
        # Create conspiracy guru
        world.npcs[0].is_guru = True
        world.guru_system.register_guru(
            world.npcs[0].id,
            DoctrineType.CONSPIRATORIAL,
            GuruType.SHADOWY_INSIDER
        )
        
        return world
    
    def revolutionary_collapse(self) -> World:
        """System collapse driving radicalization"""
        world = World("Revolution", self.config, num_npcs=50)
        
        # Trigger economic crisis
        DoctrineEvents.trigger_economic_crisis(world.npcs)
        
        for npc in world.npcs:
            npc.collapse_cycle_count = 3
            npc.coherence = 0.35
        
        # Firebrand guru
        world.npcs[0].is_guru = True
        world.guru_system.register_guru(
            world.npcs[0].id,
            DoctrineType.REVOLUTIONARY,
            GuruType.FIREBRAND_REBEL
        )
        
        return world

# ===== MAIN GAME LOOP =====

def main():
    """Main simulation with rendering"""
    
    # Load config
    config = load_config()
    
    # Initialize pygame
    pygame.init()
    width = config["display"]["width"]
    height = config["display"]["height"]
    fps = config["display"]["fps"]
    
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Coherence Trust System - Doctrine Edition")
    clock = pygame.time.Clock()
    
    # Create fonts
    fonts = {
        'header': pygame.font.Font(None, config["fonts"]["header"]),
        'large': pygame.font.Font(None, config["fonts"]["large"]),
        'small': pygame.font.Font(None, config["fonts"]["small"]),
        'tiny': pygame.font.Font(None, config["fonts"]["tiny"]),
    }
    
    # Choose scenario
    print("🚀 Coherence Trust System - Doctrine Edition")
    print("=" * 50)
    print("\nScenarios:")
    print("  1. Prosperity (baseline)")
    print("  2. Merit Indoctrination")
    print("  3. Paranoia Crisis")
    print("  4. Revolutionary Collapse")
    
    choice = input("\nChoose scenario (1-4, default 1): ").strip() or "1"
    
    scenario_builder = Scenarios(config)
    scenario_map = {
        "1": scenario_builder.prosperity_world,
        "2": scenario_builder.merit_indoctrination,
        "3": scenario_builder.paranoia_crisis,
        "4": scenario_builder.revolutionary_collapse,
    }
    
    world = scenario_map.get(choice, scenario_builder.prosperity_world)()
    
    print(f"\n✓ Loaded: {world.name}")
    print(f"✓ NPCs: {len(world.npcs)}")
    print(f"✓ Gurus: {world.guru_system.get_guru_count()}")
    print("\nControls:")
    print("  B: NPC Inspector")
    print("  S: Statistics Dashboard")
    print("  TAB: Next World")
    print("  ESC: Quit\n")
    
    # UI state
    show_inspector = False
    show_statistics = False
    inspector_zone_idx = None
    global_tick = 0
    
    running = True
    paused = False
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_b:
                    show_inspector = not show_inspector
                    show_statistics = False
                    print(f"🔍 Inspector: {'ON' if show_inspector else 'OFF'}")
                elif event.key == pygame.K_s:
                    show_statistics = not show_statistics
                    show_inspector = False
                    print(f"📊 Statistics: {'ON' if show_statistics else 'OFF'}")
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_0:
                    inspector_zone_idx = None
                elif event.key == pygame.K_1:
                    inspector_zone_idx = 0
                elif event.key == pygame.K_2:
                    inspector_zone_idx = 1
                elif event.key == pygame.K_3:
                    inspector_zone_idx = 2
                elif event.key == pygame.K_4:
                    inspector_zone_idx = 3
                elif event.key == pygame.K_5:
                    inspector_zone_idx = 4
        
        # Simulation step
        if not paused:
            world.step(global_tick)
            global_tick += 1
            
            # Print status every 100 ticks
            if global_tick % 100 == 0:
                print(f"Tick {global_tick}: {DoctrineAnalytics.get_indoctrinated_count(world.npcs)} indoctrinated")
        
        # Rendering
        screen.fill(COLORS['BLACK'])
        
        # Draw anchors
        for anchor_name, (ax, ay) in world.anchors.items():
            if anchor_name in ["HOME", "PANTHEON"]:
                pygame.draw.circle(screen, COLORS['ORANGE'] if anchor_name == "HOME" else COLORS['GOLD'],
                                 (int(ax), int(ay)), 15)
            else:
                pygame.draw.circle(screen, COLORS['WHITE'], (int(ax), int(ay)), 12)
        
        # Draw NPCs
        for npc in world.npcs:
            if npc.state == "TRAVELING" and npc.target:
                pos = (npc.x, npc.y)
            elif npc.state == "AT_HOME":
                pos = world.anchors["HOME"]
            elif npc.state == "AT_WORK" and npc.zone in world.anchors:
                pos = world.anchors[npc.zone]
            else:
                pos = world.anchors["HOME"]
            
            draw_npc_with_doctrine(screen, npc, pos, global_tick)
        
        # Draw corner stats
        draw_corner_stats(screen, world, global_tick, fonts, width, height)
        draw_color_legend(screen, 0, height - 240, 240, fonts)
        
        # Draw title
        title = fonts['large'].render(f"{world.name} - Tick {global_tick}", True, COLORS['YELLOW_TEXT'])
        screen.blit(title, (width // 2 - title.get_width() // 2, 20))
        
        # Draw pause indicator
        if paused:
            pause_text = fonts['small'].render("[PAUSED - SPACE to resume]", True, COLORS['RED_TEXT'])
            screen.blit(pause_text, (width // 2 - pause_text.get_width() // 2, 70))
        
        # Draw UI overlays
        if show_inspector:
            draw_npc_inspector(screen, world, inspector_zone_idx, fonts, width, height)
        
        if show_statistics:
            draw_statistics_dashboard(screen, world, world.active_events, fonts, width, height)
        
        pygame.display.flip()
        clock.tick(fps)
    
    pygame.quit()
    print("✓ Simulation ended")

if __name__ == "__main__":
    main()