"""Ask Groq questions about fictional contacts using two local tools."""
import json
import os
from pathlib import Path
import sys

import requests
from dotenv import load_dotenv
from contacts import draft_connection_message, search_contacts

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

TOOLS = [
    {'type': 'function', 'function': {
        'name': 'search_contacts',
        'description': 'Find fictional practice contacts by name, company, job title, or area of interest.',
        'parameters': {'type': 'object', 'properties': {
            'field': {'type': 'string', 'enum': ['name', 'company', 'job title', 'interest']},
            'query': {'type': 'string', 'description': 'Text to find in that field.'},
        }, 'required': ['field', 'query']},
    }},
    {'type': 'function', 'function': {
        'name': 'draft_connection_message',
        'description': 'Create a LinkedIn connection message for a named fictional practice contact, maximum 200 characters.',
        'parameters': {'type': 'object', 'properties': {
            'name': {'type': 'string', 'description': 'The name of one fictional contact.'},
        }, 'required': ['name']},
    }},
]
FUNCTIONS = {'search_contacts': search_contacts, 'draft_connection_message': draft_connection_message}


def ask_model(messages):
    key = os.environ.get('GROQ_API_KEY')
    if not key:
        raise ValueError('GROQ_API_KEY not found. Add it to the existing .env in the project root.')
    response = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={'Authorization': 'Bearer ' + key},
        json={'model': 'openai/gpt-oss-120b', 'messages': messages, 'tools': TOOLS},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()['choices'][0]['message']


def answer(question):
    messages = [
        {'role': 'system', 'content': 'These are fictional contacts. Use the tools for contact facts and messages. Do not invent information. If no match is found, say so.'},
        {'role': 'user', 'content': question},
    ]
    for _ in range(8):
        reply = ask_model(messages)
        calls = reply.get('tool_calls') or []
        if not calls:
            return reply.get('content') or 'The model returned an empty response.'
        messages.append(reply)
        for call in calls:
            name = call.get('function', {}).get('name', '')
            function = FUNCTIONS.get(name)
            try:
                args = json.loads(call['function']['arguments'])
                if not isinstance(args, dict) or function is None:
                    raise ValueError('Unknown tool or invalid arguments.')
                result = function(**args)
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                result = {'error': str(exc)}
            print('The model asked for:', name)
            # Print the checked draft directly: a model rewrite could exceed the limit.
            if name == 'draft_connection_message' and 'message' in result:
                return result['message']
            messages.append({'role': 'tool', 'tool_call_id': call['id'], 'content': json.dumps(result, ensure_ascii=False)})
    return 'The model made too many tool requests. Try a more specific question.'


if __name__ == '__main__':
    # Groq may return Unicode text even when Windows redirects output to a file.
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    question = ' '.join(sys.argv[1:]) or 'Draft a LinkedIn connection request for Neel Verma.'
    try:
        print('\n' + answer(question))
    except (ValueError, requests.RequestException) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)
