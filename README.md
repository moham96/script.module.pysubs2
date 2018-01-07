pysubs2 library Kodi plugin
======================

KODI plugin that implements pysubs2 library for subtitle conversion
All pysubs2 code is written by Tomas Karabela.
https://github.com/tkarabela/pysubs2


Installation in KODI:
- download plugin
- open KODI -> System -> Settings -> Add-ons -> Install from zip file
- navigate to the file you downloaded
         

Usage:
reference this plugin in your addon by:
  <requires>
    <import addon="script.module.pysubs2" version="0.0.1"/>
  </requires>

Import any2ass function in your script:
  from any2ass import any2ass




Changelog

0.0.1
- initial plugin version
- pysubs2 library version: 0.2.2
