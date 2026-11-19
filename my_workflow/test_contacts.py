import unittest
from unittest.mock import patch

from contacts import draft_connection_message, search_contacts
import tool_call
from fastmcp import Client
from mcp_server import mcp


class ContactsTests(unittest.TestCase):
    def test_search_names_case_insensitively(self):
        result = search_contacts('name', 'aarav')
        self.assertEqual([p['Name'] for p in result['matches']], ['Aarav Mehta'])

    def test_company_and_interest_search(self):
        self.assertEqual(len(search_contacts('company', 'PaperKite')['matches']), 2)
        self.assertEqual(search_contacts('interest', 'multimodal')['matches'][0]['Name'], 'Neel Verma')

    def test_missing_and_empty_search_are_clear(self):
        self.assertEqual(search_contacts('name', 'Nobody')['matches'], [])
        self.assertIn('error', search_contacts('name', '  '))
        self.assertIn('error', search_contacts('email', 'a'))

    def test_draft_uses_contact_and_is_at_most_200_characters(self):
        result = draft_connection_message('Neel Verma')
        self.assertIn('Neel', result['message'])
        self.assertIn('Mosaic Finch AI', result['message'])
        self.assertIn('Multimodal AI applications', result['message'])
        self.assertLessEqual(len(result['message']), 200)
        self.assertEqual(result['characters'], len(result['message']))

    def test_draft_rejects_missing_or_ambiguous_name(self):
        self.assertIn('error', draft_connection_message('Nobody'))
        self.assertIn('error', draft_connection_message('a'))

    def test_answer_returns_checked_draft_without_model_rewrite(self):
        reply = {'role': 'assistant', 'tool_calls': [{
            'id': 'call-1', 'type': 'function',
            'function': {'name': 'draft_connection_message', 'arguments': '{"name":"Neel Verma"}'},
        }]}
        with patch.object(tool_call, 'ask_model', return_value=reply):
            answer = tool_call.answer('Draft a message for Neel')
        self.assertIn('Mosaic Finch AI', answer)
        self.assertLessEqual(len(answer), 200)

    def test_private_sheet_failure_returns_clear_error(self):
        with patch.dict('os.environ', {'CONTACTS_SOURCE': 'google'}):
            with patch('contacts.requests.get', side_effect=__import__('requests').ConnectionError('offline')):
                self.assertIn('Could not read the Google Sheet', search_contacts('name', 'Neel')['error'])


class McpTests(unittest.IsolatedAsyncioTestCase):
    async def test_client_discovers_and_calls_both_tools(self):
        async with Client(mcp) as client:
            tools = await client.list_tools()
            self.assertEqual({tool.name for tool in tools}, {'search_contacts', 'draft_connection_message'})
            result = await client.call_tool('search_contacts', {'field': 'interest', 'query': 'multimodal'})
            self.assertIn('Neel Verma', str(result.content))
            result = await client.call_tool('draft_connection_message', {'name': 'Neel Verma'})
            self.assertIn('Mosaic Finch AI', str(result.content))


if __name__ == '__main__':
    unittest.main()
