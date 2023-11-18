import re

def getPartition(line:str) -> str:
    return ' '.join(line.split()[1:])


def preparePosition(line: str) -> str or int:
    name = re.search("(?<=Название -).+",line)
    description = re.search("(?<=Описание -).+",line)
    cost = re.search("(?<=Стоимость -).+", line)
    partition = re.search("(?<=Раздел -).+", line)
    if any([name==None,description==None,cost==None,partition==None]):
        return -1
    name = name.group().strip()
    description = description.group().strip()
    cost = float(cost.group())
    partition = int(partition.group())
    return (partition, name, description, cost)

if __name__ == "__main__":
    print(preparePosition("""Название - флдаов
    Описание -ывлдапоы
    Стоимость - 10.01
    Раздел - 1"""))
