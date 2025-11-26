@echo off
REM Terraform Deployment Script for Windows (Development Environment)
REM This script automates the deployment process for the fraud detection infrastructure

setlocal enabledelayedexpansion

set "TERRAFORM_DIR=%~dp0.."
set "ENVIRONMENT=%1:dev%"
set "ENVIRONMENT_FILE=%TERRAFORM_DIR%\environments\%ENVIRONMENT%.tfvars"
set "PLAN_FILE=%TERRAFORM_DIR%\%ENVIRONMENT%.tfplan"

echo.
echo ========================================
echo Terraform Deployment Script - %ENVIRONMENT% environment
echo ========================================
echo.

REM Check prerequisites
echo Checking prerequisites...
where terraform >nul 2>nul
if errorlevel 1 (
    echo Error: Terraform is not installed
    exit /b 1
)

where az >nul 2>nul
if errorlevel 1 (
    echo Error: Azure CLI is not installed
    exit /b 1
)

az account show >nul 2>nul
if errorlevel 1 (
    echo Error: Not authenticated with Azure. Run 'az login'
    exit /b 1
)

echo Prerequisites OK
echo.

REM Validate environment file
if not exist "%ENVIRONMENT_FILE%" (
    echo Error: Environment file not found: %ENVIRONMENT_FILE%
    exit /b 1
)

echo Environment file: %ENVIRONMENT_FILE%
echo.

REM Navigate to terraform directory
cd /d "%TERRAFORM_DIR%"

REM Initialize Terraform
echo Initializing Terraform...
call terraform init -upgrade
if errorlevel 1 (
    echo Error: Terraform init failed
    exit /b 1
)
echo.

REM Validate configuration
echo Validating Terraform configuration...
call terraform validate
if errorlevel 1 (
    echo Error: Terraform validation failed
    exit /b 1
)
echo.

REM Format code
echo Formatting Terraform code...
call terraform fmt -recursive
echo.

REM Plan deployment
echo Planning deployment...
call terraform plan -var-file="%ENVIRONMENT_FILE%" -out="%PLAN_FILE%"
if errorlevel 1 (
    echo Error: Terraform plan failed
    exit /b 1
)
echo.

REM Apply deployment
echo.
echo ========================================
echo WARNING: This will create/modify Azure resources
echo Environment: %ENVIRONMENT%
echo ========================================
echo.
set /p CONFIRM="Do you want to continue? (yes/no): "

if /i not "%CONFIRM%"=="yes" (
    echo Deployment cancelled
    exit /b 0
)

echo.
echo Applying deployment...
call terraform apply "%PLAN_FILE%"
if errorlevel 1 (
    echo Error: Terraform apply failed
    exit /b 1
)
echo.

REM Show outputs
echo.
echo ========================================
echo Deployment Outputs
echo ========================================
call terraform output
echo.

REM Optional: Get AKS credentials
set /p GET_AKS="Configure AKS credentials? (yes/no): "
if /i "%GET_AKS%"=="yes" (
    echo.
    echo Getting AKS credentials...
    for /f "tokens=*" %%i in ('terraform output -raw resource_group_name 2^>nul') do set "RG_NAME=%%i"
    for /f "tokens=*" %%i in ('terraform output -raw aks_cluster_name 2^>nul') do set "AKS_NAME=%%i"

    if "!RG_NAME!"=="" set "RG_NAME=rg-fraud-detection-%ENVIRONMENT%"
    if "!AKS_NAME!"=="" set "AKS_NAME=aks-fraud-det-%ENVIRONMENT%"

    echo Resource Group: !RG_NAME!
    echo AKS Cluster: !AKS_NAME!
    echo.

    call az aks get-credentials --resource-group "!RG_NAME!" --name "!AKS_NAME!" --overwrite-existing
    echo.
    echo Verify with: kubectl get nodes
)

echo.
echo ========================================
echo Deployment completed successfully!
echo ========================================
echo.

endlocal

