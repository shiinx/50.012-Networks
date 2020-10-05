#!/bin/bash

echo -e "GET Index page:"
curl http://127.0.0.1:5000/ \
	-i

echo -e "\n\nGET all stored strings:"
curl http://127.0.0.1:5000/strings \
	-i

echo -e "\n\nPOST create random string:"
curl http://127.0.0.1:5000/create \
	-H "Content-Type: application/json" \
	-d \
	'{
		"length":6, 
		"allowUpperCase":true,
		"allowDigits":false,
		"allowSpecialCharacters":false
	}' \
	-i

echo -e "\n\nPOST create random string:"
curl http://127.0.0.1:5000/create \
	-H "Content-Type: application/json" \
	-d \
	'{
		"length":10, 
		"allowUpperCase":true,
		"allowDigits":true,
		"allowSpecialCharacters":true
	}' \
	-i

echo -e "\n\nPOST create random string:"
curl http://127.0.0.1:5000/create \
	-H "Content-Type: application/json" \
	-d \
	'{
		"length":5, 
		"allowUpperCase":false,
		"allowDigits":false,
		"allowSpecialCharacters":false
	}' \
	-i

echo -e "\n\nGET all stored strings:"
curl http://127.0.0.1:5000/strings \
	-i

echo -e "\n\nGET specified stored string using <uid = 1>:"
curl http://127.0.0.1:5000/strings/1 \
	-i

echo -e "\n\nGET specified stored string using <uid = 5>, which does not exist:"
curl http://127.0.0.1:5000/strings/5 \
	-i

echo -e "\n\nGET specified stored string using <uid = 1> and admin account with wrong password:"
curl http://127.0.0.1:5000/admin/strings/1 \
	-X GET \
	-u admin:wrongpassword \
	-i

echo -e "\n\nGET specified stored string using <uid = 1> and admin account with correct password:"	
curl http://127.0.0.1:5000/admin/strings/1 \
	-X GET \
	-u admin:password \
	-i

echo -e "\n\nPUT to change stored string using mimetype text/plain:"
curl http://127.0.0.1:5000/admin/strings/1 \
	-X PUT \
	-u admin:password \
	-H "Content-Type: text/plain" \
	-d "replacement string 1" \
	-i
	
echo -e "\n\nPUT to change stored string using mimetype application/json:"
curl http://127.0.0.1:5000/admin/strings/1 \
	-X PUT \
	-u admin:password \
	-H "Content-Type: application/json" \
	-d '{"newString":"replacement string 2"}' \
	-i

echo -e "\n\nPUT to create string if doesn't exist:"
curl http://127.0.0.1:5000/admin/strings/5 \
	-X PUT \
	-u admin:password \
	-H "Content-Type: application/json" \
	-d '{"newString":"new string 1"}' \
	-i
	
echo -e "\n\nGET all stored strings:"	
curl http://127.0.0.1:5000/strings \
	-i

echo -e "\n\nDELETE specified stored string using <uid = 3> :"
curl http://127.0.0.1:5000/admin/strings/3 \
	-X DELETE \
	-u admin:password \
	-i
	
echo -e "\n\nGET all stored strings:"
curl http://127.0.0.1:5000/strings \
	-i

echo -e "\n\nEnd of demo"