cd api
set virtual_env="%CD%\venv"
if not exist %virtual_env% (
    mkdir %virtual_env%
)
python -m venv "%virtual_env%"