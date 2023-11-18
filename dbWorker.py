from mysql import connector
from mysql.connector import Error
import logging
from cfg import DB_HOST, DB_PASSWORD, DB_USER,DB_NAME
import time
logging.basicConfig(level=logging.INFO)


class DB():
    def __init__(self, name=DB_NAME) -> None:
        self.dbPath = name
        self.prepareBase()

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
        cur.execute("""CREATE TABLE IF NOT EXISTS Transactions(
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        content JSON,
        cost INTEGER
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS Partitions (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        name TEXT
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS Menu(
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        partition_id INTEGER,
        name TEXT,
        description TEXT,
        cost DOUBLE,
        image_path TEXT,
        FOREIGN KEY (partition_id) REFERENCES Partitions (id) ON DELETE CASCADE  
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS Privileges(
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        tg_id INTEGER,
        level INTEGER
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        tg_id INTEGER UNIQUE
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS Addresses(
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        tg_id INTEGER,
        address TEXT,
        FOREIGN KEY (tg_id) REFERENCES Users (tg_id) ON DELETE CASCADE
        )""")
        base.commit();cur.close();base.close()




# ---------PARTITION-------
    def addPartition(self, name: str) -> None:
        base, cur = self.connect()
        cur.execute("INSERT INTO Partitions (name) VALUES (%s )",(name,))
        base.commit();cur.close();base.close()


    def delPartition(self, id: int) -> None:
        base,cur = self.connect()
        cur.execute("DELETE FROM Partitions WHERE id = %s",(id,))
        base.commit();cur.close();base.close()


    def editPartition(self, id: int, name: str) -> None:
        base,cur = self.connect()
        cur.execute("UPDATE Partitions SET name = %s WHERE id = %s",(name,id))
        base.commit();cur.close();base.close()


    def getPartitionsWithID(self) -> [int,str]:
        base,cur = self.connect()
        cur.execute("SELECT id, name FROM PARTITIONS")
        res = cur.fetchall()
        cur.close();base.close()
        return res
    # -------------END-------------




    # -----------POSITION----------
    def addPosition(self, partition_id: int, name: str, description: str, cost: float, path: str ) -> None:
        base,cur = self.connect()
        cur.execute("INSERT INTO Menu (partition_id, name, description, cost, image_path) VALUES (%s, %s, %s, %s, %s)",(partition_id,name,description,cost,path))
        base.commit();cur.close();base.close()


    def delPosition(self, id: int) -> None:
        base, cur = self.connect()
        cur.execute("DELETE FROM Menu WHERE id = %s",(id,))
        base.commit();cur.close();base.close()


    def getPositions(self):
        base,cur = self.connect()
        cur.execute("SELECT  * FROM Menu")
        res = cur.fetchall()
        cur.close();base.close()
        return res


    def getPositionsWithID(self, partition_id: int):
        base, cur = self.connect()
        cur.execute("SELECT id, name FROM Menu WHERE partition_id = %s",(partition_id,))
        res = cur.fetchall()
        cur.close();base.close()
        return res


    def getPositionsIdsDict(self):
        base, cur = self.connect()
        cur.execute("SELECT id FROM Menu")
        res = {i[0]:0 for i in cur.fetchall()}
        cur.close(); base.close()
        return res


    def getPositionsNamesDict(self):
        base, cur = self.connect()
        cur.execute("SELECT id,name, cost FROM Menu")
        res = {i[0]: (i[1],i[2]) for i in cur.fetchall()}
        cur.close(); base.close()
        return res


    def getPos(self, id):
        base, cur = self.connect()
        cur.execute("SELECT * FROM Menu WHERE id = %s", (id,))
        res = cur.fetchall()
        cur.close();base.close()
        return res
    # -------------END-------------




    # ------------ADDRESSES------------
    def addAddress(self,tg_id, addr):
        base, cur = self.connect()
        cur.execute("INSERT INTO Addresses (tg_id, address) VALUES (%s, %s)",(tg_id, addr))
        base.commit();cur.close();base.close()


    def delAddress(self,id):
        base, cur = self.connect()
        cur.execute("DELETE FROM Addresses WHERE id = %s", (id,))
        base.commit();cur.close();base.close()


    def getUserAddresses(self, tg_id):
        base, cur = self.connect()
        cur.execute("SELECT id, address FROM Addresses WHERE tg_id = %s", (tg_id,))
        res = cur.fetchall()
        cur.close(); base.close()
        return res


    def getAddressByID(self,id):
        base, cur = self.connect()
        cur.execute("SELECT address FROM Addresses WHERE id = %s",(id,))
        res = cur.fetchone()
        cur.close();base.close()
        return res
    # -------------END-------------




    # ------------USERS--------------
    def addUser(self, tg_id):
        base, cur = self.connect()
        cur.execute("INSERT INTO Users (tg_id) VALUES (%s)",(tg_id,))
        base.commit();cur.close();base.close()


    def getUsers(self):
        base, cur = self.connect()
        cur.execute("SELECT tg_id FROM Users")
        res = cur.fetchall()
        cur.close();base.close()
        return res
    # -------------END-------------




    # ------------STAFF------------
    def getStaff(self) -> [int]:
        base, cur = self.connect()
        cur.execute("SELECT tg_id FROM Privileges")
        res = cur.fetchall()
        cur.close();base.close()
        return res


    def addAdmin(self, tg_id) -> None:
        base, cur = self.connect()
        cur.execute("INSERT INTO Privileges (tg_id, level) VALUES (%s, %s)",(tg_id, 1))
        base.commit(); cur.close(); base.close()


    def addDeliver(self, tg_id) -> None:
        base, cur = self.connect()
        cur.execute("INSERT INTO Privileges (tg_id, level )VALUES (%s, %s)",(tg_id, 2))
        base.commit(); cur.close(); base.close()


    def delUser(self, id) -> None:
        base, cur = self.connect()
        cur.execute("DELETE FROM Privileges WHERE id = %s", (id,))
        base.commit(); cur.close(); base.close()
    # -------------END-------------


if __name__ == "__main__":
    pass