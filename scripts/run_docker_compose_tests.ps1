# run-tests.ps1
Param(
    [switch]$Detached
)

# Change to the directory that contains your docker-compose.yml
# Replace 'docker' with the folder where your compose file resides
Set-Location "docker"

Write-Host "Starting docker-compose with --build..."

if ($Detached) {
    docker-compose up --build -d
    Write-Host "Containers are running in detached mode. Use 'docker-compose logs' or 'docker-compose down' when ready."
} else {
    docker-compose up --build
}
