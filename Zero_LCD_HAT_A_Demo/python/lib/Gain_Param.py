import os
import re 
import time
import socket


class Gain_Param():
    Get_back = [0,0,0,0,0] # Returns the memory of Disk     
    flag = 0 # Unmounted or unpartitioned   
    def GET_IP(self):
        #There will be exceptions, get stuck, get it carefully
        #Threading is better
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect_ex(('8.8.8.8',80))
        ip=s.getsockname()[0]
        s.close()
        return ip


    def GET_Temp(self):
        """Get CPU temperature, compatible with Orange Pi and Raspberry Pi"""
        thermal_zones = [
            '/sys/class/thermal/thermal_zone0/temp',
            '/sys/class/thermal/thermal_zone1/temp',
            '/sys/devices/virtual/thermal/thermal_zone0/temp'
        ]
        
        for zone in thermal_zones:
            try:
                if os.path.exists(zone):
                    with open(zone, 'rt') as f:
                        temp = int(f.read().strip()) / 1000.0
                        # Sanity check - temperature should be reasonable
                        if 0 < temp < 150:
                            return temp
            except:
                continue
                
        # If no thermal zone found, return None
        return None

    

                  
