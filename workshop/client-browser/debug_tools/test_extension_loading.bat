@echo off
echo Testing Chrome Extension Loading...
echo.

set TEST_PROFILE=C:\Automation\Profiles\TEST_EXTENSION_LOAD
set EXT_PATH=C:\Automation\Extensions\Xactware_ClickOnce,C:\Automation\Extensions\WeScope_Autofill

echo Profile: %TEST_PROFILE%
echo Extensions: %EXT_PATH%
echo.
echo Launching Chrome with extension arguments...
echo.

"C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="%TEST_PROFILE%" --profile-directory="Default" --load-extension="%EXT_PATH%" chrome://extensions/

echo.
echo Check the Chrome window that opened:
echo 1. Does it show 2 extensions loaded?
echo 2. Are they enabled?
echo 3. Do you see any error messages?
echo.
pause
