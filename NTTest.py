from networktables import NetworkTables
from networktables import NetworkTablesInstance
import time

ntinst = NetworkTablesInstance.getDefault()
ntinst.startClientTeam(2635)
ntinst.startDSClient()

sd = NetworkTables.getTable("MonsterVision")

while True:
    sd.putNumber("time", time.time())
    ntinst.flush()
    time.sleep(1)

