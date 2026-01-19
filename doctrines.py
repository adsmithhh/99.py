# ===== doctrine_registry.py ===== (ENHANCED WITH COMPATIBILITY)
"""
Unified doctrine management and effects engine
Replaces scattered logic with clean registry pattern
NOW WITH: Multi-doctrine conflict mechanics
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Set
from enum import Enum
import random
import math
from collections import deque

# ===== ENUMS =====

class NPCArchetype(Enum):
    PRAGMATIST = "PRAGMATIST"
    IDEALIST = "IDEALIST"
    ANXIOUS = "ANXIOUS"
    OUTSIDER = "OUTSIDER"
    HEDONIST = "HEDONIST"

class DoctrineType(Enum):
    MERITOCRATIC = "MERITOCRATIC"
    TRANSCENDENT = "TRANSCENDENT"
    CONSPIRATORIAL = "CONSPIRATORIAL"
    REVOLUTIONARY = "REVOLUTIONARY"
    LIBERTARIAN_CULT = "LIBERTARIAN_CULT"

class GuruType(Enum):
    PROSPERITY_PREACHER = "PROSPERITY_PREACHER"
    ENLIGHTENED_SAGE = "ENLIGHTENED_SAGE"
    SHADOWY_INSIDER = "SHADOWY_INSIDER"
    FIREBRAND_REBEL = "FIREBRAND_REBEL"
    SOVEREIGN_INDIVIDUALIST = "SOVEREIGN_INDIVIDUALIST"

# ===== DOCTRINE COMPATIBILITY MATRIX =====

DOCTRINE_COMPATIBILITY: Dict[DoctrineType, Dict[DoctrineType, float]] = {
    # Value = tension per tick when exposed (positive = builds dissonance/stress, negative = synergy)
    # 0 = neutral, can coexist peacefully
    # >0 = conflict (higher = faster escape/dissonance)
    # <0 = synergy (small bonus to strength or esteem)

    DoctrineType.MERITOCRATIC: {
        DoctrineType.MERITOCRATIC: 0.0,          # same = no tension
        DoctrineType.LIBERTARIAN_CULT: -0.015,   # quite compatible (both value individual success/wealth)
        DoctrineType.TRANSCENDENT: 0.02,         # mild friction (material vs spiritual)
        DoctrineType.CONSPIRATORIAL: 0.04,       # moderate friction
        DoctrineType.REVOLUTIONARY: 0.09,        # very high — system-justifying vs system-destroying
    },

    DoctrineType.LIBERTARIAN_CULT: {
        DoctrineType.MERITOCRATIC: -0.015,
        DoctrineType.LIBERTARIAN_CULT: 0.0,
        DoctrineType.TRANSCENDENT: 0.01,
        DoctrineType.CONSPIRATORIAL: 0.03,
        DoctrineType.REVOLUTIONARY: 0.07,        # still high (collectivist revolution threatens individual sovereignty)
    },

    DoctrineType.TRANSCENDENT: {
        DoctrineType.TRANSCENDENT: 0.0,
        DoctrineType.CONSPIRATORIAL: -0.01,      # both can appeal to "hidden meaning/truth"
        DoctrineType.MERITOCRATIC: 0.03,
        DoctrineType.LIBERTARIAN_CULT: 0.02,
        DoctrineType.REVOLUTIONARY: 0.05,        # moderate (revolution can be "spiritual cleansing")
    },

    DoctrineType.CONSPIRATORIAL: {
        DoctrineType.CONSPIRATORIAL: 0.0,
        DoctrineType.TRANSCENDENT: -0.01,
        DoctrineType.REVOLUTIONARY: 0.04,        # can blend (hidden elites must be overthrown)
        DoctrineType.MERITOCRATIC: 0.05,
        DoctrineType.LIBERTARIAN_CULT: 0.03,
    },

    DoctrineType.REVOLUTIONARY: {
        DoctrineType.REVOLUTIONARY: 0.0,
        DoctrineType.CONSPIRATORIAL: 0.04,
        DoctrineType.TRANSCENDENT: 0.05,
        DoctrineType.MERITOCRATIC: 0.10,         # max tension
        DoctrineType.LIBERTARIAN_CULT: 0.08,
    },
}

# Default for missing pairs = 0.02 (mild natural friction)
DEFAULT_DOCTRINE_TENSION = 0.02

def get_doctrine_tension(doc1: DoctrineType, doc2: DoctrineType) -> float:
    """Get tension between two doctrines"""
    if doc1 == doc2:
        return 0.0
    
    tension = DOCTRINE_COMPATIBILITY.get(doc1, {}).get(doc2, DEFAULT_DOCTRINE_TENSION)
    return tension

# ===== DATACLASSES =====

@dataclass
class DoctrineProfile:
    """NPC's current indoctrination state"""
    doctrine_type: DoctrineType
    strength: float = 0.0  # 0.0 to 1.0
    time_indoctrinated: int = 0
    guru_id: Optional[int] = None
    conflict_dissonance: float = 0.0  # Accumulated tension from incompatible doctrines
    
    def update(self):
        """Strengthen over time"""
        self.time_indoctrinated += 1
        self.strength = min(1.0, self.strength + 0.02)
    
    def apply_conflict_damage(self, tension: float):
        """Apply tension from incompatible doctrine exposure"""
        self.conflict_dissonance += tension
        self.strength = max(0.0, self.strength - tension * 0.3)

@dataclass
class GuruProfile:
    """Guru NPC influence state"""
    guru_id: int
    doctrine_type: DoctrineType
    guru_type: GuruType
    influence_radius: float = 300.0
    followers: Set[int] = field(default_factory=set)
    lifespan: int = 5000
    
    def get_rhetoric(self) -> str:
        """Return guru's characteristic message"""
        rhetoric = {
            GuruType.PROSPERITY_PREACHER: "You deserve what you earn.",
            GuruType.ENLIGHTENED_SAGE: "Your pain has meaning.",
            GuruType.SHADOWY_INSIDER: "They hide the truth.",
            GuruType.FIREBRAND_REBEL: "Tear it all down.",
            GuruType.SOVEREIGN_INDIVIDUALIST: "You owe nothing.",
        }
        return rhetoric.get(self.guru_type, "Follow me.")

# ===== ARCHETYPE VULNERABILITY MATRIX =====

ARCHETYPE_VULNERABILITIES: Dict[NPCArchetype, Dict[DoctrineType, float]] = {
    NPCArchetype.PRAGMATIST: {
        DoctrineType.MERITOCRATIC: 0.8,
        DoctrineType.LIBERTARIAN_CULT: 0.7,
        DoctrineType.TRANSCENDENT: 0.2,
        DoctrineType.CONSPIRATORIAL: 0.3,
        DoctrineType.REVOLUTIONARY: 0.4,
    },
    NPCArchetype.IDEALIST: {
        DoctrineType.TRANSCENDENT: 0.9,
        DoctrineType.REVOLUTIONARY: 0.85,
        DoctrineType.CONSPIRATORIAL: 0.4,
        DoctrineType.MERITOCRATIC: 0.5,
        DoctrineType.LIBERTARIAN_CULT: 0.3,
    },
    NPCArchetype.ANXIOUS: {
        DoctrineType.CONSPIRATORIAL: 0.95,
        DoctrineType.TRANSCENDENT: 0.85,
        DoctrineType.MERITOCRATIC: 0.6,
        DoctrineType.LIBERTARIAN_CULT: 0.4,
        DoctrineType.REVOLUTIONARY: 0.3,
    },
    NPCArchetype.OUTSIDER: {
        DoctrineType.REVOLUTIONARY: 0.95,
        DoctrineType.CONSPIRATORIAL: 0.85,
        DoctrineType.LIBERTARIAN_CULT: 0.7,
        DoctrineType.TRANSCENDENT: 0.3,
        DoctrineType.MERITOCRATIC: 0.2,
    },
    NPCArchetype.HEDONIST: {
        DoctrineType.LIBERTARIAN_CULT: 0.8,
        DoctrineType.MERITOCRATIC: 0.7,
        DoctrineType.CONSPIRATORIAL: 0.6,
        DoctrineType.TRANSCENDENT: 0.4,
        DoctrineType.REVOLUTIONARY: 0.2,
    },
}

# ===== DOCTRINE SPECIFICATIONS =====

@dataclass
class DoctrineSpec:
    """Specification for a doctrine type"""
    doctrine_type: DoctrineType
    name: str
    symbol: str
    color: tuple
    forces_zone: str
    override_frequency: float
    
    # Psychological effects callbacks
    apply_effects: Callable  # fn(npc) -> None
    check_exposure: Callable  # fn(npc) -> bool
    check_escape: Callable   # fn(npc) -> bool
    
    # Deradicalization timing
    recovery_time: int = 200

# ===== PSYCHOLOGICAL EFFECTS =====

class PsychologicalEffects:
    """All doctrine-specific psychological effects"""
    
    @staticmethod
    def meritocratic(npc):
        """Wealth = Moral Worth"""
        if npc.money < 30:
            npc.self_esteem = max(0.0, npc.self_esteem - 0.03)
            npc.stress_endured = min(100.0, npc.stress_endured + 2.0)
        else:
            npc.self_esteem = min(1.0, npc.self_esteem + 0.02)
    
    @staticmethod
    def transcendent(npc):
        """Suffering is Sacred"""
        npc.stress_endured *= 0.9
        npc.coherence = min(1.0, npc.coherence + 0.05)
        npc.self_esteem = min(1.0, npc.self_esteem + 0.02)
    
    @staticmethod
    def conspiratorial(npc):
        """Hidden Powers Control Everything"""
        npc.stress_endured = min(100.0, npc.stress_endured + 1.0)
        npc.self_esteem = min(1.0, npc.self_esteem + 0.01)
    
    @staticmethod
    def revolutionary(npc):
        """System Must Be Destroyed"""
        npc.stress_endured = min(100.0, npc.stress_endured + 0.5)
        npc.self_esteem = min(1.0, npc.self_esteem + 0.03)
        npc.coherence = max(0.0, npc.coherence - 0.02)
    
    @staticmethod
    def libertarian(npc):
        """Absolute Individual Freedom"""
        if npc.money > 150:
            npc.self_esteem = min(1.0, npc.self_esteem + 0.04)
        npc.stress_endured = min(100.0, npc.stress_endured + 0.5)

# ===== EXPOSURE CHECKS =====

class ExposureChecks:
    """When can NPCs be exposed to doctrines?"""
    
    @staticmethod
    def meritocratic(npc) -> bool:
        """Exposed when: poor + stressed + incoherent"""
        return npc.money < 30 and npc.stress_endured > 40 and npc.coherence < 0.65
    
    @staticmethod
    def transcendent(npc) -> bool:
        """Exposed when: high stress + low coherence"""
        return npc.stress_endured > 65 and npc.coherence < 0.5
    
    @staticmethod
    def conspiratorial(npc) -> bool:
        """Exposed when: stressed + witnessed failure"""
        return npc.stress_endured > 55 and npc.has_witnessed_system_failure
    
    @staticmethod
    def revolutionary(npc) -> bool:
        """Exposed when: repeated collapses"""
        return npc.collapse_cycle_count > 2 and npc.coherence < 0.4
    
    @staticmethod
    def libertarian(npc) -> bool:
        """Exposed when: wealthy + stable"""
        return npc.money > 200 and npc.coherence > 0.65

# ===== ESCAPE CHECKS =====

class EscapeChecks:
    """When do NPCs escape indoctrination?"""
    
    @staticmethod
    def meritocratic(npc) -> bool:
        """Escape: repeated failure despite effort"""
        return npc.stress_endured > 75 and npc.money < 20
    
    @staticmethod
    def transcendent(npc) -> bool:
        """Escape: promised enlightenment never comes"""
        return npc.collapse_cycle_count > 3 and npc.coherence < 0.4
    
    @staticmethod
    def conspiratorial(npc) -> bool:
        """Escape: predictions don't come true"""
        return npc.has_witnessed_system_failure and random.random() < 0.02
    
    @staticmethod
    def revolutionary(npc) -> bool:
        """Escape: system stabilizes"""
        return npc.stress_endured < 40 and npc.money > 100
    
    @staticmethod
    def libertarian(npc) -> bool:
        """Escape: crisis requires collective action"""
        return npc.stress_endured > 70 and npc.coherence < 0.45

# ===== DOCTRINE REGISTRY =====

class DoctrineRegistry:
    """Central registry for all doctrines"""
    
    _doctrines: Dict[DoctrineType, DoctrineSpec] = {}
    
    @classmethod
    def initialize(cls):
        """Register all doctrine types"""
        cls._doctrines = {
            DoctrineType.MERITOCRATIC: DoctrineSpec(
                doctrine_type=DoctrineType.MERITOCRATIC,
                name="Merit Doctrine",
                symbol="⚖️",
                color=(192, 192, 192),
                forces_zone="TRADE",
                override_frequency=0.8,
                apply_effects=PsychologicalEffects.meritocratic,
                check_exposure=ExposureChecks.meritocratic,
                check_escape=EscapeChecks.meritocratic,
                recovery_time=200,
            ),
            DoctrineType.TRANSCENDENT: DoctrineSpec(
                doctrine_type=DoctrineType.TRANSCENDENT,
                name="Transcendence Doctrine",
                symbol="✨",
                color=(255, 215, 0),
                forces_zone="PANTHEON",
                override_frequency=0.95,
                apply_effects=PsychologicalEffects.transcendent,
                check_exposure=ExposureChecks.transcendent,
                check_escape=EscapeChecks.transcendent,
                recovery_time=400,
            ),
            DoctrineType.CONSPIRATORIAL: DoctrineSpec(
                doctrine_type=DoctrineType.CONSPIRATORIAL,
                name="Conspiracy Doctrine",
                symbol="🔍",
                color=(128, 0, 128),
                forces_zone="PANTHEON",
                override_frequency=0.85,
                apply_effects=PsychologicalEffects.conspiratorial,
                check_exposure=ExposureChecks.conspiratorial,
                check_escape=EscapeChecks.conspiratorial,
                recovery_time=250,
            ),
            DoctrineType.REVOLUTIONARY: DoctrineSpec(
                doctrine_type=DoctrineType.REVOLUTIONARY,
                name="Revolutionary Doctrine",
                symbol="⚡",
                color=(255, 0, 0),
                forces_zone="PANTHEON",
                override_frequency=0.9,
                apply_effects=PsychologicalEffects.revolutionary,
                check_exposure=ExposureChecks.revolutionary,
                check_escape=EscapeChecks.revolutionary,
                recovery_time=180,
            ),
            DoctrineType.LIBERTARIAN_CULT: DoctrineSpec(
                doctrine_type=DoctrineType.LIBERTARIAN_CULT,
                name="Libertarian Cult",
                symbol="🗽",
                color=(0, 128, 255),
                forces_zone="TRADE",
                override_frequency=0.75,
                apply_effects=PsychologicalEffects.libertarian,
                check_exposure=ExposureChecks.libertarian,
                check_escape=EscapeChecks.libertarian,
                recovery_time=220,
            ),
        }
    
    @classmethod
    def get(cls, doctrine_type: DoctrineType) -> DoctrineSpec:
        """Get doctrine specification"""
        if not cls._doctrines:
            cls.initialize()
        return cls._doctrines.get(doctrine_type)
    
    @classmethod
    def all(cls) -> Dict[DoctrineType, DoctrineSpec]:
        """Get all doctrines"""
        if not cls._doctrines:
            cls.initialize()
        return cls._doctrines
    
    @classmethod
    def register_custom(cls, spec: DoctrineSpec):
        """Register custom doctrine"""
        cls._doctrines[spec.doctrine_type] = spec

# ===== NPC DOCTRINE MIXIN (ENHANCED WITH CONFLICT) =====

class DoctrineMixin:
    """Add to NPC via multiple inheritance"""
    
    def init_doctrine_fields(self):
        """Initialize doctrine-related fields"""
        self.archetype: NPCArchetype = random.choice(list(NPCArchetype))
        self.doctrine_profile: Optional[DoctrineProfile] = None
        self.doctrine_history: deque = deque(maxlen=50)
        self.deradicalization_timer: int = 0
        self.injustice_accumulated: float = 0.0
        self.collapse_cycle_count: int = 0
        self.has_witnessed_system_failure: bool = False
        self.doctrine_conflict_stress: float = 0.0  # NEW: Accumulated from incompatible doctrines
    
    def expose_to_doctrine(self, doctrine_type: DoctrineType, guru_id: Optional[int], tick: int) -> bool:
        """Attempt indoctrination (with conflict mechanics)"""
        spec = DoctrineRegistry.get(doctrine_type)
        
        # Already indoctrinated with SAME doctrine
        if self.doctrine_profile and self.doctrine_profile.doctrine_type == doctrine_type:
            self.doctrine_profile.strength = min(1.0, self.doctrine_profile.strength + 0.01)
            return False
        
        # Already indoctrinated with DIFFERENT doctrine (CONFLICT)
        if self.doctrine_profile:
            tension = get_doctrine_tension(self.doctrine_profile.doctrine_type, doctrine_type)
            
            # Synergy (negative tension): Strengthen both
            if tension < 0:
                self.doctrine_profile.strength = min(1.0, self.doctrine_profile.strength + abs(tension))
                self.self_esteem = min(1.0, self.self_esteem + abs(tension) * 0.5)
                return False
            
            # Conflict (positive tension): Apply damage
            elif tension > 0:
                self.doctrine_profile.apply_conflict_damage(tension)
                self.doctrine_conflict_stress += tension
                self.stress_endured = min(100.0, self.stress_endured + tension * 10.0)
                
                # High conflict can cause doctrine collapse
                if self.doctrine_profile.conflict_dissonance > 1.0:
                    self.doctrine_history.append((tick, self.doctrine_profile.doctrine_type.value, "DOCTRINE_COLLAPSE"))
                    self.begin_deradicalization(self.doctrine_profile.doctrine_type, tick)
                    # Now vulnerable to new doctrine
                
                return False
        
        # Not indoctrinated OR just escaped - try to indoctrinate
        base_vuln = ARCHETYPE_VULNERABILITIES.get(self.archetype, {}).get(doctrine_type, 0.5)
        
        # Stress + coherence factors
        stress_factor = min(1.0, self.stress_endured / 80.0)
        coherence_factor = (1.0 - self.coherence) * 0.5
        
        # Total susceptibility
        susceptibility = (base_vuln * 0.6 + stress_factor * 0.2 + coherence_factor * 0.2)
        
        if susceptibility > random.random():
            self.doctrine_profile = DoctrineProfile(
                doctrine_type=doctrine_type,
                strength=0.1,
                guru_id=guru_id
            )
            self.doctrine_history.append((tick, doctrine_type.value, "EXPOSED"))
            return True
        
        return False
    
    def deepen_indoctrination(self, tick: int):
        """Strengthen doctrine hold"""
        if not self.doctrine_profile:
            return
        
        spec = DoctrineRegistry.get(self.doctrine_profile.doctrine_type)
        
        # Check escape conditions (includes conflict dissonance)
        if spec.check_escape(self) or self.doctrine_profile.conflict_dissonance > 0.8:
            self.begin_deradicalization(self.doctrine_profile.doctrine_type, tick)
            return
        
        # Strengthen and apply effects
        self.doctrine_profile.update()
        spec.apply_effects(self)
        
        # Decay conflict dissonance slightly (healing over time)
        self.doctrine_profile.conflict_dissonance *= 0.98
    
    def begin_deradicalization(self, doctrine_type: DoctrineType, tick: int):
        """Start escape process"""
        spec = DoctrineRegistry.get(doctrine_type)
        self.deradicalization_timer = spec.recovery_time
        self.doctrine_history.append((tick, doctrine_type.value, "ESCAPE_BEGUN"))
    
    def update_deradicalization(self, tick: int):
        """Recovery from indoctrination"""
        if self.deradicalization_timer <= 0:
            self.doctrine_profile = None
            self.doctrine_conflict_stress *= 0.9  # Slowly heal conflict stress
            self.doctrine_history.append((tick, "NONE", "RECOVERED"))
            return
        
        self.deradicalization_timer -= 1
        self.coherence = min(1.0, self.coherence + 0.005)
    
    def get_doctrine_override(self) -> Optional[str]:
        """Check if doctrine forces zone"""
        if not self.doctrine_profile:
            return None
        
        spec = DoctrineRegistry.get(self.doctrine_profile.doctrine_type)
        
        # Weakened doctrine less likely to override
        override_strength = spec.override_frequency * self.doctrine_profile.strength
        
        if random.random() > override_strength:
            return None
        
        # Special logic for some doctrines
        if self.doctrine_profile.doctrine_type == DoctrineType.MERITOCRATIC:
            return "TRADE" if self.money < 50 else None
        elif self.doctrine_profile.doctrine_type == DoctrineType.REVOLUTIONARY:
            return "DEVELOPMENT" if random.random() < 0.3 else "PANTHEON"
        
        return spec.forces_zone
    
    def witness_injustice(self, severity: float):
        """Record system failure"""
        self.injustice_accumulated += severity
        if self.injustice_accumulated > 100:
            self.has_witnessed_system_failure = True
    
    def on_collapse(self):
        """Called when NPC collapses"""
        self.collapse_cycle_count += 1

# ===== GURU SYSTEM =====

class GuruSystem:
    """Manage gurus and their influence"""
    
    def __init__(self):
        self.gurus: Dict[int, GuruProfile] = {}
    
    def register_guru(self, npc_id: int, doctrine: DoctrineType, guru_type: GuruType):
        """Register NPC as guru"""
        self.gurus[npc_id] = GuruProfile(
            guru_id=npc_id,
            doctrine_type=doctrine,
            guru_type=guru_type
        )
    
    def spread_influence(self, guru_id: int, nearby_npcs: List, tick: int):
        """Spread ideology to nearby NPCs"""
        if guru_id not in self.gurus:
            return
        
        guru = self.gurus[guru_id]
        
        for npc in nearby_npcs:
            if npc.id == guru_id or npc.is_guru:
                continue
            
            # Vulnerability + distance decay
            vuln = ARCHETYPE_VULNERABILITIES.get(npc.archetype, {}).get(guru.doctrine_type, 0.5)
            distance = math.hypot(npc.x - 300, npc.y - 300)
            
            if distance > guru.influence_radius:
                continue
            
            influence = (1.0 - (distance / guru.influence_radius)) * vuln
            
            if influence > random.random() * 0.5:
                if npc.expose_to_doctrine(guru.doctrine_type, guru_id, tick):
                    guru.followers.add(npc.id)

# ===== ANALYTICS =====

class DoctrineAnalytics:
    """Query doctrine statistics"""
    
    @staticmethod
    def get_indoctrinated(npcs: List, doctrine: DoctrineType = None) -> List:
        """Get indoctrinated NPCs"""
        if doctrine:
            return [n for n in npcs if n.doctrine_profile and n.doctrine_profile.doctrine_type == doctrine]
        return [n for n in npcs if n.doctrine_profile]
    
    @staticmethod
    def get_by_archetype(npcs: List, arch: NPCArchetype) -> List:
        """Get NPCs by archetype"""
        return [n for n in npcs if n.archetype == arch]
    
    @staticmethod
    def get_doctrine_conflicts(npcs: List) -> List:
        """Get NPCs experiencing doctrine conflict"""
        return [n for n in npcs if n.doctrine_profile and n.doctrine_profile.conflict_dissonance > 0.3]
    
    @staticmethod
    def print_report(npcs: List, tick: int):
        """Print doctrine status"""
        counts = {}
        conflicts = 0
        
        for npc in npcs:
            if npc.doctrine_profile:
                d = npc.doctrine_profile.doctrine_type.value
                counts[d] = counts.get(d, 0) + 1
                if npc.doctrine_profile.conflict_dissonance > 0.3:
                    conflicts += 1
        
        print(f"\n[Tick {tick}] Doctrine Report")
        print(f"Total NPCs: {len(npcs)}")
        for doc, count in sorted(counts.items()):
            print(f"  {doc}: {count}")
        print(f"Doctrine Conflicts: {conflicts}")

# Initialize registry on import
DoctrineRegistry.initialize()