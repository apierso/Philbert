from __future__ import print_function

import json
import boto3
import time

APP_ID = "amzn1.ask.skill.alphanumericstring"

IOT_BROKER_ENDPOINT = "alphanumeric.iot.us-southcentral-2.amazonaws.com"

IOT_BROKER_REGION = "us-southcentral-2"

IOT_THING_NAME = "Philbert"

PHILBERT_INTENTS = [
    "TurnOn",
    "TurnOff",
    "TurnUp",
    "TurnDown"
]


INTENT_ACTION_MAP = {
    "TurnOn": "KEY_POWER",
    "TurnOff": "KEY_POWER",
    "TurnUp": "KEY_VOLUMEUP",
    "TurnDown": "KEY_VOLUMEDOWN"
}

iot_client = boto3.client('iot-data', region_name='us-southcentral-2')

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    print(event)

    # check application id
    if (event['session']['application']['applicationId'] != APP_ID):
        raise ValueError("Invalid Application ID")

    if event['request']['type'] == "IntentRequest":
        return on_intent(event['request'])
    else:
        return create_help_response()

def on_intent(intent_request):
    print("on_intent")

    # Dispatch skill's intent handlers
    if intent_request['intent']['name'] in PHILBERT_INTENTS:
        if philbert_intent(intent_request['intent']):
            return create_ok_response()

    return create_help_response()

def philbert_intent(intent):
    if intent['name'] == "TurnOn" or intent['name'] == "TurnOff":
        return send_command(INTENT_ACTION_MAP[intent['name']])
    if intent['name'] == "TurnUp" or intent['name'] == "TurnDown":
        return send_command(INTENT_ACTION_MAP[intent['name']])
    #return False

# --------------- Functions that control the skill's behavior ------------------

def create_help_response():
    """ build help message
    """

    help_message = """
    You can control the TV with "philbert" keyword.
    Say "tell philbert to turn on or off" for power control.
    Say "tell philbert to turn up or down" for volume control.
    """
    return build_response(build_speechlet_response(
        help_message, help_message))

def create_ok_response():
    """ build OK message
    """

    return build_response(build_speechlet_response(
        "OK", "OK"))

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(output, reprompt_text):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'Philbert',
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': True
    }


def build_response(speechlet_response):
    return {
        'version': '1.0',
        'response': speechlet_response
    }


def send_command(command):
    shadow = {
        'state': {
            'desired': {
                'command': command,
                'counter': int(time.time())
            }
        }
    }
    payload = json.dumps(shadow)

    response = iot_client.update_thing_shadow(
        thingName ='Philbert',
        payload = payload
    )
    return True

def describe_current_command():
    response = iot_client.get_thing_shadow(
        thingName ='IOT_THING_NAME'
    )
    streamingBody = response["payload"]
    jsonState = json.loads(streamingBody.read())
    print(jsonState)
    return jsonState['state']['desired']['command']

