#!/bin/bash

# Install a skill and link it to OpenClaw's skills directory
# Usage: ./install-skill.sh <owner/repo@skill-name>
# Example: ./install-skill.sh vercel-labs/agent-skills@vercel-react-best-practices

set -e

if [[ -z "$1" ]]; then
  echo "Usage: $0 <owner/repo@skill-name>"
  echo "Example: $0 vercel-labs/agent-skills@vercel-react-best-practices"
  exit 1
fi

FULL_SKILL_NAME="$1"

# Extract skill name (the part after @)
SKILL_NAME="${FULL_SKILL_NAME##*@}"

if [[ -z "$SKILL_NAME" || "$SKILL_NAME" == "$FULL_SKILL_NAME" ]]; then
  echo "Error: Invalid skill format. Expected: owner/repo@skill-name"
  exit 1
fi

# OpenClaw skills directory
OPENCLAW_SKILLS_DIR="$HOME/.agents/skills"
SKILL_TARGET="$OPENCLAW_SKILLS_DIR/$SKILL_NAME"

# Step 1: Install the skill using npx
echo "Installing skill: $SKILL_NAME..."
npx skills add "$FULL_SKILL_NAME" -g -y > /dev/null 2>&1

# Step 2: Verify installation
if [[ ! -d "$SKILL_TARGET" ]]; then
  echo "Error: Skill '$SKILL_NAME' installation failed"
  exit 1
fi

echo "Skill '$SKILL_NAME' installed successfully to $SKILL_TARGET"
echo ""
echo "Note: The skill is now available in your OpenClaw agent's skill list."
echo "To use it, ask your agent to load the '$SKILL_NAME' skill."
