# BrowseTerm REST
REST API to:
1. Create SSH Containers.
    - {'image_name': '<existing_image_name>', 'container_name': '<userdefined>'}
2. Start SSH Containers.
    - {'container_name': '<userdefined>'}
3. Stop SSH Containers.
2. Delete SSH Containers info based on id.
3. Retrieve SSH Container info based on id.
4. Backup/Save SSH Container.


# DEPLOYMENT PROBLEM
1. The socket server and the ssh container need to be in the same network.
2. All users will connect to the same socket server (theoretically - even if they are load balanced and all. Its one entity.)
3. So all containers of all users need to be on the same network.
4. Meaning they can all ssh into one another if they choose.
5. Therefore, enable PK ssh only or add namespaces to username.