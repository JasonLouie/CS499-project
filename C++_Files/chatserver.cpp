#include <iostream>
#include <string>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <netdb.h>
#include <sys/uio.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <fstream>
using namespace std;

int main(int argc, char *argv[])
{
	// Specify a port number for server
	if(argc != 2){
		cerr << "Usage: port" << endl;
		exit(0);
	}
	// Grab port number
	int port = atoi(argv[1]);
	// Buffer to send and receive messages with
	char msg[1500];
	
	// Setup a socket and connection tools
	sockaddr_in servAddr;
	bzero((char*)&servAddr, sizeof(servAddr));
	servAddr.sin_family = AF_INET;
	servAddr.sin_addr.s_addr = htonl(INADDR_ANY);
	servAddr.sin_port = htons(port);
	
	// Open stream oriented socket with internet address
	// Keep track of socket descriptor
	int serverSd = socket(AF_INET, SOCK_STREAM, 0);
	if(serverSd < 0){
		cerr << "Error establishing the server socket" << endl;
		exit(0);
	}
	// Bind socket to local address
	int bindStatus = bind(serverSd, (struct sockaddr*) &servAddr, sizeof(servAddr));
	if(bindStatus < 0){
		cerr << "Error building socket to local address" << endl;
		exit(0);
	}
	cout << "Waiting for a client to connect..." << endl;
	
	// Listen for up to 5 requests at a time
	listen(serverSd, 5);
	// Receive a request from a client using accept
	// New address to connect with client
	sockaddr_in newSockAddr;
	socklen_t newSockAddrSize = sizeof(newSockAddr);
	// Accept, create a new socket descriptor to handle new connection with client
	
	int newSd = accept(serverSd, (sockaddr *)&newSockAddr, &newSockAddrSize);
	if(newSd < 0){
		cerr << "Error accepting request from client!" << endl;
		exit(1);
	}
	cout << "Connected with client!" << endl;
	
	// Keep track of the amt of data sent
	int bytesRead, bytesWritten = 0;
	while(1){
		// Receive msg from client (listen)
		cout << "Awaiting client response..." << endl;
		memset(&msg, 0, sizeof(msg)); // Clear buffer
		bytesRead += recv(newSd, (char*)&msg, sizeof(msg), 0);
		if(!strcmp(msg, "exit")){
			cout << "Client has quit the session" << endl;
			break;
		}
		cout << "Client: " << msg << endl;
		cout << ">";
		string data;
		getline(cin, data);
		memset(&msg, 0, sizeof(msg)); // Clear buffer
		strcpy(msg, data.c_str());
		if (data == "exit"){
			// Inform client that server has closed the connection
			send(newSd, (char*)&msg, strlen(msg), 0);
			break;
		}
		// Send msg to client
		bytesWritten += send(newSd, (char*)&msg, strlen(msg), 0);
	}
	// Close socket descriptors upon completion
	close(newSd);
	close(serverSd);
	cout << "*******Session******" << endl;
	cout << "Bytes written: " << bytesWritten << endl;
	cout << "Bytes read: " << bytesRead << endl;
	cout << "Connection closed..." << endl;
	return 0;
}
