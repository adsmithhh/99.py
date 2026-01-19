# ===== rendering.py =====
"""
Rendering module: Inspector, Dashboard, and Doctrine visualization
Works with pygame and the modular system
"""

import pygame
import math
from typing import Dict, List, Optional, Tuple
from npc import NPC, DoctrineType, NPCArchetype

# ===== COLOR PALETTE =====

COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'TEAL': (26, 153, 153),
    'ORANGE': (204, 136, 68),
    'GREEN': (45, 122, 45),
    'LIME': (100, 255, 100),
    'GREEN_TEXT': (0, 170, 0),
    'RED_TEXT': (200, 50, 50),
    'YELLOW_TEXT': (220, 200, 100),
    'TRADE_COLOR': (200, 180, 100),
    'DEV_COLOR': (100, 150, 200),
    'FLEX_COLOR': (200, 100, 100),
    'GOLD': (255, 215, 0),
}

# Doctrine colors
DOCTRINE_COLORS = {
    'MERITOCRATIC': (192, 192, 192),    # Silver
    'TRANSCENDENT': (255, 215, 0),      # Gold
    'CONSPIRATORIAL': (128, 0, 128),    # Purple
    'REVOLUTIONARY': (255, 0, 0),       # Red
    'LIBERTARIAN_CULT': (0, 128, 255),  # Blue
}

# ===== NPC INSPECTOR HEADER EXPLANATIONS =====
NPC_INSPECTOR_HEADER_EXPLANATIONS = {
    "ID": "NPC unique ID",
    "Zone": "Current work zone",
    "Coh": "Coherence (stability)",
    "Trust": "Trustworthiness",
    "Phase": "Decision phase",
    "St": "Stress (0-100)",
    "$": "Money",
    "Energy": "Stamina (0-100)",
    "SE": "Self-Esteem (0-1)",
    "PV": "Pantheon Visits",
    "Diss": "Trade Dissonance",
    "Arch": "Archetype"
}

# ===== NPC INSPECTOR (FROM 1.py) =====

def draw_npc_inspector(surface, world, inspector_zone_idx, fonts, width, height):
    """
    Enhanced NPC inspector with coherence & trust
    Full implementation from 1.py adapted for modular system
    """
    panel_w, panel_h = 1200, 900  # Larger for better readability
    panel_x = width // 2 - panel_w // 2
    panel_y = height // 2 - panel_h // 2
    
    panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel_surf.fill((30, 30, 30, 220))
    
    # Title
    title = fonts['header'].render("🔍 NPC INSPECTOR [TRUST SYSTEM]", True, COLORS['YELLOW_TEXT'])
    panel_surf.blit(title, (panel_w//2 - title.get_width()//2, 15))
    
    # Headers
    headers = ["ID", "Zone", "Coh", "Trust", "Phase", "St", "Diss", "$", "Energy", "SE", "PV", "Arch"]
    header_line = "{:<8} {:<15} {:<8} {:<8} {:<18} {:<8} {:<8} {:<10} {:<10} {:<8} {:<6} {:<10}".format(*headers)
    header_text = fonts['small'].render(header_line, True, COLORS['RED_TEXT'])
    panel_surf.blit(header_text, (20, 50))
    
    # Filter NPCs by zone if specified
    npcs = world.npcs
    
    # Zone filtering (compatible with both systems)
    if inspector_zone_idx is not None and 0 <= inspector_zone_idx < 5:
        zone_names = ["SCIENCE", "TRADE", "DEVELOPMENT", "FLEX", "PANTHEON"]
        zone_filter = zone_names[inspector_zone_idx]
        npcs = [n for n in npcs if n.zone == zone_filter]
    
    # Render NPC rows
    max_lines = 12
    for i, npc in enumerate(npcs[:max_lines]):
        # Phase (last decision)
        phase = npc.decision_history[-1].phase if npc.decision_history else "---"
        
        # Archetype (handle both enum and string)
        archetype = "UNK"
        if hasattr(npc, 'archetype'):
            arch = npc.archetype
            archetype = (arch.value if hasattr(arch, 'value') else str(arch))[:6]
        
        # Trade dissonance (may not exist in all NPC versions)
        trade_diss = getattr(npc, 'trade_dissonance', 0.0)
        
        # Pantheon visits
        pantheon_visits = getattr(npc, 'pantheon_visit_count', 0)

        # Format data line
        data_line = "{:<8} {:<15} {:<8.2f} {:<8.2f} {:<18} {:<8.0f} {:<8.2f} {:<10.1f} {:<10.0f} {:<8.2f} {:<6} {:<10}".format(
            npc.id,
            npc.zone[:12] if npc.zone else "---",
            npc.coherence,
            npc.trustworthiness,
            phase[:15],
            npc.stress_endured,
            trade_diss,
            npc.money,
            npc.energy,
            npc.self_esteem,
            pantheon_visits,
            archetype
        )

        # Color coding by status
        color = COLORS['WHITE']
        
        if npc.is_collapsing:
            color = COLORS['RED_TEXT']
        elif hasattr(npc, 'is_guru') and npc.is_guru:
            color = (255, 215, 0)  # Gold for Gurus
        elif pantheon_visits >= 5:
            color = COLORS['YELLOW_TEXT']  # Yellow for indoctrinated
        elif hasattr(npc, 'doctrine_profile') and npc.doctrine_profile:
            doc_type = npc.doctrine_profile.doctrine_type.value if hasattr(npc.doctrine_profile.doctrine_type, 'value') else str(npc.doctrine_profile.doctrine_type)
            color = DOCTRINE_COLORS.get(doc_type, COLORS['YELLOW_TEXT'])

        line_surf = fonts['small'].render(data_line, True, color)
        panel_surf.blit(line_surf, (20, 80 + i * 30))
    
    # Instructions
    instructions = "B: Toggle | 0: All | 1-5: Filter Zone | S: Stats | ESC: Quit"
    instr_surf = fonts['tiny'].render(instructions, True, COLORS['YELLOW_TEXT'])
    panel_surf.blit(instr_surf, (panel_w // 2 - instr_surf.get_width() // 2, panel_h - 40))

    # Header explanations at bottom (2X BIGGER as requested)
    lines_rendered = min(len(npcs), max_lines)
    explanation_y = 80 + lines_rendered * 30 + 30
    
    for key, explanation in list(NPC_INSPECTOR_HEADER_EXPLANATIONS.items())[:8]:
        if explanation_y > panel_h - 100:
            break
        header_render = fonts['small'].render(f"{key}:", True, COLORS['RED_TEXT'])
        expl_render = fonts['small'].render(f" {explanation}", True, COLORS['GREEN_TEXT'])
        panel_surf.blit(header_render, (20, explanation_y))
        panel_surf.blit(expl_render, (20 + header_render.get_width(), explanation_y))
        explanation_y += 30  # Larger spacing
    
    # Final blit
    surface.blit(panel_surf, (panel_x, panel_y))
# ===== STATISTICS DASHBOARD =====

def draw_statistics_dashboard(surface, world, active_events, fonts, width, height):
    """
    Comprehensive world analytics with doctrine tracking
    Shows population, coherence, doctrine spread, pantheon status
    """
    panel_w, panel_h = 1100, 950
    panel_x = width // 2 - panel_w // 2
    panel_y = height // 2 - panel_h // 2
    
    panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel_surf.fill((20, 20, 40, 230))
    
    # Title
    title = fonts['header'].render("📊 WORLD ANALYTICS [DOCTRINE TRACKER]", True, COLORS['LIME'])
    panel_surf.blit(title, (panel_w//2 - title.get_width()//2, 15))
    
    y_offset = 70
    
    # === WORLD OVERVIEW ===
    section_title = fonts['large'].render("🌍 World Overview", True, COLORS['YELLOW_TEXT'])
    panel_surf.blit(section_title, (20, y_offset))
    y_offset += 40
    
    total_money = sum(npc.money for npc in world.npcs)
    avg_coherence = sum(npc.coherence for npc in world.npcs) / len(world.npcs) if world.npcs else 0
    avg_trust = sum(npc.trustworthiness for npc in world.npcs) / len(world.npcs) if world.npcs else 0
    avg_stress = sum(npc.stress_endured for npc in world.npcs) / len(world.npcs) if world.npcs else 0
    collapsed = sum(1 for npc in world.npcs if npc.is_collapsing)
    
    overview_stats = [
        f"Total NPCs: {len(world.npcs)}",
        f"Total Wealth: ${total_money:.1f}",
        f"Avg Coherence: {avg_coherence:.2f}",
        f"Avg Trust: {avg_trust:.2f}",
        f"Avg Stress: {avg_stress:.1f}",
        f"Collapsed NPCs: {collapsed}",
    ]
    
    for stat in overview_stats:
        text = fonts['small'].render(stat, True, COLORS['WHITE'])
        panel_surf.blit(text, (40, y_offset))
        y_offset += 28
    
    y_offset += 15
    
    # === DOCTRINE STATUS ===
    section_title = fonts['large'].render("🔮 DOCTRINE SPREAD", True, COLORS['GOLD'])
    panel_surf.blit(section_title, (20, y_offset))
    y_offset += 40
    
    # Count indoctrinated by doctrine
    doctrine_counts = {}
    for npc in world.npcs:
        if npc.doctrine_profile:
            doc_type = npc.doctrine_profile.doctrine_type.value
            doctrine_counts[doc_type] = doctrine_counts.get(doc_type, 0) + 1
    
    if doctrine_counts:
        for doctrine, count in sorted(doctrine_counts.items()):
            color = DOCTRINE_COLORS.get(doctrine, COLORS['WHITE'])
            text = fonts['small'].render(f"  {doctrine}: {count} NPCs", True, color)
            panel_surf.blit(text, (40, y_offset))
            y_offset += 26
    else:
        text = fonts['small'].render("  No active doctrines", True, COLORS['GREEN_TEXT'])
        panel_surf.blit(text, (40, y_offset))
        y_offset += 26
    
    y_offset += 10
    
    # === PANTHEON STATUS ===
    section_title = fonts['large'].render("🏛️ PANTHEON STATUS", True, COLORS['GOLD'])
    panel_surf.blit(section_title, (20, y_offset))
    y_offset += 40
    
    gurus = sum(1 for npc in world.npcs if npc.is_guru)
    indoctrinated = sum(1 for npc in world.npcs if npc.doctrine_profile)
    pantheon_active = sum(1 for npc in world.npcs if npc.zone == "PANTHEON")
    pantheon_visits_total = sum(npc.pantheon_visit_count for npc in world.npcs)
    
    pantheon_stats = [
        f"Permanent Gurus: {gurus}",
        f"Indoctrinated NPCs: {indoctrinated}",
        f"Currently at Pantheon: {pantheon_active}",
        f"Total Pantheon Visits: {pantheon_visits_total}",
    ]
    
    for stat in pantheon_stats:
        text = fonts['small'].render(stat, True, COLORS['GOLD'])
        panel_surf.blit(text, (40, y_offset))
        y_offset += 28
    
    y_offset += 15
    
    # === ARCHETYPE DISTRIBUTION ===
    section_title = fonts['large'].render("👥 ARCHETYPES", True, COLORS['YELLOW_TEXT'])
    panel_surf.blit(section_title, (20, y_offset))
    y_offset += 40
    
    archetype_counts = {}
    for npc in world.npcs:
        if hasattr(npc, 'archetype'):
            arch = npc.archetype
            arch_str = arch.value if hasattr(arch, 'value') else str(arch)
            archetype_counts[arch_str] = archetype_counts.get(arch_str, 0) + 1
    
    for arch, count in sorted(archetype_counts.items()):
        text = fonts['small'].render(f"  {arch}: {count}", True, COLORS['WHITE'])
        panel_surf.blit(text, (40, y_offset))
        y_offset += 26
    
    y_offset += 15
    
    # === ACTIVE EVENTS ===
    if active_events:
        section_title = fonts['large'].render("⚡ ACTIVE EVENTS", True, COLORS['YELLOW_TEXT'])
        panel_surf.blit(section_title, (20, y_offset))
        y_offset += 35
        
        for event in active_events[:5]:
            event_color = COLORS['GREEN_TEXT'] if hasattr(event, 'effect_type') and event.effect_type == "bonus" else COLORS['RED_TEXT']
            event_text = f"  {event.name}: {event.remaining_ticks}t left" if hasattr(event, 'remaining_ticks') else f"  {event.name}"
            text = fonts['tiny'].render(event_text, True, event_color)
            panel_surf.blit(text, (40, y_offset))
            y_offset += 22
    
    # Instructions
    controls = fonts['tiny'].render("S: Toggle Stats | B: Inspector | ESC: Quit", True, COLORS['YELLOW_TEXT'])
    panel_surf.blit(controls, (panel_w // 2 - controls.get_width() // 2, panel_h - 30))
    
    surface.blit(panel_surf, (panel_x, panel_y))

# ===== NPC RENDERING WITH DOCTRINE RINGS =====

def draw_npc_with_doctrine(surface, npc, position: Tuple[int, int], global_tick: int):
    """
    Draw NPC with doctrine visualization
    - Inner circle: base NPC color
    - Trust ring: trustworthiness indicator
    - Doctrine ring: indoctrination strength
    - Guru aura: pulsing ring if guru
    """
    x, y = int(position[0]), int(position[1])
    
    # Determine base color
    if npc.state == "AT_HOME":
        color = COLORS['ORANGE'] if npc.cycle_phase != "EXTRACTING" else COLORS['LIME']
    elif npc.state == "TRAVELING":
        color = COLORS['RED_TEXT'] if npc.cycle_phase == "COMMUTING" else (255, 100, 255)
    elif npc.state == "AT_WORK":
        zone_colors = {
            "SCIENCE": (100, 200, 255),
            "TRADE": COLORS['TRADE_COLOR'],
            "DEVELOPMENT": COLORS['DEV_COLOR'],
            "FLEX": COLORS['FLEX_COLOR'],
            "PANTHEON": COLORS['GOLD'],
        }
        color = zone_colors.get(npc.zone, COLORS['GREEN'])
    else:
        color = COLORS['WHITE']
    
    # Draw collapse indicator (red pulsing ring)
    if npc.is_collapsing:
        pulse = int(128 + 127 * math.sin(global_tick * 0.1))
        pygame.draw.circle(surface, (pulse, 0, 0), (x, y), 14, 3)
    
    # Draw doctrine ring
    if npc.doctrine_profile:
        doc_color = DOCTRINE_COLORS.get(npc.doctrine_profile.doctrine_type.value, COLORS['WHITE'])
        doc_radius = int(14 + (6 * npc.doctrine_profile.strength))
        pygame.draw.circle(surface, doc_color, (x, y), doc_radius, 2)
    
    # Draw guru aura (pulsing)
    if npc.is_guru:
        pulse = int(20 + 10 * math.sin(global_tick * 0.05))
        pygame.draw.circle(surface, COLORS['GOLD'], (x, y), 18 + pulse, 4)
        pygame.draw.circle(surface, COLORS['WHITE'], (x, y), 20, 2)
    
    # Main NPC circle
    pygame.draw.circle(surface, color, (x, y), 8)
    
    # Trust ring (green/yellow/red)
    if npc.trustworthiness > 0.7:
        trust_color = COLORS['GREEN']
    elif npc.trustworthiness > 0.4:
        trust_color = (255, 255, 0)
    else:
        trust_color = (255, 100, 100)
    
    pygame.draw.circle(surface, trust_color, (x, y), 11, 1)

# ===== CORNER PANELS =====

def draw_corner_stats(surface, world, global_tick, fonts, width, height):
    """Draw mini stat panels in corners"""
    corner_size = 240
    
    # Sample NPC for tick info
    sample_npc = world.npcs[0] if world.npcs else None
    
    total_wealth = sum(npc.money for npc in world.npcs)
    avg_coherence = sum(npc.coherence for npc in world.npcs) / len(world.npcs) if world.npcs else 0
    active_npcs = sum(1 for n in world.npcs if n.state != "AT_HOME")
    collapsed_npcs = sum(1 for n in world.npcs if n.is_collapsing)
    
    corners = [
        (0, 0, f"Tick: {global_tick}\nActive: {active_npcs}\nWealth: ${total_wealth:.0f}"),
        (width - corner_size, 0, f"NPCs: {len(world.npcs)}\nAvg Coh: {avg_coherence:.2f}\nCollapsed: {collapsed_npcs}"),
    ]
    
    for x, y, text in corners:
        pygame.draw.rect(surface, (30, 30, 30, 180), (x, y, corner_size, corner_size), border_radius=18)
        lines = text.split('\n')
        for i, line in enumerate(lines):
            text_surf = fonts['small'].render(line, True, COLORS['GREEN_TEXT'])
            surface.blit(text_surf, (x + 16, y + 16 + i * 28))

# ===== LEGEND =====

def draw_color_legend(surface, x: int, y: int, corner_size: int, fonts):
    """Draw NPC color legend in corner"""
    pygame.draw.rect(surface, (30, 30, 30, 180), (x, y, corner_size, corner_size), border_radius=18)
    
    title = fonts['small'].render("NPC Colors", True, COLORS['YELLOW_TEXT'])
    surface.blit(title, (x + 16, y + 16))
    
    legend_entries = [
        ("Guru", COLORS['GOLD']),
        ("Collapse", COLORS['RED_TEXT']),
        ("Doctrine", (128, 0, 128)),
        ("High Trust", COLORS['GREEN']),
        ("Low Trust", (255, 100, 100)),
    ]
    
    y_offset = y + 50
    for label, color in legend_entries:
        pygame.draw.circle(surface, color, (x + 20, y_offset + 8), 6)
        text = fonts['tiny'].render(label, True, COLORS['WHITE'])
        surface.blit(text, (x + 35, y_offset))
        y_offset += 24