from mysql import connector
from mysql.connector import Error
import logging
from cfg import DB_HOST, DB_PASSWORD, DB_USER,DB_NAME
import time
logging.basicConfig(level=logging.INFO)


class DB():
    def __init__(self, name=DB_NAME) -> None:
        self.dbPath = name


    def connect(self):
        try:
            logging.log(20, "Trying to connect to db")
            base = connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=self.dbPath)
            cur = base.cursor()
        except Error as e:
            logging.log(20, "Trying to connect to db again")
            time.sleep(5)
            self.connect()
        return base, cur


    def prepareBase(self):
        base,cur = self.connect()
        cur.execute("""CREATE TABLE IF NOT EXIST Partitions (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name TEXT
            )""")
        cur.execute("""CREATE TABLE IF NOT EXIST Menu(
            id INT PRIMARY KEY AUTO_INCREMENT,
            name TEXT,
            description TEXT,
            cost FLOAT,
            image_path TEXT,
            partition INT,
            FOREIGN KEY (partition) REFERENCES Partitions (id) ON DELETE CASCADE  
            )""")
        base.commit();cur.close();base.close()


    def addPartition(self) -> None:
        pass


    def delPartition(self) -> None:
        pass


    def addPosition(self) -> None:
        pass


    def delPosition(self) -> None:
        pass


if __name__ == "__main__":
    pass