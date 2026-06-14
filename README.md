# 🎸 GuitarScapes Pro

> Transforme acordes de violão em paisagens visuais vivas e emocionais, em tempo real.

GuitarScapes Pro captura o som do seu violão via microfone ou interface de áudio, reconhece os acordes tocados com alta precisão e transforma cada acorde em um cenário visual imersivo renderizado com OpenGL — tudo com latência inferior a 100ms e renderização a 60 FPS.

---

## 🎬 Visão Geral

- **Detecção de 108 acordes** — Maiores, menores, 7ª, m7, maj7, sus2, sus4, dim, aug
- **Pipeline de IA** — HPCP + Template Matching + Refinamento Neural (ONNX)
- **Efeitos visuais cinematográficos** — Estrelas, aurora, chuva, fogo, névoa, montanhas, ondas, constelações, neve, folhas, vaga-lumes, raios de luz
- **Transições suaves** — Crossfade de 1-2 segundos entre cenários
- **Partículas dinâmicas** — Sistema de partículas responsivo à intensidade do som
- **Multi-plataforma** — Windows, Linux, macOS

---

## 🏗️ Arquitetura

```
guitarscapes/
├── main.py                    # Ponto de entrada
├── audio/
│   ├── device_manager.py      # Gerenciamento de dispositivos
│   ├── audio_capture.py       # Captura em tempo real
│   └── permissions.py         # Verificação de permissões
├── detection/
│   ├── fft.py                 # FFT com detecção de picos
│   ├── chroma.py              # Extração de Chroma Features
│   ├── hpcp.py                # HPCP (Harmonic Pitch Class Profile)
│   ├── templates.py           # 108 templates de acordes
│   ├── neural_refiner.py      # Refinamento com ONNX Runtime
│   └── smoothing.py           # Suavização temporal
├── visuals/
│   ├── shaders.py             # Shaders GLSL completos
│   ├── particles.py           # Sistema de partículas
│   ├── environment.py         # Configuração de cena visual
│   ├── transitions.py         # Gerenciador de transições
│   └── renderer.py            # Renderizador OpenGL principal
├── scenes/
│   └── chord_scenes.py        # Mapeamento acorde → cenário
├── models/
│   └── train_refiner.py       # Script de treinamento do modelo
├── ui/
│   ├── device_dialog.py       # Diálogo de seleção de dispositivo
│   └── hud.py                 # Overlay de informações
├── utils/
│   ├── config.py              # Configurações centralizadas
│   ├── logger.py              # Logging estruturado
│   └── threading_utils.py     # Utilitários de threading
└── tests/                     # Testes automatizados
```

### Pipeline de Detecção

```
Microfone → Pré-processamento → FFT → HPCP → Template Matching (Top 3)
→ Refinamento Neural (ONNX, opcional) → Suavização Temporal → Acorde Final
→ Sistema Visual
```

### Modelo de Threading

| Thread | Função |
|--------|--------|
| Thread Principal | Renderização OpenGL (pygame-ce + ModernGL) |
| Thread 2 | Captura de áudio (sounddevice) |
| Thread 3 | Detecção harmônica (FFT → HPCP → Matching) |

---

## 📋 Requisitos

- **Python** 3.12+
- **OpenGL** 3.3+ 
- **Microfone** ou interface de áudio
- **Sistema Operacional**: Windows 10+, Linux, macOS 10.15+

### Dependências de Sistema (Linux)

```bash
# Ubuntu/Debian
sudo apt install libportaudio2 python3-dev

# Fedora
sudo dnf install portaudio-devel

# Arch
sudo pacman -S portaudio
```

---

## 🚀 Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd guitarscapes

# Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Instale as dependências
pip install -r requirements.txt
```

### Treinamento do Modelo (Opcional)

Para usar o refinamento neural:

```bash
pip install torch  # PyTorch para treinamento
python -m guitarscapes.models.train_refiner
```

Isto gera `models/chord_refiner.onnx`. Sem o modelo, a detecção funciona normalmente usando apenas template matching.

---

## 🎤 Permissões de Microfone

### Windows

1. Abra **Configurações** → **Privacidade e Segurança** → **Microfone**
2. Ative **Permitir que apps acessem o microfone**
3. Certifique-se de que o Python/terminal tem permissão

### macOS

1. Abra **Configurações do Sistema** → **Privacidade e Segurança** → **Microfone**
2. Adicione o Terminal ou IDE à lista de apps permitidos

### Linux

- O acesso ao microfone geralmente funciona sem configuração extra
- Se necessário, adicione o usuário ao grupo `audio`:
  ```bash
  sudo usermod -aG audio $USER
  ```
- Compatível com **PipeWire**, **PulseAudio** e **ALSA**

---

## ▶️ Execução

```bash
cd guitarscapes
python -m guitarscapes.main
```

### Atalhos de Teclado

| Tecla | Ação |
|-------|------|
| `Espaço` | Congelar/descongelar visual |
| `R` | Reiniciar ambiente |
| `F11` | Alternar tela cheia |
| `Ctrl+M` | Trocar dispositivo de áudio |
| `Esc` | Encerrar |

---

## 🧪 Testes

```bash
python -m pytest tests/ -v
```

---

## 🔧 Solução de Problemas

| Problema | Solução |
|----------|---------|
| **"Nenhum dispositivo encontrado"** | Verifique se o microfone está conectado e com permissão |
| **FPS baixo** | Reduza a resolução da janela ou desabilite efeitos visuais |
| **"OpenGL 3.3 not supported"** | Atualize drivers da placa de vídeo |
| **Latência alta** | Use uma interface de áudio USB em vez do microfone interno |
| **Erros no Linux** | Instale `libportaudio2` e verifique o grupo `audio` |
| **Acordes não detectados** | Posicione o microfone mais perto do violão |

---

## ⚠️ Limitações Atuais

- O modelo neural é treinado com dados sintéticos — treinamento com áudio real melhoraria a precisão
- A detecção funciona melhor com acordes abertos e strumming claro
- Ambientes ruidosos podem afetar a precisão
- Acordes com barra podem ter menor confiança
- GPU com OpenGL 3.3+ é necessária para renderização
