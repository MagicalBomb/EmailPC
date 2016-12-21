# -*- mode: python -*-
# -F -w 

block_cipher = None


a = Analysis(['C:\\Users\\Magicalbomb\\Desktop\\Work\\myPyLab\\Projections\\EmailPC\\EmailPC.py'],
             pathex=['W:\\Tools\\Python\\Python3.5.2_64\\Scripts'],
             binaries=[(r'W:\Tools\Python\Python3.5.2_64\Lib\site-packages\PyQt5\Qt\bin\Qt5Core.dll',r'.'),
(r'W:\Tools\Python\Python3.5.2_64\Lib\site-packages\PyQt5\Qt\bin\Qt5Gui.dll',r'.'),
(r'W:\Tools\Python\Python3.5.2_64\Lib\site-packages\PyQt5\Qt\bin\Qt5Svg.dll',r'.'),
(r'W:\Tools\Python\Python3.5.2_64\Lib\site-packages\PyQt5\Qt\bin\Qt5Widgets.dll',r'.'),
(r'W:\Tools\Python\Python3.5.2_64\Lib\site-packages\PyQt5\Qt\bin\Qt5PrintSupport.dll',r'.'),
(r'C:\Users\Magicalbomb\Desktop\Work\myPyLab\Projections\EmailPC\utils\StartUpFolderPath.dll',r'.'),
(r"W:\Tools\Python\Python3.5.2_64\Lib\site-packages\PyQt5\Qt\bin\Qt5Network.dll",r'.'),
(r"W:\Tools\Python\Python3.5.2_64\Lib\site-packages\PyQt5\Qt\bin\Qt5Multimedia.dll",r'.'),
(r"W:\Tools\Python\Python3.5.2_64\Lib\site-packages\PyQt5\Qt\bin\Qt5MultimediaWidgets.dll",r'.')],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='EmailPC',
          debug=False,
          strip=False,
          upx=True,
          console=False )
