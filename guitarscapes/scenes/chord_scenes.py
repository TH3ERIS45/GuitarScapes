"""Chord-to-scene mapping library for GuitarScapes Pro.

Maps all 108 chord names (12 roots × 9 types) to unique ``VisualEnvironment``
instances, giving every chord its own distinctive visual identity.

Chord families follow thematic guidelines:
    - **Major** — warm, bright, positive landscapes
    - **Minor** — cool, dark, moody atmospheres
    - **Dominant 7th** — jazzy, warm sunset tones
    - **Minor 7th** — deep, contemplative blues/purples
    - **Major 7th** — ethereal, dreamy pastels
    - **Sus2** — open, airy, floating
    - **Sus4** — tense, anticipating, stormy
    - **Diminished** — eerie, mysterious darkness
    - **Augmented** — surreal, sparkling, vibrant
"""

from __future__ import annotations

import logging
from typing import ClassVar

from guitarscapes.visuals.environment import ParticleConfig, VisualEnvironment

logger = logging.getLogger(__name__)


class ChordSceneLibrary:
    """Provides ``VisualEnvironment`` scenes for every supported chord.

    Usage::

        library = ChordSceneLibrary()
        scene = library.get_scene("Am")
    """

    _scenes: ClassVar[dict[str, VisualEnvironment]] = {
        # =====================================================================
        # MAJOR CHORDS — Warm, bright, positive
        # =====================================================================

        # C — Golden dawn
        "C": VisualEnvironment(
            bg_color_top=(0.95, 0.72, 0.20),
            bg_color_bottom=(0.85, 0.45, 0.12),
            effect_color=(1.0, 0.90, 0.55),
            enable_god_rays=True,
            enable_fog=True,
            enable_mountains=True,
            god_ray_position=(0.3, 0.85),
            mood="golden dawn",
        ),
        # C# — Amber fields
        "C#": VisualEnvironment(
            bg_color_top=(0.92, 0.78, 0.30),
            bg_color_bottom=(0.80, 0.55, 0.15),
            effect_color=(0.95, 0.85, 0.45),
            enable_leaves=True,
            enable_god_rays=True,
            god_ray_position=(0.5, 0.90),
            particle_config=ParticleConfig(
                emit_rate=30.0,
                color=(0.90, 0.75, 0.25, 0.7),
                size_range=(3.0, 7.0),
                velocity_range=((-0.3, 0.3), (-0.8, -0.2)),
                lifetime_range=(2.0, 5.0),
                gravity=(0.0, -0.05),
                wind=(0.15, 0.0),
            ),
            mood="amber fields",
        ),
        # D — Sunlit meadow
        "D": VisualEnvironment(
            bg_color_top=(0.55, 0.85, 0.35),
            bg_color_bottom=(0.75, 0.90, 0.40),
            effect_color=(0.95, 0.95, 0.55),
            enable_fireflies=True,
            enable_leaves=True,
            particle_config=ParticleConfig(
                emit_rate=45.0,
                color=(0.95, 0.95, 0.40, 0.9),
                size_range=(2.0, 4.0),
                velocity_range=((-0.2, 0.2), (-0.1, 0.3)),
                lifetime_range=(2.0, 4.0),
            ),
            mood="sunlit meadow",
        ),
        # D# — Tropical sunset
        "D#": VisualEnvironment(
            bg_color_top=(0.95, 0.50, 0.25),
            bg_color_bottom=(0.90, 0.30, 0.45),
            effect_color=(1.0, 0.70, 0.40),
            enable_waves=True,
            enable_god_rays=True,
            god_ray_position=(0.5, 0.75),
            mood="tropical sunset",
        ),
        # E — Clear blue sky
        "E": VisualEnvironment(
            bg_color_top=(0.30, 0.60, 0.95),
            bg_color_bottom=(0.55, 0.78, 1.0),
            effect_color=(1.0, 1.0, 0.90),
            enable_fog=True,
            enable_god_rays=True,
            god_ray_position=(0.5, 0.95),
            mood="clear blue sky",
        ),
        # F — Flower field
        "F": VisualEnvironment(
            bg_color_top=(0.85, 0.50, 0.75),
            bg_color_bottom=(0.70, 0.40, 0.80),
            effect_color=(1.0, 0.80, 0.90),
            enable_leaves=True,
            enable_fireflies=True,
            particle_config=ParticleConfig(
                emit_rate=40.0,
                color=(0.95, 0.60, 0.80, 0.8),
                size_range=(3.0, 6.0),
                velocity_range=((-0.4, 0.4), (-0.6, -0.1)),
                lifetime_range=(2.5, 5.0),
                wind=(0.1, 0.0),
            ),
            mood="flower field",
        ),
        # F# — Desert gold
        "F#": VisualEnvironment(
            bg_color_top=(0.90, 0.70, 0.25),
            bg_color_bottom=(0.82, 0.55, 0.18),
            effect_color=(1.0, 0.85, 0.40),
            enable_mountains=True,
            enable_god_rays=True,
            god_ray_position=(0.6, 0.90),
            mood="desert gold",
        ),
        # G — Starry night
        "G": VisualEnvironment(
            bg_color_top=(0.05, 0.05, 0.20),
            bg_color_bottom=(0.10, 0.08, 0.30),
            effect_color=(0.80, 0.85, 1.0),
            enable_stars=True,
            enable_constellations=True,
            enable_mountains=True,
            mood="starry night",
        ),
        # G# — Crystal cave
        "G#": VisualEnvironment(
            bg_color_top=(0.10, 0.35, 0.40),
            bg_color_bottom=(0.05, 0.25, 0.35),
            effect_color=(0.40, 0.90, 0.95),
            enable_constellations=True,
            enable_fireflies=True,
            particle_config=ParticleConfig(
                emit_rate=25.0,
                color=(0.50, 0.95, 1.0, 0.6),
                size_range=(1.0, 3.0),
                velocity_range=((-0.1, 0.1), (0.0, 0.2)),
                lifetime_range=(1.5, 3.5),
            ),
            mood="crystal cave",
        ),
        # A — Warm campfire
        "A": VisualEnvironment(
            bg_color_top=(0.20, 0.08, 0.02),
            bg_color_bottom=(0.40, 0.15, 0.05),
            effect_color=(1.0, 0.60, 0.15),
            enable_fire=True,
            enable_fireflies=True,
            particle_config=ParticleConfig(
                emit_rate=60.0,
                color=(1.0, 0.55, 0.10, 0.9),
                size_range=(2.0, 5.0),
                velocity_range=((-0.3, 0.3), (0.3, 1.0)),
                lifetime_range=(0.5, 2.0),
                gravity=(0.0, 0.02),
            ),
            mood="warm campfire",
        ),
        # A# — Harvest moon
        "A#": VisualEnvironment(
            bg_color_top=(0.35, 0.18, 0.05),
            bg_color_bottom=(0.50, 0.28, 0.08),
            effect_color=(0.95, 0.70, 0.25),
            enable_mountains=True,
            enable_god_rays=True,
            enable_fog=True,
            god_ray_position=(0.7, 0.80),
            mood="harvest moon",
        ),
        # B — Snow peaks
        "B": VisualEnvironment(
            bg_color_top=(0.80, 0.88, 0.95),
            bg_color_bottom=(0.90, 0.92, 0.98),
            effect_color=(0.95, 0.97, 1.0),
            enable_snow=True,
            enable_mountains=True,
            particle_config=ParticleConfig(
                emit_rate=55.0,
                color=(0.95, 0.97, 1.0, 0.8),
                size_range=(2.0, 5.0),
                velocity_range=((-0.2, 0.2), (-0.5, -0.1)),
                lifetime_range=(3.0, 6.0),
                gravity=(0.0, -0.03),
                wind=(0.08, 0.0),
            ),
            mood="snow peaks",
        ),

        # =====================================================================
        # MINOR CHORDS — Cool, dark, moody
        # =====================================================================

        # Cm — Midnight storm
        "Cm": VisualEnvironment(
            bg_color_top=(0.05, 0.05, 0.15),
            bg_color_bottom=(0.15, 0.15, 0.25),
            effect_color=(0.60, 0.65, 0.90),
            enable_rain=True,
            enable_god_rays=True,
            god_ray_position=(0.4, 0.70),
            particle_config=ParticleConfig(
                emit_rate=80.0,
                color=(0.60, 0.65, 0.85, 0.5),
                size_range=(1.0, 2.5),
                velocity_range=((-0.1, 0.1), (-2.0, -1.0)),
                lifetime_range=(0.3, 1.0),
                gravity=(0.0, -0.15),
            ),
            mood="midnight storm",
        ),
        # C#m — Deep ocean
        "C#m": VisualEnvironment(
            bg_color_top=(0.02, 0.10, 0.20),
            bg_color_bottom=(0.03, 0.15, 0.30),
            effect_color=(0.20, 0.50, 0.70),
            enable_waves=True,
            particle_config=ParticleConfig(
                emit_rate=15.0,
                color=(0.30, 0.60, 0.80, 0.4),
                size_range=(3.0, 8.0),
                velocity_range=((-0.05, 0.05), (0.05, 0.15)),
                lifetime_range=(3.0, 6.0),
            ),
            mood="deep ocean",
        ),
        # Dm — Misty lake
        "Dm": VisualEnvironment(
            bg_color_top=(0.30, 0.35, 0.45),
            bg_color_bottom=(0.20, 0.28, 0.40),
            effect_color=(0.60, 0.70, 0.80),
            enable_fog=True,
            enable_waves=True,
            enable_mountains=True,
            mood="misty lake",
        ),
        # D#m — Haunted woods
        "D#m": VisualEnvironment(
            bg_color_top=(0.08, 0.15, 0.08),
            bg_color_bottom=(0.12, 0.18, 0.10),
            effect_color=(0.40, 0.55, 0.35),
            enable_fog=True,
            enable_fireflies=True,
            enable_leaves=True,
            particle_config=ParticleConfig(
                emit_rate=12.0,
                color=(0.45, 0.60, 0.30, 0.3),
                size_range=(2.0, 4.0),
                velocity_range=((-0.1, 0.1), (-0.1, 0.05)),
                lifetime_range=(3.0, 6.0),
            ),
            mood="haunted woods",
        ),
        # Em — Dark forest
        "Em": VisualEnvironment(
            bg_color_top=(0.02, 0.10, 0.02),
            bg_color_bottom=(0.05, 0.12, 0.05),
            effect_color=(0.20, 0.50, 0.20),
            enable_fog=True,
            enable_mountains=True,
            enable_fireflies=True,
            particle_config=ParticleConfig(
                emit_rate=18.0,
                color=(0.30, 0.70, 0.20, 0.5),
                size_range=(1.5, 3.5),
                velocity_range=((-0.15, 0.15), (-0.05, 0.15)),
                lifetime_range=(2.0, 5.0),
            ),
            mood="dark forest",
        ),
        # Fm — Frozen tundra
        "Fm": VisualEnvironment(
            bg_color_top=(0.45, 0.55, 0.70),
            bg_color_bottom=(0.60, 0.70, 0.82),
            effect_color=(0.80, 0.88, 0.95),
            enable_snow=True,
            enable_fog=True,
            enable_mountains=True,
            particle_config=ParticleConfig(
                emit_rate=50.0,
                color=(0.85, 0.90, 1.0, 0.7),
                size_range=(2.0, 4.0),
                velocity_range=((-0.3, 0.3), (-0.4, -0.1)),
                lifetime_range=(2.5, 5.0),
                wind=(0.20, 0.0),
            ),
            mood="frozen tundra",
        ),
        # F#m — Twilight rain
        "F#m": VisualEnvironment(
            bg_color_top=(0.20, 0.12, 0.30),
            bg_color_bottom=(0.30, 0.25, 0.40),
            effect_color=(0.55, 0.45, 0.70),
            enable_rain=True,
            enable_fog=True,
            particle_config=ParticleConfig(
                emit_rate=70.0,
                color=(0.50, 0.45, 0.65, 0.5),
                size_range=(1.0, 2.0),
                velocity_range=((-0.05, 0.05), (-1.8, -0.8)),
                lifetime_range=(0.3, 0.8),
                gravity=(0.0, -0.12),
            ),
            mood="twilight rain",
        ),
        # Gm — Storm clouds
        "Gm": VisualEnvironment(
            bg_color_top=(0.12, 0.10, 0.18),
            bg_color_bottom=(0.22, 0.18, 0.30),
            effect_color=(0.50, 0.40, 0.65),
            enable_rain=True,
            enable_god_rays=True,
            god_ray_position=(0.6, 0.65),
            particle_config=ParticleConfig(
                emit_rate=90.0,
                color=(0.45, 0.45, 0.55, 0.6),
                size_range=(1.0, 2.5),
                velocity_range=((-0.15, 0.15), (-2.5, -1.2)),
                lifetime_range=(0.2, 0.7),
                gravity=(0.0, -0.20),
            ),
            mood="storm clouds",
        ),
        # G#m — Deep cave
        "G#m": VisualEnvironment(
            bg_color_top=(0.03, 0.03, 0.05),
            bg_color_bottom=(0.06, 0.05, 0.08),
            effect_color=(0.30, 0.35, 0.50),
            enable_constellations=True,
            enable_fog=True,
            mood="deep cave",
        ),
        # Am — Cold rain
        "Am": VisualEnvironment(
            bg_color_top=(0.20, 0.25, 0.35),
            bg_color_bottom=(0.15, 0.20, 0.32),
            effect_color=(0.50, 0.58, 0.70),
            enable_rain=True,
            enable_fog=True,
            enable_waves=True,
            particle_config=ParticleConfig(
                emit_rate=65.0,
                color=(0.50, 0.55, 0.70, 0.5),
                size_range=(1.0, 2.0),
                velocity_range=((-0.08, 0.08), (-1.5, -0.8)),
                lifetime_range=(0.4, 1.0),
                gravity=(0.0, -0.10),
            ),
            mood="cold rain",
        ),
        # A#m — Winter night
        "A#m": VisualEnvironment(
            bg_color_top=(0.03, 0.05, 0.15),
            bg_color_bottom=(0.08, 0.10, 0.22),
            effect_color=(0.50, 0.60, 0.85),
            enable_snow=True,
            enable_stars=True,
            particle_config=ParticleConfig(
                emit_rate=40.0,
                color=(0.80, 0.85, 1.0, 0.6),
                size_range=(1.5, 4.0),
                velocity_range=((-0.15, 0.15), (-0.3, -0.05)),
                lifetime_range=(3.0, 7.0),
                wind=(0.05, 0.0),
            ),
            mood="winter night",
        ),
        # Bm — Shadow valley
        "Bm": VisualEnvironment(
            bg_color_top=(0.05, 0.05, 0.08),
            bg_color_bottom=(0.10, 0.10, 0.15),
            effect_color=(0.35, 0.35, 0.50),
            enable_mountains=True,
            enable_fog=True,
            enable_stars=True,
            mood="shadow valley",
        ),

        # =====================================================================
        # DOMINANT 7TH — Jazzy, warm, sunset tones
        # =====================================================================

        # C7 — Amber jazz lounge
        "C7": VisualEnvironment(
            bg_color_top=(0.65, 0.35, 0.10),
            bg_color_bottom=(0.50, 0.25, 0.08),
            effect_color=(1.0, 0.75, 0.30),
            enable_fire=True,
            enable_god_rays=True,
            enable_fog=True,
            god_ray_position=(0.35, 0.75),
            particle_config=ParticleConfig(
                emit_rate=25.0,
                color=(1.0, 0.70, 0.20, 0.7),
                size_range=(2.0, 4.0),
                velocity_range=((-0.1, 0.1), (0.1, 0.4)),
                lifetime_range=(1.0, 2.5),
            ),
            mood="amber jazz lounge",
        ),
        # C#7 — Copper sunset
        "C#7": VisualEnvironment(
            bg_color_top=(0.70, 0.40, 0.15),
            bg_color_bottom=(0.55, 0.28, 0.10),
            effect_color=(0.95, 0.70, 0.35),
            enable_god_rays=True,
            enable_fog=True,
            god_ray_position=(0.45, 0.82),
            mood="copper sunset",
        ),
        # D7 — Smoky bar
        "D7": VisualEnvironment(
            bg_color_top=(0.55, 0.30, 0.12),
            bg_color_bottom=(0.40, 0.22, 0.08),
            effect_color=(0.90, 0.65, 0.25),
            enable_fire=True,
            enable_fog=True,
            particle_config=ParticleConfig(
                emit_rate=20.0,
                color=(0.90, 0.60, 0.15, 0.6),
                size_range=(1.5, 3.5),
                velocity_range=((-0.2, 0.2), (0.1, 0.3)),
                lifetime_range=(1.5, 3.0),
            ),
            mood="smoky bar",
        ),
        # D#7 — Bronze dusk
        "D#7": VisualEnvironment(
            bg_color_top=(0.60, 0.38, 0.18),
            bg_color_bottom=(0.48, 0.30, 0.12),
            effect_color=(0.88, 0.68, 0.30),
            enable_god_rays=True,
            enable_fog=True,
            god_ray_position=(0.55, 0.78),
            mood="bronze dusk",
        ),
        # E7 — Bourbon glow
        "E7": VisualEnvironment(
            bg_color_top=(0.58, 0.32, 0.08),
            bg_color_bottom=(0.42, 0.20, 0.05),
            effect_color=(0.95, 0.72, 0.28),
            enable_fire=True,
            enable_god_rays=True,
            god_ray_position=(0.40, 0.80),
            particle_config=ParticleConfig(
                emit_rate=30.0,
                color=(0.95, 0.65, 0.15, 0.8),
                size_range=(2.0, 4.5),
                velocity_range=((-0.15, 0.15), (0.2, 0.6)),
                lifetime_range=(0.8, 2.0),
            ),
            mood="bourbon glow",
        ),
        # F7 — Tangerine haze
        "F7": VisualEnvironment(
            bg_color_top=(0.75, 0.42, 0.12),
            bg_color_bottom=(0.60, 0.32, 0.08),
            effect_color=(1.0, 0.78, 0.35),
            enable_fog=True,
            enable_god_rays=True,
            god_ray_position=(0.50, 0.85),
            mood="tangerine haze",
        ),
        # F#7 — Rust sunset
        "F#7": VisualEnvironment(
            bg_color_top=(0.62, 0.28, 0.10),
            bg_color_bottom=(0.45, 0.18, 0.06),
            effect_color=(0.88, 0.55, 0.20),
            enable_fire=True,
            enable_fog=True,
            enable_mountains=True,
            particle_config=ParticleConfig(
                emit_rate=22.0,
                color=(0.85, 0.50, 0.15, 0.7),
                size_range=(2.0, 4.0),
                velocity_range=((-0.1, 0.1), (0.15, 0.35)),
                lifetime_range=(1.0, 2.5),
            ),
            mood="rust sunset",
        ),
        # G7 — Honey twilight
        "G7": VisualEnvironment(
            bg_color_top=(0.68, 0.50, 0.15),
            bg_color_bottom=(0.52, 0.35, 0.10),
            effect_color=(0.95, 0.82, 0.40),
            enable_god_rays=True,
            enable_fireflies=True,
            god_ray_position=(0.65, 0.72),
            particle_config=ParticleConfig(
                emit_rate=18.0,
                color=(0.95, 0.80, 0.30, 0.6),
                size_range=(2.0, 3.5),
                velocity_range=((-0.1, 0.1), (-0.05, 0.15)),
                lifetime_range=(2.0, 4.0),
            ),
            mood="honey twilight",
        ),
        # G#7 — Sienna embers
        "G#7": VisualEnvironment(
            bg_color_top=(0.55, 0.25, 0.12),
            bg_color_bottom=(0.38, 0.15, 0.08),
            effect_color=(0.85, 0.50, 0.18),
            enable_fire=True,
            enable_fog=True,
            particle_config=ParticleConfig(
                emit_rate=35.0,
                color=(0.90, 0.45, 0.10, 0.8),
                size_range=(1.5, 3.0),
                velocity_range=((-0.2, 0.2), (0.2, 0.5)),
                lifetime_range=(0.6, 1.5),
            ),
            mood="sienna embers",
        ),
        # A7 — Ochre blaze
        "A7": VisualEnvironment(
            bg_color_top=(0.72, 0.45, 0.10),
            bg_color_bottom=(0.58, 0.30, 0.06),
            effect_color=(1.0, 0.80, 0.30),
            enable_fire=True,
            enable_god_rays=True,
            god_ray_position=(0.50, 0.70),
            particle_config=ParticleConfig(
                emit_rate=40.0,
                color=(1.0, 0.60, 0.12, 0.85),
                size_range=(2.0, 5.0),
                velocity_range=((-0.25, 0.25), (0.3, 0.8)),
                lifetime_range=(0.5, 1.8),
            ),
            mood="ochre blaze",
        ),
        # A#7 — Caramel dusk
        "A#7": VisualEnvironment(
            bg_color_top=(0.60, 0.42, 0.18),
            bg_color_bottom=(0.45, 0.30, 0.12),
            effect_color=(0.90, 0.72, 0.35),
            enable_fog=True,
            enable_god_rays=True,
            enable_mountains=True,
            god_ray_position=(0.70, 0.76),
            mood="caramel dusk",
        ),
        # B7 — Cinnamon flame
        "B7": VisualEnvironment(
            bg_color_top=(0.58, 0.28, 0.08),
            bg_color_bottom=(0.42, 0.18, 0.05),
            effect_color=(0.90, 0.55, 0.18),
            enable_fire=True,
            enable_fog=True,
            enable_god_rays=True,
            god_ray_position=(0.45, 0.68),
            particle_config=ParticleConfig(
                emit_rate=28.0,
                color=(0.88, 0.50, 0.12, 0.75),
                size_range=(2.0, 4.5),
                velocity_range=((-0.15, 0.15), (0.2, 0.5)),
                lifetime_range=(0.8, 2.2),
            ),
            mood="cinnamon flame",
        ),

        # =====================================================================
        # MINOR 7TH — Deep, contemplative
        # =====================================================================

        # Cm7 — Indigo depths
        "Cm7": VisualEnvironment(
            bg_color_top=(0.05, 0.05, 0.25),
            bg_color_bottom=(0.08, 0.08, 0.35),
            effect_color=(0.35, 0.40, 0.85),
            enable_waves=True,
            enable_stars=True,
            enable_aurora=True,
            mood="indigo depths",
        ),
        # C#m7 — Sapphire sea
        "C#m7": VisualEnvironment(
            bg_color_top=(0.03, 0.08, 0.28),
            bg_color_bottom=(0.05, 0.12, 0.38),
            effect_color=(0.25, 0.45, 0.80),
            enable_waves=True,
            enable_stars=True,
            mood="sapphire sea",
        ),
        # Dm7 — Cobalt night
        "Dm7": VisualEnvironment(
            bg_color_top=(0.06, 0.06, 0.22),
            bg_color_bottom=(0.10, 0.10, 0.32),
            effect_color=(0.40, 0.45, 0.78),
            enable_stars=True,
            enable_aurora=True,
            enable_waves=True,
            mood="cobalt night",
        ),
        # D#m7 — Violet abyss
        "D#m7": VisualEnvironment(
            bg_color_top=(0.10, 0.04, 0.22),
            bg_color_bottom=(0.15, 0.06, 0.30),
            effect_color=(0.50, 0.30, 0.75),
            enable_waves=True,
            enable_aurora=True,
            mood="violet abyss",
        ),
        # Em7 — Midnight blue
        "Em7": VisualEnvironment(
            bg_color_top=(0.02, 0.05, 0.18),
            bg_color_bottom=(0.04, 0.08, 0.28),
            effect_color=(0.20, 0.40, 0.70),
            enable_stars=True,
            enable_waves=True,
            enable_aurora=True,
            mood="midnight blue",
        ),
        # Fm7 — Frozen violet
        "Fm7": VisualEnvironment(
            bg_color_top=(0.12, 0.08, 0.25),
            bg_color_bottom=(0.18, 0.12, 0.35),
            effect_color=(0.45, 0.35, 0.72),
            enable_aurora=True,
            enable_stars=True,
            enable_snow=True,
            particle_config=ParticleConfig(
                emit_rate=20.0,
                color=(0.50, 0.40, 0.80, 0.4),
                size_range=(1.5, 3.0),
                velocity_range=((-0.1, 0.1), (-0.2, -0.05)),
                lifetime_range=(3.0, 6.0),
            ),
            mood="frozen violet",
        ),
        # F#m7 — Purple rain
        "F#m7": VisualEnvironment(
            bg_color_top=(0.15, 0.06, 0.25),
            bg_color_bottom=(0.22, 0.10, 0.35),
            effect_color=(0.55, 0.30, 0.80),
            enable_waves=True,
            enable_stars=True,
            enable_rain=True,
            particle_config=ParticleConfig(
                emit_rate=50.0,
                color=(0.50, 0.30, 0.75, 0.5),
                size_range=(1.0, 2.0),
                velocity_range=((-0.05, 0.05), (-1.5, -0.7)),
                lifetime_range=(0.3, 0.8),
                gravity=(0.0, -0.10),
            ),
            mood="purple rain",
        ),
        # Gm7 — Twilight ocean
        "Gm7": VisualEnvironment(
            bg_color_top=(0.08, 0.05, 0.20),
            bg_color_bottom=(0.12, 0.08, 0.30),
            effect_color=(0.40, 0.35, 0.70),
            enable_waves=True,
            enable_aurora=True,
            enable_stars=True,
            mood="twilight ocean",
        ),
        # G#m7 — Obsidian deep
        "G#m7": VisualEnvironment(
            bg_color_top=(0.03, 0.03, 0.12),
            bg_color_bottom=(0.06, 0.05, 0.18),
            effect_color=(0.25, 0.25, 0.55),
            enable_waves=True,
            enable_constellations=True,
            mood="obsidian deep",
        ),
        # Am7 — Rainy blue
        "Am7": VisualEnvironment(
            bg_color_top=(0.08, 0.12, 0.25),
            bg_color_bottom=(0.12, 0.18, 0.35),
            effect_color=(0.35, 0.50, 0.75),
            enable_stars=True,
            enable_waves=True,
            enable_rain=True,
            particle_config=ParticleConfig(
                emit_rate=40.0,
                color=(0.35, 0.45, 0.70, 0.4),
                size_range=(1.0, 2.0),
                velocity_range=((-0.05, 0.05), (-1.2, -0.5)),
                lifetime_range=(0.4, 1.0),
                gravity=(0.0, -0.08),
            ),
            mood="rainy blue",
        ),
        # A#m7 — Arctic aurora
        "A#m7": VisualEnvironment(
            bg_color_top=(0.02, 0.05, 0.18),
            bg_color_bottom=(0.05, 0.08, 0.25),
            effect_color=(0.20, 0.55, 0.70),
            enable_aurora=True,
            enable_stars=True,
            enable_snow=True,
            particle_config=ParticleConfig(
                emit_rate=25.0,
                color=(0.30, 0.55, 0.80, 0.5),
                size_range=(1.5, 3.5),
                velocity_range=((-0.1, 0.1), (-0.25, -0.05)),
                lifetime_range=(3.0, 6.0),
            ),
            mood="arctic aurora",
        ),
        # Bm7 — Navy contemplation
        "Bm7": VisualEnvironment(
            bg_color_top=(0.04, 0.04, 0.15),
            bg_color_bottom=(0.08, 0.07, 0.22),
            effect_color=(0.30, 0.30, 0.60),
            enable_stars=True,
            enable_waves=True,
            enable_aurora=True,
            mood="navy contemplation",
        ),

        # =====================================================================
        # MAJOR 7TH — Ethereal, dreamy
        # =====================================================================

        # Cmaj7 — Pastel dawn
        "Cmaj7": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.80, 0.70, 0.90),
            bg_color_bottom=(0.90, 0.80, 0.95),
            effect_color=(0.95, 0.85, 1.0),
            enable_aurora=True,
            enable_stars=True,
            enable_fireflies=True,
            particle_config=ParticleConfig(
                emit_rate=20.0,
                color=(0.90, 0.80, 1.0, 0.5),
                size_range=(2.0, 4.0),
                velocity_range=((-0.1, 0.1), (-0.05, 0.1)),
                lifetime_range=(3.0, 6.0),
            ),
            mood="pastel dawn",
        ),
        # C#maj7 — Lavender mist
        "C#maj7": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.72, 0.62, 0.88),
            bg_color_bottom=(0.82, 0.72, 0.92),
            effect_color=(0.88, 0.78, 0.98),
            enable_aurora=True,
            enable_fog=True,
            enable_fireflies=True,
            particle_config=ParticleConfig(
                emit_rate=15.0,
                color=(0.82, 0.72, 0.95, 0.4),
                size_range=(2.5, 5.0),
                velocity_range=((-0.08, 0.08), (-0.03, 0.08)),
                lifetime_range=(3.5, 7.0),
            ),
            mood="lavender mist",
        ),
        # Dmaj7 — Rose quartz
        "Dmaj7": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.88, 0.68, 0.75),
            bg_color_bottom=(0.92, 0.78, 0.82),
            effect_color=(1.0, 0.85, 0.88),
            enable_aurora=True,
            enable_stars=True,
            enable_fireflies=True,
            particle_config=ParticleConfig(
                emit_rate=22.0,
                color=(1.0, 0.78, 0.82, 0.5),
                size_range=(2.0, 4.5),
                velocity_range=((-0.12, 0.12), (-0.05, 0.1)),
                lifetime_range=(2.5, 5.5),
            ),
            mood="rose quartz",
        ),
        # D#maj7 — Peach sky
        "D#maj7": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.95, 0.75, 0.60),
            bg_color_bottom=(0.98, 0.82, 0.70),
            effect_color=(1.0, 0.90, 0.80),
            enable_aurora=True,
            enable_stars=True,
            mood="peach sky",
        ),
        # Emaj7 — Aquamarine dream
        "Emaj7": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.55, 0.82, 0.88),
            bg_color_bottom=(0.65, 0.88, 0.92),
            effect_color=(0.75, 0.95, 1.0),
            enable_aurora=True,
            enable_fireflies=True,
            enable_stars=True,
            particle_config=ParticleConfig(
                emit_rate=18.0,
                color=(0.65, 0.92, 0.98, 0.5),
                size_range=(2.0, 4.0),
                velocity_range=((-0.1, 0.1), (-0.03, 0.08)),
                lifetime_range=(3.0, 6.0),
            ),
            mood="aquamarine dream",
        ),
        # Fmaj7 — Orchid glow
        "Fmaj7": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.82, 0.55, 0.78),
            bg_color_bottom=(0.88, 0.65, 0.85),
            effect_color=(0.95, 0.75, 0.92),
            enable_aurora=True,
            enable_fireflies=True,
            particle_config=ParticleConfig(
                emit_rate=25.0,
                color=(0.90, 0.65, 0.85, 0.5),
                size_range=(2.0, 4.5),
                velocity_range=((-0.1, 0.1), (-0.04, 0.1)),
                lifetime_range=(2.5, 5.5),
            ),
            mood="orchid glow",
        ),
        # F#maj7 — Champagne mist
        "F#maj7": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.90, 0.82, 0.65),
            bg_color_bottom=(0.95, 0.88, 0.72),
            effect_color=(1.0, 0.95, 0.82),
            enable_aurora=True,
            enable_fog=True,
            enable_stars=True,
            mood="champagne mist",
        ),
        # Gmaj7 — Moonlit silk
        "Gmaj7": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.60, 0.62, 0.80),
            bg_color_bottom=(0.70, 0.72, 0.88),
            effect_color=(0.82, 0.85, 0.98),
            enable_aurora=True,
            enable_stars=True,
            enable_constellations=True,
            mood="moonlit silk",
        ),
        # G#maj7 — Opal shimmer
        "G#maj7": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.62, 0.78, 0.80),
            bg_color_bottom=(0.72, 0.85, 0.88),
            effect_color=(0.80, 0.95, 0.95),
            enable_aurora=True,
            enable_fireflies=True,
            enable_constellations=True,
            particle_config=ParticleConfig(
                emit_rate=16.0,
                color=(0.70, 0.92, 0.95, 0.45),
                size_range=(1.5, 3.5),
                velocity_range=((-0.08, 0.08), (-0.02, 0.08)),
                lifetime_range=(3.0, 6.0),
            ),
            mood="opal shimmer",
        ),
        # Amaj7 — Amber velvet
        "Amaj7": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.88, 0.70, 0.55),
            bg_color_bottom=(0.92, 0.78, 0.62),
            effect_color=(1.0, 0.88, 0.72),
            enable_aurora=True,
            enable_fireflies=True,
            enable_stars=True,
            particle_config=ParticleConfig(
                emit_rate=14.0,
                color=(1.0, 0.82, 0.60, 0.45),
                size_range=(2.0, 4.0),
                velocity_range=((-0.08, 0.08), (-0.03, 0.08)),
                lifetime_range=(3.0, 5.5),
            ),
            mood="amber velvet",
        ),
        # A#maj7 — Blush cloud
        "A#maj7": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.90, 0.72, 0.72),
            bg_color_bottom=(0.95, 0.80, 0.78),
            effect_color=(1.0, 0.88, 0.85),
            enable_aurora=True,
            enable_fog=True,
            enable_stars=True,
            mood="blush cloud",
        ),
        # Bmaj7 — Ice crystal
        "Bmaj7": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.72, 0.82, 0.92),
            bg_color_bottom=(0.80, 0.88, 0.95),
            effect_color=(0.90, 0.95, 1.0),
            enable_aurora=True,
            enable_stars=True,
            enable_constellations=True,
            mood="ice crystal",
        ),

        # =====================================================================
        # SUS2 — Open, airy, floating
        # =====================================================================

        # Csus2 — Cloud drift
        "Csus2": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.78, 0.85, 0.95),
            bg_color_bottom=(0.88, 0.92, 0.98),
            effect_color=(0.95, 0.97, 1.0),
            enable_fog=True,
            particle_config=ParticleConfig(
                emit_rate=12.0,
                color=(1.0, 1.0, 1.0, 0.3),
                size_range=(5.0, 12.0),
                velocity_range=((-0.05, 0.15), (-0.02, 0.02)),
                lifetime_range=(5.0, 10.0),
                wind=(0.05, 0.0),
            ),
            mood="cloud drift",
        ),
        # C#sus2 — Morning haze
        "C#sus2": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.82, 0.80, 0.90),
            bg_color_bottom=(0.90, 0.88, 0.95),
            effect_color=(0.95, 0.92, 0.98),
            enable_fog=True,
            particle_config=ParticleConfig(
                emit_rate=10.0,
                color=(0.92, 0.88, 0.95, 0.3),
                size_range=(6.0, 14.0),
                velocity_range=((-0.08, 0.12), (-0.01, 0.01)),
                lifetime_range=(6.0, 12.0),
                wind=(0.03, 0.0),
            ),
            mood="morning haze",
        ),
        # Dsus2 — Open sky
        "Dsus2": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.60, 0.80, 0.95),
            bg_color_bottom=(0.75, 0.88, 0.98),
            effect_color=(0.85, 0.92, 1.0),
            enable_fog=True,
            enable_god_rays=True,
            god_ray_position=(0.50, 0.92),
            mood="open sky",
        ),
        # D#sus2 — Soft breeze
        "D#sus2": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.72, 0.85, 0.82),
            bg_color_bottom=(0.82, 0.90, 0.88),
            effect_color=(0.88, 0.95, 0.92),
            enable_fog=True,
            enable_leaves=True,
            particle_config=ParticleConfig(
                emit_rate=8.0,
                color=(0.85, 0.95, 0.88, 0.3),
                size_range=(3.0, 7.0),
                velocity_range=((-0.02, 0.15), (-0.05, 0.05)),
                lifetime_range=(4.0, 8.0),
                wind=(0.10, 0.0),
            ),
            mood="soft breeze",
        ),
        # Esus2 — Skylight
        "Esus2": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.55, 0.75, 1.0),
            bg_color_bottom=(0.70, 0.85, 1.0),
            effect_color=(0.82, 0.92, 1.0),
            enable_fog=True,
            enable_god_rays=True,
            god_ray_position=(0.50, 0.95),
            mood="skylight",
        ),
        # Fsus2 — Cotton clouds
        "Fsus2": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.85, 0.78, 0.90),
            bg_color_bottom=(0.92, 0.85, 0.95),
            effect_color=(0.95, 0.90, 0.98),
            enable_fog=True,
            particle_config=ParticleConfig(
                emit_rate=10.0,
                color=(0.95, 0.88, 0.95, 0.25),
                size_range=(6.0, 15.0),
                velocity_range=((-0.03, 0.10), (-0.01, 0.01)),
                lifetime_range=(5.0, 10.0),
                wind=(0.04, 0.0),
            ),
            mood="cotton clouds",
        ),
        # F#sus2 — Desert wind
        "F#sus2": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.90, 0.82, 0.68),
            bg_color_bottom=(0.95, 0.88, 0.75),
            effect_color=(1.0, 0.95, 0.82),
            enable_fog=True,
            enable_god_rays=True,
            god_ray_position=(0.55, 0.88),
            mood="desert wind",
        ),
        # Gsus2 — Floating stars
        "Gsus2": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.42, 0.48, 0.72),
            bg_color_bottom=(0.55, 0.60, 0.80),
            effect_color=(0.72, 0.78, 0.95),
            enable_fog=True,
            enable_stars=True,
            mood="floating stars",
        ),
        # G#sus2 — Misty teal
        "G#sus2": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.60, 0.82, 0.82),
            bg_color_bottom=(0.72, 0.88, 0.88),
            effect_color=(0.80, 0.95, 0.95),
            enable_fog=True,
            particle_config=ParticleConfig(
                emit_rate=8.0,
                color=(0.70, 0.92, 0.90, 0.25),
                size_range=(5.0, 12.0),
                velocity_range=((-0.05, 0.10), (-0.02, 0.02)),
                lifetime_range=(5.0, 10.0),
            ),
            mood="misty teal",
        ),
        # Asus2 — Warm drift
        "Asus2": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.88, 0.78, 0.65),
            bg_color_bottom=(0.92, 0.85, 0.72),
            effect_color=(0.98, 0.92, 0.80),
            enable_fog=True,
            enable_god_rays=True,
            god_ray_position=(0.45, 0.85),
            mood="warm drift",
        ),
        # A#sus2 — Pale amber
        "A#sus2": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.85, 0.75, 0.62),
            bg_color_bottom=(0.90, 0.82, 0.70),
            effect_color=(0.95, 0.88, 0.78),
            enable_fog=True,
            enable_leaves=True,
            particle_config=ParticleConfig(
                emit_rate=6.0,
                color=(0.90, 0.80, 0.60, 0.25),
                size_range=(3.0, 7.0),
                velocity_range=((-0.02, 0.12), (-0.05, 0.03)),
                lifetime_range=(4.0, 9.0),
                wind=(0.08, 0.0),
            ),
            mood="pale amber",
        ),
        # Bsus2 — Arctic light
        "Bsus2": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.75, 0.85, 0.95),
            bg_color_bottom=(0.85, 0.90, 0.98),
            effect_color=(0.92, 0.95, 1.0),
            enable_fog=True,
            enable_god_rays=True,
            god_ray_position=(0.50, 0.90),
            mood="arctic light",
        ),

        # =====================================================================
        # SUS4 — Tense, anticipating
        # =====================================================================

        # Csus4 — Gathering storm
        "Csus4": VisualEnvironment(
            bg_color_top=(0.25, 0.25, 0.35),
            bg_color_bottom=(0.35, 0.32, 0.42),
            effect_color=(0.60, 0.58, 0.70),
            enable_leaves=True,
            enable_fog=True,
            particle_config=ParticleConfig(
                emit_rate=35.0,
                color=(0.50, 0.48, 0.55, 0.6),
                size_range=(3.0, 6.0),
                velocity_range=((-0.8, 0.8), (-0.4, 0.2)),
                lifetime_range=(1.0, 3.0),
                wind=(0.30, 0.0),
            ),
            mood="gathering storm",
        ),
        # C#sus4 — Thunder approach
        "C#sus4": VisualEnvironment(
            bg_color_top=(0.22, 0.20, 0.32),
            bg_color_bottom=(0.32, 0.28, 0.40),
            effect_color=(0.55, 0.52, 0.68),
            enable_leaves=True,
            enable_god_rays=True,
            god_ray_position=(0.40, 0.60),
            particle_config=ParticleConfig(
                emit_rate=40.0,
                color=(0.48, 0.45, 0.55, 0.65),
                size_range=(2.5, 5.5),
                velocity_range=((-0.9, 0.9), (-0.5, 0.1)),
                lifetime_range=(0.8, 2.5),
                wind=(0.35, 0.0),
            ),
            mood="thunder approach",
        ),
        # Dsus4 — Rising wind
        "Dsus4": VisualEnvironment(
            bg_color_top=(0.30, 0.35, 0.38),
            bg_color_bottom=(0.40, 0.42, 0.45),
            effect_color=(0.65, 0.68, 0.72),
            enable_leaves=True,
            enable_fog=True,
            particle_config=ParticleConfig(
                emit_rate=50.0,
                color=(0.55, 0.58, 0.52, 0.7),
                size_range=(2.0, 5.0),
                velocity_range=((-1.0, 1.0), (-0.3, 0.3)),
                lifetime_range=(0.5, 2.0),
                wind=(0.40, 0.05),
            ),
            mood="rising wind",
        ),
        # D#sus4 — Electric tension
        "D#sus4": VisualEnvironment(
            bg_color_top=(0.28, 0.22, 0.38),
            bg_color_bottom=(0.38, 0.30, 0.48),
            effect_color=(0.62, 0.50, 0.78),
            enable_leaves=True,
            enable_god_rays=True,
            god_ray_position=(0.55, 0.55),
            particle_config=ParticleConfig(
                emit_rate=45.0,
                color=(0.55, 0.42, 0.68, 0.7),
                size_range=(2.0, 4.5),
                velocity_range=((-0.7, 0.7), (-0.4, 0.2)),
                lifetime_range=(0.6, 2.0),
                wind=(0.25, 0.0),
            ),
            mood="electric tension",
        ),
        # Esus4 — Pressure build
        "Esus4": VisualEnvironment(
            bg_color_top=(0.25, 0.30, 0.40),
            bg_color_bottom=(0.35, 0.38, 0.50),
            effect_color=(0.55, 0.62, 0.78),
            enable_leaves=True,
            enable_fog=True,
            enable_rain=True,
            particle_config=ParticleConfig(
                emit_rate=55.0,
                color=(0.50, 0.55, 0.65, 0.6),
                size_range=(2.0, 4.0),
                velocity_range=((-0.6, 0.6), (-1.0, -0.3)),
                lifetime_range=(0.4, 1.5),
                wind=(0.20, 0.0),
                gravity=(0.0, -0.08),
            ),
            mood="pressure build",
        ),
        # Fsus4 — Swirling petals
        "Fsus4": VisualEnvironment(
            bg_color_top=(0.42, 0.30, 0.42),
            bg_color_bottom=(0.52, 0.38, 0.52),
            effect_color=(0.72, 0.55, 0.72),
            enable_leaves=True,
            particle_config=ParticleConfig(
                emit_rate=45.0,
                color=(0.70, 0.45, 0.65, 0.7),
                size_range=(3.0, 6.0),
                velocity_range=((-0.8, 0.8), (-0.5, 0.2)),
                lifetime_range=(1.0, 3.0),
                wind=(0.30, 0.05),
            ),
            mood="swirling petals",
        ),
        # F#sus4 — Dust devil
        "F#sus4": VisualEnvironment(
            bg_color_top=(0.45, 0.38, 0.28),
            bg_color_bottom=(0.55, 0.45, 0.32),
            effect_color=(0.75, 0.65, 0.48),
            enable_leaves=True,
            enable_fog=True,
            particle_config=ParticleConfig(
                emit_rate=60.0,
                color=(0.65, 0.55, 0.38, 0.7),
                size_range=(2.0, 5.0),
                velocity_range=((-1.2, 1.2), (-0.3, 0.5)),
                lifetime_range=(0.5, 2.0),
                wind=(0.45, 0.0),
            ),
            mood="dust devil",
        ),
        # Gsus4 — Dark gusts
        "Gsus4": VisualEnvironment(
            bg_color_top=(0.18, 0.18, 0.28),
            bg_color_bottom=(0.28, 0.25, 0.38),
            effect_color=(0.48, 0.45, 0.62),
            enable_leaves=True,
            enable_fog=True,
            enable_mountains=True,
            particle_config=ParticleConfig(
                emit_rate=55.0,
                color=(0.42, 0.40, 0.50, 0.65),
                size_range=(2.5, 5.5),
                velocity_range=((-0.9, 0.9), (-0.4, 0.2)),
                lifetime_range=(0.6, 2.0),
                wind=(0.35, 0.0),
            ),
            mood="dark gusts",
        ),
        # G#sus4 — Brooding sky
        "G#sus4": VisualEnvironment(
            bg_color_top=(0.15, 0.20, 0.28),
            bg_color_bottom=(0.22, 0.28, 0.38),
            effect_color=(0.40, 0.50, 0.62),
            enable_leaves=True,
            enable_fog=True,
            particle_config=ParticleConfig(
                emit_rate=38.0,
                color=(0.38, 0.48, 0.55, 0.6),
                size_range=(3.0, 6.0),
                velocity_range=((-0.7, 0.7), (-0.3, 0.15)),
                lifetime_range=(1.0, 2.5),
                wind=(0.22, 0.0),
            ),
            mood="brooding sky",
        ),
        # Asus4 — Autumn gale
        "Asus4": VisualEnvironment(
            bg_color_top=(0.38, 0.28, 0.20),
            bg_color_bottom=(0.48, 0.35, 0.25),
            effect_color=(0.68, 0.55, 0.40),
            enable_leaves=True,
            enable_fog=True,
            particle_config=ParticleConfig(
                emit_rate=50.0,
                color=(0.72, 0.50, 0.25, 0.7),
                size_range=(3.0, 7.0),
                velocity_range=((-0.8, 0.8), (-0.5, 0.1)),
                lifetime_range=(1.0, 3.0),
                wind=(0.30, 0.0),
            ),
            mood="autumn gale",
        ),
        # A#sus4 — Heavy clouds
        "A#sus4": VisualEnvironment(
            bg_color_top=(0.28, 0.25, 0.30),
            bg_color_bottom=(0.38, 0.32, 0.38),
            effect_color=(0.58, 0.52, 0.58),
            enable_leaves=True,
            enable_fog=True,
            enable_god_rays=True,
            god_ray_position=(0.50, 0.55),
            particle_config=ParticleConfig(
                emit_rate=42.0,
                color=(0.52, 0.48, 0.52, 0.6),
                size_range=(2.5, 5.0),
                velocity_range=((-0.6, 0.6), (-0.3, 0.15)),
                lifetime_range=(1.0, 2.5),
                wind=(0.25, 0.0),
            ),
            mood="heavy clouds",
        ),
        # Bsus4 — Blizzard approach
        "Bsus4": VisualEnvironment(
            bg_color_top=(0.35, 0.38, 0.45),
            bg_color_bottom=(0.45, 0.48, 0.55),
            effect_color=(0.65, 0.68, 0.78),
            enable_leaves=True,
            enable_snow=True,
            enable_fog=True,
            particle_config=ParticleConfig(
                emit_rate=65.0,
                color=(0.80, 0.82, 0.90, 0.7),
                size_range=(2.0, 5.0),
                velocity_range=((-1.0, 1.0), (-0.5, 0.1)),
                lifetime_range=(0.5, 2.0),
                wind=(0.40, 0.0),
            ),
            mood="blizzard approach",
        ),

        # =====================================================================
        # DIMINISHED — Eerie, mysterious
        # =====================================================================

        # Cdim — Void whisper
        "Cdim": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.03, 0.03, 0.08),
            bg_color_bottom=(0.06, 0.05, 0.12),
            effect_color=(0.25, 0.20, 0.40),
            enable_fog=True,
            enable_constellations=True,
            mood="void whisper",
        ),
        # C#dim — Abyss echo
        "C#dim": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.04, 0.02, 0.08),
            bg_color_bottom=(0.07, 0.04, 0.12),
            effect_color=(0.28, 0.18, 0.42),
            enable_fog=True,
            enable_constellations=True,
            mood="abyss echo",
        ),
        # Ddim — Phantom fog
        "Ddim": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.05, 0.05, 0.06),
            bg_color_bottom=(0.08, 0.08, 0.10),
            effect_color=(0.22, 0.22, 0.30),
            enable_fog=True,
            enable_constellations=True,
            mood="phantom fog",
        ),
        # D#dim — Shadow pulse
        "D#dim": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.06, 0.03, 0.10),
            bg_color_bottom=(0.10, 0.05, 0.15),
            effect_color=(0.30, 0.18, 0.45),
            enable_fog=True,
            enable_constellations=True,
            enable_god_rays=True,
            god_ray_position=(0.50, 0.50),
            mood="shadow pulse",
        ),
        # Edim — Crypt silence
        "Edim": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.02, 0.04, 0.06),
            bg_color_bottom=(0.05, 0.07, 0.10),
            effect_color=(0.15, 0.25, 0.35),
            enable_fog=True,
            enable_constellations=True,
            mood="crypt silence",
        ),
        # Fdim — Wraith mist
        "Fdim": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.05, 0.03, 0.08),
            bg_color_bottom=(0.08, 0.05, 0.12),
            effect_color=(0.28, 0.20, 0.38),
            enable_fog=True,
            enable_constellations=True,
            particle_config=ParticleConfig(
                emit_rate=8.0,
                color=(0.25, 0.18, 0.35, 0.2),
                size_range=(4.0, 10.0),
                velocity_range=((-0.05, 0.05), (0.01, 0.05)),
                lifetime_range=(4.0, 8.0),
            ),
            mood="wraith mist",
        ),
        # F#dim — Dark matter
        "F#dim": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.02, 0.02, 0.05),
            bg_color_bottom=(0.04, 0.04, 0.08),
            effect_color=(0.18, 0.18, 0.30),
            enable_fog=True,
            enable_constellations=True,
            mood="dark matter",
        ),
        # Gdim — Hollow echo
        "Gdim": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.04, 0.04, 0.10),
            bg_color_bottom=(0.07, 0.06, 0.15),
            effect_color=(0.22, 0.22, 0.42),
            enable_fog=True,
            enable_constellations=True,
            mood="hollow echo",
        ),
        # G#dim — Frozen void
        "G#dim": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.03, 0.05, 0.08),
            bg_color_bottom=(0.05, 0.08, 0.12),
            effect_color=(0.18, 0.28, 0.38),
            enable_fog=True,
            enable_constellations=True,
            enable_snow=True,
            particle_config=ParticleConfig(
                emit_rate=10.0,
                color=(0.20, 0.28, 0.40, 0.25),
                size_range=(1.0, 3.0),
                velocity_range=((-0.05, 0.05), (-0.1, -0.02)),
                lifetime_range=(4.0, 8.0),
            ),
            mood="frozen void",
        ),
        # Adim — Spectral chill
        "Adim": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.04, 0.03, 0.07),
            bg_color_bottom=(0.07, 0.05, 0.10),
            effect_color=(0.25, 0.20, 0.35),
            enable_fog=True,
            enable_constellations=True,
            mood="spectral chill",
        ),
        # A#dim — Obsidian mist
        "A#dim": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.03, 0.03, 0.06),
            bg_color_bottom=(0.05, 0.05, 0.09),
            effect_color=(0.20, 0.20, 0.32),
            enable_fog=True,
            enable_constellations=True,
            particle_config=ParticleConfig(
                emit_rate=6.0,
                color=(0.18, 0.18, 0.30, 0.2),
                size_range=(3.0, 8.0),
                velocity_range=((-0.03, 0.03), (0.01, 0.04)),
                lifetime_range=(5.0, 10.0),
            ),
            mood="obsidian mist",
        ),
        # Bdim — Grave silence
        "Bdim": VisualEnvironment(
            enable_fractal=True,
            bg_color_top=(0.03, 0.04, 0.06),
            bg_color_bottom=(0.05, 0.06, 0.10),
            effect_color=(0.18, 0.22, 0.32),
            enable_fog=True,
            enable_constellations=True,
            mood="grave silence",
        ),

        # =====================================================================
        # AUGMENTED — Surreal, sparkling
        # =====================================================================

        # Caug — Prism burst
        "Caug": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.40, 0.20, 0.60),
            bg_color_bottom=(0.55, 0.30, 0.75),
            effect_color=(0.80, 0.50, 1.0),
            enable_aurora=True,
            enable_fireflies=True,
            enable_constellations=True,
            particle_config=ParticleConfig(
                emit_rate=35.0,
                color=(0.75, 0.45, 1.0, 0.6),
                size_range=(2.0, 5.0),
                velocity_range=((-0.3, 0.3), (-0.1, 0.3)),
                lifetime_range=(1.5, 4.0),
            ),
            mood="prism burst",
        ),
        # C#aug — Neon nebula
        "C#aug": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.45, 0.15, 0.55),
            bg_color_bottom=(0.60, 0.25, 0.70),
            effect_color=(0.85, 0.45, 0.95),
            enable_aurora=True,
            enable_constellations=True,
            enable_fireflies=True,
            particle_config=ParticleConfig(
                emit_rate=30.0,
                color=(0.80, 0.40, 0.92, 0.55),
                size_range=(2.0, 4.5),
                velocity_range=((-0.2, 0.2), (-0.08, 0.2)),
                lifetime_range=(2.0, 4.5),
            ),
            mood="neon nebula",
        ),
        # Daug — Electric lime
        "Daug": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.30, 0.55, 0.15),
            bg_color_bottom=(0.45, 0.70, 0.25),
            effect_color=(0.60, 0.95, 0.40),
            enable_aurora=True,
            enable_fireflies=True,
            enable_constellations=True,
            particle_config=ParticleConfig(
                emit_rate=40.0,
                color=(0.55, 0.92, 0.35, 0.65),
                size_range=(1.5, 4.0),
                velocity_range=((-0.25, 0.25), (-0.1, 0.25)),
                lifetime_range=(1.5, 3.5),
            ),
            mood="electric lime",
        ),
        # D#aug — Magenta flash
        "D#aug": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.55, 0.12, 0.40),
            bg_color_bottom=(0.70, 0.20, 0.55),
            effect_color=(0.95, 0.35, 0.75),
            enable_aurora=True,
            enable_fireflies=True,
            enable_constellations=True,
            particle_config=ParticleConfig(
                emit_rate=38.0,
                color=(0.90, 0.30, 0.70, 0.6),
                size_range=(2.0, 4.5),
                velocity_range=((-0.3, 0.3), (-0.1, 0.3)),
                lifetime_range=(1.0, 3.0),
            ),
            mood="magenta flash",
        ),
        # Eaug — Teal surge
        "Eaug": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.10, 0.45, 0.50),
            bg_color_bottom=(0.18, 0.60, 0.65),
            effect_color=(0.30, 0.90, 0.95),
            enable_aurora=True,
            enable_fireflies=True,
            enable_constellations=True,
            particle_config=ParticleConfig(
                emit_rate=32.0,
                color=(0.25, 0.85, 0.90, 0.55),
                size_range=(2.0, 4.0),
                velocity_range=((-0.2, 0.2), (-0.08, 0.2)),
                lifetime_range=(2.0, 4.0),
            ),
            mood="teal surge",
        ),
        # Faug — Violet spark
        "Faug": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.35, 0.15, 0.55),
            bg_color_bottom=(0.50, 0.25, 0.70),
            effect_color=(0.72, 0.40, 0.95),
            enable_aurora=True,
            enable_fireflies=True,
            enable_constellations=True,
            particle_config=ParticleConfig(
                emit_rate=35.0,
                color=(0.68, 0.35, 0.90, 0.6),
                size_range=(1.5, 4.0),
                velocity_range=((-0.25, 0.25), (-0.1, 0.25)),
                lifetime_range=(1.5, 3.5),
            ),
            mood="violet spark",
        ),
        # F#aug — Gold plasma
        "F#aug": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.55, 0.42, 0.10),
            bg_color_bottom=(0.70, 0.55, 0.18),
            effect_color=(0.95, 0.82, 0.30),
            enable_aurora=True,
            enable_fireflies=True,
            enable_constellations=True,
            particle_config=ParticleConfig(
                emit_rate=30.0,
                color=(0.92, 0.78, 0.25, 0.6),
                size_range=(2.0, 4.5),
                velocity_range=((-0.2, 0.2), (-0.08, 0.2)),
                lifetime_range=(1.5, 3.5),
            ),
            mood="gold plasma",
        ),
        # Gaug — Cosmic jade
        "Gaug": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.08, 0.35, 0.28),
            bg_color_bottom=(0.15, 0.50, 0.40),
            effect_color=(0.25, 0.85, 0.68),
            enable_aurora=True,
            enable_fireflies=True,
            enable_constellations=True,
            particle_config=ParticleConfig(
                emit_rate=28.0,
                color=(0.22, 0.80, 0.62, 0.55),
                size_range=(2.0, 4.0),
                velocity_range=((-0.18, 0.18), (-0.05, 0.18)),
                lifetime_range=(2.0, 4.5),
            ),
            mood="cosmic jade",
        ),
        # G#aug — Sapphire fire
        "G#aug": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.10, 0.15, 0.55),
            bg_color_bottom=(0.18, 0.25, 0.72),
            effect_color=(0.30, 0.45, 0.98),
            enable_aurora=True,
            enable_fireflies=True,
            enable_constellations=True,
            particle_config=ParticleConfig(
                emit_rate=33.0,
                color=(0.28, 0.42, 0.95, 0.6),
                size_range=(1.5, 4.0),
                velocity_range=((-0.25, 0.25), (-0.1, 0.25)),
                lifetime_range=(1.5, 3.5),
            ),
            mood="sapphire fire",
        ),
        # Aaug — Ruby pulse
        "Aaug": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.50, 0.08, 0.15),
            bg_color_bottom=(0.65, 0.15, 0.22),
            effect_color=(0.95, 0.25, 0.35),
            enable_aurora=True,
            enable_fireflies=True,
            enable_constellations=True,
            particle_config=ParticleConfig(
                emit_rate=36.0,
                color=(0.90, 0.20, 0.30, 0.6),
                size_range=(2.0, 4.5),
                velocity_range=((-0.25, 0.25), (-0.1, 0.25)),
                lifetime_range=(1.5, 3.5),
            ),
            mood="ruby pulse",
        ),
        # A#aug — Amber lightning
        "A#aug": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.50, 0.35, 0.08),
            bg_color_bottom=(0.65, 0.48, 0.12),
            effect_color=(0.92, 0.72, 0.20),
            enable_aurora=True,
            enable_fireflies=True,
            enable_constellations=True,
            enable_god_rays=True,
            god_ray_position=(0.50, 0.60),
            particle_config=ParticleConfig(
                emit_rate=40.0,
                color=(0.88, 0.68, 0.18, 0.65),
                size_range=(1.5, 4.0),
                velocity_range=((-0.3, 0.3), (-0.1, 0.3)),
                lifetime_range=(1.0, 3.0),
            ),
            mood="amber lightning",
        ),
        # Baug — Frost nova
        "Baug": VisualEnvironment(
            enable_nebula=True,
            bg_color_top=(0.25, 0.38, 0.55),
            bg_color_bottom=(0.35, 0.50, 0.70),
            effect_color=(0.55, 0.78, 0.98),
            enable_aurora=True,
            enable_fireflies=True,
            enable_constellations=True,
            particle_config=ParticleConfig(
                emit_rate=34.0,
                color=(0.50, 0.72, 0.95, 0.6),
                size_range=(2.0, 4.5),
                velocity_range=((-0.25, 0.25), (-0.1, 0.25)),
                lifetime_range=(1.5, 4.0),
            ),
            mood="frost nova",
        ),
    }

    # Default scene for silence / unrecognised chords.
    _default_scene: ClassVar[VisualEnvironment] = VisualEnvironment(
        bg_color_top=(0.02, 0.02, 0.05),
        bg_color_bottom=(0.05, 0.05, 0.10),
        effect_color=(0.30, 0.30, 0.45),
        enable_stars=True,
        mood="calm silence",
    )

    def get_scene(self, chord_name: str) -> VisualEnvironment:
        """Return the ``VisualEnvironment`` mapped to *chord_name*.

        Falls back to :meth:`get_default_scene` when the chord is not found.

        Args:
            chord_name: Chord identifier, e.g. ``"Am"``, ``"C#maj7"``.

        Returns:
            The matching :class:`VisualEnvironment`.
        """
        if chord_name == "—" or chord_name == "":
            return self.get_default_scene()
            
        scene = self._scenes.get(chord_name)
        if scene is None:
            logger.warning("Unknown chord '%s' — returning default scene.", chord_name)
            return self.get_default_scene()
        return scene

    def get_default_scene(self) -> VisualEnvironment:
        """Return the calm default scene used for silence or unknown chords.

        Returns:
            A minimal :class:`VisualEnvironment` with a dark sky and stars.
        """
        return self._default_scene

    @classmethod
    def available_chords(cls) -> list[str]:
        """Return all chord names registered in the library.

        Returns:
            Sorted list of chord name strings.
        """
        return sorted(cls._scenes.keys())

    @classmethod
    def count(cls) -> int:
        """Return the total number of registered chord scenes.

        Returns:
            Number of scenes in the library.
        """
        return len(cls._scenes)
