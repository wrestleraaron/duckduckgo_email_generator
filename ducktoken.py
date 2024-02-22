'''
Create DuckDuckGo email addresses based on user input.  There is a limit of 5 email addresses
that can be created in each execution.

You will need a valid duck.com account already setup
You will need to be have access to your email account setup as a forward to get the OTP sent

This may fail due to DuckDuckGo's bot prevention.

Created 2024/02/22
Tested with Python 3.12.2

Comments to: yvs9j135@duck.com
'''
import sys
import requests

UA_STRING = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'


def get_count_of_addresses() -> int:
    '''
    Prompts the user for the number of email addresses desired and validates it.

    This function retrieves a user's input representing the desired number of
    email addresses. It enforces a maximum limit of 5 addresses and returns the
    validated integer value.

    Returns:
       An integer representing the number of desired email addresses (between 1 and 5).

    Raises:
       ValueError: If the user input is invalid (non-numeric or outside the allowed range).
    '''

    count = input('How many e-mail addresses do you want (limit 5)? ')
    if count.isdigit() is False:
        raise TypeError('Entry must be a number!')

    if int(count) > 5 or int(count) < 1:
        raise ValueError("Entry be between 1 and 5")

    return int(count)


def get_username() -> str:
    '''
    Prompts the user for a DuckDuckGo username and removes any domain suffix.

    This function prompts the user to enter their DuckDuckGo username without
    the "@duck.com" suffix. It validates the input to ensure it doesn't include
    an "@" and returns the cleaned username as a string.

    Returns:
      The extracted username string without the "@duck.com" domain suffix.

    Raises:
      ValueError: If the user input includes an "@" symbol.
    '''

    duck_username = input("Enter your DuckDuckGo username (without @duck.com): ")

    if r'@' in duck_username:
        raise ValueError("Username cannot contain an @ symbol.")

    return duck_username


def send_otp_email(duck_user: str) -> None:
    '''
    Initiates a web call to DuckDuckGo's login link API.

    This function sends a GET request to DuckDuckGo's login link API endpoint
    using the provided username. It prints the HTTP status code of the response.

    Args:
      duck_user: The DuckDuckGo username to use in the API request.

    Returns:
      None. The function primarily prints the status code and doesn't return data.

    Raises:
      requests.exceptions.RequestException: If an error occurs during the request.

    Examples:
      >>> send_otp_email("my_username")
      200  # If the request is successful
    '''

    headers = {'User-Agent': UA_STRING}

    try:
        response = requests.get(
            f'https://quack.duckduckgo.com/api/auth/loginlink?user={duck_user}',
            headers=headers,
            timeout=30
        )
        response.raise_for_status()  # Raise exception for non-2xx status codes
    except requests.exceptions.RequestException as err:
        print(f'Error making web call: {err}')
        sys.exit(1)

#    return None


def get_token(duck_user: str) -> str:
    '''
    Retrieves an authentication token from DuckDuckGo using a one-time passcode (OTP).

    This function prompts the user for an OTP received via email and attempts to
    exchange it for an authentication token using DuckDuckGo's login API. It
    returns the token if successful, raising an exception otherwise.

    Args:
      duck_user: The DuckDuckGo username (without "@duck.com") used for login.

    Returns:
      The retrieved authentication token as a string, or raises an exception.

    Raises:
      requests.exceptions.RequestException: If an error occurs during the request.
      ValueError: If the OTP input contains spaces or is invalid.

    Examples:
      >>> token = get_token("my_username")
      print(f"Your token is {token}")
    '''

    headers = {
        'User-Agent': UA_STRING
    }

    try:
        otp_input = input("Please enter the OTP from your email: ")
        otp_input.replace(' ', '+')

        response = requests.get(
            f'https://quack.duckduckgo.com/api/auth/login?otp={otp_input}&user={duck_user}',
            headers=headers,
            timeout=30
        ).json()

    except requests.exceptions.RequestException as err:
        print(f'Error using OTP to get token: {err}')
        sys.exit(1)

    try:
        a_token = response['token']
    except ValueError as err:
        print(f'Invalid OTP format: {err}')
        sys.exit(2)

    return a_token


def get_bearer_token(a_token: str) -> str:
    '''
    Retrieves a bearer token using an authentication token (a_token) and a one-time passcode (OTP).

    This function takes an initial authentication token (a_token) and prompts the
   user for an OTP received via email. It attempts to exchange the a_token and OTP
   for a new bearer token using DuckDuckGo's email API and returns the bearer token
   if successful.

   Args:
     a_token: An existing DuckDuckGo authentication token (string).

   Returns:
     The retrieved bearer token as a string, or raises an exception on failure.

   Raises:
     requests.exceptions.RequestException: If an error occurs during the request.
     ValueError: If the OTP input contains spaces or is invalid.
     requests.exceptions.HTTPError: If the API request fails with a non-2xx status code.

   Examples:
     >>> bearer_token = get_bearer_token("YOUR_AUTHENTICATION_TOKEN")
     print(f"Your new bearer token is {bearer_token}")
    '''

    if not a_token:
        raise ValueError(f'Authentication token {a_token} cannot be empty.')

    headers = {
        'User-Agent': UA_STRING,
        'Authorization': f'Bearer {a_token}'
    }

    try:
        response = requests.get(
            'https://quack.duckduckgo.com/api/email/dashboard',
            headers=headers,
            timeout=30
        ).json()

    except requests.exceptions.RequestException as err:
        print(f'Error getting bearer token: {err}')
        sys.exit(1)

    try:
        b_token = response['user']['access_token']
    except ValueError as err:
        print(f'Invalid Token format: {err}')
        sys.exit(2)

    return b_token


def get_email_addresses(count: int, b_token: str) -> None:
    '''
    Fetches and prints requested number of email addresses using a DuckDuckGo API call.

    This function fetches a specified number of email addresses from DuckDuckGo's
    email API using the provided access token. It iterates through the requested
    count, making API calls and printing the retrieved email addresses.

    Args:
      count: The number of email addresses to fetch (integer).
      b_token: A valid DuckDuckGo API access token (string).

    Returns:
      None. The function primarily prints email addresses and doesn't return data.

    Raises:
      requests.exceptions.RequestException: If an error occurs during the API calls.
      ValueError: If the requested count is invalid (non-positive).

   Examples:
     >>> get_email_addresses(3, "YOUR_ACCESS_TOKEN")
     Email #1: some_email@duck.com
     Email #2: another_email@duck.com
     Email #3: third_email@duck.com

    '''

    if count <= 0:
        raise ValueError("Count must be a positive integer.")

    headers = {
        'User-Agent': UA_STRING,
        'Authorization': f'Bearer {b_token}'
    }

    for i in range(count):
        try:
            response = requests.post(
                'https://quack.duckduckgo.com/api/email/addresses',
                headers=headers,
                timeout=30
            ).json()
            email = response['address']
            print(f'Email #{i+1}: {email}@duck.com')
        except requests.exceptions.RequestException as err:
            print(f'Error getting email #{i+1}: {err}')
            sys.exit(1)


email_count = get_count_of_addresses()
username = get_username()
send_otp_email(username)
token = get_token(username)
bearer_token = get_bearer_token(token)
get_email_addresses(email_count, bearer_token)
