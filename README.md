# Android2Wp_SMSConverter

**Android2Wp_SMSConverter** is a Python script to convert SMS from Android to Windows Phone.


### Usage

1. On Android phone:
  * Download [SMS Backup&Restore](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore&hl=en) application
  * Backup SMS to a XML file
  * Copy .xml file on the computer

2. On Windows Phone:
  * Download [contact+message backup](https://www.microsoft.com/en-us/store/apps/contacts-message-backup/9nblgggz57gm) application
  * Backup SMS
  * Copy .msg file on the computer

3. On the computer:
  * Clone this project, create a virtual env to retrieve dependencies and launch the conversion process
  ```
  $ git clone https://github.com/gpailler/Android2Wp_SMSConverter
  $ cd Android2Wp_SMSConverter
  $ pyvenv venv
  $ source venv/bin/activate
  $ pip install -r requirements.txt
  $ python converter.py --xml android.xml --msg windowsphone.msg
  ```
  * The script will append all SMS from Android to the Windows Phone backup and regenerate a valid integrity checksum
  * Copy generated files **result.msg** and **result.hsh** on the Windows Phone

4. On Windows Phone:
  * Launch messaging application, click select then select all (in extended menu) and delete all messages
  * Launch contact+message backup application and restore all SMS


### Background

I switched from Android to Windows Phone. I tried to use **Transfer my data** application but this app was unable to copy SMS.
So I searched applications to export/import SMS on these two platforms and wrote this script to achieve the conversion.
The only tricky part was to generate the integrity check required by Windows Phone app to be able to import SMS. I used lot of [magic](http://gph.is/Quih86) to achieve this part.
