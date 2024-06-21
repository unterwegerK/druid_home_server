# Druid Home Server
This repository is a collection of scripts used to maintain a home server which is intended as a file-backup system. It follows the following design principles:

- This server should not be running 24/7 but only starts when required and shuts down automatically when being inactive. Hence, there is functionality to shut the server down if it is no longer required.
- The scripts perform the basic maintenance tasks for the server:
  - Snapshotting of the filesystem
  - Scrubbing of the filesystem for errors
  - Update of packages
  - Notification via e-mail about performed tasks and problems
- This collection of scripts is supposed to provide a lightweight solution for a backup system. Hence, it is not designed to be very extensible. For more flexibility, probably a integration of dedicated tools is a better approach.

## Server-side
Required Python packages:
- smtplib

Required Ubuntu packages:
- ifstat
