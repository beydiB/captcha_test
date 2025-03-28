import os
from dotenv import load_dotenv
from seleniumbase import SB

# Load environment variables from .env file
load_dotenv()

print(os.getenv("PROXY"))

with SB(uc=True, test=True, proxy=os.getenv("PROXY")) as sb:
    url = "https://gitlab.com/users/sign_in"
    sb.activate_cdp_mode(url)
    sb.uc_gui_click_captcha()
    sb.sleep(2)
    sb.uc_gui_handle_captcha()
    sb.sleep(20)

    #leave window open