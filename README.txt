This is a server side of a smart-sleeper project

This server will manage the api side, the connection to DB and the ML algorithm

Run Api:

install flask by "pip install flask" command

run this command "flask --app API run"

Run Mysql:

sudo apt install mysql-server

sudo systemctl start mysql.service

to get into mysql run "sudo mysql"

to add user please write inside the mysql  CREATE USER 'artiom'@'localhost' IDENTIFIED BY 'password';

run "python3 MySQL.py" to create the DB if necessary please change the name and the password
