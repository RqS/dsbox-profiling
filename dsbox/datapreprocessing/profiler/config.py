

D3M_API_VERSION = '2018.1.5'
VERSION = "1.0.0"
TAG_NAME = ""

REPOSITORY = "https://github.com/usc-isi-i2/dsbox-profiling"
PACAKGE_NAME = "dsbox-dataprofiling"

D3M_PERFORMER_TEAM = 'ISI'

if TAG_NAME:
    PACKAGE_URI = "git+" + REPOSITORY + "@" + TAG_NAME
else:
    PACKAGE_URI = "git+" + REPOSITORY 

PACKAGE_URI = PACKAGE_URI + "#egg=" + PACAKGE_NAME


INSTALLATION_TYPE = 'GIT'
if INSTALLATION_TYPE == 'PYPI':
    INSTALLATION = {
        "type" : "PIP",
        "package": PACAKGE_NAME,
        "version": VERSION
    }
else:
    # INSTALLATION_TYPE == 'GIT'
    INSTALLATION = {
        "type" : "PIP",
        "package_uri": PACKAGE_URI,
    }
