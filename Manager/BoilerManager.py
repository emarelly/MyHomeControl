import sys
import BoilerStatus
import Boiler
import ManagerRestApi
import threading
# main
status = BoilerStatus.BoilerStatus()

Blm = Boiler.Boiler(status)
# starting Rest API server with link to status class
tr = threading.Thread(target=ManagerRestApi.runserver, args=(status,))
tr.start()
# start boiler monitor
Blm.BoilerMonitor()
print ("exit Boiler Monitor!!!")
