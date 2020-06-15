sudo rm ./source/rst/modules.rst
sudo rm ./source/rst/paramak.rst
sudo rm ./source/rst/setup.rst
sudo rm ./source/rst/tests.rst
sudo rm ./source/rst/paramak.parametric_shapes.rst
sphinx-apidoc -o ./source/rst/ ..
sphinx-build -b html ./source/rst/ ./build/html/