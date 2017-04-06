"""
Modified as a free demo for trakerr.
"""

import json
import string

from django.http import JsonResponse
from django.views.generic import View

from chatterbot import ChatBot
from chatterbot.ext.django_chatterbot import settings

from trakerr import TrakerrClient

class ChatterBotViewMixin(object):
    """
    Subclass this mixin for access to the 'chatterbot' attribute.
    """

    chatterbot = ChatBot(**settings.CHATTERBOT)

    def validate(self, data):
        """
        Validate the data recieved from the client.

        * The data should contain a text attribute.
        """
        from django.core.exceptions import ValidationError

        if 'text' not in data:
            raise ValidationError('The attribute "text" is required.')

    def get_chat_session(self, request):
        """
        Return the current session for the chat if one exists.
        Create a new session if one does not exist.
        """
        chat_session_id = request.session.get('chat_session_id', None)
        chat_session = self.chatterbot.conversation_sessions.get(chat_session_id, None)

        if not chat_session:
            chat_session = self.chatterbot.conversation_sessions.new()
            request.session['chat_session_id'] = chat_session.id_string

        return chat_session


class ChatterBotView(ChatterBotViewMixin, View):
    """
    Provide an API endpoint to interact with ChatterBot.
    """

    def _serialize_conversation(self, session):
        if session.conversation.empty():
            return []

        conversation = []

        for statement, response in session.conversation:
            conversation.append([statement.serialize(), response.serialize()])

        return conversation

    def post(self, request, *args, **kwargs):
        """
        Return a response to the statement in the posted data.
        """
        input_data = json.loads(request.read().decode('utf-8'))

        self.validate(input_data)

        chat_session = self.get_chat_session(request)

        client = TrakerrClient("b2f59d0778004e503ddf685382297a741205333295736")

        value = str(input_data)
        value = value.lower()
        value = value.translate(None, string.punctuation)
        keyword = ["tylenol", "drugs", "prescription", "marajuana", "smoke"]
        session_id = request.session.session_key

        if session_id is None:
            request.session.Create()
            session_id = request.session.session_key

        print len(session_id)

        if any(x in value for x in keyword):
            client.log({"user":"test@trakker.io", "session":session_id,
                        "errname":"user asked a protected question",
                        "errmessage":"User teaching my robot bad things"},
                       "Warning", "input", False)

        if "make error" in value:
            try:
                self._some_method()
            except ArithmeticError:
                client.log({"user":"test@trakker.io", "session":session_id}, "error")

        if "make fatal" in value:
            try:
                self._some_method()
            except ArithmeticError:
                client.log({"user":"test@trakker.io", "session":session_id}, "fatal")

        if "make info" in value:
            client.log({"user":"test@trakker.io", "session":session_id,
                        "errname":"chatbot info", "errmessage":"Chatbot made an info for you!"},
                       "info")

        if "make debug" in value:
            client.log({"user":"test@trakker.io", "session":session_id,
                        "errname":"chatbot debug",
                        "errmessage":"Chatbot sometimes helps you debug!"},
                       "debug")

        response = self.chatterbot.get_response(input_data, chat_session.id_string)
        response_data = response.serialize()

        return JsonResponse(response_data, status=200)

    def get(self, request, *args, **kwargs):
        """
        Return data corresponding to the current conversation.
        """
        chat_session = self.get_chat_session(request)

        data = {
            'detail': 'You should make a POST request to this endpoint.',
            'name': self.chatterbot.name,
            'conversation': self._serialize_conversation(chat_session)
        }

        # Return a method not allowed response
        return JsonResponse(data, status=405)

    def patch(self, request, *args, **kwargs):
        """
        The patch method is not allowed for this endpoint.
        """
        data = {
            'detail': 'You should make a POST request to this endpoint.'
        }

        # Return a method not allowed response
        return JsonResponse(data, status=405)

    def delete(self, request, *args, **kwargs):
        """
        The delete method is not allowed for this endpoint.
        """
        data = {
            'detail': 'You should make a POST request to this endpoint.'
        }

        # Return a method not allowed response
        return JsonResponse(data, status=405)


    def _some_method(self):
        self._another_method()

    def _another_method(self):
        self._our_code()

    def _our_code(self):
        self._is_throwing()

    def _is_throwing(self):
        self._throwing_method()

    def _an_error(self):
        self._throwing_method()

    def _throwing_method(self):
        raise ArithmeticError("Matrix Math is hard")
