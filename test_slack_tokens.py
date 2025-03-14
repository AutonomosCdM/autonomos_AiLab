import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Create a test script to verify Slack tokens
def test_slack_tokens():
    # Load tokens from environment
    load_dotenv()
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    app_token = os.getenv("SLACK_APP_TOKEN")
    
    print(f"Testing bot token: {bot_token[:10]}...")
    print(f"Testing app token: {app_token[:10]}...")
    
    # Test bot token with auth.test
    bot_client = WebClient(token=bot_token)
    try:
        bot_response = bot_client.auth_test()
        print("✅ Bot token is valid!")
    except SlackApiError as e:
        print("❌ Bot token validation failed!")
    
    # Test app token with apps.connections.open
    if app_token and app_token.startswith("xapp-"):
        try:
            app_response = bot_client.apps_connections_open(app_token=app_token)
            print("✅ App token is valid!")
        except SlackApiError as e:
            print("❌ App token validation failed!")
            print("Note: App token should be complete and the app must have connections:write scope")
    else:
        print("❌ App token is missing or does not start with xapp-")
        
    # Print token lengths for verification
    print(f"Bot token length: {len(bot_token) if bot_token else 0}")
    print(f"App token length: {len(app_token) if app_token else 0}")
    
    # Provide guidance
    print("\nTypical token lengths:")
    print("- Bot tokens (xoxb-): ~60-70 characters")
    print("- App tokens (xapp-): ~80-90 characters")
    
if __name__ == "__main__":
    test_slack_tokens()
