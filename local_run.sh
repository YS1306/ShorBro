echo "Initiating the app"
echo "Trying to get the app into running state"

if [ -d ".project_env" ];
then 
    echo "Virtual Environment Enabled" 
else 
    echo "Environment not installed"
    echo "Install the environment first using local_setup.sh"
    exit N 
fi

. .project_env/bin/activate 
export ENV=development
export FLASK_APP=main.py
export FLASK_DEBUG=development
python3 main.py
deactivate 