"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from time import time

# Server class
class Server(object):

	# Variables saving clients information
	clients = {}
	cu_images = {}
	user = 1

	# Connection variables
	HOST = 'localhost'
	PORT = 33000
	BUFSIZ = 1024

	def create_server(self, HOST, PORT):
		"""Init the server listen"""
		self.HOST = HOST
		self.PORT = PORT
		self.SERVER = socket(AF_INET, SOCK_STREAM)
		self.SERVER.bind((HOST,PORT))
		self.SERVER.listen(5)
		self.time_init = time()
		ACCEPT_THREAD = Thread(target=self.accept_incoming_connections)
		ACCEPT_THREAD.start()
		ACCEPT_THREAD.join()

	def kill_server(self):
		"""kill server when token changes"""
		self.SERVER.close()
		for client in self.clients.copy():
			client.close()

	def accept_incoming_connections(self):
		"""Sets up handling for incoming clients."""
		while True:
			try:
				client, client_address = self.SERVER.accept()
				client.send(bytes('n' + str(len(self.clients) + 1), "utf8"))
				Thread(target=self.handle_client, args=(client,)).start()
			except:
				break

	def handle_client(self, client):  # Takes client socket as argument.
		"""Handles a single client connection."""

		indi_user = "User" + str(self.user)
		if time() - self.time_init > 3:
			msg = "m%s has joined the chat!" % "New user"
			self.broadcast(bytes(msg, "utf8"), client)
		self.broadcast(bytes("1", "utf8"), client, "a")

		self.clients[client] = indi_user
		self.user += 1

		# Send current images from another users
		if self.cu_images:
			for key, value in self.cu_images.items():
				client.send(bytes(key + "c" + value, "utf8"))

		while True:
			try:
				msg = client.recv(self.BUFSIZ)
				if msg.decode("utf8")[0] == 'c': # Checking current images used by user
					self.cu_images[indi_user] = msg.decode("utf8")[1:]
					self.broadcast(msg, client, indi_user)
				elif msg.decode("utf8")[0] == 'p': # Checking still conected
					continue
				else:
					self.broadcast(msg, client, "m" + indi_user + ": ")
			except:
				client.close() # Disconect client
				del self.clients[client]
				self.user -= 1
				self.broadcast(bytes("-1", "utf8"), client, "a")
				try:
					del self.cu_images[client] # Eliminate if exist
				except:
					pass  # do nothing!
				break

	def broadcast(self, msg, client, prefix=""):
		"""Broadcasts a message to all the clients."""

		for sock in self.clients:
			if sock != client:
				sock.send(bytes(prefix, "utf8") + msg)