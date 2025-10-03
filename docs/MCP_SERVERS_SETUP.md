# 🔧 MCP Servers Installation Guide

## ✅ Successfully Installed

### **1. Context7 MCP Server**
- **Package**: `@upstash/context7-mcp`
- **Purpose**: Provides up-to-date, version-specific documentation and code examples
- **Executable**: `/opt/homebrew/bin/context7-mcp`

### **2. Puppeteer MCP Server**
- **Package**: `puppeteer-mcp-server`
- **Purpose**: Browser automation capabilities through Puppeteer
- **Executable**: `/opt/homebrew/bin/mcp-server-puppeteer`

---

## 🔌 Configuration for Claude Code

### **Method 1: Using Claude Code CLI**

```bash
# Add Context7 MCP Server
claude mcp add-json "context7" '{"command":"npx","args":["-y","@upstash/context7-mcp"]}'

# Add Puppeteer MCP Server
claude mcp add-json "puppeteer" '{"command":"npx","args":["-y","puppeteer-mcp-server"]}'
```

### **Method 2: Manual Configuration**

If you need to manually configure, add this to your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "puppeteer": {
      "command": "npx", 
      "args": ["-y", "puppeteer-mcp-server"]
    }
  }
}
```

---

## 🚀 Usage Examples

### **Context7 Usage**
- Include "**use context7**" in any prompt where you want updated documentation
- Example: "use context7 to show me the latest React hooks documentation"
- Context7 will fetch current official docs and inject them into your prompt

### **Puppeteer Usage**
- Provides browser automation capabilities
- Can take screenshots, interact with web pages, execute JavaScript
- Allows AI models to control a web browser programmatically

---

## 🔍 Verification Commands

```bash
# Check if executables are available
which context7-mcp
which mcp-server-puppeteer

# Test Context7 directly (may take time to start)
npx -y @upstash/context7-mcp

# Test Puppeteer directly 
npx -y puppeteer-mcp-server
```

---

## 📝 Configuration Files Location

Depending on your setup, MCP configuration may be stored in:
- `~/.claude/config.json`
- `~/.cursor/mcp.json`
- `~/Library/Application Support/Claude/claude_desktop_config.json`

---

## 🚨 Troubleshooting

### **If Context7 doesn't work:**
1. Try: `npx -y @upstash/context7-mcp`
2. Use bunx instead: `bunx @upstash/context7-mcp`
3. Check network permissions for fetching docs

### **If Puppeteer doesn't work:**
1. Ensure Chrome/Chromium is installed
2. Try: `npx -y puppeteer-mcp-server`
3. May need to install Chromium: `npx puppeteer browsers install chrome`

### **General MCP Issues:**
1. Restart Claude Code after configuration
2. Check Claude Code logs for MCP connection errors
3. Verify MCP server processes are running

---

## 🎯 Key Benefits

### **Context7:**
- ✅ Real-time documentation access
- ✅ Version-specific code examples  
- ✅ Eliminates manual doc searches
- ✅ Always up-to-date information

### **Puppeteer:**
- ✅ Browser automation for AI
- ✅ Web page interaction capabilities
- ✅ Screenshot and testing features
- ✅ JavaScript execution in browser context

---

## 📚 Additional Resources

- **Context7 GitHub**: https://github.com/upstash/context7
- **Puppeteer MCP**: https://github.com/merajmehrabi/puppeteer-mcp-server
- **MCP Documentation**: https://modelcontextprotocol.io/

Both servers are now installed and ready to use with Claude Code! 🎉