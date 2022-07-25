#include <cstring>
#include <iostream>
#include <string>

#include <arpa/inet.h>
#include <netdb.h>
#include <sys/socket.h>

#include <unistd.h>

int main(int argc, chat* argv[])
{
	// Check if port number is provided
	if (argc != 2){
		std::cerr << "Run program as 'program <port> '\n";
		return -1
	}
	
	auto &portNum = argv[1]
	const unsigned int backLog = 8; // number of connections allowed on the incoming queue
	
	addrinfo hints, *res, *p; // 2 pointers: res to hold and p to iterate over
	memset(&hints, 0, sizeof(hints));
	
	hints.ai_family = AF_UNSPEC; // don't specify which IP version to use yet
	hints.ai_socktype = SOCK_STREAM; // TCP socket
	hints.ai_flags = AI_PASSIVE;
	
	// man getaddrinfo for more info
	int gAddRes = getaddrinfo(NULL, portNum, &hints, &res);
	if (gAddRes != 0){
		std::cerr << gai_strerror(gAddRes) << "\n";
		return -2;
	
	std::cout << "Detecting addresses" << std::endl;
	
}
