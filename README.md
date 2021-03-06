# replicated-data-service #
Our replicated data service focus on optimizing the efficiency of the servers to process client requests in the quickest and most organized way possible.Our project simulates bank transactions between a client and the bank allowing clients to withdraw, deposit and check on their balance with the minimum latency delay possible.

## Group Members ##
* [Shenghua You](https://github.com/shenghuayou), shenghuayou@gmail.com
* [Victor Fung](https://github.com/VictorFung1), victor.fung122@gmail.com
* [Zhenxian Huang](https://github.com/zhengxianh), 619913512hzx@gmail.com 

## Usage ##
By default controller is set to port 9996, so don't re-use the port for any servers
The controller must be up and running first before any servers or clients/bots can connect.
```
To run controller.py
python controller.py

To run server.py
python server.py [port-id]

To run the bot.py
python bot.py [client-id]
```
## Screen Command ##
The screen program allows you to use multiple windows in Unix. In other words the screen command lets you detach from a terminal session and then attach it back at a later time. (use command "screen" to keep running server codes and controller codes on AWS)
```
screen  #create a new screen session
screen -ls  #check running screens
screen -r screenID   #resume to a screen
screen -X -S screenID kill   #end a screen
```

## Setup MySQL Replication ##
#### Master (AWS RDS)
  1. Create new slave
```mysql
CREATE USER '[SLAVE USERNAME]'@'%' IDENTIFIED BY '[SLAVE PASSWORD]';
```
  2. Give it access
```mysql
GRANT REPLICATION SLAVE ON *.* TO '[SLAVE USERNAME]'@'%';  
```
#### Slave (AWS EC2 Server)
  1. [Bash] Import the database from master
```bash
mysqldump -h [SERVER IP] -u root -p [DB NAME] > dump.sql
```
  2. [Bash] Import the dump.sql into your database
```bash
mysql [DB NAME] < dump.sql
```
  3. [Bash] Edit the /etc/my.cnf - will require root access, add the follow lines. Remember to keep server-id different (currently using 10, so next is 11, etc...)
```
#Give the server a unique ID
server-id               = [CHANGE THIS TO NUMBER]

#Ensure there's a relay log
relay-log               = /var/lib/mysql/mysql-relay-bin.log

#Keep the binary log on
log_bin                 = /var/lib/mysql/mysql-bin.log
replicate_do_db            = [DB NAME]
```
  4. [Bash] Restart mysqld
```bash
service mysqld restart
```
#### Master-Slave Connection Creation
  1. On master (RDS) - Keep note of File and Position. We will need to fill these infomation in next step.
```mysql
show master status;
+----------------------------+----------+--------------+------------------+-------------------+
| File                       | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
+----------------------------+----------+--------------+------------------+-------------------+
| mysql-bin-changelog.010934 |      400 |              |                  |                   |
+----------------------------+----------+--------------+------------------+-------------------+
```
  2. On the slave - Connect to master (RDS) for replication.
```mysql
CHANGE MASTER TO MASTER_HOST=[MASTER IP], MASTER_USER='[SLAVE NAME]', MASTER_PASSWORD='[SLAVE PASSWORD]', MASTER_LOG_FILE='[MASTER FILE] ', MASTER_LOG_POS= [MASTER POSITION];
 ```
  3. On the slave - Start slave for replication.
```mysql
START SLAVE;
```
  4. Make sure the slave started
```myaql
SHOW SLAVE STATUS\G;
```
  5. You can always triple check by adding a new row to database in master then see if it updates in slave.

#### Troubleshooting
- If for some reason you mess up the slave in step 2.
	[mysql] on the slave side
```mysql
reset slave;
```
- If in SHOW SLAVE STATUS\G shows error. Try
```mysql
STOP SLAVE;
SET GLOBAL SQL_SLAVE_SKIP_COUNTER = 1;
START SLAVE;
```
