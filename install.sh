#!/usr/bin/env bash

echo Installing Python modules
pip3 install -r requirements.txt

echo Installing Ngrok
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-arm.zip
unzip ngrok-stable-linux-arm.zip

echo Please sign up for an Ngrok account https://dashboard.ngrok.com/signup
echo Please provide your auth token https://dashboard.ngrok.com/get-started/your-authtoken
read -r token
./ngrok authtoken "$token"
./ngrok http 5000 --log=stdout > ngrok.log &

echo Starting Smart Garage
flask run