#include <bits/stdc++.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <errno.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <thread>
#include <mutex>
#define MAX_LEN 200
#define NUM_COLORS 6
using namespace std;

class User{
	public:
		// Default constructor
		User() : username_(""), socket_(0) {}
		
		// Parameterized constructor
		User(int socket){
			socket_ = socket;
		}

		// Setter functions
		void setUser(string username){
			username_ = username;
		}

		void setSocket(int socket){
			socket_ = socket;
		}
		
		void setThread(thread t){
			th = move(t);
		}

		// Getter functions
		string getUser(){ return username_; }
		int getSocket(){ return socket_; }
		thread getThread(){ return move(th); }

		// Termination functions
		void endThread(){ th.detach(); }

		// Operator overloads
		friend bool operator== (const User& u1, const User& u2){
			return (u1.username_ == u2.username_ && u1.socket_ == u2.socket_);
		}

		friend bool operator!= (const User& u1, const User& u2){
			return (u1.username_ != u2.username_ || u1.socket_ != u2.socket_);
		}

		private:
			string username_;
			int socket_;
			thread th;
	
};

class Server{
	public:
		Server() {
			server.sin_family = AF_INET;
			server.sin_port = htons(chatPort);
			server.sin_addr.s_addr = INADDR_ANY;
			bzero(&server.sin_zero,0);
		}
		bool setUpServer(){
			// Create a socket for the server and if the value is -1, there was an error
			if((server_socket = socket(AF_INET,SOCK_STREAM,0)) == -1){
				perror("Socket: ");
				exit(-1);
				return false;
			}
			// Bind socket to local address
			if((bind(server_socket,(struct sockaddr *)&server,sizeof(struct sockaddr_in))) ==-1){
				perror("Bind error: ");
				exit(-1);
				return false;
			}
			// Listen for up to 8 connections at a time
			if((listen(server_socket,8)) == -1){
				perror("listen error: ");
				exit(-1);
				return false;
			}
			return true;
		}

		void start(){
			if (setUpServer()){
				receive();
			} else{
				cout << "An error occurred" << endl;
			}
		}

		void receive(){
			cout << "Listening for connections..." << endl;
			sockaddr_in client;
			int client_socket;
			unsigned int len = sizeof(sockaddr_in);
			while(true){
			// Accept client
				if((client_socket = accept(server_socket,(struct sockaddr *)&client,&len)) == -1){
					perror("Error accepting client: ");
					exit(-1);
				}
				User newUser(client_socket);
				thread t(handle_client, newUser);
				newUser.setThread(move(t));
				lock_guard<mutex> guard(clients_mtx);
			}
			// Wait for all clients' threads to end first
			for(int i=0; i<clients.size(); i++){
				if(clients[i].getThread().joinable()){
					clients[i].getThread().join();
				}
			}
			close(server_socket);
		}

		// For synchronisation of cout statements
		void shared_print(string str, bool endLine=true){	
			lock_guard<mutex> guard(cout_mtx);
			cout << str;
			if(endLine){
				cout<<endl;
			}
		}

		// Broadcast message to all clients
		void broadcast(string message){
			char temp[MAX_LEN];
			strcpy(temp,message.c_str());
			for(int i = 0; i < clients.size(); i++){
				send(clients[i].getSocket(),temp,sizeof(temp),0);
			}
		}

		// Broadcast message to all clients except the sender
		void sendMessage(string message, User sender){
			char temp[MAX_LEN];
			strcpy(temp,message.c_str());
			for(int i = 0; i < clients.size(); i++){
				send(clients[i].getSocket(),temp,sizeof(temp),0);
			}
		}

	void handle_client(User user){
		char name[MAX_LEN],str[MAX_LEN];
		recv(user.getSocket(),name,sizeof(name),0);
		user.setUser(name);

		// Display welcome message
		string welcome_message=string(name)+string(" has joined");								
		broadcast(welcome_message);
		shared_print(welcome_message);
	
		while(true){
			int bytes_received=recv(client_socket,str,sizeof(str),0);
			if(bytes_received<=0)
				return;
			if(strcmp(str,"#exit")==0){
				// Display leaving message
				string message=string(name)+string(" has left");				
				broadcast(message);
				shared_print(color(id)+message+def_col);
				end_connection(id);							
				return;
			}
			broadcast_message(string(name));					
			shared_print(name+": "+str);
		}	
}

	private:
		mutex cout_mtx,clients_mtx;
		vector<User> clients;
		int chatPort = 55555;
		int server_socket;
		sockaddr_in server;
};

void handle_client(int client_socket);

int main(){
	
	return 0;
}
/*
void end_connection(int id){
	for(int i=0; i<clients.size(); i++){
		if(clients[i].id==id){
			lock_guard<mutex> guard(clients_mtx);
			clients[i].th.detach();
			clients.erase(clients.begin()+i);
			close(clients[i].socket);
			break;
		}
	}				
}
*/