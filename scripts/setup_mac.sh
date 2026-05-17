#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
LAUNCHER="$HOME/Desktop/Nutripuncture Desk.command"
APP_URL="http://127.0.0.1:5173"

log() {
  printf "\n\033[1;34m==>\033[0m %s\n" "$1"
}

fail() {
  printf "\nErreur: %s\n" "$1" >&2
  exit 1
}

if [ "$(uname -s)" != "Darwin" ]; then
  fail "ce script doit etre lance sur macOS."
fi

log "Verification des outils Apple"
if ! xcode-select -p >/dev/null 2>&1; then
  xcode-select --install || true
  fail "installez les Xcode Command Line Tools, puis relancez: bash scripts/setup_mac.sh"
fi

log "Verification de Homebrew"
if ! command -v brew >/dev/null 2>&1; then
  NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

if [ -x /opt/homebrew/bin/brew ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -x /usr/local/bin/brew ]; then
  eval "$(/usr/local/bin/brew shellenv)"
fi

command -v brew >/dev/null 2>&1 || fail "Homebrew est introuvable apres installation."

BREW_SHELLENV='eval "$($(brew --prefix)/bin/brew shellenv)"'
if [ -f "$HOME/.zprofile" ]; then
  grep -Fq "brew shellenv" "$HOME/.zprofile" || printf '\n%s\n' "$BREW_SHELLENV" >> "$HOME/.zprofile"
else
  printf '%s\n' "$BREW_SHELLENV" > "$HOME/.zprofile"
fi

log "Installation des dependances systeme"
brew update
if brew info python@3.12 >/dev/null 2>&1; then
  brew install python@3.12
else
  brew install python
fi
brew install node tesseract tesseract-lang git
brew install rust || echo "Rust non installe automatiquement. Utile seulement pour construire l'app Tauri."

if brew --prefix python@3.12 >/dev/null 2>&1; then
  PYTHON_BIN="$(brew --prefix python@3.12)/bin/python3.12"
fi
if [ -z "${PYTHON_BIN:-}" ] || [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="$(command -v python3)"
fi

log "Preparation du backend Python"
cd "$BACKEND_DIR"
"$PYTHON_BIN" -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m app.seed

log "Preparation du frontend"
cd "$FRONTEND_DIR"
npm install
npm run build

log "Creation du lanceur double-clic"
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
set -euo pipefail

if [ -x /opt/homebrew/bin/brew ]; then
  eval "\$(/opt/homebrew/bin/brew shellenv)"
elif [ -x /usr/local/bin/brew ]; then
  eval "\$(/usr/local/bin/brew shellenv)"
fi

cd "$ROOT_DIR"
bash scripts/start_app.sh
EOF
chmod +x "$LAUNCHER"

log "Verification rapide"
tesseract --list-langs | grep -Eq '(^|[[:space:]])fra($|[[:space:]])' || fail "la langue OCR francaise 'fra' n'est pas disponible dans Tesseract."
curl -fsS "$APP_URL" >/dev/null 2>&1 || true

cat <<EOF

Installation terminee.

Pour lancer le POC chez le client:
  1. double-cliquer sur: $LAUNCHER
  2. attendre l'ouverture du navigateur
  3. utiliser: $APP_URL

Si macOS bloque le fichier .command:
  clic droit > Ouvrir, puis confirmer.

EOF
