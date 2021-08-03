# MIT License
#
# Copyright (c) 2021 Kristjan Vilgo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# Short guide
# 1. Install python -> https://www.python.org/downloads/release/python-3711/
# 2. Install needed modules -> open cmd and use command "python -m pip install --user opdm-api"
# 3. Update settings.py -> just open/edit with any text editor
# 4. Run the script

import OPDM
import settings

## Process

# Create connection to OPDM
service = OPDM.create_client(settings.OPDM_SERVER, username=settings.OPMD_USERNAME, password=settings.OPDM_PASSWORD)
print(f"Connection created to OPDM at {settings.OPDM_SERVER} as {settings.OPMD_USERNAME}")

# Create list of all time horizons
time_horizons = [f"{item:02d}" for item in list(range(1,32))] + ["ID", "1D", "2D", "YR"]

# Create subscription for each time horizon
for time_horizon in time_horizons:
    print(f"Adding subscription for {time_horizon}")
    response = service.publication_subscribe("IGM", subscription_id=f"IGM-{time_horizon}", metadata_dict={'pmd:timeHorizon': time_horizon})
    print(response)


