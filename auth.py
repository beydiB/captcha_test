import os

# Login credentials
EMAIL = os.environ['UPWORK_EMAIL']
PASSWORD = os.environ['UPWORK_PASSWORD']

def login(sb):
    """
    Handle the Upwork login process.
    
    Args:
        sb: SeleniumBase instance for browser interaction
        
    Returns:
        bool: True if login was successful, False otherwise
    """
    print("Attempting to login...")
    try:
        sb.assert_element('a[href="/ab/account-security/login"]', timeout=30)
        login_link = sb.find_element('a[href="/ab/account-security/login"]')
        print("Login link found - not logged in")
        # Click the login link
        print("Clicking login link...")
        login_link.click()
        sb.sleep(2)
        
        # Enter email
        sb.assert_element("#login_username", timeout=10)
        print("Entering email...")
        sb.type("#login_username", EMAIL)
        
        # Click continue button after email
        print("Clicking continue button after email...")
        sb.click("#login_password_continue")
        sb.sleep(2)
        
        # Enter password
        sb.assert_element("#login_password", timeout=10)
        print("Entering password...")
        sb.type("#login_password", PASSWORD)
        
        # Check "Keep me logged in" checkbox
        print("Checking 'Keep me logged in' checkbox...")
        sb.click("#login_rememberme")
        
        # Click login button
        print("Clicking login button...")
        sb.click("#login_control_continue")
        
        # Wait for potential security question
        print("Waiting for potential security question...")
        sb.sleep(10)
        
        # Check if security question appears
        try:
            security_question = sb.find_element("#login_answer", timeout=10)
            print("Security question detected!")
            
            # Enter mother's maiden name
            sb.assert_element("#login_answer", timeout=10)
            print("Entering mother's maiden name...")
            sb.type("#login_answer", os.environ["UPWORK_SECURITY_QUESTION_ANSWER"])  
            
            # Check "Remember this device" if present
            try:
                remember_device = sb.find_element("#login_remember", timeout=10)
                print("Checking 'Remember this device' checkbox...")
                remember_device.click()
            except:
                print("No 'Remember this device' checkbox found")
            
            # Click continue button
            print("Clicking continue button after security question...")
            sb.assert_element("#login_control_continue", timeout=10)
            sb.click("#login_control_continue")
            sb.sleep(10)
            
        except:
            print("No security question detected, proceeding...")
        
        # Check if login was successful
        if "nx/client/dashboard" in sb.get_current_url():
            print("Login successful!")
            return True
        else:
            print("Login might have failed")
            return False
            
    except Exception as e:
        # If we can't find the login link, we might be already logged in
        if "job-tile" in sb.get_page_source() or "dashboard" in sb.get_current_url() or "my-feed" in sb.get_current_url():
            print("Already logged in!")
            return True
        else:
            print(f"Error during login check: {e}")
            return False

