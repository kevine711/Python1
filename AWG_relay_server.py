# ##### Started from online
#http://www.binarytides.com/python-socket-server-code-example/
#By Kevin Ersoy and Julian St. James, for use with AWG

##### Script description
#this script has two main parts
#1. a listen server that takes any number of incoming connections
#   and listens to them, relaying back and forth between the MATLAB server what the connections say
#2. a TCP server open to the matlab client run by iserial on 127.0.0.1 at port 50000
#   this socket is used to relay back and forth information requested by the server
#   python should try to connect to iserial when it opens. If it can't, wait until it can

# Socket server in python using select function

import socket, select
import time  #used for sleep
import string
import sys

if __name__ == "__main__":


  ##### SERVER FOR AWG TO TALK TO ######
  #opened port in firewall on AWG: 49589
  # Wait for AWG to connect to this script at AWG_IP and on AWG_PORT
  AWG_PORT = 50000
  AWG_IP = "127.0.0.1"
  RECV_BUFFER = 4096  # Advisable to keep it as an exponent of 2
  AWG_CONNECTIONS = []

  awg_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  awg_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  
  awg_server_socket.bind((AWG_IP, AWG_PORT))
  awg_server_socket.listen(10)
  AWG_CONNECTIONS.append([awg_server_socket,AWG_IP,AWG_PORT])
  
  while 1:
    socket_list = [item[0] for item in AWG_CONNECTIONS] 
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
    for sock in read_sockets:
      if sock == awg_server_socket: 
        #new connection received, AWG connected, yay
        print 'AWG socket found'
        sockfd, addr = awg_server_socket.accept()
        AWG_CONNECTIONS.append([sockfd,addr[0],addr[1]]) 
        awg_socket = sockfd
  
    if ( len(AWG_CONNECTIONS) > 1 ): #connected
      print 'AWG connected'
      break
    else:
      print 'Waiting for AWG'
      time.sleep(1)

  ########### TCP SERVER TO OUTSIDE WORLD #############
  #now it is connected to AWG, start listen server

  CONNECTION_LIST = []  # list of socket clients

  SERVER_PORT = 49589
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # this has no effect, why ?
  server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  server_socket.bind(("0.0.0.0", SERVER_PORT))
  server_socket.listen(10)

  # CONNECTION_LIST for the socket objects / address / port  
  # Add server socket to the list of readable connections
  CONNECTION_LIST.append([server_socket,"0.0.0.0",SERVER_PORT])
  # Add AWG socket to the list of readable connections
  # consider it like a read
  CONNECTION_LIST.append([awg_socket, AWG_IP, AWG_PORT])

  print "Chat server started on port " + str(SERVER_PORT)
  
  data = ''

  while 1:
    # Get the list sockets which are ready to be read through select
    socket_list = [item[0] for item in CONNECTION_LIST] #get first item of each item in CONNECTION_LIST
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
    #passing the server socket as connection of potential readers
    #passing AWG_socket as

    for sock in read_sockets:

      #New connection
      if sock == server_socket:
        # Handle the case in which there is a new connection recieved through server_socket
        sockfd, addr = server_socket.accept()  #accept returns a new socket object, sockfd, and address of the other end of the socket
        CONNECTION_LIST.append([sockfd,addr[0],addr[1]])  #add the new socket to the list
        print "Client %s, %s connected" % (addr[0],addr[1])

      elif sock == awg_socket:
        #this is the case where the AWG replied back with something, in response to query
        #format from AWG: <socket address>,<socket port>,<response>
        data = sock.recv(RECV_BUFFER)
        if ( len(data) == 0 ): #disconnected
          print 'awg disconnected, ending server'
          sys.exit()
          
          
        #find which socket to send it to
        temp = data.split(',') #split it based on comma separator
        #print CONNECTION_LIST
        if ( len(temp) == 3 ): #proper format
          receiver = [i for i in CONNECTION_LIST if i[1]==temp[0] and str(i[2])==temp[1]]
          #receiver = [i for i in CONNECTION_LIST if i[1]==temp[0]]
          #find which address and port that is
          if ( len(receiver) == 0 ): #no socket found
            print "No external client sockets found"
          elif ( len(receiver) > 1): #multiple sockets found
            print "Multiple external client sockets found"
          else: #one socket found, good
            print "Sending external client : " + str(temp[2])
            receiver[0][0].send(temp[2]) #send back what the AWG said
      #Some incoming message from a client
      else:  # Data received from client, process it
        try:
          #In Windows, sometimes when a TCP program closes abruptly,
          # a "Connection reset by peer" exception will be thrown
          data = sock.recv(RECV_BUFFER)
          if data:
            #got data, send it to the awg in proper format     
            #for some reason, data has some formatting characters
            #when printing, it loses the first letter. showing only printable characters fixes this
            
            data = "".join(ch for ch in data if (ord(ch)>31 and ord(ch)<126) or ord(ch) == 0 )            
            #sock.send('OK ... ' + data + '\r\n') DEBUG, REPLY BACK TO SENDER
            potentialclient = [element for element in CONNECTION_LIST if element[0] == sock]
            if ( len(potentialclient) == 0 ): #no socket found somehow, shouldnt happen
              pass #shouldn't happen, maybe handle somehow?
            elif ( len(potentialclient) > 1 ): #multiple sockets mapped, again shouldnt happen
              pass
            else: # one socket found, should happen
              tosend = potentialclient[0][1] + ',' + str(potentialclient[0][2]) + ',' + data 
              print "Sending AWG:" + tosend
              awg_socket.sendall(tosend)
          elif (len(data) == 0): #disconnected
            print 'client disconnected'
            #sock.close()
            toremove = [element for element in CONNECTION_LIST if element[0] == sock]
            #print toremove 
            #print "\n"
            #print CONNECTION_LIST
            removeIndex = CONNECTION_LIST.index(toremove[0])
            #print removeIndex
            #CONNECTION_LIST.remove(removeIndex)
            #print CONNECTION_LIST
            #print "\n"
            del CONNECTION_LIST[removeIndex]
            #print CONNECTION_LIST
            #sock.shutdown()
            sock.close()
        # client disconnected, so remove from socket list
        except Exception as e:
          #print "I/O error {0} : {1}".format(e.errno, e.strerror)
          print "Error:", sys.exc_info()[0]
          print "Client (%s, %s) is offline" % addr
          sock.close()
          toremove = [element for element in CONNECTION_LIST if element[0] == sock]
          removeIndex = CONNECTION_LIST.index(toremove[0])
          del CONNECTION_LIST[removeIndex]
          continue