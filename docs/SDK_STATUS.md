# SDK Integration Status

## Current Recommendation: Use report_refine_simple.py

**TL;DR:** The simple CLI version works reliably. The SDK version has persistent empty response issues.

## Working Solution: report_refine_simple.py

**Status:** ✅ Fully functional

**Usage:**
```bash
./report_refine_simple.py              # Auto-find latest report
./report_refine_simple.py --file path  # Specific report
./report_refine_simple.py --review-only # Just suggestions
```

**Features:**
- Direct Claude CLI calls via subprocess
- Interactive conversation mode
- Knowledge base integration
- Conversation logging
- Aurora visibility table integration
- Flare notation clarification
- Reliable, fast responses

**How it works:**
- Calls `claude --print` directly
- Includes report content in prompt
- Runs from `/tmp` to avoid workspace trust issues
- Uses `--dangerously-skip-permissions` for non-interactive mode

## SDK Version Issues: report_refine_sdk.py

**Status:** ❌ Not working - Empty responses

**Issues Encountered:**

1. **Pre-flight Check Hangs** (SOLVED)
   - Problem: SDK hung during initialization
   - Solution: `setting_sources=['user']` + `cwd="/tmp"`
   - Status: Fixed - no longer hangs

2. **Empty Response Problem** (UNSOLVED)
   - Problem: SDK completes but returns no text
   - Attempted fixes:
     - ✅ Added `setting_sources=['user']`
     - ✅ Changed `cwd` to `/tmp`
     - ✅ Included report content in prompt (not file path)
     - ❌ Still getting empty responses
   - Status: **Blocking issue**

3. **Possible Causes:**
   - SDK may be silently failing during response streaming
   - Message format might not match expected structure
   - CLI subprocess may be completing without generating output
   - Permission/settings interaction despite workarounds

## Technical Details

### What Works (Simple Version)
```python
subprocess.run([
    "/opt/homebrew/bin/claude",
    "--print",
    "--dangerously-skip-permissions",
    prompt  # Contains full report content
], cwd="/tmp")
```

### What Doesn't Work (SDK Version)
```python
async with ClaudeSDKClient(options=ClaudeAgentOptions(
    cwd="/tmp",
    setting_sources=['user'],
    cli_path="/opt/homebrew/bin/claude",
    ...
)) as client:
    await client.query(prompt)  # Contains full report content
    async for message in client.receive_response():
        # message.text is always empty
```

## Recommendation

**For daily use:** Stick with `report_refine_simple.py`

**Advantages of simple version:**
- Reliable and tested
- Fast responses
- All features you need
- Easy to debug
- No SDK complexity

**SDK benefits (if it worked):**
- Stateful conversations with better context
- Tool use (Read, Write, Bash, etc.)
- Resume capabilities
- Bidirectional communication

**Reality:** The simple version's subprocess approach is more reliable than the SDK wrapper for this use case.

## Future Investigation

If you want to troubleshoot the SDK further:

1. **Check SDK debug logs:**
   ```bash
   ANTHROPIC_LOG=debug ./report_refine_sdk.py
   ```

2. **Test with minimal example:**
   ```bash
   python3.11 test_sdk_workaround.py
   ```

3. **Compare SDK vs CLI output:**
   - SDK returns empty
   - CLI returns full response
   - Something in SDK message parsing may be broken

4. **Potential SDK bug:**
   - May be issue with current SDK version (0.1.6)
   - Could file issue with Anthropic if reproducible

## Conclusion

Use `report_refine_simple.py` for your daily workflow. It has all the features you need and works reliably.

The SDK integration remains in the codebase for future investigation, but is not recommended for production use until the empty response issue is resolved.
