
#assumes anaconda-client and conda-build have been installed
# conda install -y anaconda-client
# conda install -y conda-build
# anaconda login


mkdir -p /tmp/conda-build
rm -rf /tmp/conda-build


conda-build conda/ -c cadquery -c conda-forge --croot /tmp/conda-build 

conda convert /tmp/conda-build/linux-64/*.tar.bz2 --platform all  -o /tmp/conda-build

# # convert package to other platforms, all converts to:
# platforms=( osx-64 linux-32 linux-64 win-32 win-64 )
# find /tmp/conda-build/linux-64/ -name *.tar.bz2 | while read file
# do
#     echo $file
#     #conda convert --platform all $file  -o /tmp/conda-build 
#     for platform in "${platforms[@]}"
#     do
#        conda convert --platform $platform $file  -o /tmp/conda-build/
#     done
# done

anaconda upload -f /tmp/conda-build/*/*.tar.bz2
# find /tmp/conda-build/ -name *.tar.bz2 | while read file
# do
#     echo $file
#     anaconda upload $file
# done
