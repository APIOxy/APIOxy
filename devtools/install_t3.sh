# Temporarily change directory to $HOME to install software
pushd .
#APIOxy
export PYTHONPATH=$PYTHONPATH:$(pwd)
echo "export PYTHONPATH=$PYTHONPATH:$(pwd)" >> ~/.bashrc

cd ..
# RMG-database
git clone https://github.com/ReactionMechanismGenerator/RMG-database
#changing to API_db branch. Future this will be deprecated
cd RMG-database
git checkout api_db
cd ..
# RMG-Py
git clone https://github.com/ReactionMechanismGenerator/RMG-Py
cd RMG-Py
export PYTHONPATH=$PYTHONPATH:$(pwd)
echo "export PYTHONPATH=$PYTHONPATH:$(pwd)" >> ~/.bashrc
# compile RMG
make
#changing to api_degradation branch. Future this will be deprecated
git checkout api_degradation

cd ..
# ARC
git clone https://github.com/ReactionMechanismGenerator/ARC
cd ARC
export PYTHONPATH=$PYTHONPATH:$(pwd)
echo "export PYTHONPATH=$PYTHONPATH:$(pwd)" >> ~/.bashrc

cd ..
# T3
git clone https://github.com/ReactionMechanismGenerator/T3.git
cd T3
export PYTHONPATH=$PYTHONPATH:$(pwd)
echo "export PYTHONPATH=$PYTHONPATH:$(pwd)" >> ~/.bashrc


# Restore original directory
popd || exit
