import time
import os
import can
import matplotlib.pyplot as plt
from pandas import DataFrame
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# Extend class of can.Listener 
# When message is sending over CAN bus, this class activate on_message_received function
# Parameters:
# minID = Int minumunID that activate the function
# maxID = Int maximunID that activate the function
# target = Fuction function that is executed when one message arrive 
class MyListener( can.Listener ):
	def __init__ (self, minID , maxID , target ):
		self.minID = minID
		self.maxID = maxID
		self.target = target
	
	def on_message_received ( self , msg ):
		if ( msg.arbitration_id >= self.minID ) and ( msg.arbitration_id <= self.maxID ):
			self.target ( msg )
# Function that get the information of the message and keep it in a list
# Parameter
# msg = can.message . Message of CAN bus
def getData ( msg ):
	global currentTime
	global data
	# Get the message content
	mesgData = msg.data[7]
	# Get the time when the message is reciving
	partitionalTime = time.time ()
	timeR = round( partitionalTime - currentTime , 2 )
	data['x'].append( timeR )
	data['y'].append( mesgData )
	# Get the id of the message
	data['z'].append( int ( str( msg.arbitration_id ) , 16 ) )


# Fuction that make the kmeans and put the results in one output window # with graphs	
def Kmeans():
	global data
	# Initialize data frame with recolects datas
	df = DataFrame( data , columns = [ 'x' , 'y' , 'z' ] ) 
	# Start kmeans
	kmeans = KMeans( n_clusters = 2 ).fit( df )
	# Give the centroids of the kmean
	centroids = kmeans.cluster_centers_
	# Configure the output windows to 9:5 ofthe screen
	plt.figure( figsize = ( 9 , 5 ) )
	# Put the arguments in dictionary
	name = { 'x' : 'Time' , 'y' : 'Data' , 'z':'ID' }
	arg = { 'plt' : plt ,'kmeans' : kmeans , 'df' : df , 'centroids' : centroids , 'number' : 1 , 'name' : name } 
	makeSubPlot ( arg )
	name = { 'x' :'ID' , 'y' : 'Data'   }
	arg = { 'plt' : plt  , 'kmeans' : kmeans , 'df' : df , 'centroids' : centroids , 'number' : 2 , 'name' : name }
	makeSubPlot ( arg )
	# Adjust layout in the window
	plt.tight_layout()
	# See the grafics in a output window
	plt.show()

# Make the two graphs of the window
def makeSubPlot(  arg ):
	# Give parameters
	plt = arg[ 'plt' ]
	number = arg [ 'number' ]
	df = arg [ 'df' ]
	centroids = arg [ 'centroids' ]
	name = arg [ 'name' ]
	kmeans = arg [ 'kmeans' ]
	# If is the firts of the second graph
	if number == 1:
		# Make the first graph with the data of x and y coordinates
		plt.subplot( 1 , 2 , 1 )
		plt.scatter( df [ 'x' ] ,  df [ 'y' ] , c = kmeans.labels_.astype( float ) , )
		# Put the centroids in the grafic in red color
		plt.scatter( centroids [ : , 0 ] , centroids [: , 1 ] , c = 'red', )		
	else:
		# Make the second graph with the data of z and y coordinates
		plt.subplot( 1 , 2 , 2 )
		plt.scatter( df [ 'z' ] ,  df [ 'y' ] , c = kmeans.labels_.astype( float ) , )
		# Put the centroids in the grafic in red color
		plt.scatter( centroids [ : , 2 ] , centroids [: , 1 ] , c = 'red', )	
	# Assign the name to the coordinates
	plt.xlabel( name [ 'x' ] )
	plt.ylabel( name [ 'y' ] )
		
# Main program
try:
	global currentTime
	global data
	#Bring up vcan0
	can_interface = 'vcan0'
	bus = can.interface.Bus( can_interface , bustype = 'socketcan_native' )
	# Initialize the listener	
	myList = MyListener ( 0x2de, 0x2ff )
	# Initialize the listener
	notifier = can.Notifier( bus, [ myList ] )
	# Initialize the time
	currentTime = time.time()
	data = { 'x' : [] , 'y' : [] , 'z' : [] }
	i = 0
	# Wait 10 seconds
	while i < 10:
		i = i  + 1;
		time.sleep(1)
	# Stop the listener
	notifier.stop()
	# Start the kmeans algorithm
	Kmeans()

# If the program is stopped manually  goes here      
except KeyboardInterrupt:
    print ("key error")
# If the program is stopped by some error  goes here 
except:
    print ("something wrong")
finally: 
	# Terminate the conections 	
finally:
	notifier.stop()
	bus.shutdown()
