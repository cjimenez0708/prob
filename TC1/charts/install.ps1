# Navegar a bootstrap
Set-Location bootstrap
Remove-Item Chart.lock -Force -ErrorAction SilentlyContinue
Remove-Item charts -Recurse -Force -ErrorAction SilentlyContinue
helm dependency update
Set-Location ..
helm upgrade --install bootstrap bootstrap
Start-Sleep -Seconds 20

# monitoring-stack
Set-Location monitoring-stack
Remove-Item Chart.lock -Force -ErrorAction SilentlyContinue
Remove-Item charts -Recurse -Force -ErrorAction SilentlyContinue
helm dependency update
Set-Location ..
helm upgrade --install monitoring-stack monitoring-stack
Start-Sleep -Seconds 20

# databases
Set-Location databases
Remove-Item Chart.lock -Force -ErrorAction SilentlyContinue
Remove-Item charts -Recurse -Force -ErrorAction SilentlyContinue
helm dependency update
Set-Location ..
helm upgrade --install databases databases
Start-Sleep -Seconds 60

# app
helm upgrade --install app app
Start-Sleep -Seconds 20

# grafana-config
Set-Location grafana-config
Remove-Item Chart.lock -Force -ErrorAction SilentlyContinue
Remove-Item charts -Recurse -Force -ErrorAction SilentlyContinue
helm dependency update
Set-Location ..
helm upgrade --install grafana-config grafana-config
