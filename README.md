amortization-calculator
========================

A simple Flask app to calculate a loan's amortization schedule. 


Configuration steps:

Clone the project:
```
https://github.com/cmachine/amort.git
```

Environment requires python 2.7

To check python version:
```
python --version
```

If not 2.7.x, install Python 2.7. Follow direction at https://www.python.org/downloads/ or use a package manager

Ubuntu:
```
sudo apt-get install python2.7
```

Redhat:
```
yum install python-devel
```

Mac OSX (using Homebrew):
```
brew install python
```

You will also need some python module dependencies. The easiest and best way to install these is using pip. pip should be installed already. 

To check, run 
```
command -v pip
```

If pip location is not returned download get-pip.py from https://pip.pypa.io/en/stable/installing/

Then run
```
python get-pip.py
```
Use pip to install dependencies. Run the following from this repo's directory:
```
pip install -r requirements.txt
```

Start the app by running amort.py:
```
python amort.py
```

The app should be viewable by a local web browswer at http://localhost:8080/

To run unit tests:
```
python tests.py
```
