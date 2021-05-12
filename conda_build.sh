
pkg='paramak'
array=( 3.6 3.7 3.8 )

rm -rf /tmp/conda-build

for i in "${array[@]}"
do
	conda-build conda/ -c cadquery -c conda-forge --croot /tmp/conda-build --python $i 
	# conda build conda/meta.yaml -c cadquery -c conda-forge --croot /tmp/cbld
done


# # convert package to other platforms
platforms=( osx-64 linux-32 linux-64 win-32 win-64 )
platforms=( linux-64 )
find /tmp/conda-build/linux-64/ -name *.tar.bz2 | while read file
do
    echo $file
    #conda convert --platform all $file  -o $HOME/conda-bld/
    for platform in "${platforms[@]}"
    do
       conda convert --platform $platform $file  -o /tmp/conda-build/
    done
done

# conda install anaconda-client

# find /tmp/conda-build/ -name *.tar.bz2 | while read file
# do
#     echo $file
#     anaconda upload $file
# done
