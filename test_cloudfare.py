from seleniumbase import SB

with SB(uc=True, test=True, proxy="boss:Money!@222.127.189.131:8080") as sb:
    url = "https://gitlab.com/users/sign_in"
    sb.activate_cdp_mode(url)
    sb.uc_gui_click_captcha()
    sb.sleep(2)
    sb.uc_gui_handle_captcha()
   