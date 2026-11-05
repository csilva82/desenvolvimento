# Editor de Nós – Arduino / ESP32

Editor visual (estilo Node-RED) que gera código C++, compila com `arduino-cli`,
simula AVR no navegador (avr8js) e grava na placa.

## Arquivos
- `index.html` – editor de nós, gerador de código, simulador
- `server.py`  – backend Flask (compilar, listar portas, gravar)

## Instalação

1. Instale o **arduino-cli**: https://arduino.github.io/arduino-cli/latest/installation/
2. Instale os cores:
   ```
   arduino-cli core update-index
   arduino-cli core install arduino:avr

   # ESP32 (opcional)
   arduino-cli config init
   arduino-cli config add board_manager.additional_urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
   arduino-cli core update-index
   arduino-cli core install esp32:esp32
   ```
3. `pip install flask`
4. `python server.py`
5. Abra **http://localhost:5000**

## Uso
- Botões da esquerda criam nós. Arraste pelo cabeçalho para mover.
- Arraste da bolinha de saída (direita) até a bolinha de entrada (esquerda) de outro nó.
- Clique em um fio para removê-lo. `×` remove o nó.
- Nós **Setup** e **Loop** são o início de `setup()` e `loop()`.
- **Compilar** → aba "Log / Downloads" lista os arquivos (`.hex` no AVR, `.bin` no ESP32).
- **Simular** (Uno/Nano) → compila e executa o `.hex` no navegador (precisa de internet para carregar o avr8js via CDN).
- **Gravar na placa** → `arduino-cli compile --upload` na porta escolhida (o servidor roda no seu PC).

## Limitações
- Simulação: só ATmega328 (Uno/Nano), sem ADC; PWM aparece como liga/desliga.
- ESP32 gera `.bin`. Para gravar manualmente: `esptool.py --chip esp32 write_flash 0x0 sketch.ino.merged.bin`.
- Botões da simulação: pressionado = LOW, solto = HIGH (use INPUT_PULLUP).

---

## Usando no GitHub

### A) GitHub Codespaces (tudo funciona: compilar, simular, baixar .hex/.bin)
1. No repositório: **Code ▸ Codespaces ▸ Create codespace on main**.
2. Aguarde o `postCreateCommand` (instala arduino-cli + cores; a 1ª vez leva alguns minutos).
3. A porta 5000 abre sozinha no navegador. Se não abrir, use a aba **Ports**.
4. "Gravar na placa" **não** funciona aí (a placa está no seu PC); baixe o `.hex`/`.bin` e grave localmente.

### B) GitHub Pages (editor) + backend em outro serviço
O Pages só serve arquivos estáticos, então compilar exige um backend:
1. **Settings ▸ Pages ▸ Source: GitHub Actions** (o workflow `pages.yml` publica o `index.html`).
2. Suba o backend usando o `Dockerfile` (ex.: Render ▸ New Web Service ▸ Docker). Defina a variável
   `ALLOWED_ORIGIN=https://SEU_USUARIO.github.io`. Para imagem menor, use o build arg `WITH_ESP32=0`.
3. Abra uma vez: `https://SEU_USUARIO.github.io/REPO/?api=https://seu-backend.onrender.com`
   (a URL fica salva no navegador).

Sem backend, o Pages mostra o editor e o código gerado, mas Compilar/Simular não funcionam.
Atenção: o backend compila código enviado por qualquer pessoa; não o deixe público sem limites.

### Publicar o repositório
```
git init && git add . && git commit -m "Editor de nós Arduino/ESP32"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
git push -u origin main
```
