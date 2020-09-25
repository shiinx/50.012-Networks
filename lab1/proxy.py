# 50.012 network lab 1

import _thread as thread
import os

# TODO: delete before submission
import shutil
import sys
from socket import *

proxy_port = 8055
cache_directory = "./cache/"


def client_thread(clientFacingSocket):
    clientFacingSocket.settimeout(5.0)

    try:
        message = clientFacingSocket.recv(4096).decode()
        msgElements = message.split()

        if len(msgElements) < 5 or msgElements[0].upper() != 'GET' or 'Range:' in msgElements:
            # print("non-supported request: " , msgElements)
            clientFacingSocket.close()
            return

        # Extract the following info from the received message
        #   webServer: the web server's host name
        #   resource: the web resource requested
        #   file_to_use: a valid file name to cache the requested resource
        #   Assume the HTTP reques is in the format of:
        #      GET http://www.mit.edu/ HTTP/1.1\r\n
        #      Host: www.mit.edu\r\n
        #      User-Agent: .....
        #      Accept:  ......

        resource = msgElements[1].replace("http://", "", 1)
        resource = resource.split("?")[0]

        hostHeaderIndex = msgElements.index('Host:')
        webServer = msgElements[hostHeaderIndex + 1]
        port = 80

        print("webServer:", webServer)
        print("resource:", resource)

        message = message.replace("Connection: keep-alive", "Connection: close")

        website_directory = cache_directory + webServer.replace("/", "-") + "/"

        if not os.path.exists(website_directory):
            os.makedirs(website_directory)

        # Not using "." as it is incompatible with windows,
        # Avoiding using "." in filenames to make life easier also,
        # windows recognize trailing dots as something related to file extensions
        r = resource.replace("/", "_")
        r = r.replace(".", "-")

        file_to_use = website_directory + r


    except:
        print(str(sys.exc_info()[0]))
        clientFacingSocket.close()
        return

    # Check weather the file exists in the cache
    try:
        with open(file_to_use, "rb") as f:
            # ProxyServer finds a cache hit and generates a response message
            print(thread.get_ident(), ": Served from the cache")
            while True:
                print(thread.get_ident(), ": Reading from cache")
                buff = f.read(4096)
                if buff:
                    print(thread.get_ident(), ": Sending to client")
                    clientFacingSocket.send(buff)
                else:
                    print(thread.get_ident(), ": Finished sending to client")
                    break

    except FileNotFoundError as e:
        serverFacingSocket = socket(AF_INET, SOCK_STREAM)
        try:
            print(thread.get_ident(), ": Served from the server")
            serverFacingSocket.connect((webServer, port))
            serverFacingSocket.send(message.encode())

            with open(file_to_use, "wb") as cacheFile:
                while True:
                    print(thread.get_ident(), ": Recv from server")
                    buff = serverFacingSocket.recv(4096)
                    print(thread.get_ident(), ": ", buff)
                    cacheFile.write(buff)
                    if buff:
                        print(thread.get_ident(), ": Sending to client")
                        clientFacingSocket.send(buff)
                    else:
                        print(thread.get_ident(), ": Finished sending to client")
                        break
        except:
            print(str(sys.exc_info()[0]))
        finally:
            serverFacingSocket.close()
            clientFacingSocket.close()
    except:
        print(str(sys.exc_info()[0]))
    finally:
        clientFacingSocket.close()


if len(sys.argv) > 2:
    print('Usage : "python proxy.py port_number"\n')
    sys.exit(2)
if len(sys.argv) == 2:
    proxy_port = int(sys.argv[1])

# TODO: Delete line before submission
shutil.rmtree('cache')

if not os.path.exists(cache_directory):
    os.makedirs(cache_directory)

# Create a server socket, bind it to a port and start listening
welcomeSocket = socket(AF_INET, SOCK_STREAM)

welcomeSocket.bind(('', proxy_port))
welcomeSocket.listen(1)

print('Proxy ready to serve at port', proxy_port)

try:
    while True:
        # Start receiving data from the client
        clientFacingSocket, addr = welcomeSocket.accept()
        # print('Received a connection from:', addr)

        # the following function starts a new thread, taking the function name as the first argument, and a tuple of arguments to the function as its second argument
        thread.start_new_thread(client_thread, (clientFacingSocket,))

except KeyboardInterrupt:
    print('bye...')

finally:
    welcomeSocket.shutdown(SHUT_RDWR)
    welcomeSocket.close()
