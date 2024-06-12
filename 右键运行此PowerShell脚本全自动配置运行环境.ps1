# 定义 Python 安装程序的下载链接和文件名 通过华为云下载python 3.9.13安装包
$installerUrl = "https://mirrors.huaweicloud.com/python/3.9.13/python-3.9.13-amd64.exe"
$installerFile = "python-3.9.13-amd64.exe"
# 检查是否有3.9.13版本
$python3913Installed = $false

# 定义安装路径
$userInstallPath = "$env:LOCALAPPDATA\Programs\Python\Python3913"
try
{
    # 获取当前Windows用户所有已安装的Python版本
    $pythonVersions = Get-ChildItem -Path "HKCU:\SOFTWARE\Python\PythonCore" | ForEach-Object { $_.PSChildName }

    
    foreach ($version in $pythonVersions)
    {
        Write-Host "检测到本机已有 Python "+$version
        if ($version -eq "3.9.13")
        {
            $python3913Installed = $true
            break
        }
    }

   
}
catch {
    Write-Host "An error occurred: $_"
}

# 输出结果
if ($python3913Installed)
{
    Write-Host "Python 3.9.13 已安装在计算机上。"
}
else
{
    Write-Host "Python 3.9.13 未在计算机上安装，准备自动安装Python 3.9.13。"
}

Write-Host "正在加载中，请耐心等待，切勿关闭此窗口！"

try{
    # 如果没安装Python 3.9.13 则自动安装
    if ($python3913Installed -eq $false)
    {
        # 下载 Python 安装程序
        Write-Host "正在下载 Python 安装程序..."
        Invoke-WebRequest -Uri $installerUrl -OutFile $installerFile

        # 安装 Python
        Write-Host "正在安装 Python，请稍候..."
        # 运行 Python 3.9.13 安装程序
        Start-Process -FilePath $installerFile -ArgumentList "/quiet", "InstallAllUsers=0", "PrependPath=1", "DefaultJustForMeTargetDir=`"$userInstallPath`"" -Wait

        # 将 Python 3.9.13 添加到系统环境变量中
        $env:Path += ";$userInstallPath"

        # 将 Python 3.9.13 添加到注册表
        $pythonPath = Join-Path $userInstallPath "python.exe"
        $pythonVersion = "3.9.13"
        $pythonKey = "HKCU:\Software\Python\PythonCore\$pythonVersion"
        New-Item -Path $pythonKey
        New-ItemProperty -Path $pythonKey -Name "(Default)" -Value $pythonVersion
        New-ItemProperty -Path $pythonKey -Name "InstallPath" -Value $userInstallPath
        New-ItemProperty -Path $pythonKey -Name "ExecutablePath" -Value $pythonPath

        # 删除安装程序
        Write-Host "Python 安装完成！删除安装程序..."
        Remove-Item $installerFile

        Write-Host "Python 3.9.13 已安装成功"
    }


    # 创建虚拟环境
    python -m venv venv

    # 激活虚拟环境
    .\venv\Scripts\Activate.ps1

    # 通过镜像源pip安装项目依赖库
    pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/

    # 通过jupyter打开
    # jupyter notebook ./src/main.ipynb

    # Write-Host "运行本项目中，切勿关闭此窗口！"
}
catch {
    Write-Host "An error occurred: $_"
}