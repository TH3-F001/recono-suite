#!/bin/bash

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

source "$SCRIPT_DIR/../common/basic-operations.lib"
source "$SCRIPT_DIR/install.lib"

echo "📦 Installing Subdomainizer..."
if ! command_exists subdomainizer; then
    INSTALL_DIR="$HOME/SubDomainizer"
    VENV_DIR="$INSTALL_DIR/venv"
    LINK_NAME="/usr/local/bin/subdomainizer"
    WRAPPER_SCRIPT="$INSTALL_DIR/subdomainizer.sh"

    git clone https://github.com/nsonaniya2010/SubDomainizer.git "$INSTALL_DIR"
    python3 -m venv "$VENV_DIR"

    "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

    cat << EOF > "$WRAPPER_SCRIPT"
    #!/bin/bash
    source "$VENV_DIR/bin/activate"
    python "$INSTALL_DIR/SubDomainizer.py" "\$@"
EOF

    chmod +x "$WRAPPER_SCRIPT"

    sudo ln -sf "$WRAPPER_SCRIPT" "$LINK_NAME"
else
    echo -e "\tSubdomainizer is already installed!"
fi

if command_exists subdomainizer; then
    print_success "SubDomainizer successfully installed"
else
    print_error "An problem occurred while installing SubDomainizer"
    exit 1
fi
