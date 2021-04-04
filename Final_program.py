import pycurl, json
from StringIO import StringIO
import RPi.GPIO as GPIO
from sense_hat import SenseHat
import time
from time import asctime

sense = SenseHat()
sense.clear()

cold = 37
hot = 40
pushMessage = ""

#############################################
#Code for Display number
 OFFSET_LEFT = 1
 OFFSET_TOP = 2

 NUMS = [1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, # 0
         0, 1. 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, # 1
         1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, # 2
         1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, # 3
         1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, # 4
         1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, # 5
         1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, # 6
         1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, # 7
         1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, # 8
         1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1] # 9

 #Display a single digit (0-9)
 def show_digit(val, xd, yd, r, g, b)
     offset = val * 15
     for p in range(offset, offset + 15):
         xt = p % 3
         yt = (p - offset) // 3
         sense.set_pixel(xt + xd, yt + yd, r * NUMS[p], g * NUMS[p], b * NUMS[p])

#Display a two-digits positive number (0-99)
 def show_number(val, r, g, b)
     abs_val = abs(val)
     tens = abs_val // 10
     units = abs_val() % 10
     if (abs_val > 9): show_digit(tens, OFFSET_LEFT, OFFSET_TOP, r, g, b)
     show_digit(units, OFFSET_LEFT + 4, OFFSET_TOP, r, g, b)

#############################

temp = round(sense.get_temperature())
humidity = round(sense.get_humidity())
pressure = round(sense.get_pressure())
message = " T = %dF, H = %d, P = %d" %(temp, humidity, pressure)

#setup instaPush variables
# add our Instapush Application ID
appID = "59bb6e6ba4c48a1cd67e33d"

#add our Instapush Application secret
appSecret = "fd127d824390296b5f84818cddafeebe"
pushEvent = "TempNotify"

#use Curl to post to the InstaPush API
c = pycurl.Curl()

#set api url
c.setopt(c.URL, 'https://api.instapush.im/v1/post')

#setup custom headers for authentication variables and content type
c.setopt(c.HTTPHEADER, ['x-instapush-appid: ' + appID,
                            'x-instapush-appsecret: ' + appSecret,
                             'Content-Type: application/json'])

#use this to capture the response from our push API call
buffer = StringIO()
##########################################
def p(pushMessage):
    #create a dict structure for the JSON data to post
    json_fields = {}

    #setup JSON values
    json_fields['event'] = pushEvent
    json_fields['trackers'] = {}
    json_fields['trackers']['message'] = pushMessage
    #print(json_fields
    postfields = json.dumps(json_fields)

    #make sure to send the JSON with post
    c.setopt(c.POSTFIELDS, postfields)

    #set this so we can capture the response in our buffer
    c.setopt(c.WRITEFUNCTION, buffer.write)

    #uncomment to see the post sent
    c.setopt(c.VERBOSE, True)

#setup an indefinite loopo that looks for temperature
while True:
    temp = round(sense.get_temperature())
    humidity = round(sense.get_humidity())
    pressure = round(sense.get_pressure())
    message = " T = %dF, H = %d, P = %d" % (temp, humidity, pressure)
    time.sleep(4)
    log = open('weather.txt', "a")
    now = str(asctime())
    temp = int(temp)
    show_number(temp, 200, 0, 60)
    temp1 = temp

    log.write(now + '' + message + '\n')
    print(message)
    log.close()
    time.sleep(5)

    if temp >= hot:
        pushMessage = "Its hot: " + message
        p(pushMessage)
        c.perform()
        #capture the response from the server
        body = buffer.getvalue()
        pushMessage = ""

    elif temp <= cold:
        pushMessage = "Its cold: " + message
        p(pushMessage)
        c.perform()
        # capture the response from the server
        body = buffer.getvalue()
        pushMessage = ""

    #print the response
    #print(body)

    #reset the buffer
    buffer.truncate(0)
    buffer.seek(0)

#cleanup
c.close()
GPIO.cleanup()
