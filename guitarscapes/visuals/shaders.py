"""GLSL shader source strings for GuitarScapes Pro visual rendering.

All shaders target OpenGL 3.3 Core Profile (#version 330 core).
"""

# ─── Fullscreen Quad Vertex Shader ──────────────────────────────────────────

VERTEX_SHADER = """
#version 330 core

in vec2 in_vert;
out vec2 uv;

void main() {
    uv = in_vert * 0.5 + 0.5;
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
"""

# ─── Main Scene Fragment Shader ─────────────────────────────────────────────

SCENE_FRAGMENT_SHADER = """
#version 330 core

uniform float u_time;
uniform vec2 u_resolution;
uniform float u_intensity;

uniform vec3 u_bg_color_top;
uniform vec3 u_bg_color_bottom;
uniform vec3 u_effect_color;
uniform vec2 u_god_ray_pos;

uniform bool u_enable_stars;
uniform bool u_enable_fog;
uniform bool u_enable_rain;
uniform bool u_enable_fire;
uniform bool u_enable_aurora;
uniform bool u_enable_waves;
uniform bool u_enable_mountains;
uniform bool u_enable_fireflies;
uniform bool u_enable_constellations;
uniform bool u_enable_god_rays;
uniform bool u_enable_snow;
uniform bool u_enable_leaves;
uniform bool u_enable_nebula;
uniform bool u_enable_fractal;

in vec2 uv;
out vec4 fragColor;

// ── Utility Functions ──────────────────────────────────────────────────────

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(
        mix(hash(i + vec2(0.0, 0.0)), hash(i + vec2(1.0, 0.0)), u.x),
        mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x),
        u.y
    );
}

float fbm(vec2 p) {
    float v = 0.0;
    float a = 0.5;
    mat2 rot = mat2(0.8, 0.6, -0.6, 0.8);
    for (int i = 0; i < 5; i++) {
        v += a * noise(p);
        p = rot * p * 2.0;
        a *= 0.5;
    }
    return v;
}

// ── Stars ──────────────────────────────────────────────────────────────────

vec3 stars(vec2 uv) {
    vec3 col = vec3(0.0);
    for (int layer = 0; layer < 3; layer++) {
        float scale = 10.0 + float(layer) * 15.0;
        float brightness_factor = 1.0 - float(layer) * 0.25;
        vec2 suv = uv * scale + float(layer) * 7.32;
        vec2 id = floor(suv);
        vec2 gv = fract(suv) - 0.5;

        for (int y = -1; y <= 1; y++) {
            for (int x = -1; x <= 1; x++) {
                vec2 offset = vec2(float(x), float(y));
                vec2 cellId = id + offset;
                float n = hash21(cellId);
                vec2 starPos = vec2(n, fract(n * 34.56)) - 0.5;
                float dist = length(gv - offset - starPos);
                float twinkle = 0.6 + 0.4 * sin(u_time * (1.0 + n * 3.0) + n * 6.28);
                float size = 0.015 + n * 0.02;
                float star = smoothstep(size, 0.0, dist) * n * brightness_factor * twinkle;
                col += star * mix(vec3(0.9, 0.95, 1.0), u_effect_color, 0.3);
            }
        }
    }
    return col;
}

// ── Fog / Mist ─────────────────────────────────────────────────────────────

vec3 fog(vec2 uv) {
    float f = 0.0;
    f += fbm(uv * 3.0 + vec2(u_time * 0.08, 0.0)) * 0.5;
    f += fbm(uv * 6.0 + vec2(-u_time * 0.04, u_time * 0.02)) * 0.3;
    f += fbm(uv * 10.0 + vec2(u_time * 0.06, -u_time * 0.03)) * 0.2;
    float gradient = smoothstep(0.0, 0.7, 1.0 - uv.y);
    f *= gradient;
    vec3 fogCol = mix(vec3(0.15, 0.15, 0.2), u_effect_color * 0.5, f * 0.5);
    return fogCol * f * 0.6;
}

// ── Cosmic Nebula ──────────────────────────────────────────────────────────

mat2 rot(float a) {
    float s = sin(a), c = cos(a);
    return mat2(c, -s, s, c);
}

vec3 nebula(vec2 uv) {
    vec2 p = uv * 2.0 - 1.0;
    p.x *= u_resolution.x / u_resolution.y;
    
    p *= 1.5;
    
    float t = u_time * 0.2 + u_intensity * 1.5;
    
    vec2 q = vec2(0.0);
    q.x = fbm(p + vec2(t * 0.1, t * 0.2));
    q.y = fbm(p + vec2(-t * 0.15, t * 0.1));
    
    vec2 r = vec2(0.0);
    r.x = fbm(p + 1.0 * q + vec2(1.7, 9.2) + t * 0.15);
    r.y = fbm(p + 1.0 * q + vec2(8.3, 2.8) - t * 0.12);
    
    float f = fbm(p + r * 2.0 + t);
    
    vec3 color = mix(u_bg_color_bottom, u_bg_color_top, clamp(f * f * 3.0, 0.0, 1.0));
    color = mix(color, u_effect_color, clamp(length(q), 0.0, 1.0));
    color = mix(color, vec3(1.0, 1.0, 1.0), clamp(length(r.x) * u_intensity, 0.0, 1.0));
    
    float core = 0.05 / length(p * rot(u_time * 0.5) - q * 0.2);
    core *= 0.5 + u_intensity * 2.0;
    color += u_effect_color * core;
    
    return color * f * 2.0;
}

// ── Fractal Tunnel ─────────────────────────────────────────────────────────

vec3 palette(float t) {
    vec3 a = u_bg_color_top;
    vec3 b = u_bg_color_bottom;
    vec3 c = u_effect_color;
    vec3 d = vec3(0.263, 0.416, 0.557);
    return a + b * cos(6.28318 * (c * t + d));
}

vec3 fractal(vec2 uv) {
    vec2 p = uv * 2.0 - 1.0;
    p.x *= u_resolution.x / u_resolution.y;
    vec2 p0 = p;
    
    float t = u_time * 0.5;
    vec3 col = vec3(0.0);
    
    for(float i = 0.0; i < 4.0; i++) {
        p = fract(p * 1.5) - 0.5;
        float d = length(p) * exp(-length(p0));
        
        vec3 c = palette(length(p0) + i * 0.4 + t * 0.4);
        
        d = sin(d * 8.0 + t) / 8.0;
        d = abs(d);
        d = pow(0.01 / d, 1.2);
        
        col += c * d * (0.5 + u_intensity * 2.0);
    }
    
    return col;
}

// ── Rain ───────────────────────────────────────────────────────────────────

vec3 rain(vec2 uv) {
    float r = 0.0;
    for (int layer = 0; layer < 3; layer++) {
        float scale_x = 8.0 + float(layer) * 8.0;
        float scale_y = 4.0 + float(layer) * 3.0;
        float speed = 1.5 + float(layer) * 0.5;
        float alpha = 1.0 - float(layer) * 0.3;
        vec2 ruv = uv * vec2(scale_x, scale_y) + vec2(float(layer) * 2.3, 0.0);
        ruv.y += u_time * speed;
        vec2 rid = floor(ruv);
        vec2 rgv = fract(ruv);
        float n = hash21(rid + float(layer) * 100.0);
        float xOff = n * 0.7 + 0.15;
        float drop = smoothstep(0.03, 0.0, abs(rgv.x - xOff));
        float yPos = fract(n * 34.56 + u_time * (0.4 + n * 0.3));
        drop *= smoothstep(0.0, 0.1, rgv.y - yPos) * smoothstep(0.35, 0.1, rgv.y - yPos);
        r += drop * (0.4 + n * 0.4) * alpha;
    }
    return vec3(0.4, 0.5, 0.7) * r * u_effect_color;
}

// ── Fire ───────────────────────────────────────────────────────────────────

vec3 fire(vec2 uv) {
    vec2 fireUV = uv;
    fireUV.y -= u_time * 0.4;
    fireUV.x += sin(uv.y * 10.0 + u_time * 3.0) * 0.03;

    float f = 0.0;
    f += fbm(fireUV * 4.0) * 0.5;
    f += fbm(fireUV * 8.0 + u_time * 0.3) * 0.25;
    f += fbm(fireUV * 14.0 + u_time * 0.6) * 0.125;

    float shape = smoothstep(1.0, 0.0, uv.y) * smoothstep(0.0, 0.25, uv.y);
    float centerDist = abs(uv.x - 0.5) * 2.0;
    shape *= smoothstep(0.8, 0.2, centerDist);
    f *= shape;

    vec3 col = vec3(0.0);
    col = mix(col, vec3(0.8, 0.1, 0.0), smoothstep(0.0, 0.3, f));
    col = mix(col, vec3(1.0, 0.4, 0.0), smoothstep(0.3, 0.55, f));
    col = mix(col, vec3(1.0, 0.8, 0.2), smoothstep(0.55, 0.75, f));
    col = mix(col, vec3(1.0, 1.0, 0.8), smoothstep(0.75, 0.95, f));
    return col * f;
}

// ── Aurora Borealis ────────────────────────────────────────────────────────

vec3 aurora(vec2 uv) {
    float a = 0.0;
    for (int i = 0; i < 3; i++) {
        float fi = float(i);
        vec2 auv = uv;
        auv.x += sin(auv.y * 3.0 + u_time * 0.3 + fi * 2.1) * 0.25;
        auv.x += sin(auv.y * 7.0 + u_time * 0.5 + fi * 1.4) * 0.1;
        float band = exp(-auv.x * auv.x * 8.0);
        float n = fbm(vec2(auv.x * 2.0, auv.y * 4.0 - u_time * 0.15 + fi));
        band *= n;
        band *= smoothstep(-0.1, 0.2, uv.y) * smoothstep(0.85, 0.35, uv.y);
        a += band * (0.6 - fi * 0.15);
    }
    vec3 auroraCol = vec3(0.0);
    auroraCol += vec3(0.1, 0.8, 0.4) * a;
    auroraCol += vec3(0.3, 0.1, 0.7) * a * smoothstep(0.4, 0.7, uv.y);
    auroraCol += u_effect_color * 0.3 * a;
    return auroraCol;
}

// ── Waves ──────────────────────────────────────────────────────────────────

vec3 waves(vec2 uv) {
    float waterLine = 0.35;
    float wave = 0.0;
    wave += sin(uv.x * 6.0 + u_time * 1.5) * 0.04;
    wave += sin(uv.x * 12.0 - u_time * 2.0) * 0.02;
    wave += sin(uv.x * 20.0 + u_time * 0.8) * 0.01;
    float wl = waterLine + wave;

    if (uv.y > wl) return vec3(0.0);

    float depth = smoothstep(wl, 0.0, uv.y);
    vec3 surfCol = mix(vec3(0.0, 0.25, 0.45), vec3(0.0, 0.05, 0.15), depth);
    surfCol *= u_effect_color;
    float foam = smoothstep(0.008, 0.0, abs(uv.y - wl));
    surfCol += foam * vec3(0.7, 0.8, 0.9);
    float caustic = noise(uv * 18.0 + u_time) * noise(uv * 14.0 - u_time * 0.6);
    surfCol += caustic * 0.12;
    return surfCol;
}

// ── Mountains ──────────────────────────────────────────────────────────────

vec3 mountains(vec2 uv) {
    vec3 col = vec3(0.0);
    for (int i = 0; i < 4; i++) {
        float fi = float(i);
        float offset = fi * 3.5 + 1.0;
        float scale = 0.15 + fi * 0.06;
        float h = 0.0;
        h += sin(uv.x * 1.5 + offset) * 0.28;
        h += sin(uv.x * 3.5 + offset * 1.3) * 0.14;
        h += sin(uv.x * 8.0 + offset * 0.7) * 0.04;
        float mountain_line = h * scale + 0.15 + fi * 0.05;
        float mask = 1.0 - smoothstep(mountain_line - 0.005, mountain_line + 0.005, uv.y);
        float darkness = 0.15 + fi * 0.12;
        vec3 mCol = u_effect_color * darkness;
        col = mix(col, mCol, mask);
    }
    return col;
}

// ── Fireflies ──────────────────────────────────────────────────────────────

vec3 fireflies(vec2 uv) {
    vec3 col = vec3(0.0);
    for (int i = 0; i < 15; i++) {
        float fi = float(i);
        float n1 = hash(vec2(fi * 13.7, fi * 7.3));
        float n2 = hash(vec2(fi * 23.1, fi * 17.9));
        vec2 pos = vec2(
            n1 + sin(u_time * 0.3 + fi * 1.7) * 0.15,
            n2 * 0.6 + sin(u_time * 0.4 + fi * 2.3) * 0.08
        );
        float dist = length(uv - pos);
        float pulse = 0.5 + 0.5 * sin(u_time * (1.5 + n1 * 2.0) + fi * 3.14);
        float glow = exp(-dist * dist * 800.0) * pulse;
        col += glow * mix(vec3(0.8, 1.0, 0.3), u_effect_color, 0.4);
    }
    return col;
}

// ── Constellations ─────────────────────────────────────────────────────────

float distToSegment(vec2 p, vec2 a, vec2 b) {
    vec2 pa = p - a;
    vec2 ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h);
}

vec3 constellations(vec2 uv) {
    vec3 col = vec3(0.0);
    float gridSize = 4.0;
    vec2 id = floor(uv * gridSize);

    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 nid = id + vec2(float(x), float(y));
            float n = hash21(nid);
            vec2 starPos = (nid + vec2(hash21(nid + 0.1), hash21(nid + 0.2)) * 0.6 + 0.2) / gridSize;

            float starDist = length(uv - starPos);
            float star = smoothstep(0.006, 0.0, starDist);
            float glow = exp(-starDist * starDist * 5000.0);
            col += (star + glow * 0.4) * mix(vec3(0.7, 0.85, 1.0), u_effect_color, 0.3);

            for (int ny = -1; ny <= 1; ny++) {
                for (int nx = -1; nx <= 1; nx++) {
                    vec2 nid2 = nid + vec2(float(nx), float(ny));
                    if (nid2 == nid) continue;
                    vec2 sp2 = (nid2 + vec2(hash21(nid2 + 0.1), hash21(nid2 + 0.2)) * 0.6 + 0.2) / gridSize;
                    float d = length(starPos - sp2);
                    if (d < 0.35 / gridSize * 2.0) {
                        float lineDist = distToSegment(uv, starPos, sp2);
                        float line = smoothstep(0.0015, 0.0, lineDist);
                        float reveal = smoothstep(0.0, 1.0,
                            sin(u_time * 0.4 + hash21(nid + nid2) * 6.28) * 0.5 + 0.5);
                        col += line * reveal * vec3(0.15, 0.25, 0.45) * 0.4;
                    }
                }
            }
        }
    }
    return col;
}

// ── God Rays ───────────────────────────────────────────────────────────────

vec3 god_rays(vec2 uv) {
    vec2 dir = uv - u_god_ray_pos;
    float dist = length(dir);
    float angle = atan(dir.y, dir.x);

    float rays = 0.0;
    rays += (sin(angle * 12.0 + u_time * 0.5) * 0.5 + 0.5) * 0.4;
    rays += (sin(angle * 20.0 - u_time * 0.3) * 0.5 + 0.5) * 0.25;
    rays += (sin(angle * 8.0 + u_time * 0.7) * 0.5 + 0.5) * 0.15;
    rays *= exp(-dist * 1.8);

    float centralGlow = exp(-dist * dist * 6.0);
    return (u_effect_color * rays * 0.5 + vec3(1.0, 0.95, 0.85) * centralGlow * 0.3);
}

// ── Snow ───────────────────────────────────────────────────────────────────

vec3 snow(vec2 uv) {
    float s = 0.0;
    for (int layer = 0; layer < 3; layer++) {
        float scale = 6.0 + float(layer) * 6.0;
        float speed = 0.3 + float(layer) * 0.15;
        float alpha = 1.0 - float(layer) * 0.25;
        vec2 suv = uv * vec2(scale, scale * 0.5) + vec2(float(layer) * 3.7, 0.0);
        suv.y += u_time * speed;
        suv.x += sin(u_time * 0.3 + uv.y * 3.0) * 0.3;
        vec2 sid = floor(suv);
        vec2 sgv = fract(suv);
        float n = hash21(sid + float(layer) * 50.0);
        vec2 snowPos = vec2(n * 0.7 + 0.15, fract(n * 45.67) * 0.7 + 0.15);
        float dist = length(sgv - snowPos);
        float size = 0.02 + n * 0.03;
        s += smoothstep(size, 0.0, dist) * alpha * (0.5 + n * 0.5);
    }
    return vec3(0.9, 0.92, 1.0) * s;
}

// ── Leaves ─────────────────────────────────────────────────────────────────

vec3 leaves(vec2 uv) {
    float l = 0.0;
    vec3 leafCol = vec3(0.0);
    for (int i = 0; i < 12; i++) {
        float fi = float(i);
        float n = hash(vec2(fi * 17.3, fi * 11.7));
        float speed = 0.2 + n * 0.3;
        float swing = sin(u_time * (0.8 + n) + fi * 2.0) * 0.1;
        vec2 pos = vec2(
            fract(n * 3.7 + u_time * 0.03 * (1.0 + n) + swing),
            fract(fi * 0.083 + u_time * speed)
        );
        float dist = length(uv - pos);
        float leaf = smoothstep(0.015, 0.0, dist);
        l += leaf;
        vec3 c = mix(
            vec3(0.4, 0.7, 0.2),
            mix(vec3(0.8, 0.5, 0.1), u_effect_color, 0.3),
            n
        );
        leafCol += leaf * c;
    }
    return leafCol;
}

// ── Main Composition ───────────────────────────────────────────────────────

void main() {
    // Aspect-ratio-corrected UV for effects that need circular symmetry
    float aspect = u_resolution.x / u_resolution.y;
    vec2 auv = vec2(uv.x * aspect, uv.y);

    // Background gradient
    vec3 col = mix(u_bg_color_bottom, u_bg_color_top, uv.y);

    // Intensity modulation (louder = more vivid)
    float intensity = 0.4 + u_intensity * 0.6;
    vec3 finalColor = col;

    // Composite effects (order matters: background first, foreground last)
    if (u_enable_mountains)     finalColor += mountains(uv) * intensity;
    if (u_enable_waves)         finalColor += waves(uv) * intensity;
    if (u_enable_fog)           finalColor += fog(uv) * intensity;
    if (u_enable_stars)         finalColor += stars(auv) * intensity;
    if (u_enable_constellations) finalColor += constellations(auv) * intensity;
    if (u_enable_aurora)        finalColor += aurora(uv) * intensity;
    if (u_enable_god_rays)      finalColor += god_rays(uv) * intensity;
    if (u_enable_fire)          finalColor += fire(uv) * intensity;
    if (u_enable_rain)          finalColor += rain(uv) * intensity;
    if (u_enable_snow)          finalColor += snow(auv) * intensity;
    if (u_enable_leaves)        finalColor += leaves(uv) * intensity;
    if (u_enable_fireflies)     finalColor += fireflies(auv) * intensity;
    if (u_enable_nebula)        finalColor += nebula(uv) * intensity;
    if (u_enable_fractal)       finalColor += fractal(uv) * intensity;

    // Add audio-reactive "bloom" or flash to the whole scene
    finalColor += u_effect_color * u_intensity * 0.15;

    fragColor = vec4(finalColor, 1.0);
}
"""

# ─── Particle Vertex Shader ────────────────────────────────────────────────

PARTICLE_VERTEX_SHADER = """
#version 330 core

in vec2 in_pos;
in vec4 in_color;
in float in_size;

out vec4 v_color;

void main() {
    gl_Position = vec4(in_pos, 0.0, 1.0);
    gl_PointSize = in_size;
    v_color = in_color;
}
"""

# ─── Particle Fragment Shader ──────────────────────────────────────────────

PARTICLE_FRAGMENT_SHADER = """
#version 330 core

in vec4 v_color;
out vec4 fragColor;

void main() {
    vec2 pc = gl_PointCoord - 0.5;
    float dist = length(pc) * 2.0;

    float alpha = 1.0 - smoothstep(0.0, 1.0, dist);
    float glow = exp(-dist * dist * 4.0);
    float combined = alpha * 0.6 + glow * 0.4;

    fragColor = vec4(v_color.rgb, v_color.a * combined);
}
"""

# ─── Transition Fragment Shader ────────────────────────────────────────────

TRANSITION_FRAGMENT_SHADER = """
#version 330 core

uniform sampler2D sceneA;
uniform sampler2D sceneB;
uniform float mixFactor;

in vec2 uv;
out vec4 fragColor;

void main() {
    vec4 colorA = texture(sceneA, uv);
    vec4 colorB = texture(sceneB, uv);
    fragColor = mix(colorA, colorB, mixFactor);
}
"""

# ─── HUD Vertex Shader ────────────────────────────────────────────────────

HUD_VERTEX_SHADER = """
#version 330 core

in vec2 in_vert;
in vec2 in_texcoord;

out vec2 v_texcoord;

void main() {
    v_texcoord = in_texcoord;
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
"""

# ─── HUD Fragment Shader ──────────────────────────────────────────────────

HUD_FRAGMENT_SHADER = """
#version 330 core

uniform sampler2D u_texture;
uniform vec4 u_tint;

in vec2 v_texcoord;
out vec4 fragColor;

void main() {
    vec4 texel = texture(u_texture, v_texcoord);
    fragColor = texel * u_tint;
}
"""
