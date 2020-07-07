import sys 
import trace 
import threading 
import time
import numpy 
import can
import os
import RPi.GPIO as GPIO
import sys

# Extend class of can.Listener 
# When message is sending over CAN bus, this class activate on_message_received function
# Parameters:
# minID = Int minumunID that activate the function
# maxID = Int maximunID that activate the function
# target = Fuction function that is executed when one message arrive 
class MyListener( can.Listener ):
	def __init__ ( self , target, **keywords ):
		self.target = target
		if 'needMsg' in keywords:
			self.needMsg = keywords['needMsg']
		else:
			self.needMsg = False

	def on_message_received ( self , msg ):
		# Execute the parameter function
		if self.needMsg:
			self.target (msg)
		else:
			self.target()

# Extend class of threading.Thread
# Class to control threads 
# Parameters
# target = Fuction. function that thread have to do
# waitTime = Int . time in second between thread  to repeat the fuction , defaul 1 second
# work = Boolean. If thread  execute the fuction or not , default True	
class stopThread( threading.Thread ):
	
	def __init__ ( self , *args , **keywords ):
		# Get parameters
		threading.Thread.__init__( self )
		self.target = keywords[ 'target' ] 
		self.do_run = True
		if 'waitTime' in keywords:
			self.waitTime = keywords[ 'waitTime' ]
		else:
			self.waitTime = 1
		if 'work' in keywords:
			self.do_work = keywords[ 'work' ]
		else:
			self.do_work = True
			
	# Finish the thread loop
	def kill(self):
		self.do_run = False	
	
	# Stop the execution of the fuction	
	def stop(self):
		self.do_work = False
	
	# Restart the execution of the fuction
	def restart(self):
		self.do_work = True

	# Loop that does the function when is necessary
	def run( self ):
		while self.do_run:
			if self.do_work:
				self.target()
			time.sleep(self.waitTime)

	# Return if the thread is executing the fuction or not 
	def isWorking ():
		return self.do_work

# Function that change random number between 70 to 110 and send message with this number
def sendMessage():
	global bus
	randomNumber = numpy.random.choice( 40 )
	randomNumber =  randomNumber + 70 
	msg = can.Message( arbitration_id = 0x2de , data = [ 0 , 0, 0, 0, 0, 0, 0, randomNumber ] , extended_id = False )
	try:
		bus.send(msg)	
	except can.CanError:
		print("Message NOT sent")
		
# Function that put the light up 1 second
def lightUp ():			
	GPIO.output( 22 , True )
	time.sleep( 1 )
	GPIO.output( 22 , False )

# Function that create CAN message and send it over the bus	
def sendAttackMessage():
	global bus
	# Create message
	msg = can.Message( arbitration_id = 0x2ff , data = [ 0 , 0 , 0 , 0 , 0 , 0 , 0 , 150 ] , extended_id = False )
	# Send message
	try:
		bus.send( msg )
	except can.CanError:
		print( "Message not send" )

# Function that send message over CAN bus if the button is pressed
def pushButon():
	global bus
	msg = can.Message( arbitration_id = 0x7ff , data = [0, 25, 0, 1, 3, 1, 4, 1] , extended_id = False )
	# If the button is pressed , send message
	if  not GPIO.input( 24 ):
		try:
			bus.send( msg )
		except can.CanError:
			print("Message not send")

# Funtion that chande the duty cycle of the pwd_led 
# depending of can message content 
# Parameters
# msg = can message	of can.Listener	
def changeLedDuty ( msg ):
	global pwd_led
	# Get the last byte of the message data
	data = msg.data[7]
	# Depending of the content of the message change the led duty cycle
	# to 0 , 10 or 100 %
	if ( data < 85 ):
		duty = 0
	else:
		if ( data >= 85 ) and ( data < 105 ):
			duty = 10
		else:
			duty = 100	
	pwd_led.ChangeDutyCycle( duty )
		
def inicialitzation ( filters ):
	global bus
	GPIO.setmode( GPIO.BCM )
	GPIO.setwarnings( False )
	os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
	# Bring up can0
	can_interface = 'can0'
	if filters == None:
		bus = can.interface.Bus( can_interface , bustype = 'socketcan_native' )
	else:
		bus = can.interface.Bus( can_interface , bustype = 'socketcan_native' , can_filters = filters )
	
def ECUI():
	global bus
	try:
		GPIO.setup( 24 , GPIO.IN , pull_up_down=GPIO.PUD_UP )
		msg = can.Message(arbitration_id=0x7de,data=[0, 25, 0, 1, 3, 1, 4, 1],extended_id=False)
		# Began infinitive loop
		while True:
			# If the button is pressed,  send message
			try:
				if  not GPIO.input( 24 ):
					bus.send(msg)
			except can.CanError:
					print("Message not send")
			# Wait one second
			time.sleep(1)
	except:
		print ("something wrong")
		
def ECUII ():
	global bus
	global pwd_led
	try:
		GPIO.setup( 22 , GPIO.OUT )
		pwd_led = GPIO.PWM ( 22, 50 )
		# Start the led in off
		pwd_led.start(0)
		myList = MyListener (  changeLedDuty , needMsg = True )
		# Enable the Listener
		notifier = can.Notifier( bus, [myList] )
		# Start Infinite Loop
		while True:
			time.sleep(1)
	except:
		print ("something wrong")
	finally: 
		# Terminate the conections 
		notifier.running.clear()
		
		
def ECUIII():
	global bus
	try:
		GPIO.setup( 23 , GPIO.IN , pull_up_down = GPIO.PUD_UP )
		GPIO.setup( 24 , GPIO.IN , pull_up_down = GPIO.PUD_UP )
		thr1 = stopThread( target = sendAttackMessage , work = False , waitTime = 0.25)
		thr2 = stopThread( target = pushButon )
		thr1.start()
		thr2.start()	
		# Continue the loop until one of the threads be killed
		while (  thr2.is_alive() and thr1.is_alive()  ):
			# If the button if pressed
			if  not GPIO.input( 23 ):
				# If the thr1 is executing the fuction
							enable = thr1.isWorking()
							if enable:
						# Stop the execution
									thr1.stop()
				# Else
							else:
						# Restart the execution
									thr1.restart()
			time.sleep(1)
	except:
		print ("something wrong")
	finally: 
		# Terminate the conections 
		# If the thr1 still alive , killed 
		if (  thr1.is_alive() ):
			thr1.kill()
		# If the thr2 still alive , killed 
		if ( thr2.is_alive() ):
			thr2.kill()
		
def ECUIV():
	global bus
	try:
		GPIO.setup( 22 , GPIO.OUT )
		t1 = stopThread( target = sendMessage )
		# Enable the thread 
		t1.start()
		# Initialize the listener
		myList = MyListener (  lightUp )
		# Enable the listener
		notifier = can.Notifier( bus, [myList] )
		#  Continue the loop until  the threads be killed
		while (  t1.is_alive() ):
			time.sleep(1);
	except:
		print ("something wrong")
	finally: 
		# Terminate the conections 
		# If the thr1 still alive , killed 
		if (  t1.is_alive() ):
				t1.kill()
		notifier.running.clear()
			
try:
	global bus
	# Bring up GPIO led
	ECU = int(sys.argv[1] )
	ECUS = { 1 : ECUI, 2 : ECUII , 3 : ECUIII , 4 : ECUIV }
	if  ECU == 4 :
		filters = [{ "can_id" : 0x7ce , "can_mask" : 0xfce }]
	else:
		if ECU == 2:
			filters = [{ "can_id" : 0x2ce , "can_mask" : 0xfce }]
		else:
			filters = None
	inicialitzation ( filters )
	ECUS[ ECU ]()
	# Initialize thread
# If the program is stopped manually  goes here      
except KeyboardInterrupt:
    print ("key error")
# If the program is stopped by some error  goes here 
except:
    print ("something wrong")
finally: 
	# Terminate the conections 
	GPIO.cleanup()
	bus.shutdown()
