"""Main OpenGL renderer using pygame-ce and ModernGL.

Runs in the main thread (required by macOS for OpenGL/pygame). Reads chord
data from a queue, manages scene transitions, particles, and HUD overlay.
"""

from __future__ import annotations

import time
from typing import Optional, Tuple

import numpy as np

from guitarscapes.utils.config import VisualConfig
from guitarscapes.utils.logger import get_logger
from guitarscapes.utils.threading_utils import SafeQueue
from guitarscapes.visuals.environment import VisualEnvironment
from guitarscapes.visuals.particles import ParticleSystem
from guitarscapes.visuals.transitions import TransitionManager

logger = get_logger("visuals.renderer")


class Renderer:
    """OpenGL renderer using pygame-ce + ModernGL.

    Must run in the **main thread** (macOS requirement for OpenGL).
    Call ``run_main_thread()`` to enter the render loop.
    """

    def __init__(
        self,
        config: VisualConfig,
        chord_queue: SafeQueue,
        command_queue: SafeQueue,
    ) -> None:
        self.config = config
        self.chord_queue = chord_queue
        self.command_queue = command_queue

        # State
        self.device_name: str = "Unknown"
        self.ai_active: bool = False
        self._running: bool = False
        self._frozen: bool = False
        self._fullscreen: bool = config.fullscreen
        self._current_chord: str = "—"
        self._current_confidence: float = 0.0
        self._current_rms: float = 0.0
        self._start_time: float = 0.0
        self._show_welcome: bool = True
        self._welcome_timer: float = 5.0

        # Will be initialized in run_main_thread
        self._ctx = None
        self._scene_program = None
        self._particle_program = None
        self._transition_program = None
        self._hud_program = None
        self._quad_vao = None
        self._particle_vbo = None
        self._particle_vao = None
        self._fbo_a = None
        self._fbo_b = None

        self._transition_manager = TransitionManager(
            default_duration=config.transition_duration
        )
        self._particles = ParticleSystem(max_particles=config.max_particles)
        self._scene_library = None
        self._hud = None
        self._clock = None
        self._particle_emit_accum: float = 0.0

    # ── Main Entry Point ────────────────────────────────────────────────────

    def run_main_thread(self) -> None:
        """Enter the render loop (blocking). Must be called from main thread."""
        try:
            self._init_pygame()
            self._init_opengl()
            self._init_scenes()
            self._running = True
            self._start_time = time.time()
            logger.info(
                "Renderer started at %dx%d",
                self.config.window_width,
                self.config.window_height,
            )
            self._render_loop()
        except Exception as exc:
            logger.error("Renderer error: %s", exc, exc_info=True)
        finally:
            self._cleanup()

    # ── Initialization ──────────────────────────────────────────────────────

    def _init_pygame(self) -> None:
        """Initialize pygame display with OpenGL context."""
        import pygame

        pygame.init()
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK,
            pygame.GL_CONTEXT_PROFILE_CORE,
        )
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True
        )

        flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
        if self._fullscreen:
            flags |= pygame.FULLSCREEN

        self._screen = pygame.display.set_mode(
            (self.config.window_width, self.config.window_height),
            flags,
        )
        pygame.display.set_caption("GuitarScapes Pro")
        self._clock = pygame.time.Clock()

        # Initialize font system for HUD
        pygame.font.init()
        logger.debug("pygame initialized")

    def _init_opengl(self) -> None:
        """Create ModernGL context, compile shaders, create buffers."""
        import moderngl
        from guitarscapes.visuals.shaders import (
            VERTEX_SHADER,
            SCENE_FRAGMENT_SHADER,
            PARTICLE_VERTEX_SHADER,
            PARTICLE_FRAGMENT_SHADER,
            TRANSITION_FRAGMENT_SHADER,
            HUD_VERTEX_SHADER,
            HUD_FRAGMENT_SHADER,
        )

        self._ctx = moderngl.create_context()
        ctx = self._ctx

        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)
        ctx.enable(moderngl.PROGRAM_POINT_SIZE)

        # ── Scene shader program ───────────────────────────────────────────
        self._scene_program = ctx.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader=SCENE_FRAGMENT_SHADER,
        )

        # ── Fullscreen quad VAO ────────────────────────────────────────────
        quad_verts = np.array(
            [1.0, 1.0, -1.0, 1.0, 1.0, -1.0, -1.0, -1.0], dtype="f4"
        )
        quad_vbo = ctx.buffer(quad_verts.tobytes())
        self._quad_vao = ctx.simple_vertex_array(
            self._scene_program, quad_vbo, "in_vert"
        )

        # ── Particle shader program ────────────────────────────────────────
        self._particle_program = ctx.program(
            vertex_shader=PARTICLE_VERTEX_SHADER,
            fragment_shader=PARTICLE_FRAGMENT_SHADER,
        )

        # Particle VBO (dynamic, max capacity)
        max_p = self.config.max_particles
        # Each particle: 2f pos + 4f color + 1f size = 7 floats
        self._particle_vbo = ctx.buffer(reserve=max_p * 7 * 4, dynamic=True)
        self._particle_vao = ctx.vertex_array(
            self._particle_program,
            [(self._particle_vbo, "2f 4f 1f", "in_pos", "in_color", "in_size")],
        )

        # ── Transition shader program ──────────────────────────────────────
        self._transition_program = ctx.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader=TRANSITION_FRAGMENT_SHADER,
        )
        self._transition_vao = ctx.simple_vertex_array(
            self._transition_program, quad_vbo, "in_vert"
        )

        # ── HUD shader program ─────────────────────────────────────────────
        self._hud_program = ctx.program(
            vertex_shader=HUD_VERTEX_SHADER,
            fragment_shader=HUD_FRAGMENT_SHADER,
        )
        # HUD quad with texture coordinates
        hud_verts = np.array(
            [
                # pos       texcoord
                 1.0,  1.0,  1.0, 1.0,
                -1.0,  1.0,  0.0, 1.0,
                 1.0, -1.0,  1.0, 0.0,
                -1.0, -1.0,  0.0, 0.0,
            ],
            dtype="f4",
        )
        hud_vbo = ctx.buffer(hud_verts.tobytes())
        self._hud_vao = ctx.vertex_array(
            self._hud_program,
            [(hud_vbo, "2f 2f", "in_vert", "in_texcoord")],
        )

        # ── FBOs for transitions ───────────────────────────────────────────
        # Use actual display surface size (may differ from config on HiDPI)
        w, h = self._screen.get_size()
        self._fbo_a = self._create_fbo(w, h)
        self._fbo_b = self._create_fbo(w, h)

        # ── HUD texture ────────────────────────────────────────────────────
        self._hud_texture = ctx.texture((w, h), 4)
        self._hud_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

        logger.debug("OpenGL context and shaders initialized")

    def _create_fbo(self, width: int, height: int):
        """Create a framebuffer object with a color texture attachment."""
        tex = self._ctx.texture((width, height), 4)
        tex.filter = (self._ctx.LINEAR, self._ctx.LINEAR)
        return self._ctx.framebuffer(color_attachments=[tex])

    def _init_scenes(self) -> None:
        """Load the chord scene library."""
        from guitarscapes.scenes.chord_scenes import ChordSceneLibrary

        self._scene_library = ChordSceneLibrary()
        default_scene = self._scene_library.get_default_scene()
        self._transition_manager.set_immediate(default_scene)
        logger.debug("Scene library loaded")

    # ── Render Loop ─────────────────────────────────────────────────────────

    def _render_loop(self) -> None:
        """Main render loop running at target FPS."""
        import pygame

        while self._running:
            dt = self._clock.tick(self.config.target_fps) / 1000.0
            dt = min(dt, 0.1)  # Cap delta time to avoid explosion

            # Process events
            self._process_events()

            # Process commands
            self._process_commands()

            # Update chord data from detection thread
            self._update_chord_data()

            if not self._frozen:
                # Update transition
                self._transition_manager.update(dt)

                # Update particles
                self._update_particles(dt)

                # Update welcome timer
                if self._show_welcome:
                    self._welcome_timer -= dt
                    if self._welcome_timer <= 0:
                        self._show_welcome = False

            # Render
            self._render_frame()

            pygame.display.flip()

    def _process_events(self) -> None:
        """Handle pygame events and keyboard shortcuts."""
        import pygame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._running = False

                elif event.key == pygame.K_SPACE:
                    self._frozen = not self._frozen
                    logger.info("Visual %s", "frozen" if self._frozen else "unfrozen")

                elif event.key == pygame.K_r:
                    self._restart_scene()

                elif event.key == pygame.K_F11:
                    self._toggle_fullscreen()

                elif event.key == pygame.K_m and (
                    pygame.key.get_mods() & pygame.KMOD_CTRL
                ):
                    self.command_queue.put_nowait("switch_device")

            elif event.type == pygame.VIDEORESIZE:
                self.config.window_width = event.w
                self.config.window_height = event.h
                self._ctx.viewport = (0, 0, event.w, event.h)

    def _process_commands(self) -> None:
        """Process commands from other threads."""
        cmd = self.command_queue.get_nowait()
        while cmd is not None:
            if cmd == "quit":
                self._running = False
            elif cmd == "freeze":
                self._frozen = not self._frozen
            elif cmd == "restart":
                self._restart_scene()
            elif cmd == "toggle_fullscreen":
                self._toggle_fullscreen()
            cmd = self.command_queue.get_nowait()

    def _update_chord_data(self) -> None:
        """Read latest chord data from the detection thread."""
        data = self.chord_queue.get_latest()
        if data is None:
            return

        chord_name, confidence, rms = data
        self._current_rms = rms

        # Only update scene if chord actually changed
        if chord_name != self._current_chord and chord_name != "—":
            self._current_chord = chord_name
            self._current_confidence = confidence

            # Trigger scene transition
            if self._scene_library is not None:
                new_scene = self._scene_library.get_scene(chord_name)
                self._transition_manager.start_transition(
                    new_scene, self.config.transition_duration
                )
                logger.debug(
                    "Chord → %s (conf=%.2f) scene='%s'",
                    chord_name,
                    confidence,
                    new_scene.mood,
                )
        elif chord_name != "—":
            self._current_confidence = confidence

    def _update_particles(self, dt: float) -> None:
        """Update and emit particles based on current scene."""
        state = self._transition_manager.get_current_state()
        env = state.target
        pc = env.particle_config

        if pc is not None:
            # Accumulate emit count
            self._particle_emit_accum += pc.emit_rate * dt * (
                0.5 + self._current_rms * 2.0
            )
            to_emit = int(self._particle_emit_accum)
            if to_emit > 0:
                self._particle_emit_accum -= to_emit
                # Random spawn position across screen
                spawn_x = np.random.uniform(-1.0, 1.0)
                spawn_y = np.random.uniform(0.8, 1.1)
                self._particles.emit(
                    count=to_emit,
                    position=(spawn_x, spawn_y),
                    velocity_range=pc.velocity_range,
                    color=pc.color,
                    size_range=pc.size_range,
                    lifetime_range=pc.lifetime_range,
                )

            self._particles.update(dt, gravity=pc.gravity, wind=pc.wind)
        else:
            self._particles.update(dt)

    # ── Rendering ───────────────────────────────────────────────────────────

    def _render_frame(self) -> None:
        """Render one complete frame."""
        import moderngl

        ctx = self._ctx
        state = self._transition_manager.get_current_state()
        t = time.time() - self._start_time

        if state.is_transitioning:
            # Render source scene to FBO A
            self._fbo_a.use()
            self._fbo_a.clear(*self.config.background_color, 1.0)
            self._render_scene(state.source, t)

            # Render target scene to FBO B
            self._fbo_b.use()
            self._fbo_b.clear(*self.config.background_color, 1.0)
            self._render_scene(state.target, t)

            # Composite to screen
            ctx.screen.use()
            ctx.screen.clear(*self.config.background_color, 1.0)
            self._fbo_a.color_attachments[0].use(location=0)
            self._fbo_b.color_attachments[0].use(location=1)
            su = self._set_uniform
            su(self._transition_program, "sceneA", 0)
            su(self._transition_program, "sceneB", 1)
            su(self._transition_program, "mixFactor", state.progress)
            self._transition_vao.render(moderngl.TRIANGLE_STRIP)
        else:
            # Render directly to screen
            ctx.screen.use()
            ctx.screen.clear(*self.config.background_color, 1.0)
            self._render_scene(state.target, t)

        # Render particles on top
        self._render_particles()

        # Render HUD on top of everything
        self._render_hud(t)

    @staticmethod
    def _set_uniform(prog, name: str, value) -> None:
        """Set a shader uniform, silently skipping if optimized away."""
        if name in prog:
            prog[name].value = value

    def _render_scene(self, env: VisualEnvironment, t: float) -> None:
        """Render a single scene's shader effects."""
        import moderngl

        prog = self._scene_program
        su = self._set_uniform

        su(prog, "u_time", t)
        su(prog, "u_resolution", (
            float(self.config.window_width),
            float(self.config.window_height),
        ))
        su(prog, "u_intensity", min(self._current_rms * 5.0, 1.0))
        su(prog, "u_bg_color_top", env.bg_color_top)
        su(prog, "u_bg_color_bottom", env.bg_color_bottom)
        su(prog, "u_effect_color", env.effect_color)
        su(prog, "u_god_ray_pos", env.god_ray_position)

        # Effect toggles
        su(prog, "u_enable_stars", env.enable_stars)
        su(prog, "u_enable_fog", env.enable_fog)
        su(prog, "u_enable_rain", env.enable_rain)
        su(prog, "u_enable_fire", env.enable_fire)
        su(prog, "u_enable_aurora", env.enable_aurora)
        su(prog, "u_enable_waves", env.enable_waves)
        su(prog, "u_enable_mountains", env.enable_mountains)
        su(prog, "u_enable_fireflies", env.enable_fireflies)
        su(prog, "u_enable_constellations", env.enable_constellations)
        su(prog, "u_enable_god_rays", env.enable_god_rays)
        su(prog, "u_enable_snow", env.enable_snow)
        su(prog, "u_enable_leaves", env.enable_leaves)
        su(prog, "u_enable_nebula", env.enable_nebula)
        su(prog, "u_enable_fractal", env.enable_fractal)

        self._quad_vao.render(moderngl.TRIANGLE_STRIP)

    def _render_particles(self) -> None:
        """Upload live particle data to GPU and render as point sprites."""
        import moderngl

        if self._particles.alive_count == 0:
            return

        positions, colors, sizes = self._particles.get_live_data()
        n = len(positions)
        if n == 0:
            return

        # Interleave: [pos_x, pos_y, r, g, b, a, size] per particle
        data = np.empty((n, 7), dtype=np.float32)
        data[:, 0:2] = positions
        data[:, 2:6] = colors
        data[:, 6] = sizes

        buf = data.tobytes()
        if len(buf) <= self._particle_vbo.size:
            self._particle_vbo.write(buf)
            self._particle_vao.render(moderngl.POINTS, vertices=n)

    def _render_hud(self, t: float) -> None:
        """Render the HUD overlay using pygame font → texture."""
        import pygame
        import moderngl

        # Use actual display surface size (may differ from config on HiDPI)
        display_surface = pygame.display.get_surface()
        if display_surface is None:
            return
        w, h = display_surface.get_size()

        surface = pygame.Surface((w, h), pygame.SRCALPHA)

        fps = self._clock.get_fps()

        # Fonts
        try:
            font_large = pygame.font.SysFont("Arial", 64)
            font_medium = pygame.font.SysFont("Arial", 24)
            font_small = pygame.font.SysFont("Arial", 18)
        except Exception:
            font_large = pygame.font.Font(None, 64)
            font_medium = pygame.font.Font(None, 24)
            font_small = pygame.font.Font(None, 18)

        white = (255, 255, 255)
        gray = (180, 180, 180)
        green = (100, 255, 150)
        yellow = (255, 220, 100)

        # ── Chord name (centered top) ──────────────────────────────────────
        chord_text = font_large.render(self._current_chord, True, white)
        chord_rect = chord_text.get_rect(centerx=w // 2, top=30)

        # Background panel
        panel = pygame.Surface(
            (chord_rect.width + 40, chord_rect.height + 16), pygame.SRCALPHA
        )
        panel.fill((0, 0, 0, 120))
        surface.blit(panel, (chord_rect.x - 20, chord_rect.y - 8))
        surface.blit(chord_text, chord_rect)

        # ── Confidence bar ─────────────────────────────────────────────────
        bar_w = 200
        bar_h = 8
        bar_x = w // 2 - bar_w // 2
        bar_y = chord_rect.bottom + 15

        # Background
        pygame.draw.rect(surface, (50, 50, 50, 180), (bar_x, bar_y, bar_w, bar_h))
        # Fill
        conf_w = int(bar_w * self._current_confidence)
        conf_color = green if self._current_confidence > 0.6 else yellow
        pygame.draw.rect(
            surface, conf_color + (220,), (bar_x, bar_y, conf_w, bar_h)
        )

        conf_label = font_small.render(
            f"Confiança: {self._current_confidence:.0%}", True, gray
        )
        surface.blit(
            conf_label,
            (bar_x + bar_w + 10, bar_y - 3),
        )

        # ── RMS intensity ──────────────────────────────────────────────────
        rms_bar_y = bar_y + 25
        rms_label = font_small.render("Intensidade", True, gray)
        surface.blit(rms_label, (bar_x, rms_bar_y))
        rms_x = bar_x + rms_label.get_width() + 10
        pygame.draw.rect(
            surface, (50, 50, 50, 180), (rms_x, rms_bar_y + 2, 100, 6)
        )
        rms_fill = int(100 * min(self._current_rms * 5.0, 1.0))
        pygame.draw.rect(
            surface, (255, 150, 50, 220), (rms_x, rms_bar_y + 2, rms_fill, 6)
        )

        # ── FPS (top right) ────────────────────────────────────────────────
        fps_text = font_small.render(f"FPS: {fps:.0f}", True, gray)
        surface.blit(fps_text, (w - fps_text.get_width() - 15, 15))

        # ── Device name (bottom left) ──────────────────────────────────────
        dev_text = font_small.render(f"♪ {self.device_name}", True, gray)
        surface.blit(dev_text, (15, h - 30))

        # ── AI status (bottom right) ───────────────────────────────────────
        ai_status = "IA: Ativa" if self.ai_active else "IA: Inativa"
        ai_color = green if self.ai_active else gray
        ai_text = font_small.render(ai_status, True, ai_color)
        surface.blit(ai_text, (w - ai_text.get_width() - 15, h - 30))

        # ── Welcome message ────────────────────────────────────────────────
        if self._show_welcome:
            alpha = int(255 * min(self._welcome_timer / 2.0, 1.0))
            welcome = font_medium.render(
                "♪ Toque seu violão e veja a música ganhar vida ♪",
                True,
                (255, 255, 255, alpha),
            )
            wr = welcome.get_rect(centerx=w // 2, centery=h // 2)
            # Panel
            wp = pygame.Surface(
                (wr.width + 40, wr.height + 20), pygame.SRCALPHA
            )
            wp.fill((0, 0, 0, min(alpha, 160)))
            surface.blit(wp, (wr.x - 20, wr.y - 10))
            surface.blit(welcome, wr)

        # ── Upload surface to texture ──────────────────────────────────────
        # Convert to raw bytes (no flip — we handle orientation in the quad)
        tex_data = pygame.image.tobytes(surface, "RGBA", True)

        # Recreate texture if surface size differs from current texture
        tex_w, tex_h = self._hud_texture.size
        if tex_w != w or tex_h != h:
            self._hud_texture.release()
            self._hud_texture = self._ctx.texture((w, h), 4)
            self._hud_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

        # Safety check: only write if sizes match
        expected = w * h * 4
        if len(tex_data) == expected:
            self._hud_texture.write(tex_data)
        else:
            # Pad or truncate to match (fallback for stride mismatch)
            if len(tex_data) < expected:
                tex_data = tex_data + b'\x00' * (expected - len(tex_data))
            else:
                tex_data = tex_data[:expected]
            self._hud_texture.write(tex_data)

        # Render HUD quad
        self._hud_texture.use(location=0)
        su = self._set_uniform
        su(self._hud_program, "u_texture", 0)
        su(self._hud_program, "u_tint", (1.0, 1.0, 1.0, 1.0))
        self._hud_vao.render(moderngl.TRIANGLE_STRIP)

    # ── Utility ─────────────────────────────────────────────────────────────

    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        import pygame

        self._fullscreen = not self._fullscreen
        if self._fullscreen:
            pygame.display.set_mode(
                (0, 0), pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN
            )
            info = pygame.display.Info()
            self.config.window_width = info.current_w
            self.config.window_height = info.current_h
        else:
            pygame.display.set_mode(
                (1280, 720),
                pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE,
            )
            self.config.window_width = 1280
            self.config.window_height = 720

        self._ctx.viewport = (0, 0, self.config.window_width, self.config.window_height)
        logger.info(
            "Fullscreen %s", "enabled" if self._fullscreen else "disabled"
        )

    def _restart_scene(self) -> None:
        """Restart the current visual environment."""
        self._particles.clear()
        self._start_time = time.time()
        self._particle_emit_accum = 0.0
        logger.info("Scene restarted")

    def _cleanup(self) -> None:
        """Clean up pygame and OpenGL resources."""
        import pygame

        try:
            if self._ctx:
                self._ctx.release()
        except Exception:
            pass

        try:
            pygame.quit()
        except Exception:
            pass

        logger.info("Renderer cleaned up")
