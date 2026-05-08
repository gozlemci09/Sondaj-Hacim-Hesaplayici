[Setup]
AppName=Sondaj Hacim Hesaplayici
AppVersion=1.0
DefaultDirName={pf}\SondajHacimHesaplayici
DefaultGroupName=Sondaj Hacim Hesaplayici
OutputBaseFilename=Sondaj_Hacim_Kurulum
Compression=lzma
SolidCompression=yes
WizardStyle=modern 
WizardImageFile=logo.bmp

[Tasks]
Name: "desktopicon"; Description: "Masaüstüne kısayol oluştur"; GroupDescription: "Ek Kısayollar:"

[Files]
Source: "dist\SondajHacimHesaplayici.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Sondaj Hacim Hesaplayici"; Filename: "{app}\SondajHacimHesaplayici.exe"
Name: "{commondesktop}\Sondaj Hacim Hesaplayici"; Filename: "{app}\SondajHacimHesaplayici.exe"; Tasks: desktopicon

[Dirs]
Name: "{app}"; Permissions: users-modify