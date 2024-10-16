#!/bin/bash

# Get the data
python app.py > /dev/null 2>&1 &

sleep 5

curl http://127.0.0.1:5000/data -o response.txt
echo "Response saved to response.txt"

pkill -f "python app.py"
