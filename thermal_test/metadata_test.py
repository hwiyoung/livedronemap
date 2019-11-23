import subprocess

input_file = "C:/Users/InnoPAM/Desktop/20191121/2-500m/20191121_112030.tiff"
exe = "../exiftool.exe"

process = subprocess.Popen([exe, input_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

metadata = process.stdout.read().decode()
longitude_field = metadata.find('GPS Longitude                   : ')
latitude_field = metadata.find('GPS Latitude                    : ')
altitude_field = metadata.find('GPS Altitude                    : ')
roll_field = metadata.find('MAV Roll')
pitch_field = metadata.find('MAV Pitch')
yaw_field = metadata.find('MAV Yaw')

lon_deg_value = float(metadata[longitude_field+34:longitude_field+34+3])
lon_min_value = float(metadata[longitude_field+34+3+5:longitude_field+34+3+5+2])
lon_sec_value = float(metadata[longitude_field+34+3+5+2+2:longitude_field+34+3+5+2+2+5])
lon_value = lon_deg_value + lon_min_value / 60 + lon_sec_value / 3600


lat_deg_value = float(metadata[latitude_field+34:latitude_field+34+2])
lat_min_value = float(metadata[latitude_field+34+2+5:latitude_field+34+2+5+2])
lat_sec_value = float(metadata[latitude_field+34+2+5+2+2:latitude_field+34+2+5+2+2+5])
lat_value = lat_deg_value + lat_min_value / 60 + lat_sec_value / 3600

alt_value = float(metadata[altitude_field+34:altitude_field+34+5])

roll_value = float(metadata[roll_field+34:roll_field+34+6])

pitch_value = float(metadata[pitch_field+34:pitch_field+34+6])

yaw_value = float(metadata[yaw_field+34:yaw_field+34+6])

print(lon_value, lat_value, alt_value, roll_value, pitch_value, yaw_value)
