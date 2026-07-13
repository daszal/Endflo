import os, json, urllib.request

base = 'https://weironglee.tail40ab19.ts.net'
headers = {'X-N8N-API-KEY': os.getenv('N8N_API_KEY', '')}

# Fetch current workflow
req = urllib.request.Request(f'{base}/api/v1/workflows/53c2PVNoX2NkJE0T', headers=headers)
wf = json.loads(urllib.request.urlopen(req).read())

# New code — uses plain string concatenation, no backticks
new_code = (
    "var decisions = $('Collect Superseded Data').first().json.decisions;\n"
    "var messages = $input.all();\n"
    "\n"
    "var text = '\\u{1f504} Decisions superseded (' + decisions.length + ')\\n\\n';\n"
    "\n"
    "for (var i = 0; i < decisions.length; i++) {\n"
    "  text += (i + 1) + '. ' + decisions[i].summary + '\\n';\n"
    "}\n"
    "\n"
    "if (messages.length > 0) {\n"
    "  text += '\\n\\u{1f4ce} Referenced messages:\\n';\n"
    "  for (var j = 0; j < messages.length; j++) {\n"
    "    var msg = messages[j].json;\n"
    "    var preview = (msg.reference_content || '').substring(0, 120);\n"
    "    var time = '';\n"
    "    if (msg.sent_at) {\n"
    "      time = new Date(msg.sent_at).toLocaleString('en-SG', { dateStyle: 'short', timeStyle: 'short' });\n"
    "    }\n"
    "    text += '\\u2022 ' + (msg.sender_name || 'Unknown') + ' (' + time + '): ' + preview + '\\n';\n"
    "  }\n"
    "}\n"
    "\n"
    "var projectTag = '';\n"
    "var firstDecision = decisions[0];\n"
    "if (firstDecision && firstDecision.tags) {\n"
    "  for (var k = 0; k < firstDecision.tags.length; k++) {\n"
    "    if (String(firstDecision.tags[k]).indexOf('project:') === 0) {\n"
    "      projectTag = firstDecision.tags[k].replace('project:', '');\n"
    "      break;\n"
    "    }\n"
    "  }\n"
    "}\n"
    "\n"
    "return [{\n"
    "  json: {\n"
    "    text: text,\n"
    "    chat_id: projectTag\n"
    "  }\n"
    "}];"
)

# Update the node
for n in wf['nodes']:
    if n['name'] == 'Format Telegram Message':
        n['parameters']['jsCode'] = new_code
        print(f"Updated code on node: {n['name']} ({n['id'][:8]})")
        break
else:
    print("ERROR: Format Telegram Message node not found")
    exit(1)

# Build PUT payload (strip read-only fields)
save_wf = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': {
        'executionOrder': wf['settings'].get('executionOrder', 'v1'),
        'callerPolicy': wf['settings'].get('callerPolicy', 'workflowsFromSameOwner'),
        'timezone': wf['settings'].get('timezone', 'Asia/Singapore'),
    },
}

data = json.dumps(save_wf).encode()
req = urllib.request.Request(
    f'{base}/api/v1/workflows/53c2PVNoX2NkJE0T',
    data=data,
    headers={**headers, 'Content-Type': 'application/json'},
    method='PUT'
)
try:
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    print(f"Saved: {result.get('name')} ({len(result.get('nodes', []))} nodes)")
    # Verify
    for n in result.get('nodes', []):
        if n['name'] == 'Format Telegram Message':
            print()
            print("=== Verified saved code ===")
            print(n['parameters']['jsCode'])
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"ERROR {e.code}: {body[:500]}")
