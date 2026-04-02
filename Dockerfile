# Clawd-Lobster — Docker Setup
# Runs Claude Code with pre-configured skills wrapper
#
# Build:  docker build -t clawd-lobster .
# Run:    docker run -it --name clawd -v clawd-data:/root/.clawd-lobster clawd-lobster
# Resume: docker start -ai clawd

FROM node:22-slim

# System dependencies (+ cron for scheduler)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv git curl ca-certificates cron \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code
RUN npm install -g @anthropic-ai/claude-code

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update && apt-get install -y gh && rm -rf /var/lib/apt/lists/*

# Copy wrapper
WORKDIR /opt/clawd-lobster
COPY . .

# Install MCP Memory Server
RUN python3 -m pip install --break-system-packages -e skills/memory-server/

# Create non-root user
RUN useradd -m -s /bin/bash clawd

# Create workspace directory
USER clawd
RUN mkdir -p /home/clawd/Documents/Workspace /home/clawd/.clawd-lobster /home/clawd/.claude

# Generate default config (with machine_id)
RUN echo '{"machine_id":"docker","wrapper_dir":"/opt/clawd-lobster","data_dir":"/opt/clawd-lobster","workspace_root":"/home/clawd/Documents/Workspace","knowledge_dir":"/opt/clawd-lobster/knowledge","l4_provider":"github","oracle":{"enabled":false},"embedding":{"provider":"none"}}' \
    > /home/clawd/.clawd-lobster/config.json

# Configure MCP
RUN echo '{"mcpServers":{"memory":{"command":"python3","args":["-X","utf8","-m","mcp_memory.server"],"cwd":"/opt/clawd-lobster/skills/memory-server"}}}' \
    > /home/clawd/.claude/.mcp.json

# Generate CLAUDE.md
RUN sed 's|{{DATA_DIR}}|/opt/clawd-lobster|g' templates/global-CLAUDE.md > /home/clawd/.claude/CLAUDE.md

# Copy settings template
RUN cp templates/settings.json.template /home/clawd/.claude/settings.json

# Set up cron for sync + heartbeat (every 30 min)
USER root
RUN mkdir -p /opt/clawd-lobster/.claude-memory && chown clawd:clawd /opt/clawd-lobster/.claude-memory
RUN echo "*/30 * * * * clawd bash /opt/clawd-lobster/scripts/sync-all.sh >> /opt/clawd-lobster/.claude-memory/sync.log 2>&1" > /etc/cron.d/clawd-lobster \
    && echo "*/30 * * * * clawd bash /opt/clawd-lobster/scripts/heartbeat.sh >> /opt/clawd-lobster/.claude-memory/heartbeat.log 2>&1" >> /etc/cron.d/clawd-lobster \
    && chmod 0644 /etc/cron.d/clawd-lobster
RUN chmod +x /opt/clawd-lobster/scripts/*.sh
USER clawd

# Volumes for persistence
VOLUME ["/home/clawd/.clawd-lobster", "/home/clawd/.claude", "/home/clawd/Documents/Workspace"]

# Entry: start cron + shell
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["sudo cron 2>/dev/null; echo 'Clawd-Lobster ready. Cron started. Run: claude auth login' && exec bash"]
