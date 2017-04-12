"""
Modified as a free demo for trakerr.
"""

import datetime
import json
import string

from django.http import JsonResponse
from django.views.generic import View

from chatterbot import ChatBot
from chatterbot.ext.django_chatterbot import settings

from trakerr import TrakerrClient
from trakerr_client.models import CustomData, CustomStringData, CustomDoubleData

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
        a = datetime.datetime.now()
        input_data = json.loads(request.read().decode('utf-8'))

        self.validate(input_data)

        chat_session = self.get_chat_session(request)

        client = TrakerrClient("05bb07736fdaed2788d5bb123373381f21869593598803")

        value = input_data["text"]
        value = value.lower()
        translate_table = [ord(unicode(c)) for c in string.punctuation]
        value = value.translate(translate_table)
        keyword = ["tylenol", "drugs", "prescription", "marajuana", "smoke"]
        session_id = request.session.session_key
        browser_name = request.user_agent.browser.family
        browser_version = request.user_agent.browser.version_string

        sweets = ["sugar", "candy", "chocolate", "dessert", "cookies"]
        snacks = ["pretzel", "crackers", "cookies"]

        if session_id is None:
            request.session.create()
            session_id = request.session.session_key

        medicine_seg = None
        sweet_seg = None
        snacks_seg = None

        if self._words_in_string(sweets, value):
            try:
                #gets a random word that was found in the string.
                sweet_seg = self._words_in_string(sweets, value).pop()
                #sweet_seg = "sweets"
            except KeyError:
                pass

        if self._words_in_string(snacks, value):
            try:
                snacks_seg = self._words_in_string(snacks, value).pop()
                #snacks_seg = "snacks"
            except KeyError:
                pass

        if self._words_in_string(keyword, value):
            try:
                medicine_seg = self._words_in_string(keyword, value).pop()
                #medicine_seg = "medicine"
            except KeyError:
                pass

            event = client.create_new_app_event("warning", "User Input",
                                                "User asked a protected question",
                                                "User teaching my robot bad things")
            event.event_user = "test@trakker.io"
            event.event_session = session_id
            event.context_app_browser = browser_name
            event.context_app_browser_version = browser_version

            event.custom_properties = CustomData(CustomStringData(value), CustomDoubleData(self._timer(a)))
            event.custom_segments = CustomData(CustomStringData())

            if medicine_seg is not None:
                event.custom_segments.string_data.custom_data3 = medicine_seg

            if sweet_seg is not None:
                event.custom_segments.string_data.custom_data1 = sweet_seg

            if snacks_seg is not None:
                event.custom_segments.string_data.custom_data2 = snacks_seg
            client.send_event_async(event)

        if "make fatal" in value:
            try:
                self._some_method()
            except ArithmeticError:
                event = client.create_new_app_event("fatal", exc_info=True)
                event.event_user = "test@trakker.io"
                event.event_session = session_id
                event.context_app_browser = browser_name
                event.context_app_browser_version = browser_version

                event.custom_properties = CustomData(CustomStringData(value), CustomDoubleData(self._timer(a)))
                event.custom_segments = CustomData(CustomStringData())

                if sweet_seg is not None:
                    event.custom_segments.string_data.custom_data1 = sweet_seg

                if snacks_seg is not None:
                    event.custom_segments.string_data.custom_data2 = snacks_seg

                client.send_event_async(event)

        if "make error" in value:
            try:
                self._some_method()
            except ArithmeticError:
                event = client.create_new_app_event("error", exc_info=True)
                event.event_user = "test@trakker.io"
                event.event_session = session_id
                event.context_app_browser = browser_name
                event.context_app_browser_version = browser_version

                event.custom_properties = CustomData(CustomStringData(value), CustomDoubleData(self._timer(a)))
                event.custom_segments = CustomData(CustomStringData())

                if sweet_seg is not None:
                    event.custom_segments.string_data.custom_data1 = sweet_seg

                if snacks_seg is not None:
                    event.custom_segments.string_data.custom_data2 = snacks_seg

                client.send_event_async(event)

        if "make info" in value:
            event = client.create_new_app_event("info", "info here!",
                                                "Chatbot info", "Chatbot made an info for you!")
            event.event_user = "test@trakker.io"
            event.event_session = session_id
            event.context_app_browser = browser_name
            event.context_app_browser_version = browser_version

            event.custom_properties = CustomData(CustomStringData(value), CustomDoubleData(self._timer(a)))
            event.custom_segments = CustomData(CustomStringData())

            if sweet_seg is not None:
                event.custom_segments.string_data.custom_data1 = sweet_seg

            if snacks_seg is not None:
                event.custom_segments.string_data.custom_data2 = snacks_seg
            client.send_event_async(event)

        if "make debug" in value:
            event = client.create_new_app_event("debug", "Debug statement!",
                                                "Chatbot debug",
                                                "Chatbot sometimes helps you debug!")
            event.event_user = "test@trakker.io"
            event.event_session = session_id
            event.context_app_browser = browser_name
            event.context_app_browser_version = browser_version

            event.custom_properties = CustomData(CustomStringData(value), CustomDoubleData(self._timer(a)))
            event.custom_segments = CustomData(CustomStringData())

            if sweet_seg is not None:
                event.custom_segments.string_data.custom_data1 = sweet_seg

            if snacks_seg is not None:
                event.custom_segments.string_data.custom_data2 = snacks_seg

            client.send_event_async(event)

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

    def _timer(self, a):
        """
        Takes a datetime and returns a timedelta from now in miliseconds
        """
        return int((datetime.datetime.now() - a).total_seconds() * 1000)

    def _words_in_string(self, word_list, a_string):
        """
        Takes a string and a list of words and conversts both into a set before finding the intersection.
        :returns: A set of words from the list that were found in the string. test the method to see true false,
        but the set also lets you get the words found in the string.
        """
        return set(word_list).intersection(a_string.split())


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
