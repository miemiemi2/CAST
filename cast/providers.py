"""Strands model construction; credentials stay outside the project."""
import os


def provider_name():
    # Keep library/test imports offline by default.  Production launchers set
    # CAST_PROVIDER=vertex explicitly (the gateway script does this), while a
    # bare import must not silently consume model quota or fabricate output.
    return os.getenv('CAST_PROVIDER', 'bedrock').lower()


def model_id():
    default = 'gemini-2.5-flash' if provider_name() == 'vertex' else 'amazon.nova-micro-v1:0'
    return os.getenv('CAST_MODEL_ID', default)


def create_model():
    provider = provider_name()
    if provider == 'vertex':
        adc = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not adc:
            adc = os.path.expanduser('~/.config/gcloud/application_default_credentials.json')
        # A deliberately unset provider is treated as unavailable in offline
        # installs; explicit CAST_PROVIDER=vertex is allowed to construct the
        # SDK client (tests and remote gateway may supply credentials later).
        if not os.path.exists(adc) and 'CAST_PROVIDER' not in os.environ:
            raise ValueError('Vertex is disabled until Google Application Default Credentials are configured. No rule was generated or installed.')
        from strands.models.gemini import GeminiModel
        return GeminiModel(
            model_id=model_id(),
            client_args={
                'vertexai': True,
                'project': os.getenv('GOOGLE_CLOUD_PROJECT', 'ata-creative-change-2026'),
                'location': os.getenv('GOOGLE_CLOUD_LOCATION', 'global'),
                'http_options': {'timeout': 45000, 'retry_options': {'attempts': 1}},
            },
            params={'max_output_tokens': 1024, 'temperature': 0.2,
                    'thinking_config': {'thinking_budget': 0}},
        )
    if provider == 'bedrock':
        if os.getenv('CAST_USE_BEDROCK') != '1':
            raise ValueError('Bedrock is disabled. No rule was generated or installed.')
        from strands.models import BedrockModel
        from botocore.config import Config
        return BedrockModel(model_id=model_id(),
            region_name=os.getenv('AWS_REGION', 'us-east-1'), max_tokens=1024,
            boto_client_config=Config(retries={'total_max_attempts': 1},
                                     read_timeout=45, connect_timeout=10))
    raise ValueError(f'Unknown model provider: {provider}')
