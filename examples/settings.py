# Settings
import os

OPDM_USERNAME = os.environ.get('OPDM_USERNAME', "user")
OPDM_PASSWORD = os.environ.get('OPDM_PASSWORD', "pass")
OPDM_SERVER = os.environ.get('OPDM_SERVER', "https://opde.elering.sise:8443")

# Write here path to specific folder, for now it will write file to the same location from where the script is ran
EXPORT_FOLDER = os.environ.get('EXPORT_FOLDER', os.getcwd())

# Put here a path to the folder that contains IGM-s you want to upload
IGM_SOURCE_FOLDER = os.environ.get('IGM_SOURCE_FOLDER', r"C:\IGM_EXPORT_PATH")

# OPDM Client-s that are responsible for providing Ruleset Library (RSL),
RSL_OFFICIAL_NODES = os.environ.get('RSL_OFFICIAL_NODES', "10V1001C--002430,10V1001C--002422").split(",")

