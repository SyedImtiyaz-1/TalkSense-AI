import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'ap-south-1')
S3_BUCKET = 'live-call-insight'
S3_PREFIX = 'knowledge-base/'

# Streamlit Page Configuration
PAGE_TITLE = "AI Call Center - Live Insights"
PAGE_ICON = "🤖"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# Voice Configuration
CUSTOMER_VOICE_EDGE = "en-US-AriaNeural"  # US female voice
AGENT_VOICE_EDGE = "en-GB-SoniaNeural"    # UK female voice
CUSTOMER_VOICE_ALT = "en-US-ChristopherNeural"  # US male voice
AGENT_VOICE_ALT = "en-GB-RyanNeural"           # UK male voice 