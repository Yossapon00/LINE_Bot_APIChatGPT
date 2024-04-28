import Data
import re

# Rule-based chatbot
class RuleBasedChatbot:
    def __init__(self):
        self.rules = {
            # All Greeting
            'greeting': {'patterns': ['hello', 'hey' , 'What up'],
                         'response': 'Hello! How can I help you?'},
            'goodbye': {'patterns': ['bye', 'goodbye', 'see you'],
                        'response': 'Goodbye! Have a great day!'},
            'thanks': {'patterns': ['thank you', 'thanks'],
                       'response': 'You\'re welcome!'},
            'title': {'patterns': ['title'],
                      'response': 'INSTRUMENT DOCUMENT PROJECT ENGINEERING SPECIFICATION FOR INTEGRATED CONTROL AND SAFETY SYSTEM (ICSS)'},
            
            # would you like to insert data from file Data.py you can write like this
            # This structure for 1 pattern
            'World': {'patterns': ['world1', 'world2'],
                    'response': Data.textshow}, # or 'response': Data.Picture_1} for show picture
            
            'default': {'response': 'I\'m sorry, I didclsn\'t understand that. Can you please rephrase?'}
        }

    
    def preprocess_input(self, user_input):
        # Remove punctuation and convert to lowercase
        cleaned_input = re.sub(r'[/*\-\+\@\?\%\#\!\_\-]', '', user_input).lower()
        return cleaned_input

    def respond(self, user_input):
        cleaned_input = self.preprocess_input(user_input)
        for key, rule in self.rules.items():
            for pattern in rule.get('patterns', []):
                if re.search(pattern, cleaned_input,re.IGNORECASE):
                    return rule['response']

        return self.rules['default']['response']