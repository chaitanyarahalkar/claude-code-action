# Claude Code Action

General-purpose Claude agent for GitHub PRs and issues. Can answer questions and implement code changes.

## Overview

This GitHub Action integrates Claude AI into your GitHub workflow, allowing Claude to:
- Answer questions about code and issues
- Implement code changes and bug fixes
- Review pull requests
- Create new features based on requirements

## Setup

### 1. Authentication

#### Option A: Anthropic API (Direct)
Set the `ANTHROPIC_API_KEY` secret in your repository:
```yaml
- uses: your-username/claude-code-action@main
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

#### Option B: Amazon Bedrock
Configure AWS credentials and enable Bedrock:
```yaml
- uses: your-username/claude-code-action@main
  with:
    use_bedrock: true
    model: "anthropic.claude-3-5-sonnet-20241022-v2:0"
  env:
    AWS_REGION: us-east-1
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

#### Option C: Google Vertex AI
Configure GCP credentials and enable Vertex:
```yaml
- uses: your-username/claude-code-action@main
  with:
    use_vertex: true
    model: "claude-3-5-sonnet-v2@20241022"
  env:
    ANTHROPIC_VERTEX_PROJECT_ID: your-project-id
    CLOUD_ML_REGION: us-central1
    GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GOOGLE_APPLICATION_CREDENTIALS }}
```

### 2. GitHub Token
The action automatically uses GitHub App authentication. For custom token:
```yaml
with:
  github_token: ${{ secrets.CUSTOM_GITHUB_TOKEN }}
```

## Usage

### Basic Workflow

```yaml
name: Claude Code Assistant
on:
  issue_comment:
    types: [created]
  issues:
    types: [opened, assigned]
  pull_request_review_comment:
    types: [created]

jobs:
  claude:
    if: contains(github.event.comment.body, '@claude') || github.event.assignee.login == 'claude'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: your-username/claude-code-action@main
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Triggering Claude

#### Comment Trigger
Add `@claude` in any comment on issues or PRs:
```
@claude can you fix the bug in the login function?
```

#### Assignee Trigger
Assign `@claude` to an issue to trigger the action.

#### Direct Prompt
Skip trigger detection and provide direct instructions:
```yaml
with:
  direct_prompt: "Review this PR and suggest improvements"
```

## Configuration Options

### Core Settings
- `trigger_phrase`: Custom trigger phrase (default: `@claude`)
- `assignee_trigger`: Username that triggers action when assigned
- `base_branch`: Base branch for new branches (defaults to repo default)
- `model`: AI model to use (provider-specific format)
- `max_turns`: Maximum conversation turns
- `timeout_minutes`: Execution timeout (default: 30)

### Customization
- `custom_instructions`: Additional instructions for Claude
- `allowed_tools`: Extra tools Claude can use
- `disallowed_tools`: Tools Claude cannot use
- `claude_env`: Custom environment variables (YAML format)
- `mcp_config`: Additional MCP server configuration

### Example with Custom Configuration
```yaml
- uses: your-username/claude-code-action@main
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    trigger_phrase: "@ai-assistant"
    custom_instructions: |
      Always follow our coding standards:
      - Use TypeScript for new files
      - Include unit tests
      - Follow conventional commits
    allowed_tools: "pytest,eslint"
    max_turns: 10
    timeout_minutes: 45
```

## Examples

### Bug Fix Request
```
@claude there's a memory leak in the file processor. Can you investigate and fix it?
```

### Feature Implementation
```
@claude implement a user authentication system with JWT tokens. Include:
- Login/logout endpoints
- Password hashing
- Token validation middleware
```

### Code Review
```
@claude please review this PR and check for:
- Security vulnerabilities
- Performance issues
- Code style consistency
```

## Advanced Configuration

### MCP Servers
Add custom MCP servers for extended functionality:
```yaml
with:
  mcp_config: |
    {
      "servers": {
        "custom-tools": {
          "command": "node",
          "args": ["./mcp-server.js"]
        }
      }
    }
```

### Environment Variables
Pass custom environment to Claude Code:
```yaml
with:
  claude_env: |
    NODE_ENV: production
    API_BASE_URL: https://api.example.com
    DEBUG: true
```

## Outputs

- `execution_file`: Path to Claude Code execution output file

Access the execution report in subsequent steps:
```yaml
- name: Process Results
  run: |
    echo "Execution details:"
    cat ${{ steps.claude.outputs.execution_file }}
```

## Permissions

Ensure your workflow has appropriate permissions:
```yaml
permissions:
  contents: write
  pull-requests: write
  issues: write
```

## Troubleshooting

### Common Issues

1. **Action not triggering**: Check trigger phrase and permissions
2. **Authentication errors**: Verify API keys and tokens
3. **Timeout issues**: Increase `timeout_minutes` for complex tasks
4. **Tool restrictions**: Check `allowed_tools` and `disallowed_tools`

### Debug Mode
Enable verbose logging by setting debug environment variables in your workflow.

## Security

- Never commit API keys to your repository
- Use GitHub secrets for sensitive configuration
- Review Claude's changes before merging
- Set appropriate tool restrictions for your use case

## License

MIT License - see LICENSE file for details.