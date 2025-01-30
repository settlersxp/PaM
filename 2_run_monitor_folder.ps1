$window_name = "monitor_folder"
$window_title = "monitor_folder"
$window_class = "monitor_folder"

# activate virtual environment
.\venv\Scripts\activate

# run monitor_folder.py
start-process -WindowStyle Hidden -PassThru powershell -ArgumentList "-ExecutionPolicy Bypass -File src\monitor_folder.py" -Name $window_name -WorkingDirectory $PSScriptRoot