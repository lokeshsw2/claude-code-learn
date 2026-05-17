from anthropic import Anthropic
from pathlib import Path
import  subprocess

client = Anthropic()

WORK_DIR = Path.cwd()

def safe_path(p: str):
    path = (WORK_DIR / p).resolve()
    if not path.is_relative_to(WORK_DIR):
        raise ValueError(f'Path escapes workspace: {p}')
    return path

def run_bash(command: str) -> str:

    dangerous = ['rm -rf /', 'sudo', 'shutdown', 'reboot', '> /dev/']
    if any(d in command for d in dangerous):
        return "Error: dangerous command blocked"

    try:
        result = subprocess.run(command, shell=True, timeout=120, capture_output=True, cwd=WORK_DIR, text=True)
        out  = (result.stdout + result.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: timeout(120s)"


def read_file(path: str, limit: int = None):
    try:
        text = safe_path(path).read_text()
        lines = text.splitlines()

        if limit and len(lines) > limit:
            lines = lines[:limit] + [f'... ({len(lines) - limit} more lines)']

        return '\n'.join(lines)[:50000]

    except Exception as e:
        return f'Error: {e}'

def run_write(path: str, content: str) -> str:
    try:
        file_path = safe_path(path)
        # create parent directories if not exist / if already exist dont throw error
        file_path.parent.mkdir(parents=True, exist_ok=True)
        # write conten to file
        file_path.write_text(content)
        return f'Wrote {len(content)} bytes to {path}'
    except Exception as e:
        return f'Error : {e}'


def run_edit(path: str, old_text: str, new_text: str) -> str:
    # Find-and-replace first occurrence safely.
    try:
        fp = safe_path(path)
        content = fp.read_text()
        if old_text not in content:
            return f'Error: text not found in {path}'
        fp.write_text(content.replace(old_text, new_text, 1))
        return f'Edited path: {path}'
    except Exception as e:
        return f'Error : {e}'

TOOL_HANDLERS = {
    'bash': lambda **kw: run_bash(kw['command']),
    'read_file': lambda **kw: read_file(kw['path'], kw.get('limit')),
    'write_file': lambda **kw: run_write(kw['path'], kw['content']),
    'edit_file': lambda **kw: run_edit(kw['path'], kw['old_text'], kw['new_text'])
}

TOOLS = [
    {"name": "bash", "description": "Run a shell command.",
     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
    {"name": "read_file", "description": "Read file contents.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["path"]}},
    {"name": "write_file", "description": "Write content to file.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
    {"name": "edit_file", "description": "Replace exact text in file.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "old_text": {"type": "string"}, "new_text": {"type": "string"}}, "required": ["path", "old_text", "new_text"]}},
]

if __name__ == '__main__':
    history = []

    while True:
        user_input = input('user > ').strip()
        if user_input.lower() in ('q', 'quit', 'exit'):
            break

        history.append({'role': 'user', 'content': user_input})

        while True:

            response = client.messages.create(
                model='claude-haiku-4-5',
                max_tokens=8000,
                tools=TOOLS,
                messages=history
            )

            history.append({'role': 'assistant', 'content': response.content})

            if response.stop_reason == 'end_turn':
                for block in response.content:
                    if block.type == 'text':
                        print(f'assistant: {block.text}')
                break

            if response.stop_reason == 'tool_use':
                tool_results = []

                # create tool results here
                for block in response.content:

                    if block.type == 'text':
                        print(f'assistant > {block.text}')

                    if block.type == 'tool_use':
                        print(f'tool call {block.name} : {block.input}')
                        tool_handler = TOOL_HANDLERS[block.name]
                        r = tool_handler(**block.input)
                        tool_results.append({
                            'type': 'tool_result',
                            'tool_use_id': block.id,
                            'content': r
                        })

                history.append({'role': 'user', 'content': tool_results})