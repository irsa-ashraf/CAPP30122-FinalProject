echo -e "1. Creating new virtual environment..."

python3 -m venv env 

echo -e "2. Installing Requirements..."

source env/bin/activate 

pip install -r requirements.txt  

echo -e ""
echo -e "Install is complete! Ready to run app.py!"



