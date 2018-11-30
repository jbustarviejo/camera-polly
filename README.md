python3 -m pip install --user virtualenv
python3 -m virtualenv app
source app/bin/activate

Update and install from freeze
pip3 freeze > requirements.txt
pip3 install -r requirements.txt
