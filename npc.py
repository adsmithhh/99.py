# ===== npc.py =====
"""
Complete NPC class with doctrine support
Includes: state machine, work logic, trust system, AND doctrine mechanics
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
from collections import defaultdict, deque
import itertools
import random
import math

# ===== DOCTRINE TYPES (minimal, don't import to avoid circular deps) =====

class DoctrineType:
    MERITOCRATIC = "MERITOCRATIC"
    TRANSCENDENT = "TRANSCENDENT"
    CONSPIRATORIAL = "CONSPIRATORIAL"
    REVOLUTIONARY = "REVOLUTIONARY"
    LIBERTARIAN_CULT = "LIBERTARIAN_CULT"

class NPCArchetype:
    PRAGMATIST = "PRAGMATIST"
    IDEALIST = "IDEALIST"
    ANXIOUS = "ANXIOUS"
    OUTSIDER = "OUTSIDER"
    HEDONIST = "HEDONIST"

# ===== DATA STRUCTURES =====

@dataclass
class Commitment:
    """Work contract tracker"""
    key: str
    created_tick: int
    due_tick: int
    strength: float = 0.5
    honored: bool = False
    broken: bool = False

@dataclass
class DecisionRecord:
    """Decision history tracker"""
    tick: int
    choice: str
    phase: str

@dataclass
class DoctrineProfile:
    """NPC's current indoctrination state"""
    doctrine_type: str  # Use string to avoid import
    strength: float = 0.0
    time_indoctrinated: int = 0
    guru_id: Optional[int] = None
    
    def update(self):
        self.time_indoctrinated += 1
        self.strength = min(1.0, self.strength + 0.02)

# ===== MAIN NPC CLASS =====

@dataclass
class NPC:
    """
    Complete NPC with state machine, work, trust, AND doctrine mechanics
    All in one class - no inheritance needed
    """
    
    # ===== POSITION & STATE =====
    x: float
    y: float
    zone: str = ""
    state: str = "AT_HOME"
    target: Optional[str] = None
    speed: float = 4.0
    
    # ===== IDENTITY =====
    id: int = field(default_factory=lambda: next(itertools.count(1)))
    
    # ===== RESOURCES =====
    money: float = 190.0
    energy: float = 100.0
    coherence: float = 0.7
    self_esteem: float = 0.7
    stress_endured: float = 0.0
    
    # ===== WORK & SKILLS =====
    skills: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    commitments: Dict[str, Commitment] = field(default_factory=dict)
    trust_log: deque = field(default_factory=lambda: deque(maxlen=300))
    decision_history: deque = field(default_factory=lambda: deque(maxlen=80))
    
    # ===== PANTHEON (old system) =====
    pantheon_visit_count: int = 0
    pantheon_doctrine_bias: float = 0.0
    pantheon_doctrine_type: Optional[str] = None
    is_guru: bool = False
    
    # ===== WORK CYCLES =====
    travel_budget: int = 0
    work_budget: int = 0
    shift_offset: int = 0
    cycle_phase: str = "RESTING"
    is_collapsing: bool = False
    trustworthiness: float = 0.5
    trade_dissonance: float = 0.0
    
    # ===== DOCTRINE SYSTEM (NEW) =====
    archetype: str = ""
    doctrine_profile: Optional[DoctrineProfile] = None
    doctrine_history: deque = field(default_factory=lambda: deque(maxlen=50))
    deradicalization_timer: int = 0
    injustice_accumulated: float = 0.0
    collapse_cycle_count: int = 0
    has_witnessed_system_failure: bool = False
    
    def __post_init__(self):
        """Initialize after dataclass creation"""
        # Assign random archetype
        archetypes = [
            NPCArchetype.PRAGMATIST,
            NPCArchetype.IDEALIST,
            NPCArchetype.ANXIOUS,
            NPCArchetype.OUTSIDER,
            NPCArchetype.HEDONIST,
        ]
        self.archetype = "PRAGMATIST"  # String, not NPCArchetype.PRAGMATIST
        self.archetype = NPCArchetype.PRAGMATIST  # Enum with .value
    # ===== TRUST SYSTEM =====
    
    def compute_trustworthiness(self) -> float:
        """Trust from commitment history and resilience"""
        honors = sum(1 for e in self.trust_log if len(e) > 0 and e[0] == "HONOR")
        breaks = sum(1 for e in self.trust_log if len(e) > 0 and e[0] == "BREAK")
        contract_score = (honors + 1) / (honors + breaks + 2)
        
        stress = min(1.0, self.stress_endured / 100.0)
        resilience = max(0.0, 1.0 - stress)
        
        tw = (0.6 * contract_score + 0.4 * resilience) * (self.coherence ** 2)
        self.trustworthiness = max(0.0, min(1.0, tw))
        return self.trustworthiness
    
    # ===== MOVEMENT =====
    
    def move_toward_target(self, anchors: Dict, config: Dict) -> bool:
        """Animate toward target anchor"""
        if not self.target or self.target not in anchors:
            return False
        
        target_x, target_y = anchors[self.target]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)
        
        if distance < 3:
            self.x, self.y = target_x, target_y
            return True
        
        move_x = (dx / distance) * self.speed
        move_y = (dy / distance) * self.speed
        self.x += move_x
        self.y += move_y
        
        # Travel costs
        if self.target in config.get("zone_travel_costs", {}):
            costs = config["zone_travel_costs"][self.target]
            self.energy -= costs.get("energy_cost_per_tick", 0.1)
            self.money -= costs.get("money_cost_per_tick", 0.02)
        
        return False
    
    # ===== WORK EXECUTION =====
    
    def perform_work(self, config: Dict):
        """Execute work in current zone"""
        if self.state != "AT_WORK" or not self.zone:
            return
        
        load = (self.stress_endured / 100.0) + (1.0 - (self.energy / 100.0))
        efficiency = max(0.1, min(1.0, self.self_esteem - (load * 0.3)))
        
        if self.zone == "SCIENCE":
            self.self_esteem = min(1.0, self.self_esteem + 0.05)
            self.money -= 1.0 * (1.5 - efficiency)
            self.stress_endured *= 0.95
        
        elif self.zone == "TRADE":
            self.money += 15.0 * efficiency
            self.stress_endured += 4.0
            if 15.0 * efficiency < 12.0:
                self.trade_dissonance += (12.0 - 15.0 * efficiency) * 0.2
        
        elif self.zone == "DEVELOPMENT":
            self.energy = min(100.0, self.energy + 15.0 * efficiency)
            self.self_esteem -= 0.07
        
        elif self.zone == "FLEX":
            self.stress_endured -= 12.0 * efficiency
            self.energy -= 10.0
        
        elif self.zone == "PANTHEON":
            self.self_esteem = min(1.0, self.self_esteem + 0.12)
            self.stress_endured = max(0.0, self.stress_endured * 0.5)
            self.coherence += 0.06
            self.pantheon_visit_count += 1
            
            if self.pantheon_visit_count == 1:
                if self.stress_endured > 60:
                    self.pantheon_doctrine_type = "TRANSCENDENCE"
                elif self.money < 20:
                    self.pantheon_doctrine_type = "MERITOCRACY"
                else:
                    self.pantheon_doctrine_type = "COHERENCE"
            
            self.pantheon_doctrine_bias = min(1.0, self.pantheon_doctrine_bias + 0.03)
            
            if not self.is_guru and self.pantheon_visit_count >= 10:
                self.is_guru = True
            
            if not self.is_guru:
                self.energy -= 8.0
            else:
                self.energy = min(100.0, self.energy + 0.5)
        
        # Skill gain
        if self.zone in self.skills:
            self.skills[self.zone] += 0.01 * efficiency
        
        # Clamp resources
        self.money = max(0, self.money)
        self.energy = max(0, min(100, self.energy))
        self.stress_endured = max(0, min(100, self.stress_endured))
    
    # ===== DECISION MAKING =====
    
    def decide_work_zone(self, anchors: Dict, tick: int) -> str:
        """Autonomous zone selection"""
        # Check doctrine override first
        forced = self.get_doctrine_override()
        if forced:
            return forced
        
        # Normal decision-making
        allowed = {"SCIENCE", "TRADE", "DEVELOPMENT", "FLEX", "PANTHEON"}
        
        if self.energy < 15:
            return "HOME"
        
        scores = {}
        
        # Pantheon attraction (vulnerability)
        if "PANTHEON" in allowed and self.self_esteem < 0.5:
            scores["PANTHEON"] = (0.5 - self.self_esteem) * 3.2 + (1.0 - self.coherence) * 2.1
        
        # Zone preferences
        if "SCIENCE" in allowed:
            scores["SCIENCE"] = (1.0 - self.coherence) * 1.6
        if "TRADE" in allowed:
            scores["TRADE"] = max(0.0, (50.0 - self.money) / 50.0) * 2.2
        if "DEVELOPMENT" in allowed:
            scores["DEVELOPMENT"] = ((100.0 - self.energy) / 100.0) * 0.8
        if "FLEX" in allowed:
            scores["FLEX"] = (self.stress_endured / 100.0) * 1.0
        
        for z in scores:
            scores[z] += random.uniform(0, 0.5 * (1.0 - self.coherence))
        
        return max(scores, key=scores.get) if scores else "HOME"
    
    # ===== STATE MACHINE =====
    
    def update_state(self, anchors: Dict, config: Dict, tick: int):
        """State machine: HOME -> TRAVELING -> WORK -> HOME"""
        # Decay
        self.coherence *= config["coherence"]["inertia"]
        self.coherence -= (self.stress_endured * 0.001)
        self.coherence = max(0.0, min(1.0, self.coherence))
        
        if self.coherence < 0.3 and not self.is_collapsing:
            self.is_collapsing = True
            self.on_collapse()
        
        shift_duration = config["shift"]["duration"]
        travel_budget = int(shift_duration * config["shift"]["travel_ratio"])
        work_budget = shift_duration - travel_budget
        
        if self.state == "TRAVELING":
            reached = self.move_toward_target(anchors, config)
            if reached:
                if self.target == "HOME":
                    self.state = "AT_HOME"
                    self.cycle_phase = "RESTING"
                elif self.target in {"SCIENCE", "TRADE", "DEVELOPMENT", "FLEX", "PANTHEON"}:
                    self.state = "AT_WORK"
                    self.zone = self.target
                    self.cycle_phase = "WORKING"
                self.target = None
        
        elif self.state == "AT_HOME":
            self.energy = min(100.0, self.energy + 0.8)
            self.stress_endured = max(0.0, self.stress_endured - 0.3)
            
            current_cycle = (tick - self.shift_offset) % (shift_duration * 2)
            if current_cycle == 0 and tick > self.shift_offset:
                self.travel_budget = travel_budget
                self.work_budget = work_budget
                chosen = self.decide_work_zone(anchors, tick)
                if chosen != "HOME":
                    self.target = chosen
                    self.state = "TRAVELING"
                    self.cycle_phase = "COMMUTING"
        
        elif self.state == "AT_WORK" and self.zone:
            self.perform_work(config)
            self.work_budget -= 1
            
            if self.work_budget <= 0 and not (self.is_guru and self.zone == "PANTHEON"):
                self.target = "HOME"
                self.state = "TRAVELING"
                self.cycle_phase = "RETURNING"
                self.zone = ""
    
    # ===== DOCTRINE SYSTEM =====
    
    def expose_to_doctrine(self, doctrine_type: str, guru_id: Optional[int], tick: int) -> bool:
        """Attempt indoctrination"""
        # Already indoctrinated same doctrine
        if self.doctrine_profile and self.doctrine_profile.doctrine_type == doctrine_type:
            self.doctrine_profile.strength += 0.01
            return False
        
        # Calculate susceptibility
        vulnerability = {
            NPCArchetype.PRAGMATIST: {DoctrineType.MERITOCRATIC: 0.8, DoctrineType.LIBERTARIAN_CULT: 0.7},
            NPCArchetype.IDEALIST: {DoctrineType.TRANSCENDENT: 0.9, DoctrineType.REVOLUTIONARY: 0.85},
            NPCArchetype.ANXIOUS: {DoctrineType.CONSPIRATORIAL: 0.95, DoctrineType.TRANSCENDENT: 0.85},
            NPCArchetype.OUTSIDER: {DoctrineType.REVOLUTIONARY: 0.95, DoctrineType.CONSPIRATORIAL: 0.85},
            NPCArchetype.HEDONIST: {DoctrineType.LIBERTARIAN_CULT: 0.8, DoctrineType.MERITOCRATIC: 0.7},
        }
        
        base_vuln = vulnerability.get(self.archetype, {}).get(doctrine_type, 0.5)
        stress_factor = min(1.0, self.stress_endured / 80.0)
        coherence_factor = (1.0 - self.coherence) * 0.5
        
        susceptibility = base_vuln * 0.6 + stress_factor * 0.2 + coherence_factor * 0.2
        
        if susceptibility > random.random():
            self.doctrine_profile = DoctrineProfile(
                doctrine_type=doctrine_type,
                strength=0.1,
                guru_id=guru_id
            )
            self.doctrine_history.append((tick, doctrine_type, "EXPOSED"))
            return True
        
        return False
    
    def deepen_indoctrination(self, tick: int):
        """Strengthen doctrine hold"""
        if not self.doctrine_profile:
            return
        
        # Check escape conditions
        if self._check_escape_conditions():
            self.begin_deradicalization(self.doctrine_profile.doctrine_type, tick)
            return
        
        # Strengthen and apply effects
        self.doctrine_profile.update()
        self._apply_doctrine_effects()
    
    def _apply_doctrine_effects(self):
        """Apply psychological effects based on doctrine"""
        if not self.doctrine_profile:
            return
        
        doc = self.doctrine_profile.doctrine_type
        
        if doc == DoctrineType.MERITOCRATIC:
            if self.money < 30:
                self.self_esteem -= 0.03
                self.stress_endured += 2.0
            else:
                self.self_esteem = min(1.0, self.self_esteem + 0.02)
        
        elif doc == DoctrineType.TRANSCENDENT:
            self.stress_endured *= 0.9
            self.coherence = min(1.0, self.coherence + 0.05)
            self.self_esteem = min(1.0, self.self_esteem + 0.02)
        
        elif doc == DoctrineType.CONSPIRATORIAL:
            self.stress_endured = min(100.0, self.stress_endured + 1.0)
            self.self_esteem = min(1.0, self.self_esteem + 0.01)
        
        elif doc == DoctrineType.REVOLUTIONARY:
            self.stress_endured = min(100.0, self.stress_endured + 0.5)
            self.self_esteem = min(1.0, self.self_esteem + 0.03)
            self.coherence = max(0.0, self.coherence - 0.02)
        
        elif doc == DoctrineType.LIBERTARIAN_CULT:
            if self.money > 150:
                self.self_esteem = min(1.0, self.self_esteem + 0.04)
            self.stress_endured = min(100.0, self.stress_endured + 0.5)
    
    def _check_escape_conditions(self) -> bool:
        """Check if NPC should escape indoctrination"""
        if not self.doctrine_profile:
            return False
        
        doc = self.doctrine_profile.doctrine_type
        
        if doc == DoctrineType.MERITOCRATIC:
            return self.stress_endured > 75 and self.money < 20
        elif doc == DoctrineType.TRANSCENDENT:
            return self.collapse_cycle_count > 3 and self.coherence < 0.4
        elif doc == DoctrineType.CONSPIRATORIAL:
            return self.has_witnessed_system_failure and random.random() < 0.02
        elif doc == DoctrineType.REVOLUTIONARY:
            return self.stress_endured < 40 and self.money > 100
        elif doc == DoctrineType.LIBERTARIAN_CULT:
            return self.stress_endured > 70 and self.coherence < 0.45
        
        return False
    
    def begin_deradicalization(self, doctrine_type: str, tick: int):
        """Start escape process"""
        recovery_times = {
            DoctrineType.MERITOCRATIC: 200,
            DoctrineType.TRANSCENDENT: 400,
            DoctrineType.CONSPIRATORIAL: 250,
            DoctrineType.REVOLUTIONARY: 180,
            DoctrineType.LIBERTARIAN_CULT: 220,
        }
        self.deradicalization_timer = recovery_times.get(doctrine_type, 200)
        self.doctrine_history.append((tick, doctrine_type, "ESCAPE_BEGUN"))
    
    def update_deradicalization(self, tick: int):
        """Recovery from indoctrination"""
        if self.deradicalization_timer <= 0:
            self.doctrine_profile = None
            self.doctrine_history.append((tick, "NONE", "RECOVERED"))
            return
        
        self.deradicalization_timer -= 1
        self.coherence = min(1.0, self.coherence + 0.005)
    
    def get_doctrine_override(self) -> Optional[str]:
        """Check if doctrine forces zone choice"""
        if not self.doctrine_profile:
            return None
        
        doc = self.doctrine_profile.doctrine_type
        
        overrides = {
            DoctrineType.MERITOCRATIC: ("TRADE", 0.8),
            DoctrineType.TRANSCENDENT: ("PANTHEON", 0.95),
            DoctrineType.CONSPIRATORIAL: ("PANTHEON", 0.85),
            DoctrineType.REVOLUTIONARY: ("PANTHEON", 0.9),
            DoctrineType.LIBERTARIAN_CULT: ("TRADE", 0.75),
        }
        
        if doc not in overrides:
            return None
        
        forced_zone, freq = overrides[doc]
        
        if random.random() > freq:
            return None
        
        if doc == DoctrineType.MERITOCRATIC:
            return "TRADE" if self.money < 50 else None
        elif doc == DoctrineType.REVOLUTIONARY:
            return "DEVELOPMENT" if random.random() < 0.3 else "PANTHEON"
        
        return forced_zone
    
    def witness_injustice(self, severity: float):
        """Record system failure"""
        self.injustice_accumulated += severity
        if self.injustice_accumulated > 100:
            self.has_witnessed_system_failure = True
    
    def on_collapse(self):
        """Called when NPC collapses"""
        self.collapse_cycle_count += 1
    
    # ===== MAIN UPDATE =====
    
    def act(self, anchors: Dict, config: Dict, tick: int):
        """Main update loop"""
        # State machine
        self.update_state(anchors, config, tick)
        
        # Doctrine mechanics
        if self.doctrine_profile:
            self.deepen_indoctrination(tick)
        
        if self.deradicalization_timer > 0:
            self.update_deradicalization(tick)
        
        # Trust computation
        if tick % 10 == 0:
            self.compute_trustworthiness()