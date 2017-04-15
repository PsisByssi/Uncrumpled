# This will work in or out of a virtualenv
set-variable -name PYTHON -value $(python -c "import sys; print(sys.exec_prefix)")

#####
# Kivy
#####
curl -o Kivy-1.9.2.dev0-cp35-cp35m-win32.whl https://github.com/nudebandage/uncrumpled_deps/raw/master/windows/Kivy-1.9.2.dev0-cp35-cp35m-win32.whl
pip install Kivy-1.9.2.dev0-cp35-cp35m-win32.whl # PINNED
pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew

#####
# Fzf
#####
choco install fzf
# curl -o fzf.zip https://github.com/junegunn/fzf-bin/releases/download/0.16.6/fzf-0.16.6-windows_386.zip #PINNED
# Expand-Archive fzf.zip
# mkdir bin
# mv fzf\\fzf.exe bin\\fzf.exe
# TODO somereason not borking fml
# $env:Path += ";$($PWD)\bin";
# rm fzf.zip
# rm -r fzf

#####
# pywin32
#####
pip install pypiwin32
python $PYTHON\\Scripts\\pywin32_postinstall.py -install

