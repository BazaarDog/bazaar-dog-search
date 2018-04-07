# bazaar-dog-search

[![Build Status](https://travis-ci.org/BazaarDog/bazaar-dog-search.svg?branch=master)](https://travis-ci.org/BazaarDog/bazaar-dog-search)


# requirements


```
# debian-based system requirements
sudo apt-get install python3-pip git sqlite3
```


# install 



```
# get the code

git clone https://github.com/BazaarDog/bazaar-dog-search.git
cd bazaar-dog-search


# install a python3 virtual environment

pip3 install virtualenv
virtualenv ~/.bazaar_dog_venv
source ~/.bazaar_dog_venv/bin/activate

# install project requirements

pip install -r requirements.txt

./manage.py makemigrations ob # Breaks here due to psql specific issues.
./manage.py migrate
./manage.py runserver

```
