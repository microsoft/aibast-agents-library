"""One cumulative corpus for the AI Migration key matchers.

Every case comes from a reviewed report or an earlier test: the redaction rounds
before PR #362, #362 itself, #366, #370, #376 and the round after it. The corpus only grows.
Never delete a case to make a change pass; if two cases truly conflict, stop and
ask. Every value here is a synthetic placeholder, and a failure names the case
number and the setting name only, never the value.
"""

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
AGENT_FILE = ROOT / "docs" / "experimental" / "ai-migration" / "ai_migration_agent.py"
_spec = importlib.util.spec_from_file_location("ai_migration_agent_corpus", AGENT_FILE)
MODULE = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MODULE)

R = "[REDACTED]"

# (text, values that must vanish). An empty tuple means the text must come back
# exactly as written.
REDACT_TEXT_CORPUS = [
    # ── Ordinary words and settings that must keep their values ──
    # Round 3 (before #362): words that only contain a key word.
    ("Author: Jane Smith", ()),
    ("Primary key: customer_id", ()),
    ("Authorization flow: read the docs", ()),
    # PR #366 test.
    ("primaryKey: customer_id", ()),
    ("keyboard: qwerty", ()),
    ("authoring: drafts first", ()),
    # Round 5: token counts, sign-in methods and plain words.
    ("max_tokens: 4096", ()),
    ("Max tokens: 4096", ()),
    ("tokens: 1200", ()),
    ("budget_tokens=2000", ()),
    ("thinking_tokens: 1024", ()),
    ("Tokenizer: tiktoken", ()),
    ("Secretary: Janet", ()),
    ("OAuth: enabled", ()),
    ("auth_method: oauth", ()),
    ("author_id: u12345678", ()),
    ("Monkey: banana12345", ()),
    ("Call the model with max_tokens: 4096 and thinking_tokens: 1024.", ()),
    ("Auth method for the SharePoint site: OAuth: enabled", ()),
    ("Send the summary to the Secretary: Janet", ()),
    # Plain prose and links around the matcher.
    ("See https://docs.example.com/guide for setup.", ()),
    ("Note: keep answers short.", ()),
    # Round 6 controls: count and limit settings beside the new any-word rule.
    ("max_token: 4096", ()),
    ("MAX_TOKENS_PER_REQUEST=8000", ()),
    ("token_budget: 2000", ()),
    ("token_limit=128000", ()),
    ("thinking_token_budget: 1024", ()),
    ("PASSWORD_MIN_LENGTH: 12", ()),
    ("TOKEN_EXPIRY_SECONDS=3600", ()),
    ("secret_rotation_days: 90", ()),
    ("Tokenizer_name: tiktoken", ()),
    ("author_name: Jane", ()),
    ("OAuth_provider: entra", ()),
    ("auth_type: oauth", ()),
    ("ACCESS_TOKEN_TTL: 3600", ()),

    # ── Secrets that must vanish ──
    # Original redaction test.
    ("token=abcd1234efgh", ("abcd1234efgh",)),
    ("use sk-abcdefghijklmnop1234 here", ("sk-abcdefghijklmnop1234",)),
    ("Bearer abcdefghijklmnop12", ("abcdefghijklmnop12",)),
    ("API_KEY=sk-INLINEfake0000999988887777666655554444", ("sk-INLINEfake0000999988887777666655554444",)),
    ("SECRET=DOTENV-CONTENT-NEVER-READ-45", ("DOTENV-CONTENT-NEVER-READ-45",)),
    ('SEARCH_KEY = "FAKEtomlSECRET123456789012345678901234"', ("FAKEtomlSECRET123456789012345678901234",)),
    ("refresh OAUTH-FILE-CONTENT-NEVER-READ-43", ("OAUTH-FILE-CONTENT-NEVER-READ-43",)),
    # Round 3 test (post-fix secrets).
    ("api_key: abcd1234efgh5678", ("abcd1234efgh5678",)),
    ("password = hunter22x", ("hunter22x",)),
    ("AUTH_TOKEN=abc123def456", ("abc123def456",)),
    ("auth: xyz123abc456", ("xyz123abc456",)),
    # Round 4: joined names and letters-only values.
    ("APIKEY=Zq8rTmw2LpXv", ("Zq8rTmw2LpXv",)),
    ("DBPASSWORD=placeholder2pass", ("placeholder2pass",)),
    ("OPENAI_APIKEY: placeholderpass", ("placeholderpass",)),
    ("accesstoken: abcdefgh1234", ("abcdefgh1234",)),
    ("MYAPP_AUTH=fakeletmeinvalue", ("fakeletmeinvalue",)),
    ("auth: fakeplainvalue", ("fakeplainvalue",)),
    ("DB_PASSWORD=placeholderpass", ("placeholderpass",)),
    ("Connect with DBPASSWORD=placeholderpass and OPENAI_APIKEY: placeholderkey\naccesstoken: fakeaccessvalue",
     ("placeholderpass", "placeholderkey", "fakeaccessvalue")),
    # PR #366 test (JOINED_SECRET_SETTINGS).
    ("DBPASSWORD=placeholderpass", ("placeholderpass",)),
    ("APIKEY=Fakefakefake", ("Fakefakefake",)),
    ("OPENAI_APIKEY: placeholderkey", ("placeholderkey",)),
    ("accesstoken: fakeaccessvalue", ("fakeaccessvalue",)),
    ("MYAPP_AUTH=fakeauthvalue", ("fakeauthvalue",)),
    ("auth: fakeauthvalue", ("fakeauthvalue",)),
    ("dbPassword: placeholderpass", ("placeholderpass",)),
    ("accessToken=fakeaccessvalue", ("fakeaccessvalue",)),
    ("apiKey: fakeplaceholder", ("fakeplaceholder",)),
    ("clientSecret=fakesecretvalue", ("fakesecretvalue",)),
    ("SMTP_PASSWD=fakepassword", ("fakepassword",)),
    ("db_pwd: fakepassword", ("fakepassword",)),
    ("AWS_ACCESSKEY=fakeaccessvalue", ("fakeaccessvalue",)),
    ("privatekey: fakeprivatevalue", ("fakeprivatevalue",)),
    ("github_token=placeholdervalue", ("placeholdervalue",)),
    ("ConnectionString=fakeconnectionvalue", ("fakeconnectionvalue",)),
    ("connection_string: fakeconnectionvalue", ("fakeconnectionvalue",)),
    ("authToken = 'fakeauthvalue'", ("fakeauthvalue",)),
    ("SIGNINGKEY=fakesigningvalue", ("fakesigningvalue",)),
    # Round 5 controls: short values on plain secret names.
    ("api_key: abcd", ("abcd",)),
    ("password: fake2pw", ("fake2pw",)),
    ('password = "placeholderpass"', ("placeholderpass",)),
    ('export DB_PASSWORD="placeholderpass"', ("placeholderpass",)),
    # Round 5: quoted JSON and dict keys.
    ('{"clientSecret": "fakesecretvalue"}', ("fakesecretvalue",)),
    ('"password": "placeholder2pass"', ("placeholder2pass",)),
    ("'db_password': 'placeholderpass'", ("placeholderpass",)),
    ('{"apiKey":"Fakefakefake123"}', ("Fakefakefake123",)),
    ('Use this config: {"clientId": "sample-app", "clientSecret": "fakesecretvalue", "password": "placeholderpass"}',
     ("fakesecretvalue", "placeholderpass")),
    ('{"oauthAccount": {"accessToken": "CREDENTIAL-FILE-CONTENT-NEVER-READ-42"}}',
     ("CREDENTIAL-FILE-CONTENT-NEVER-READ-42",)),
    # A quoted value with spaces is hidden whole, not just its first word.
    ('password: "fake pass phrase"', ("fake", "pass phrase")),
    # Round 6: the secret word is not the last word of the name (SECRET_KEY is
    # the standard web-framework setting); any value shape must still be hidden.
    ("SECRET_KEY=changemeplease", ("changemeplease",)),
    ("JWT_SECRET_KEY: fakejwtsigningvalue", ("fakejwtsigningvalue",)),
    ("STRIPE_SECRET_KEY: fakestripevalue", ("fakestripevalue",)),
    ("API_SECRET_KEY=placeholdervalue", ("placeholdervalue",)),
    ("SECRET_KEY_BASE=placeholdervalue", ("placeholdervalue",)),
    ("DB_PASSWORD_PROD=placeholderpass", ("placeholderpass",)),
    ("PASSWORD_1=placeholderpass", ("placeholderpass",)),
    ("Password1: placeholderpass", ("placeholderpass",)),
    ("API_TOKEN_V2=fakeTokenValue", ("fakeTokenValue",)),
    ("GITHUB_TOKEN_CLASSIC=placeholdervalue", ("placeholdervalue",)),
    ("client_secret_value=fakevalue", ("fakevalue",)),
    ("API_KEY_PROD=placeholdervalue", ("placeholdervalue",)),
    ("APIKEY_PROD: placeholdervalue", ("placeholdervalue",)),
    ("ACCESS_KEY_ID_PROD=placeholdervalue", ("placeholdervalue",)),
    ("PRIVATE_KEY_PEM: placeholdervalue", ("placeholdervalue",)),
    ("CONNECTION_STRING_PROD=fakeconnectionvalue", ("fakeconnectionvalue",)),
    ("DB_PASSWD_STAGING=placeholderpass", ("placeholderpass",)),
    ("db_pwd_old: placeholderpass", ("placeholderpass",)),
    ("secretKey: fakesecretvalue", ("fakesecretvalue",)),
    ('{"secretKeyBase": "placeholdervalue"}', ("placeholdervalue",)),
    ("ACCESS_TOKEN_DEV=placeholdervalue", ("placeholdervalue",)),
    # A count word elsewhere in the name does not excuse a real token value.
    ("ACCESS_TOKEN_TTL=fakeaccessvalue", ("fakeaccessvalue",)),
    ("INPUT_TOKEN=placeholdervalue", ("placeholdervalue",)),
    ("SESSION_SECRET_MAX=placeholdervalue", ("placeholdervalue",)),
    ("Deploy with:\nSECRET_KEY=changemeplease\nJWT_SECRET_KEY: fakejwtsigningvalue\nDB_PASSWORD_PROD=placeholderpass",
     ("changemeplease", "fakejwtsigningvalue", "placeholderpass")),

    # ── Round 7 ──
    # A count word somewhere in the name does not excuse a numeric secret: only
    # a whole count or limit name (its last word is the count) keeps a number.
    ("INPUT_PASSWORD=48213907", ("48213907",)),
    ("CONTEXT_API_KEY=482139075512", ("482139075512",)),
    ("USAGE_API_TOKEN=4821390755", ("4821390755",)),
    ("PER_USER_SECRET=99887766", ("99887766",)),
    # Fail-closed controls for the count rule.
    ("USAGE_TOKEN=4821390755", ("4821390755",)),
    ("password: 48213907", ("48213907",)),
    ("PIN_PASSWORD=4821", ("4821",)),
    ("PASSWORD_MAX=48213907", ("48213907",)),
    ("SECRET_LIMIT=99887766", ("99887766",)),
    ("MAX_TOKEN=placeholdervalue", ("placeholdervalue",)),
    ("token_budget: placeholdervalue", ("placeholdervalue",)),
    ("PASSWORD_MIN_LENGTH: placeholderpass", ("placeholderpass",)),
    # Settings that only describe a secret (its type, address, name, file or
    # store) keep their values; these are what a user needs to rewire a setup.
    ("token_type: bearer", ()),
    ("token_endpoint: https://login.example.com/oauth2/v2.0/token", ()),
    ("TOKEN_URL=https://login.example.com/token", ()),
    ("key_vault_name: kv-prod-eastus2", ()),
    ("KEY_VAULT_URL=https://example-prod.vault.azure.net/", ()),
    ("credentials_path: ~/.config/app/creds.json", ()),
    ("password_policy: strong", ()),
    ("secret_name: app-signing", ()),
    ("SECRET_STORE=keychain", ()),
    ("api_key_env: MY_SERVICE_API_KEY", ()),
    ("apiKeyEnvVar: MY_SERVICE_API_KEY", ()),
    ("tokenFile: ~/.config/app/token.json", ()),
    ("credential_provider: azure-cli", ()),
    ("use_credential_manager: true", ()),
    ("primary_key_column: order_id2024", ()),
    # A key-shaped value is still hidden under a describing name.
    ("secret_name: Zq8rTmw2LpXvZq8rTmw2LpXvZq8rTmw2LpXv", ("Zq8rTmw2LpXvZq8rTmw2LpXvZq8rTmw2LpXv",)),
    ("token_endpoint: Bearer abcdefghijklmnop12", ("abcdefghijklmnop12",)),
    ("api_key_env: sk-abcdefghijklmnop1234", ("sk-abcdefghijklmnop1234",)),
    # Nothing is ever taken from another line.
    ("token_type: bearer\ntoken_endpoint: https://login.example.com/oauth2/v2.0/token", ()),
    ("token_type: Bearer\ntoken_endpoint: https://login.example.com/oauth2/v2.0/token", ()),
    ("password:\nnote: keep answers short", ()),
    ("api_key =\nnote: keep answers short", ()),
    # A YAML value written on the next, indented line is still hidden.
    ("password:\n  placeholderpass\nnote: keep answers short", ("placeholderpass",)),
    ("db:\n  password: |\n    placeholderpass\n  host: db.example.com", ("placeholderpass",)),
]

# Text that must survive next to a hidden value.
KEPT_NEXT_TO_SECRETS = [
    ('Use this config: {"clientId": "sample-app", "clientSecret": "fakesecretvalue", "password": "placeholderpass"}',
     ('"clientId": "sample-app"', "Use this config:")),
    ("Call with max_tokens: 4096 and api_key: abcd1234efgh5678", ("max_tokens: 4096",)),
    ("note: DB_PASSWORD=placeholderpass", ("note:",)),
    ("Use max_tokens: 4096 with SECRET_KEY=changemeplease and auth_method: oauth",
     ("max_tokens: 4096", "auth_method: oauth")),
    # Round 7: a hidden bearer value never takes the next line's setting with it.
    ("Authorization: Bearer abcdefghijklmnop12\ntoken_endpoint: https://login.example.com/oauth2/v2.0/token",
     ("\ntoken_endpoint: https://login.example.com/oauth2/v2.0/token", "Authorization: ")),
    ("Bearer abcdefghijklmnop12\nTOKEN_URL=https://login.example.com/token", ("\nTOKEN_URL=https://login.example.com/token",)),
    ("INPUT_PASSWORD=48213907\nmax_tokens: 4096\ntoken_type: bearer",
     ("\nmax_tokens: 4096\ntoken_type: bearer",)),
    ("password:\n  placeholderpass\nnote: keep answers short", ("password:", "\nnote: keep answers short")),
]

# (file name, is a key file). Round 3 report plus the earlier tests.
SECRET_NAME_CORPUS = [
    ("authoring-guide", False), ("design-tokens", False), ("session-notes", False),
    ("cookiecutter-template", False), ("blog-author", False), ("SKILL.md", False), ("MEMORY.md", False),
    ("-Users-me-code-auth-service", False), ("token-budget.md", False), ("auth-helper", False),
    ("authoring", False), ("pdf", False),
    (".env", True), (".env.local", True), ("auth.json", True), (".credentials.json", True),
    ("credentials.json", True), ("oauth_creds.json", True), ("server.pem", True), ("id_rsa", True),
    ("id_ed25519", True), ("cert.p12", True), ("tls.key", True), (".netrc", True), ("tokens.json", True),
]

# Tool-server args: (args, values that must vanish).
SERVER_ARGS_CORPUS = [
    (["--token=abc123456"], ("abc123456",)),
    (["-y", "tickets-mcp", "--api-key", "ghp_FAKEargTOKEN000011112222333344445555"],
     ("ghp_FAKEargTOKEN000011112222333344445555",)),
    (["--port", "9000"], ()),
]


def _label(index, text):
    head = text.split(":")[0].split("=")[0]
    return f"case {index} ({head[:40]!r})"


@pytest.mark.parametrize("index", range(len(REDACT_TEXT_CORPUS)))
def test_redact_text_corpus(index):
    text, secrets = REDACT_TEXT_CORPUS[index]
    out = MODULE.redact_text(text)
    if not secrets:
        assert out == text, _label(index, text) + " was changed"
        return
    assert R in out, _label(index, text) + " was not redacted"
    for value in secrets:
        assert value not in out, _label(index, text) + " still shows a value"


@pytest.mark.parametrize("index", range(len(KEPT_NEXT_TO_SECRETS)))
def test_ordinary_text_next_to_a_secret_is_kept(index):
    text, kept = KEPT_NEXT_TO_SECRETS[index]
    out = MODULE.redact_text(text)
    assert R in out, _label(index, text)
    for fragment in kept:
        assert fragment in out, _label(index, text) + " lost ordinary text"


@pytest.mark.parametrize("index", range(len(SECRET_NAME_CORPUS)))
def test_secret_file_name_corpus(index):
    name, expected = SECRET_NAME_CORPUS[index]
    assert MODULE._is_secret_name(name) is expected, name


@pytest.mark.parametrize("index", range(len(SERVER_ARGS_CORPUS)))
def test_server_args_corpus(index):
    args, secrets = SERVER_ARGS_CORPUS[index]
    blob = json.dumps(MODULE.redact_server("x", {"command": "tool", "args": args}))
    for value in secrets:
        assert value not in blob, f"args case {index}"
    if not secrets:
        for arg in args:
            assert arg in blob, f"args case {index}"


def test_corpus_has_not_shrunk():
    # The corpus only grows. Raise these floors when you add cases; never lower them.
    assert len(REDACT_TEXT_CORPUS) >= 145
    assert len(KEPT_NEXT_TO_SECRETS) >= 8
    assert len(SECRET_NAME_CORPUS) >= 25
    assert len(SERVER_ARGS_CORPUS) >= 3


def test_apply_keeps_ordinary_settings_and_drops_quoted_secrets(tmp_path, monkeypatch):
    home = tmp_path / "home"
    for name, body in (
        ("summarize", "Call the model with max_tokens: 4096 and thinking_tokens: 1024.\n"
                      "Auth method for the SharePoint site: OAuth: enabled\n"),
        ("crm-sync", 'Use this config: {"clientId": "sample-app", "clientSecret": "fakesecretvalue", '
                     '"password": "placeholderpass"}\n'),
    ):
        skill = home / ".claude" / "skills" / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(body, encoding="utf-8")
    (home / ".claude" / "CLAUDE.md").write_text("auth_method: oauth\n", encoding="utf-8")
    imports, agents = tmp_path / "imports", tmp_path / "agents"
    agents.mkdir()
    monkeypatch.setenv("AI_MIGRATION_IMPORTS_DIR", str(imports))
    monkeypatch.setenv("AGENTS_PATH", str(agents))
    MODULE.AIMigrationAgent().perform(action="apply", home_path=str(home), project_path=str(tmp_path / "none"),
                                      export_path=str(tmp_path / "none"), dry_run=False)
    staged = "\n".join(f.read_text(encoding="utf-8", errors="ignore") for f in imports.rglob("*") if f.is_file())
    for kept in ("max_tokens: 4096", "thinking_tokens: 1024", "OAuth: enabled", "auth_method: oauth", "sample-app"):
        assert kept in staged, kept
    for fake in ("fakesecretvalue", "placeholderpass"):
        assert fake not in staged, "a placeholder value was copied"
