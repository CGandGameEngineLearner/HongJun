# ���� Python ��װ������������Ӻ��ļ��� ͨ����Ϊ������python 3.9.13��װ��
$installerUrl = "https://mirrors.huaweicloud.com/python/3.9.13/python-3.9.13-amd64.exe"
$installerFile = "python-3.9.13-amd64.exe"
# ����Ƿ���3.9.13�汾
$python3913Installed = $false

# ���尲װ·��
$userInstallPath = "$env:LOCALAPPDATA\Programs\Python\Python3913"
try
{
    # ��ȡ��ǰWindows�û������Ѱ�װ��Python�汾
    $pythonVersions = Get-ChildItem -Path "HKCU:\SOFTWARE\Python\PythonCore" | ForEach-Object { $_.PSChildName }

    
    foreach ($version in $pythonVersions)
    {
        Write-Host "��⵽�������� Python "+$version
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

# ������
if ($python3913Installed)
{
    Write-Host "Python 3.9.13 �Ѱ�װ�ڼ�����ϡ�"
}
else
{
    Write-Host "Python 3.9.13 δ�ڼ�����ϰ�װ��׼���Զ���װPython 3.9.13��"
}

Write-Host "���ڼ����У������ĵȴ�������رմ˴��ڣ�"

try{
    # ���û��װPython 3.9.13 ���Զ���װ
    if ($python3913Installed -eq $false)
    {
        # ���� Python ��װ����
        Write-Host "�������� Python ��װ����..."
        Invoke-WebRequest -Uri $installerUrl -OutFile $installerFile

        # ��װ Python
        Write-Host "���ڰ�װ Python�����Ժ�..."
        # ���� Python 3.9.13 ��װ����
        Start-Process -FilePath $installerFile -ArgumentList "/quiet", "InstallAllUsers=0", "PrependPath=1", "DefaultJustForMeTargetDir=`"$userInstallPath`"" -Wait

        # �� Python 3.9.13 ��ӵ�ϵͳ����������
        $env:Path += ";$userInstallPath"

        # �� Python 3.9.13 ��ӵ�ע���
        $pythonPath = Join-Path $userInstallPath "python.exe"
        $pythonVersion = "3.9.13"
        $pythonKey = "HKCU:\Software\Python\PythonCore\$pythonVersion"
        New-Item -Path $pythonKey
        New-ItemProperty -Path $pythonKey -Name "(Default)" -Value $pythonVersion
        New-ItemProperty -Path $pythonKey -Name "InstallPath" -Value $userInstallPath
        New-ItemProperty -Path $pythonKey -Name "ExecutablePath" -Value $pythonPath

        # ɾ����װ����
        Write-Host "Python ��װ��ɣ�ɾ����װ����..."
        Remove-Item $installerFile

        Write-Host "Python 3.9.13 �Ѱ�װ�ɹ�"
    }


    # �������⻷��
    python -m venv venv

    # �������⻷��
    .\venv\Scripts\Activate.ps1

    # ͨ������Դpip��װ��Ŀ������
    pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/

    # ͨ��jupyter��
    # jupyter notebook ./src/main.ipynb

    # Write-Host "���б���Ŀ�У�����رմ˴��ڣ�"
}
catch {
    Write-Host "An error occurred: $_"
}