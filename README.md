**WebDesktop** is a service for remote file system management, remote desktop, and tools for enterprise warehouse management.

The program allows you to browse the user's disks and file system, as well as download their files. Remote desktop support is available, including image from desktop transfer and keyboard and mouse input to the remote desktop.

- For server-side operation:

	- Have the latest version of Python installed with the Pip package manager;
	- Install all project dependencies with the command:
		- `pip install -r .\requirements.txt"`
		- In this case, you need to be in the "server" folder.
	- Start the server with the command:
		- `python main.py`
		- (in the "server" folder)

	A virtual environment is also available. The default HTTP port is *3000*, and the default GRPC port is *50051*. These can be changed in the *main.py* and *grpc_server.py* files, respectively.

- For client-side operation:

	**RUN IT AS ADMINISTRATOR(!!!)**
	
	- Run the *.exe file. The compiled version is located in desktop/dist/main.exe (logo.png included!)
	- Enter the IP address and port of the server that was previously launched and deployed. For example, "127.0.0.1:50051." Next, enter the username and password, and click the button to log in.
	- Done!
	
	If desired, you can run it from your own Python interpreter. In the "Desktop" folder, follow the same steps: download the dependencies using the same command and run it using the same command.
