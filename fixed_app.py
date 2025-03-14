import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Load environment variables
load_dotenv()

# Initialize Slack app with bot token
app = App(token=os.getenv('SLACK_BOT_TOKEN'))

@app.event('app_mention')
def handle_mention(event, say):
    """Basic handler for app mentions"""
    user = event.get('user', 'someone')
    say(f'Hello <@{user}>! I am Lucius your AI assistant.')

@app.message('hello')
def say_hello(message, say):
    """Respond to hello messages"""
    user = message.get('user', 'someone')
    say(f'Hi there <@{user}>! How can I help you today?')

def main():
    """Main function to start the Slack bot"""
    # Use Socket Mode with app token
    handler = SocketModeHandler(app, os.getenv('SLACK_APP_TOKEN'))
    handler.start()

if __name__ == '__main__':
    main()
