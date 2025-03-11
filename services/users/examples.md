curl -v -X POST 'localhost:8090/signup' \
    --data '{"username": "ilya", "password": "123", "email": "ivdovets@ntr.ai"}'
----------------------------------------------------------------
Note: Unnecessary use of -X or --request, POST is already inferred.
* Host localhost:8090 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:8090...
* Connected to localhost (::1) port 8090
> POST /signup HTTP/1.1
> Host: localhost:8090
> User-Agent: curl/8.5.0
> Accept: */*
> Content-Length: 67
> Content-Type: application/x-www-form-urlencoded
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.0 Python/3.9.21
< Date: Fri, 28 Feb 2025 21:21:15 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 0
< Set-Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzc2NzV9.jT5b_zm9cjC5S_CrbD1OtYtd4EPF25GghQrAk9_zCkLboARpK2pIcLDpwIniWCNGFlCe9MgFG4ewDjUvkAhHTyuAMq8_EZDvX08GEG6e1BWu79957BFNusQ8gDO7y1NqfYRS4Nb2yRxUzuBWi1WEGqTzPdWp-VnaQOCIuNtxtCpg1q33pc9dDrf2mw8CsUbDw7KV7zV-pCgshrAWt5FxaHMcHChIFTPEwVa0q0YVXv-pWNOc-NKopuvLbnFEp6eypR0WVWvUIDdbVF5dRbtluR5uZT5I9fPgFRBU3vyfH3cmmVaqhHoJMF7qe0yGGHo3OoCbAtAfKPG7EUl8bCEofg; Path=/
< Connection: close
< 
* Closing connection
----------------------------------------------------------------
curl -v -X POST 'localhost:8090/login' --data '{"username": "ilya", "password": "123"}'
----------------------------------------------------------------
Note: Unnecessary use of -X or --request, POST is already inferred.
* Host localhost:8090 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:8090...
* Connected to localhost (::1) port 8090
> POST /login HTTP/1.1
> Host: localhost:8090
> User-Agent: curl/8.5.0
> Accept: */*
> Content-Length: 39
> Content-Type: application/x-www-form-urlencoded
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.0 Python/3.9.21
< Date: Fri, 28 Feb 2025 21:16:59 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 0
< Set-Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzc0MTl9.JPtEzRC5eRZColDC-yLkVqsUoHUzfjbRr5O4CxREqwvj8i9K-jF9RDbMG4iE198z4SIJfFM81w_CzAvl-hLxUfAZUawdufeH2nKCLNviw6fCU1bDTyWtqGwamxEKSKOLDo7ZeDOSyh-GGsw3HYso1qgQ-Iy0VMEhgabtRBtEtMHAYAXcVqgBekYSp_MujdtnO8f0W1aqDKtRTMepffZLwsCscJjcdI6Abc-9Xm584ccaJuNq_dGnf-36xfUx8JIq8PEzVKN9Hc_UA38z-pFBzdhIXwfOWj-XYTqTpkAU7XkUtetsQNoDnGQvL4-R6fXt8ySgePE2D4a0neVoQZP1jQ; Path=/
< Connection: close
< 
* Closing connection
----------------------------------------------------------------
curl -v -X DELETE 'localhost:8090/drop_tables'    -H 'Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImtlayIsImlhdCI6MTc0MDYwNzM4NX0.Yw-bTH-nXtqi2niMd0m3Y5UFE_IYWFzjWmQi3el5jmjirJKyCQeRsFxiUoUz8KqrLr7kA2JnCe3m3YOke2L4X5-hYyJUFYHqhTtLoi5s0QIkzSKilqKDZJulMlS3jY6U57LSrPHFvmdI60zw52za7jsBfEAS6Mz9KNFEv0ybMSSMCV8sFrhz0QLwmGFLvv_sZnGAf_mMMdr2CNRHQRyBQpK_2vrV_pZ3LP-4o3ELOdQgnw0LS4twy7smjsYRsgOkebVOrP9p14Yr6e84B18oaTaichh9excS4nq5OOndbXCfZnrWGX0tgBMBu6QvHkbg7a7LvxQqYCHh6DPnPuLsCg'    -H "Content-Type: application/json"    --data '{"tables": ["users", "user_profiles", "sessions", "user_roles"]}'  
----------------------------------------------------------------
* Host localhost:8090 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:8090...
* Connected to localhost (::1) port 8090
> DELETE /drop_tables HTTP/1.1
> Host: localhost:8090
> User-Agent: curl/8.5.0
> Accept: */*
> Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImtlayIsImlhdCI6MTc0MDYwNzM4NX0.Yw-bTH-nXtqi2niMd0m3Y5UFE_IYWFzjWmQi3el5jmjirJKyCQeRsFxiUoUz8KqrLr7kA2JnCe3m3YOke2L4X5-hYyJUFYHqhTtLoi5s0QIkzSKilqKDZJulMlS3jY6U57LSrPHFvmdI60zw52za7jsBfEAS6Mz9KNFEv0ybMSSMCV8sFrhz0QLwmGFLvv_sZnGAf_mMMdr2CNRHQRyBQpK_2vrV_pZ3LP-4o3ELOdQgnw0LS4twy7smjsYRsgOkebVOrP9p14Yr6e84B18oaTaichh9excS4nq5OOndbXCfZnrWGX0tgBMBu6QvHkbg7a7LvxQqYCHh6DPnPuLsCg
> Content-Type: application/json
> Content-Length: 64
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.0 Python/3.9.21
< Date: Fri, 28 Feb 2025 21:19:51 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 27
< Connection: close
< 
* Closing connection
Tables deleted successfully%     
----------------------------------------------------------------
curl -v -X GET 'localhost:8090/profile' \ --data '{"username": "ilya"}' \    -H 'Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzc0MTl9.JPtEzRC5eRZColDC-yLkVqsUoHUzfjbRr5O4CxREqwvj8i9K-jF9RDbMG4iE198z4SIJfFM81w_CzAvl-hLxUfAZUawdufeH2nKCLNviw6fCU1bDTyWtqGwamxEKSKOLDo7ZeDOSyh-GGsw3HYso1qgQ-Iy0VMEhgabtRBtEtMHAYAXcVqgBekYSp_MujdtnO8f0W1aqDKtRTMepffZLwsCscJjcdI6Abc-9Xm584ccaJuNq_dGnf-36xfUx8JIq8PEzVKN9Hc_UA38z-pFBzdhIXwfOWj-XYTqTpkAU7XkUtetsQNoDnGQvL4-R6fXt8ySgePE2D4a0neVoQZP1jQ'
--------------------------------------------------------
curl -v -X GET 'localhost:8090/profile' \ --data '{"username": "ilya"}' \    -H 'Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzc0MTl9.JPtEzRC5eRZColDC-yLkVqsUoHUzfjbRr5O4CxREqwvj8i9K-jF9RDbMG4iE198z4SIJfFM81w_CzAvl-hLxUfAZUawdufeH2nKCLNviw6fCU1bDTyWtqGwamxEKSKOLDo7ZeDOSyh-GGsw3HYso1qgQ-Iy0VMEhgabtRBtEtMHAYAXcVqgBekYSp_MujdtnO8f0W1aqDKtRTMepffZLwsCscJjcdI6Abc-9Xm584ccaJuNq_dGnf-36xfUx8JIq8PEzVKN9Hc_UA38z-pFBzdhIXwfOWj-XYTqTpkAU7XkUtetsQNoDnGQvL4-R6fXt8ySgePE2D4a0neVoQZP1jQ'    
Note: Unnecessary use of -X or --request, GET is already inferred.
* Host localhost:8090 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:8090...
* Connected to localhost (::1) port 8090
> GET /profile HTTP/1.1
> Host: localhost:8090
> User-Agent: curl/8.5.0
> Accept: */*
> Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzc0MTl9.JPtEzRC5eRZColDC-yLkVqsUoHUzfjbRr5O4CxREqwvj8i9K-jF9RDbMG4iE198z4SIJfFM81w_CzAvl-hLxUfAZUawdufeH2nKCLNviw6fCU1bDTyWtqGwamxEKSKOLDo7ZeDOSyh-GGsw3HYso1qgQ-Iy0VMEhgabtRBtEtMHAYAXcVqgBekYSp_MujdtnO8f0W1aqDKtRTMepffZLwsCscJjcdI6Abc-9Xm584ccaJuNq_dGnf-36xfUx8JIq8PEzVKN9Hc_UA38z-pFBzdhIXwfOWj-XYTqTpkAU7XkUtetsQNoDnGQvL4-R6fXt8ySgePE2D4a0neVoQZP1jQ
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.0 Python/3.9.21
< Date: Fri, 28 Feb 2025 21:22:55 GMT
< Content-Type: application/json
< Content-Length: 174
< Connection: close
< 
{"bio":null,"birthdate":null,"created_at":"Fri, 28 Feb 2025 21:21:15 GMT","email":"ivdovets@ntr.ai","first_name":null,"last_name":null,"phone_number":null,"username":"ilya"}
* Closing connection
----------------------------------------------------------------
curl -v -X PUT 'localhost:8090/profile' \ --data '{"username": "ilya"}' \    -H 'Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzc0MTl9.JPtEzRC5eRZColDC-yLkVqsUoHUzfjbRr5O4CxREqwvj8i9K-jF9RDbMG4iE198z4SIJfFM81w_CzAvl-hLxUfAZUawdufeH2nKCLNviw6fCU1bDTyWtqGwamxEKSKOLDo7ZeDOSyh-GGsw3HYso1qgQ-Iy0VMEhgabtRBtEtMHAYAXcVqgBekYSp_MujdtnO8f0W1aqDKtRTMepffZLwsCscJjcdI6Abc-9Xm584ccaJuNq_dGnf-36xfUx8JIq8PEzVKN9Hc_UA38z-pFBzdhIXwfOWj-XYTqTpkAU7XkUtetsQNoDnGQvL4-R6fXt8ySgePE2D4a0neVoQZP1jQ' --data '{"bio": "I love monkeys"}'
--------------------------------------------------------
* Host localhost:8090 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:8090...
* Connected to localhost (::1) port 8090
> PUT /profile HTTP/1.1
> Host: localhost:8090
> User-Agent: curl/8.5.0
> Accept: */*
> Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzc0MTl9.JPtEzRC5eRZColDC-yLkVqsUoHUzfjbRr5O4CxREqwvj8i9K-jF9RDbMG4iE198z4SIJfFM81w_CzAvl-hLxUfAZUawdufeH2nKCLNviw6fCU1bDTyWtqGwamxEKSKOLDo7ZeDOSyh-GGsw3HYso1qgQ-Iy0VMEhgabtRBtEtMHAYAXcVqgBekYSp_MujdtnO8f0W1aqDKtRTMepffZLwsCscJjcdI6Abc-9Xm584ccaJuNq_dGnf-36xfUx8JIq8PEzVKN9Hc_UA38z-pFBzdhIXwfOWj-XYTqTpkAU7XkUtetsQNoDnGQvL4-R6fXt8ySgePE2D4a0neVoQZP1jQ
> Content-Length: 25
> Content-Type: application/x-www-form-urlencoded
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.0 Python/3.9.21
< Date: Fri, 28 Feb 2025 21:26:39 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 15
< Connection: close
< 
* Closing connection
----------------------------------------------------------------
curl -v -X POST 'localhost:8090/roles'    -H 'Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzc0MTl9.JPtEzRC5eRZColDC-yLkVqsUoHUzfjbRr5O4CxREqwvj8i9K-jF9RDbMG4iE198z4SIJfFM81w_CzAvl-hLxUfAZUawdufeH2nKCLNviw6fCU1bDTyWtqGwamxEKSKOLDo7ZeDOSyh-GGsw3HYso1qgQ-Iy0VMEhgabtRBtEtMHAYAXcVqgBekYSp_MujdtnO8f0W1aqDKtRTMepffZLwsCscJjcdI6Abc-9Xm584ccaJuNq_dGnf-36xfUx8JIq8PEzVKN9Hc_UA38z-pFBzdhIXwfOWj-XYTqTpkAU7XkUtetsQNoDnGQvL4-R6fXt8ySgePE2D4a0neVoQZP1jQ' --data '{"role_name": "admin"}' 
----------------------------------------------------------------
Note: Unnecessary use of -X or --request, POST is already inferred.
* Host localhost:8090 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:8090...
* Connected to localhost (::1) port 8090
> POST /roles HTTP/1.1
> Host: localhost:8090
> User-Agent: curl/8.5.0
> Accept: */*
> Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzc0MTl9.JPtEzRC5eRZColDC-yLkVqsUoHUzfjbRr5O4CxREqwvj8i9K-jF9RDbMG4iE198z4SIJfFM81w_CzAvl-hLxUfAZUawdufeH2nKCLNviw6fCU1bDTyWtqGwamxEKSKOLDo7ZeDOSyh-GGsw3HYso1qgQ-Iy0VMEhgabtRBtEtMHAYAXcVqgBekYSp_MujdtnO8f0W1aqDKtRTMepffZLwsCscJjcdI6Abc-9Xm584ccaJuNq_dGnf-36xfUx8JIq8PEzVKN9Hc_UA38z-pFBzdhIXwfOWj-XYTqTpkAU7XkUtetsQNoDnGQvL4-R6fXt8ySgePE2D4a0neVoQZP1jQ
> Content-Length: 22
> Content-Type: application/x-www-form-urlencoded
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.0 Python/3.9.21
< Date: Fri, 28 Feb 2025 21:29:07 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 13
< Connection: close
< 
* Closing connection
Role assigned%      
----------------------------------------------------------------
curl -v -X GET 'localhost:8090/roles'    -H 'Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzc0MTl9.JPtEzRC5eRZColDC-yLkVqsUoHUzfjbRr5O4CxREqwvj8i9K-jF9RDbMG4iE198z4SIJfFM81w_CzAvl-hLxUfAZUawdufeH2nKCLNviw6fCU1bDTyWtqGwamxEKSKOLDo7ZeDOSyh-GGsw3HYso1qgQ-Iy0VMEhgabtRBtEtMHAYAXcVqgBekYSp_MujdtnO8f0W1aqDKtRTMepffZLwsCscJjcdI6Abc-9Xm584ccaJuNq_dGnf-36xfUx8JIq8PEzVKN9Hc_UA38z-pFBzdhIXwfOWj-XYTqTpkAU7XkUtetsQNoDnGQvL4-R6fXt8ySgePE2D4a0neVoQZP1jQ'               
--------------------------------------------------------
Note: Unnecessary use of -X or --request, GET is already inferred.
* Host localhost:8090 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:8090...
* Connected to localhost (::1) port 8090
> GET /roles HTTP/1.1
> Host: localhost:8090
> User-Agent: curl/8.5.0
> Accept: */*
> Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzc0MTl9.JPtEzRC5eRZColDC-yLkVqsUoHUzfjbRr5O4CxREqwvj8i9K-jF9RDbMG4iE198z4SIJfFM81w_CzAvl-hLxUfAZUawdufeH2nKCLNviw6fCU1bDTyWtqGwamxEKSKOLDo7ZeDOSyh-GGsw3HYso1qgQ-Iy0VMEhgabtRBtEtMHAYAXcVqgBekYSp_MujdtnO8f0W1aqDKtRTMepffZLwsCscJjcdI6Abc-9Xm584ccaJuNq_dGnf-36xfUx8JIq8PEzVKN9Hc_UA38z-pFBzdhIXwfOWj-XYTqTpkAU7XkUtetsQNoDnGQvL4-R6fXt8ySgePE2D4a0neVoQZP1jQ
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.0 Python/3.9.21
< Date: Fri, 28 Feb 2025 21:30:08 GMT
< Content-Type: application/json
< Content-Length: 87
< Connection: close
< 
[{"assigned_at":"Fri, 28 Feb 2025 21:29:07 GMT","is_active":true,"role_name":"admin"}]
* Closing connection
----------------------------------------------------------------
curl -v -X DELETE 'localhost:8090/roles'    -H 'Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzc0MTl9.JPtEzRC5eRZColDC-yLkVqsUoHUzfjbRr5O4CxREqwvj8i9K-jF9RDbMG4iE198z4SIJfFM81w_CzAvl-hLxUfAZUawdufeH2nKCLNviw6fCU1bDTyWtqGwamxEKSKOLDo7ZeDOSyh-GGsw3HYso1qgQ-Iy0VMEhgabtRBtEtMHAYAXcVqgBekYSp_MujdtnO8f0W1aqDKtRTMepffZLwsCscJjcdI6Abc-9Xm584ccaJuNq_dGnf-36xfUx8JIq8PEzVKN9Hc_UA38z-pFBzdhIXwfOWj-XYTqTpkAU7XkUtetsQNoDnGQvL4-R6fXt8ySgePE2D4a0neVoQZP1jQ' --data '{"role_name": "admin"}'
----------------------------------------------------------------
* Host localhost:8090 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:8090...
* Connected to localhost (::1) port 8090
> DELETE /roles HTTP/1.1
> Host: localhost:8090
> User-Agent: curl/8.5.0
> Accept: */*
> Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzc0MTl9.JPtEzRC5eRZColDC-yLkVqsUoHUzfjbRr5O4CxREqwvj8i9K-jF9RDbMG4iE198z4SIJfFM81w_CzAvl-hLxUfAZUawdufeH2nKCLNviw6fCU1bDTyWtqGwamxEKSKOLDo7ZeDOSyh-GGsw3HYso1qgQ-Iy0VMEhgabtRBtEtMHAYAXcVqgBekYSp_MujdtnO8f0W1aqDKtRTMepffZLwsCscJjcdI6Abc-9Xm584ccaJuNq_dGnf-36xfUx8JIq8PEzVKN9Hc_UA38z-pFBzdhIXwfOWj-XYTqTpkAU7XkUtetsQNoDnGQvL4-R6fXt8ySgePE2D4a0neVoQZP1jQ
> Content-Length: 22
> Content-Type: application/x-www-form-urlencoded
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.0 Python/3.9.21
< Date: Fri, 28 Feb 2025 21:31:34 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 12
< Connection: close
< 
* Closing connection
Role deleted%      
----------------------------------------------------------------
curl -v -X GET 'localhost:8090/sessions'    -H 'Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzg0NzF9.WqhVwsvp6CsJkPQtcrWTp-idmT30frXjv0LqXgt04-xJzCwhr6WwrX6hPootPCIqUcFWcD-PtCV7O0qO0LMVxD0Ekist8tvMFdbux0uckoLO6tpL08veVdiX08U6JZG5Vnfq9JuCuBqDoxQBE8b6d2dLNhzd2NtUtgMQfZtGPBercWrg1fkBo0bHx11Qey1uPmARSvC_JutDO2PgMw0eZKyQMhQ3gVzM1WloH8qWg5q5y5L39RSL8hlug-2du5hr5V_da1wCOXGWWylX0H6km17v_-YCESWsjRlRHud8c5okJBS6RzD6SHhv5orIEzOCDWPBQxSAyfAAn7B-Gc9ubw'
--------------------------------------------------------
Note: Unnecessary use of -X or --request, GET is already inferred.
* Host localhost:8090 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:8090...
* Connected to localhost (::1) port 8090
> GET /sessions HTTP/1.1
> Host: localhost:8090
> User-Agent: curl/8.5.0
> Accept: */*
> Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzg0NzF9.WqhVwsvp6CsJkPQtcrWTp-idmT30frXjv0LqXgt04-xJzCwhr6WwrX6hPootPCIqUcFWcD-PtCV7O0qO0LMVxD0Ekist8tvMFdbux0uckoLO6tpL08veVdiX08U6JZG5Vnfq9JuCuBqDoxQBE8b6d2dLNhzd2NtUtgMQfZtGPBercWrg1fkBo0bHx11Qey1uPmARSvC_JutDO2PgMw0eZKyQMhQ3gVzM1WloH8qWg5q5y5L39RSL8hlug-2du5hr5V_da1wCOXGWWylX0H6km17v_-YCESWsjRlRHud8c5okJBS6RzD6SHhv5orIEzOCDWPBQxSAyfAAn7B-Gc9ubw
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.0 Python/3.9.21
< Date: Fri, 28 Feb 2025 21:34:54 GMT
< Content-Type: application/json
< Content-Length: 101
< Connection: close
< 
[{"created_at":"Fri, 28 Feb 2025 21:34:31 GMT","session_id":"4f8343d5-add8-4b1e-9ff3-df541d875098"}]
* Closing connection
----------------------------------------------------------------
curl -v -X DELETE 'localhost:8090/logout'    -H 'Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzg0NzF9.WqhVwsvp6CsJkPQtcrWTp-idmT30frXjv0LqXgt04-xJzCwhr6WwrX6hPootPCIqUcFWcD-PtCV7O0qO0LMVxD0Ekist8tvMFdbux0uckoLO6tpL08veVdiX08U6JZG5Vnfq9JuCuBqDoxQBE8b6d2dLNhzd2NtUtgMQfZtGPBercWrg1fkBo0bHx11Qey1uPmARSvC_JutDO2PgMw0eZKyQMhQ3gVzM1WloH8qWg5q5y5L39RSL8hlug-2du5hr5V_da1wCOXGWWylX0H6km17v_-YCESWsjRlRHud8c5okJBS6RzD6SHhv5orIEzOCDWPBQxSAyfAAn7B-Gc9ubw' --data '{"session_id": "4f8343d5-add8-4b1e-9ff3-df541d875098"}'
--------------------------------------------------------
* Host localhost:8090 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:8090...
* Connected to localhost (::1) port 8090
> DELETE /logout HTTP/1.1
> Host: localhost:8090
> User-Agent: curl/8.5.0
> Accept: */*
> Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImlseWEiLCJpYXQiOjE3NDA3Nzg0NzF9.WqhVwsvp6CsJkPQtcrWTp-idmT30frXjv0LqXgt04-xJzCwhr6WwrX6hPootPCIqUcFWcD-PtCV7O0qO0LMVxD0Ekist8tvMFdbux0uckoLO6tpL08veVdiX08U6JZG5Vnfq9JuCuBqDoxQBE8b6d2dLNhzd2NtUtgMQfZtGPBercWrg1fkBo0bHx11Qey1uPmARSvC_JutDO2PgMw0eZKyQMhQ3gVzM1WloH8qWg5q5y5L39RSL8hlug-2du5hr5V_da1wCOXGWWylX0H6km17v_-YCESWsjRlRHud8c5okJBS6RzD6SHhv5orIEzOCDWPBQxSAyfAAn7B-Gc9ubw
> Content-Length: 54
> Content-Type: application/x-www-form-urlencoded
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.0 Python/3.9.21
< Date: Fri, 28 Feb 2025 21:36:35 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 18
< Connection: close
< 
* Closing connection
Session logged out%       