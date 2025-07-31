#!/usr/bin/env bash

VENV_DIR=~/.venvs/{{ cookiecutter.package_name }}

APP_NAME="{{ cookiecutter.package_name }}"
PACKAGE_NAME="{{ cookiecutter.package_name.replace("-", "_") }}"
PACKAGE_VERSION="0.1.0"

APP_SETTINGS_DIR=~/.${APP_NAME}
APP_CONFIG=${APP_SETTINGS_DIR}/${APP_NAME}.toml
APP_LOG=${APP_SETTINGS_DIR}/${APP_NAME}.log

SUPERVISOR_CONF=/etc/supervisor/conf.d/${APP_NAME}.conf

# -----------------------------------------------------------------------------
# Create config
# -----------------------------------------------------------------------------

# Create app settings dir
# [ -d ${APP_SETTINGS_DIR} ] || mkdir -p ${APP_SETTINGS_DIR}

# # Create config file
# if [ ! -f ${APP_CONFIG} ]; then
#     sh -c "cat > ${APP_CONFIG}" <<EOF
# [default]
# foo = bar
# EOF
#     echo "Created ${APP_CONFIG}"
# else
#     echo "[✔] ${APP_CONFIG}"
# fi

# # Create log file
# if [ ! -f ${APP_LOG} ]; then
#     touch ${APP_LOG}
# fi

# -----------------------------------------------------------------------------
# Create Virtualenv
# -----------------------------------------------------------------------------

if ! command -v uv &> /dev/null; then
    echo "==> uv not found. Installing..."
    if command -v curl &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"  # in case it's installed via cargo
    else
        echo "curl is not available. Please install uv manually."
        exit 1
    fi
else
    echo "[✔] uv is installed: $(command -v uv)"
fi

if [ ! -d ${VENV_DIR} ]; then
    echo "==> Create virtualenv with uv..."
    uv venv ${VENV_DIR}
else
    echo "[✔] ${VENV_DIR}"
fi

# -----------------------------------------------------------------------------
# Install App
# -----------------------------------------------------------------------------

cwd=$(pwd)

source ${VENV_DIR}/bin/activate

if [ "$1" == "--force" ]; then
    echo "==> Force install ${APP_NAME}..."
    uv pip install --force-reinstall https://xstudios-pypi.s3.amazonaws.com/${PACKAGE_NAME}-${PACKAGE_VERSION}-py3-none-any.whl
fi

if ! hash ${APP_NAME} 2>/dev/null; then
    echo "==> Install ${APP_NAME}..."
    uv pip install -U pip wheel
    uv pip install https://xstudios-pypi.s3.amazonaws.com/${PACKAGE_NAME}-${PACKAGE_VERSION}-py3-none-any.whl
else
    echo "[✔] $(command -v ${APP_NAME})"
fi

# -----------------------------------------------------------------------------
# Install & Configure Supervisor
# -----------------------------------------------------------------------------

if [ ! -f /usr/bin/supervisorctl ]; then
    echo "==> Install Supervisor..."
    sudo apt install -y supervisor
fi

cd ${cwd}

# Copy supervisor.conf file
if [ ! -f ${SUPERVISOR_CONF} ]; then
    echo "==> Create supervisor ${APP_NAME}.conf..."
    sudo sh -c "cat > ${SUPERVISOR_CONF}" <<EOF
[program:${PACKAGE_NAME}]
command=${VENV_DIR}/bin/${APP_NAME} --log-level=DEBUG
process_name=%(program_name)s
user=${USER}
autostart=true
autorestart=true
EOF
    echo "Created ${SUPERVISOR_CONF}"
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl start ${PACKAGE_NAME}
else
    echo "[✔] ${SUPERVISOR_CONF}"
fi

echo "==> ALL DONE!"
