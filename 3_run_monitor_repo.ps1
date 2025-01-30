# set window name to "monitor_repo"
$window_name = "monitor_repo"
$window_title = "monitor_repo"
$window_class = "monitor_repo"

# activate virtual environment
.\venv\Scripts\activate

# run monitor_repo.py
start-process -WindowStyle Hidden -PassThru powershell -ArgumentList "-ExecutionPolicy Bypass -File src\monitor_repo.py" -Name $window_name -WorkingDirectory $PSScriptRoot