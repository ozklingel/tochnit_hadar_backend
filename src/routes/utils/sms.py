from typing import Dict, Union, List

import requests

import config


def send_json_request(data: Dict):
    """
    Sends a JSON request containing SMS data to the specified URL.

    Parameters:
        data (Dict): A dictionary containing the SMS data to be sent in JSON format.

    Returns:
        requests.Response: The response object returned by the HTTP POST request.

    Raises:
        Any exceptions raised during the HTTP request will propagate upwards.

    Note:
        - The function utilizes get_header_for_send_sms() to retrieve the appropriate headers for the request.
        - It sends an HTTP POST request to the URL obtained via get_url(), with the provided data in JSON format.
        - The response JSON is checked for the "status" and "message" fields to ensure the SMS was sent successfully.
          If the status is not 0 or the message is not 'SMS will be sent', a problem message is printed.

    Example usage:
        response = send_json_request({"sms": {"user": {"username": "user123"}, "source": "source1",
                                            "destinations": {"phone": [{"$": {"id": ""}, "_": "9876543210"}]},
                                            "message": "Hello, this is a test message."}})
        """
    headers = get_header_for_send_sms()
    response = requests.post(config.SendMessages.Sms.url, json=data, headers=headers)
    response_json = response.json()
    if ("status" not in response_json or response_json["status"] != 0 or
            "message" not in response_json or response_json['message'] != 'SMS will be sent'):
        print(config.SendMessages.Sms.problem_sms_wasnt_sent + " ,response_json:\n" + str(response_json))
        return response_json
    return None


def get_header_for_send_sms():
    token = config.SendMessages.Sms.token
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    return headers


def get_data_filled(source: str, recipients: List[str], message: str):
    """
   Creates a dictionary containing filled data for sending SMS messages.

   Parameters:
       source (str): The source identifier from which the message will be sent.
       recipients (List[str]): A list of phone numbers representing the recipients of the SMS messages.
       message (str): The message content to be sent to the recipients.

   Returns:
       dict: A dictionary containing filled data for sending SMS messages. The structure of the dictionary is as follows:
           {
               "sms": {
                   "user": {
                       "username": <username>,
                   },
                   "source": <source>,
                   "destinations": {
                       "phone": [
                           {
                               "$": {
                                   "id": ""
                               },
                               "_": <recipient_phone_number>
                           },
                           ...
                       ]
                   },
                   "message": <message_content>,
               }
           }

   Note:
       - The function uses get_username() to retrieve the username for the SMS user.
       - The "destinations" section of the data dictionary is structured to include multiple recipient phone numbers.
       - Each recipient phone number is added as a dictionary with an empty "id" field and the phone number under "_".

   Example usage:
       data = get_data_filled("source1", ["9876543210", "8765432109"], "Hello, this is a test message.")
   """
    data = {
        "sms": {
            "user": {
                "username": config.SendMessages.Sms.username,
            },
            "source": "0" + source,
            "destinations": {
                "phone":
                    [
                        {
                            "$": {
                                "id": ""
                            },
                            "_": str("0" + recipient)
                        }
                        for recipient in recipients]
            },
            "message": message,
        }
    }
    return data


def send_sms_019(sources: Union[List[str], str], recipients: List[str], message: str):
    """
    Sends SMS messages to recipients using specified sources.

    Parameters:
        sources (Union[List[str], str]): A string or a list of strings representing the source(s) from which the message
                                          is sent. If multiple sources are provided, the message will be sent from each
                                          of them. Format of a number: 05XXXXXXXX
        recipients (List[str]): A list of phone numbers representing the recipients of the SMS messages.
        Format of a number: 05XXXXXXXX
        message (str): The message content to be sent to the recipients.

    Returns:
        None

    Raises:
        Any exceptions raised during the process of retrieving data or sending requests will propagate upwards.

    Example usage:
        send_sms_019('1234567890', ['9876543210', '8765432109'], 'Hello, this is a test message.')
        send_sms_019(['source1', 'source2'], ['9876543210'], 'Hello, this is a test message.')
    """
    if isinstance(sources, str):
        sources = [sources]
    errors = {}
    for source in sources:
        data = get_data_filled(source=source, recipients=recipients, message=message)
        print("data", data)
        response = send_json_request(data)
        if response is not None:
            errors[source] = response
    if len(errors) > 0:
        return errors
    return None
