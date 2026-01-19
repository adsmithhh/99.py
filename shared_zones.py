# ===== shared_zones_rendering.py ===== (ENHANCED)
"""
Rendering functions for multi-territory shared zones
Used by 99.py (multi-world simulation)
"""

import pygame
import math
from typing import Dict, List

ZONE_COLORS = {
    "PANTHEON": (255, 215, 0),      # Gold
    "SCIENCE": (100, 200, 255),     # Blue
    "TRADE": (200, 180, 100),       # Yellow-brown
    "DEVELOPMENT": (100, 150, 200), # Light blue
    "FLEX": (200, 100, 100),        # Red
}

TERRITORY_COLORS = {
    1: (0, 255, 128),    # Green (Territory 1)
    2: (255, 128, 0),    # Orange (Territory 2)
    3: (128, 0, 255),    # Purple (Territory 3)
}

COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'CYAN': (0, 255, 255),
    'YELLOW_TEXT': (220, 200, 100),
    'GOLD': (255, 215, 0),
    'LIME': (100, 255, 100),
    'RED_TEXT': (200, 50, 50),
}

# ===== SHARED ZONES TRACKER =====

class SharedZoneTracker:
    """
    Tracks NPCs at shared zones across all 3 territories
    """
    
    def __init__(self):
        # Shared zone occupants: zone_name -> {zone_1: set, zone_2: set, zone_3: set}
        self.shared_zones = {
            "PANTHEON": {"zone_1": set(), "zone_2": set(), "zone_3": set()},
            "SCIENCE": {"zone_1": set(), "zone_2": set(), "zone_3": set()},
            "TRADE": {"zone_1": set(), "zone_2": set(), "zone_3": set()},
            "DEVELOPMENT": {"zone_1": set(), "zone_2": set(), "zone_3": set()},
            "FLEX": {"zone_1": set(), "zone_2": set(), "zone_3": set()},
        }
        self.events = []
        
        # Visual layout for shared zones (normalized 0-1)
        self.zone_positions = {
            "PANTHEON": (0.5, 0.25),
            "SCIENCE": (0.25, 0.5),
            "TRADE": (0.75, 0.5),
            "DEVELOPMENT": (0.35, 0.75),
            "FLEX": (0.65, 0.75),
        }
    
    def npc_enters_shared_zone(self, npc_id: int, zone_name: str, origin_territory: int, tick: int):
        """Log NPC entering shared zone"""
        territory_key = f"zone_{origin_territory}"
        if zone_name in self.shared_zones and territory_key in self.shared_zones[zone_name]:
            self.shared_zones[zone_name][territory_key].add(npc_id)
            self.events.append({
                "tick": tick,
                "npc_id": npc_id,
                "zone": zone_name,
                "territory": origin_territory,
                "event": "ENTER",
            })
    
    def npc_leaves_shared_zone(self, npc_id: int, zone_name: str, tick: int):
        """Log NPC leaving shared zone"""
        for territory_key in ["zone_1", "zone_2", "zone_3"]:
            self.shared_zones[zone_name][territory_key].discard(npc_id)
        self.events.append({
            "tick": tick,
            "npc_id": npc_id,
            "zone": zone_name,
            "event": "LEAVE",
        })
    
    def get_shared_zone_stats(self, zone_name: str) -> Dict:
        """Get statistics for a shared zone"""
        if zone_name not in self.shared_zones:
            return {}
        
        z1_count = len(self.shared_zones[zone_name]["zone_1"])
        z2_count = len(self.shared_zones[zone_name]["zone_2"])
        z3_count = len(self.shared_zones[zone_name]["zone_3"])
        
        return {
            "zone_name": zone_name,
            "zone_1_occupants": z1_count,
            "zone_2_occupants": z2_count,
            "zone_3_occupants": z3_count,
            "total_occupants": z1_count + z2_count + z3_count,
        }
    
    def print_all_shared_zones(self):
        """Print status of all shared zones"""
        print("\n" + "="*60)
        print("🌐 SHARED ZONES ACROSS ALL TERRITORIES")
        print("="*60)
        for zone_name in self.shared_zones:
            stats = self.get_shared_zone_stats(zone_name)
            print(f"\n{zone_name}:")
            print(f"  Zone 1: {stats['zone_1_occupants']} | Zone 2: {stats['zone_2_occupants']} | Zone 3: {stats['zone_3_occupants']}")
            print(f"  Total cross-territory NPCs: {stats['total_occupants']}")

# ===== VISUAL RENDERING FUNCTIONS =====

def draw_shared_zones_view(surface, shared_zones, fonts, width, height):
    """Draw VISUAL spatial view of all shared zones with NPCs"""
    surface.fill(COLORS['BLACK'])
    
    # Title
    title = fonts['header'].render("🌐 SHARED ZONES - CROSS-TERRITORY VIEW", True, COLORS['CYAN'])
    surface.blit(title, (width // 2 - title.get_width() // 2, 20))
    
    # Territory legend (top-right)
    legend_x = width - 250
    legend_y = 20
    pygame.draw.rect(surface, (30, 30, 30, 180), (legend_x, legend_y, 230, 140), border_radius=10)
    
    legend_title = fonts['small'].render("Territories:", True, COLORS['WHITE'])
    surface.blit(legend_title, (legend_x + 10, legend_y + 10))
    
    for i, (terr_num, color) in enumerate(TERRITORY_COLORS.items()):
        y = legend_y + 40 + i * 30
        pygame.draw.circle(surface, color, (legend_x + 30, y), 8)
        pygame.draw.circle(surface, COLORS['WHITE'], (legend_x + 30, y), 10, 1)
        text = fonts['tiny'].render(f"Territory {terr_num}", True, COLORS['WHITE'])
        surface.blit(text, (legend_x + 50, y - 10))
    
    # Draw each shared zone as spatial area
    for zone_name, (norm_x, norm_y) in shared_zones.zone_positions.items():
        zone_x = int(norm_x * width)
        zone_y = int(norm_y * height) + 80  # Offset for title
        zone_color = ZONE_COLORS.get(zone_name, COLORS['WHITE'])
        stats = shared_zones.get_shared_zone_stats(zone_name)
        
        # Zone base circle (large)
        zone_radius = 80
        pygame.draw.circle(surface, zone_color, (zone_x, zone_y), zone_radius, 4)
        pygame.draw.circle(surface, (*zone_color, 30), (zone_x, zone_y), zone_radius - 5)
        
        # Zone name
        zone_label = fonts['large'].render(zone_name, True, zone_color)
        surface.blit(zone_label, (zone_x - zone_label.get_width() // 2, zone_y - zone_radius - 30))
        
        # Draw NPCs from each territory as colored dots
        territory_data = [
            (1, stats['zone_1_occupants'], 0),
            (2, stats['zone_2_occupants'], 120),
            (3, stats['zone_3_occupants'], 240),
        ]
        
        for territory_num, count, angle_offset in territory_data:
            if count > 0:
                color = TERRITORY_COLORS[territory_num]
                
                # Arrange NPCs in arc around zone
                for i in range(min(count, 15)):  # Cap visual display at 15
                    angle = math.radians(angle_offset + (i * 10))
                    offset_dist = 35 + (i % 3) * 15
                    npc_x = zone_x + int(math.cos(angle) * offset_dist)
                    npc_y = zone_y + int(math.sin(angle) * offset_dist)
                    
                    # NPC dot
                    pygame.draw.circle(surface, color, (npc_x, npc_y), 5)
                    pygame.draw.circle(surface, COLORS['WHITE'], (npc_x, npc_y), 6, 1)
                
                # Count badge
                if count > 15:
                    badge_text = fonts['tiny'].render(f"+{count - 15}", True, color)
                    angle = math.radians(angle_offset + 60)
                    badge_x = zone_x + int(math.cos(angle) * 55)
                    badge_y = zone_y + int(math.sin(angle) * 55)
                    surface.blit(badge_text, (badge_x, badge_y))
        
        # Total occupants badge (center)
        total = stats['total_occupants']
        if total > 0:
            total_text = fonts['small'].render(str(total), True, COLORS['GOLD'])
            surface.blit(total_text, (zone_x - total_text.get_width() // 2, zone_y - 10))
    
    # Statistics panel (bottom)
    panel_y = height - 150
    pygame.draw.rect(surface, (20, 20, 40, 200), (0, panel_y, width, 150))
    
    stats_title = fonts['large'].render("CROSS-TERRITORY TRAFFIC", True, COLORS['LIME'])
    surface.blit(stats_title, (20, panel_y + 10))
    
    # Summary stats
    y_offset = panel_y + 50
    for i, zone_name in enumerate(["PANTHEON", "SCIENCE", "TRADE", "DEVELOPMENT", "FLEX"]):
        stats = shared_zones.get_shared_zone_stats(zone_name)
        total = stats['total_occupants']
        color = ZONE_COLORS[zone_name]
        
        text = fonts['small'].render(
            f"{zone_name}: {stats['zone_1_occupants']}/{stats['zone_2_occupants']}/{stats['zone_3_occupants']} = {total}",
            True, color
        )
        x_pos = 20 + (i % 3) * 400
        y_pos = y_offset + (i // 3) * 30
        surface.blit(text, (x_pos, y_pos))
    
    # Controls hint
    controls = fonts['tiny'].render("C: Exit Combined View | P/N/T: Specific Zones", True, COLORS['YELLOW_TEXT'])
    surface.blit(controls, (width - controls.get_width() - 20, height - 20))

def draw_specific_shared_zone(surface, shared_zones, zone_name: str, fonts, width, height):
    """Draw detailed VISUAL view of specific shared zone"""
    surface.fill(COLORS['BLACK'])
    
    stats = shared_zones.get_shared_zone_stats(zone_name)
    zone_color = ZONE_COLORS.get(zone_name, COLORS['WHITE'])
    
    # Title
    title = fonts['header'].render(f"🏛️ SHARED {zone_name}", True, zone_color)
    surface.blit(title, (width // 2 - title.get_width() // 2, 30))
    
    # Central zone visualization
    center_x = width // 2
    center_y = height // 2
    zone_radius = 150
    
    # Zone base
    pygame.draw.circle(surface, zone_color, (center_x, center_y), zone_radius, 6)
    pygame.draw.circle(surface, (*zone_color, 40), (center_x, center_y), zone_radius - 10)
    
    # Territory sections (3 arcs)
    territory_sections = [
        (1, 0, 120, "T1"),
        (2, 120, 240, "T2"),
        (3, 240, 360, "T3"),
    ]
    
    for territory_num, start_angle, end_angle, label in territory_sections:
        color = TERRITORY_COLORS[territory_num]
        count = stats[f'zone_{territory_num}_occupants']
        
        # Draw arc separator
        angle_rad = math.radians(start_angle)
        line_end_x = center_x + int(math.cos(angle_rad) * zone_radius)
        line_end_y = center_y + int(math.sin(angle_rad) * zone_radius)
        pygame.draw.line(surface, COLORS['WHITE'], (center_x, center_y), (line_end_x, line_end_y), 2)
        
        # Draw NPCs in sector
        if count > 0:
            angle_range = end_angle - start_angle
            for i in range(min(count, 20)):
                angle = math.radians(start_angle + (i + 1) * (angle_range / (min(count, 20) + 1)))
                dist = 50 + (i % 4) * 25
                npc_x = center_x + int(math.cos(angle) * dist)
                npc_y = center_y + int(math.sin(angle) * dist)
                
                pygame.draw.circle(surface, color, (npc_x, npc_y), 6)
                pygame.draw.circle(surface, COLORS['WHITE'], (npc_x, npc_y), 8, 1)
        
        # Territory label
        label_angle = math.radians((start_angle + end_angle) / 2)
        label_x = center_x + int(math.cos(label_angle) * (zone_radius + 40))
        label_y = center_y + int(math.sin(label_angle) * (zone_radius + 40))
        
        label_surf = fonts['large'].render(f"{label}: {count}", True, color)
        surface.blit(label_surf, (label_x - label_surf.get_width() // 2, label_y - label_surf.get_height() // 2))
    
    # Total count (center)
    total_text = fonts['header'].render(str(stats['total_occupants']), True, COLORS['GOLD'])
    surface.blit(total_text, (center_x - total_text.get_width() // 2, center_y - total_text.get_height() // 2))
    
    # Statistics panel (left side)
    panel_x = 20
    panel_y = 150
    panel_w = 350
    panel_h = 400
    
    pygame.draw.rect(surface, (30, 30, 50, 220), (panel_x, panel_y, panel_w, panel_h), border_radius=10)
    
    stats_title = fonts['large'].render("STATISTICS", True, COLORS['LIME'])
    surface.blit(stats_title, (panel_x + 20, panel_y + 20))
    
    y_offset = panel_y + 70
    stat_lines = [
        f"Territory 1: {stats['zone_1_occupants']} NPCs",
        f"Territory 2: {stats['zone_2_occupants']} NPCs",
        f"Territory 3: {stats['zone_3_occupants']} NPCs",
        "",
        f"Total: {stats['total_occupants']} NPCs",
        "",
        "Cross-Territory Mixing:",
        f"  Diversity Index: {calculate_diversity(stats):.2f}",
    ]
    
    for i, line in enumerate(stat_lines):
        if line.startswith("Territory"):
            terr_num = int(line[10])
            color = TERRITORY_COLORS[terr_num]
        elif "Total" in line:
            color = COLORS['GOLD']
        else:
            color = COLORS['WHITE']
        
        text = fonts['small'].render(line, True, color)
        surface.blit(text, (panel_x + 20, y_offset + i * 30))
    
    # Recent activity (right side)
    activity_x = width - 370
    activity_y = 150
    
    pygame.draw.rect(surface, (30, 30, 50, 220), (activity_x, activity_y, 350, 400), border_radius=10)
    
    activity_title = fonts['large'].render("RECENT ACTIVITY", True, COLORS['YELLOW_TEXT'])
    surface.blit(activity_title, (activity_x + 20, activity_y + 20))
    
    # Filter events for this zone
    recent_events = [e for e in shared_zones.events if e["zone"] == zone_name][-10:]
    
    y_offset = activity_y + 70
    for i, event in enumerate(recent_events):
        event_color = TERRITORY_COLORS[event["territory"]]
        symbol = "→" if event["event"] == "ENTER" else "←"
        
        event_text = f"T{event['territory']} NPC#{event['npc_id']:03d} {symbol}"
        text = fonts['small'].render(event_text, True, event_color)
        surface.blit(text, (activity_x + 20, y_offset + i * 30))
        
        tick_text = fonts['tiny'].render(f"Tick {event['tick']}", True, COLORS['WHITE'])
        surface.blit(tick_text, (activity_x + 250, y_offset + i * 30 + 5))
    
    # Controls
    controls = fonts['tiny'].render(
        "P: Pantheon | N: Science | T: Trade | C: Combined View | ESC: Exit",
        True, COLORS['WHITE']
    )
    surface.blit(controls, (width // 2 - controls.get_width() // 2, height - 20))

def calculate_diversity(stats: Dict) -> float:
    """Calculate diversity index (0 = single territory, 1 = perfectly balanced)"""
    total = stats['total_occupants']
    if total == 0:
        return 0.0
    
    counts = [stats['zone_1_occupants'], stats['zone_2_occupants'], stats['zone_3_occupants']]
    proportions = [c / total for c in counts if c > 0]
    
    if len(proportions) <= 1:
        return 0.0
    
    # Shannon entropy normalized
    entropy = -sum(p * math.log(p, 3) for p in proportions if p > 0)
    return entropy