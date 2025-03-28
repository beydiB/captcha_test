import os
from seleniumbase import SB

print("the secret is ", os.environ["PROXY"])  #leave

with SB(uc=True, test=True, proxy=os.environ["PROXY"]) as sb:
    url = "https://gitlab.com/users/sign_in"
    sb.activate_cdp_mode(url)
    sb.uc_gui_click_captcha()
    sb.sleep(2)
    sb.uc_gui_handle_captcha()
    sb.sleep(20)

