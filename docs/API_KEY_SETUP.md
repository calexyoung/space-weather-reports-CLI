# Setting Up Your Anthropic API Key

## Quick Start

### 1. Get Your API Key

1. Go to https://console.anthropic.com/
2. Sign in or create an account
3. Navigate to **API Keys** section
4. Click **Create Key**
5. Copy your new API key (starts with `sk-ant-`)

### 2. Add to .env File

Open the `.env` file in your space-weather-reports directory:

```bash
cd ~/Documents/Obsidian/CAY-power-vault/space-weather-reports
nano .env
```

Replace the empty value with your API key:

```bash
# Before:
ANTHROPIC_API_KEY=

# After:
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

Save and exit (Ctrl+X, then Y, then Enter in nano)

### 3. Install Dependencies

```bash
pip3 install -r requirements.txt
```

This installs:
- `anthropic` - Claude API client
- `python-dotenv` - Loads .env file automatically

### 4. Test It

```bash
python3 space_weather_automation.py
```

If configured correctly, you'll see:
```
✅ Claude API integration enabled
✅ Generating professional report...
```

## File Structure

```
space-weather-reports/
├── .env                    # YOUR file with actual API key (NEVER share!)
├── .env.example            # Template file (safe to share)
└── .gitignore              # Ensures .env is never committed to git
```

## Security Best Practices

### ✅ DO:
- Keep `.env` file private
- Never commit `.env` to version control
- Use different keys for different projects
- Rotate keys periodically
- Use `.env.example` as a template for others

### ❌ DON'T:
- Share your `.env` file
- Post API keys in chat/email
- Commit API keys to GitHub
- Use the same key everywhere
- Store keys in code files

## Environment Variable Methods

The automation supports multiple ways to provide your API key:

### Method 1: .env File (Recommended)
```bash
# In .env file
ANTHROPIC_API_KEY=sk-ant-api03-your-key
```

**Pros:**
- ✅ Secure and organized
- ✅ Easy to manage
- ✅ Separate from code
- ✅ Works automatically

### Method 2: System Environment Variable
```bash
# In ~/.zshrc or ~/.bash_profile
export ANTHROPIC_API_KEY='sk-ant-api03-your-key'
```

**Pros:**
- ✅ Available to all scripts
- ✅ Persists across sessions

**Cons:**
- ⚠️ Needs shell restart or `source ~/.zshrc`

### Method 3: Per-Session Export
```bash
# In terminal before running
export ANTHROPIC_API_KEY='sk-ant-api03-your-key'
python3 space_weather_automation.py
```

**Pros:**
- ✅ Quick testing
- ✅ Temporary

**Cons:**
- ⚠️ Lost when terminal closes

## Verification

### Check if API Key is Loaded

```bash
cd ~/Documents/Obsidian/CAY-power-vault/space-weather-reports
python3 -c "import os; from dotenv import load_dotenv; load_dotenv('.env'); print('✅ API key loaded' if os.getenv('ANTHROPIC_API_KEY') else '❌ API key not found')"
```

### Test Claude API Connection

```python
python3 << 'EOF'
from claude_integration import ClaudeReportGenerator

generator = ClaudeReportGenerator()
if generator.enabled:
    print("✅ Claude API is ready!")
    print(f"   Using model: claude-sonnet-4-20250514")
else:
    print("❌ Claude API not configured")
    print("   1. Check .env file has ANTHROPIC_API_KEY=...")
    print("   2. Run: pip3 install anthropic")
EOF
```

## Troubleshooting

### "API key not found"

**Solution 1:** Check .env file exists and has correct format
```bash
cat .env
# Should show: ANTHROPIC_API_KEY=sk-ant-...
```

**Solution 2:** Ensure no extra spaces
```bash
# Wrong:
ANTHROPIC_API_KEY = sk-ant-...

# Right:
ANTHROPIC_API_KEY=sk-ant-...
```

### "Module 'dotenv' not found"

**Solution:** Install python-dotenv
```bash
pip3 install python-dotenv
```

### "Module 'anthropic' not found"

**Solution:** Install Anthropic SDK
```bash
pip3 install anthropic
```

### "Invalid API key"

**Solution 1:** Verify key starts with `sk-ant-`

**Solution 2:** Generate a new key at https://console.anthropic.com/

**Solution 3:** Check for copy/paste errors (no spaces, complete key)

### "API key works in terminal but not in script"

**Solution:** The script looks for `.env` file in the script directory
```bash
# Verify location
ls -la ~/Documents/Obsidian/CAY-power-vault/space-weather-reports/.env
```

## API Key Management

### Rotate Keys

It's good practice to rotate API keys periodically:

1. Generate new key at https://console.anthropic.com/
2. Update `.env` file with new key
3. Test the automation
4. Delete old key from Anthropic console

### Multiple Keys

For different environments (testing vs production):

```bash
# .env.development
ANTHROPIC_API_KEY=sk-ant-test-key

# .env.production  
ANTHROPIC_API_KEY=sk-ant-prod-key
```

Load the appropriate file:
```python
from dotenv import load_dotenv
load_dotenv('.env.production')
```

## Cost Management

### Monitor Usage

- Dashboard: https://console.anthropic.com/
- Check usage regularly
- Set up billing alerts

### Estimate Costs

Each space weather report:
- Input: ~2,000 tokens (data sources)
- Output: ~4,000 tokens (formatted report)
- **Total: ~6,000 tokens per report**

At 4 reports per day (every 6 hours):
- Daily: ~24,000 tokens
- Monthly: ~720,000 tokens

Current Claude Sonnet pricing:
- Input: $3 per million tokens
- Output: $15 per million tokens

**Monthly cost estimate: ~$6-8/month for automated reports**

### Reduce Costs

1. **Run less frequently:** Change to 12-hour intervals
```yaml
schedule:
  interval_hours: 12  # Instead of 6
```

2. **Use manual generation:** Only generate when needed
```bash
python3 space_weather_automation.py  # On-demand only
```

3. **Disable Claude API:** Use basic templates
```yaml
# Comment out or leave blank in .env
# ANTHROPIC_API_KEY=
```

## Advanced Configuration

### Additional Environment Variables

Add to `.env` for extended functionality:

```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-your-key

# Logging
LOG_LEVEL=INFO
LOG_FILE=space_weather_automation.log

# Browser MCP
MCP_BROWSER=chrome
MCP_TIMEOUT=60

# Email Notifications (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_EMAIL=alerts@example.com
```

### Using Different Models

Edit `claude_integration.py` to change models:

```python
message = self.client.messages.create(
    model="claude-sonnet-4-20250514",  # Current
    # model="claude-opus-4-20250514",  # More powerful, more expensive
    # model="claude-3-5-sonnet-20241022",  # Older version
    max_tokens=16000,
    messages=[...]
)
```

## Summary

✅ **Created files:**
- `.env` - Your private API key file
- `.env.example` - Template for sharing
- `.gitignore` - Protects your keys

✅ **Next steps:**
1. Get API key from https://console.anthropic.com/
2. Add to `.env` file
3. Run `pip3 install -r requirements.txt`
4. Test with `python3 space_weather_automation.py`

✅ **Your API key enables:**
- Fully automated report generation
- Professional formatting
- No manual intervention needed
- 24/7 operation

---

**Need help?** Check the logs:
```bash
tail -f space_weather_automation.log
```
