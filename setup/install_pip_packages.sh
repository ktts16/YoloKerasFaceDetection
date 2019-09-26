# install required Python packages 
for req in $(cat pip_requirements.txt); do pip install $req; done
