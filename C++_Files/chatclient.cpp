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

int main(int argc, char *argv[]){
	// 2 parameters: ip address and port required.
	if(argc != 3){
		cerr << "Usage: ip_address port" << endl;
		exit(0);
	}
	// Retrieve IP address and port number
	char *serverIP = argv[1];
	int port = atoi(argv[2]);
	// Create msg buffer
	char msg[1500];
	struct hostent* host = gethostbyname(serverIP);
	sockaddr_in sendSockAddr;
	bzero((char*)&sendSockAddr, sizeof(sendSockAddr));
	sendSockAddr.sin_family = AF_INET;
	sendSockAddr.sin_addr.s_addr = inet_addr(inet_ntoa(*(struct in_addr*)*host->h_addr_list));
	sendSockAddr.sin_port = htons(port);
	int clientSd = socket(AF_INET, SOCK_STREAM, 0);
	// attempt to connect
	int status = connect(clientSd, (sockaddr*) &sendSockAddr, sizeof(sendSockAddr));

	if (status < 0){
		cout << "Error connecting to socket!" << endl;
		exit(0);
		// Original code used break but cannot break if not in a loop
	}
	cout << "Connected to the server!" << endl;
	int bytesRead, bytesWritten = 0;
	while(1){
		cout << ">";
		string data;
		getline(cin, data);
		memset(&msg, 0, sizeof(msg)); // Clear buffer
		strcpy(msg, data.c_str());
		// Handle leaving server
		if (data == "exit"){
			send(clientSd, (char*)&msg, strlen(msg), 0);
			break;
		}
		bytesWritten += send(clientSd, (char*)&msg, strlen(msg), 0);
		cout << "Awaiting server response..." << endl;
		memset(&msg, 0, sizeof(msg)); // Clear buffer
		bytesRead += recv(clientSd, (char*)&msg, sizeof(msg), 0);
		if (!strcmp(msg, "exit")){
			cout << "Server was shutdown" << endl;
			break;
		}
		cout << "Server: " << msg << endl;
	}
	close(clientSd);
	cout << "******Session******" << endl;
	cout << "Bytes written: " << bytesWritten << endl;
	cout << "Bytes read: " << bytesRead << endl;
	cout << "Connection closed" << endl;
	return 0;
}