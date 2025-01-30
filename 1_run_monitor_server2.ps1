$window_name = "monitor_server2"
$window_title = "monitor_server2"
$window_class = "monitor_server2"

# activate virtual environment
.\venv\Scripts\activate

# run monitor_server2.py
start-process -WindowStyle Hidden -PassThru powershell -ArgumentList "-ExecutionPolicy Bypass -File src\monitor_server2.py" -Name $window_name -WorkingDirectory $PSScriptRoot