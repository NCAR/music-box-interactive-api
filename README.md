# music-box-interactive
## User interface for the MusicBox box/column model

**Configure, run, and plot results for the MusicBox model, and edit chemical mechanisms.**

**Installation prerequisites:**
* Python >3.0
* Matplotlib
* Scipy
* Pandas


**To run interface without model:**

       cd music-box-interactive
       cd interactive
       python3 manage.py runserver



**To save configuration ZIP file after editing:**

  From the Conditions tab, select *Review* at the top right. Click *Download Configuration File*



**To use a configuration ZIP file in the model:**

  From the Getting Started page, click *Load Configuration File*. Select your ZIP file and click *Upload*



**Inside the ZIP configuration file:**

* my_config.json contains model conditions.
* camp_data contains the chemical mechanism files.
