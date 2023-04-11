if [ -d ".project_env" ] ;
then 
    echo "Environment already installed. Installing requirements through pip.";
else 
    echo "Installing a new environment and installing using pip."
    python3 -m venv .project_env
fi

#Environment activation  
. .project_env/bin/activate 

#installing packages
pip install --upgrade pip
pip install -r requirements.txt 

# deactivating the environment as the task is completed
deactivate 
