#!/usr/bin/env bash

# update_python_path.sh
# Updates PATH to prioritize Python 3.13 over Python 3.14

# Python 3.13 path (Windows path format)
PYTHON313_PATH="C:/Users/nobu/AppData/Local/Microsoft/WindowsApps/PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0"

# Convert to Git Bash format (POSIX)
PYTHON313_POSIX="/c/Users/nobu/AppData/Local/Microsoft/WindowsApps/PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0"
PYTHON313_SCRIPTS="/c/Users/nobu/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0/LocalCache/local-packages/Python313/Scripts"

# Remove Python 3.14 from PATH
export PATH=$(echo $PATH | sed -e 's|:/c/Python314/Scripts||g' -e 's|:/c/Python314||g' -e 's|^/c/Python314/Scripts:||g' -e 's|^/c/Python314:||g')

# Add Python 3.13 to the beginning of PATH
export PATH="$PYTHON313_POSIX:$PYTHON313_SCRIPTS:$PATH"

echo "✅ Updated PATH to use Python 3.13"
echo ""
echo "Current Python version:"
python --version
echo ""
echo "Python location:"
which python
echo ""
echo "Pip location:"
which pip
echo ""
echo "=============================="
which uv
uv --version