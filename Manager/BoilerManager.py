import sys
import BoilerStatus
import Boiler
import ManagerRestApi
# main
status = Boiler.BoilerStatus()
Blm = BoilerManager(status)
# starting Rest API server with link to status class
tr = threading.Thread(target=ManagerRestApi.runserver, args=(status,))
tr.start()
# start boiler monitor
Blm.BoilerMonitor()
print ("exit Boiler Monitor!!!")
