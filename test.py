import paramiko


def run_ssh_commands(hostname, port, username, password, commands):
    # Create SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the SSH server
        client.connect(hostname, port=port, username=username, password=password)

        # Execute commands
        for command in commands:
            stdin, stdout, stderr = client.exec_command(command)
            print(f"Command: {command}")
            print("Output:")
            print(stdout.read().decode())
            print("Error:")
            print(stderr.read().decode())

    finally:
        # Close the SSH connection
        client.close()

# Example usage
hostname = 'hpcc.msu.edu'
port = 22
username = 'miralavy'
password = 'OhLove!1'
commands = ['ls', 'pwd', 'echo "Hello, World!"']

run_ssh_commands(hostname, port, username, password, commands)

# ####################################################################################################

# import matplotlib.pyplot as plt
# import numpy as np
#
# harvest = np.array([[0.8, 2.4, 2.5, 3.9, 0.0, 4.0, 0.0],
#                     [2.4, 0.0, 4.0, 1.0, 2.7, 0.0, 0.0],
#                     [1.1, 2.4, 0.8, 4.3, 1.9, 4.4, 0.0],
#                     [0.6, 0.0, 0.3, 0.0, 3.1, 0.0, 0.0],
#                     [0.7, 1.7, 0.6, 2.6, 2.2, 6.2, 0.0],
#                     [1.3, 1.2, 0.0, 0.0, 0.0, 3.2, 5.1],
#                     [0.1, 2.0, 0.0, 1.4, 0.0, 1.9, 6.3]])
#
#
# fig, ax = plt.subplots()
# im = ax.imshow(harvest, interpolation="quadric")
# plt.show()
