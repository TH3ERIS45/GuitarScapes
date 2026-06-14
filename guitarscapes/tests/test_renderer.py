"""Tests for visual renderer components (non-GPU tests)."""

from __future__ import annotations

import numpy as np
import pytest

from guitarscapes.visuals.environment import VisualEnvironment, ParticleConfig
from guitarscapes.visuals.transitions import TransitionManager
from guitarscapes.visuals.particles import ParticleSystem


class TestVisualEnvironment:
    """Test VisualEnvironment data structure."""

    def test_default_values(self):
        """Default environment should have all effects disabled."""
        env = VisualEnvironment()
        assert not env.enable_stars
        assert not env.enable_rain
        assert not env.enable_fire
        assert env.particle_config is None

    def test_custom_environment(self):
        """Should create environment with specific effects."""
        env = VisualEnvironment(
            bg_color_top=(0.8, 0.5, 0.2),
            enable_stars=True,
            enable_fog=True,
            mood="golden dawn",
        )
        assert env.enable_stars
        assert env.enable_fog
        assert env.mood == "golden dawn"


class TestParticleSystem:
    """Test particle system without GPU."""

    @pytest.fixture
    def particles(self) -> ParticleSystem:
        return ParticleSystem(max_particles=100)

    def test_initial_state(self, particles):
        """Fresh particle system should have no alive particles."""
        assert particles.alive_count == 0

    def test_emit_particles(self, particles):
        """Emitting should create alive particles."""
        emitted = particles.emit(10, position=(0.0, 0.0))
        assert emitted == 10
        assert particles.alive_count == 10

    def test_emit_respects_capacity(self, particles):
        """Cannot emit more than max_particles."""
        emitted = particles.emit(200, position=(0.0, 0.0))
        assert emitted == 100  # max_particles
        assert particles.alive_count == 100

    def test_update_decreases_lifetime(self, particles):
        """Update should decrease particle lifetime."""
        particles.emit(5, position=(0.0, 0.0), lifetime_range=(1.0, 1.0))
        initial_alive = particles.alive_count

        # Update by 0.5 seconds
        particles.update(0.5)
        assert particles.alive_count == initial_alive  # Still alive

        # Update by another 0.6 seconds (total > 1.0)
        particles.update(0.6)
        assert particles.alive_count == 0  # All expired

    def test_get_live_data_shape(self, particles):
        """Live data should have correct shapes."""
        particles.emit(5, position=(0.0, 0.0))
        positions, colors, sizes = particles.get_live_data()

        assert positions.shape == (5, 2)
        assert colors.shape == (5, 4)
        assert sizes.shape == (5,)

    def test_clear(self, particles):
        """Clear should kill all particles."""
        particles.emit(50, position=(0.0, 0.0))
        particles.clear()
        assert particles.alive_count == 0

    def test_alpha_fading(self, particles):
        """Alpha should decrease as lifetime decreases."""
        particles.emit(
            1,
            position=(0.0, 0.0),
            color=(1.0, 1.0, 1.0, 1.0),
            lifetime_range=(2.0, 2.0),
        )

        # At half lifetime
        particles.update(1.0)
        _, colors, _ = particles.get_live_data()
        if len(colors) > 0:
            assert colors[0, 3] < 1.0  # Alpha should have faded


class TestTransitionManager:
    """Test transition state machine."""

    @pytest.fixture
    def tm(self) -> TransitionManager:
        return TransitionManager(default_duration=1.0)

    def test_initial_state_not_transitioning(self, tm):
        """Initially should not be transitioning."""
        assert not tm.is_transitioning
        assert tm.progress == 1.0

    def test_start_transition(self, tm):
        """Starting transition should set transitioning state."""
        target = VisualEnvironment(mood="rain")
        tm.start_transition(target)

        assert tm.is_transitioning
        assert tm.progress == 0.0

    def test_transition_completes(self, tm):
        """Transition should complete after duration."""
        target = VisualEnvironment(mood="rain")
        tm.start_transition(target, duration=1.0)

        # Step through
        for _ in range(20):
            tm.update(0.1)

        assert not tm.is_transitioning
        assert tm.progress == 1.0
        assert tm.current_environment.mood == "rain"

    def test_smoothstep_interpolation(self, tm):
        """Progress should follow smoothstep curve."""
        target = VisualEnvironment(mood="test")
        tm.start_transition(target, duration=1.0)

        # At halfway, smoothstep of 0.5 = 0.5
        tm.update(0.5)
        assert abs(tm.progress - 0.5) < 0.01

    def test_set_immediate(self, tm):
        """set_immediate should skip transition."""
        env = VisualEnvironment(mood="instant")
        tm.set_immediate(env)

        assert not tm.is_transitioning
        assert tm.progress == 1.0
        assert tm.current_environment.mood == "instant"

    def test_reset(self, tm):
        """Reset should return to default state."""
        target = VisualEnvironment(mood="rain")
        tm.start_transition(target)
        tm.update(0.5)

        tm.reset()

        assert not tm.is_transitioning
        assert tm.progress == 1.0
