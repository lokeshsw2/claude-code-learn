from anthropic import Anthropic
import subprocess

# tool definition
tools = [
    {
        'name': 'bash',
        'description': 'Execute a bash command and return its output',
        'input_schema': {
            'type': 'object',
            'properties': {
                'command': {
                    'type': 'string',
                    'description': 'The bash command to execute'
                }
            },
            'required': ['command']
        }
    }
]

def run_tool(name, tool_input):
    if name == 'bash':

        """
        result — The returned object contains:

        result.stdout — The command's output/response
        result.stderr — Any error messages
        result.returncode — Exit code (0 = success, non-zero = failure)
        """
        result = subprocess.run(
            tool_input['command'],
            shell=True, # execute command in shell
            capture_output=True, # capture output instead of printing to terminal,
            text=True # return raw text not bytes
        )

        return result.stdout + result.stderr
    return f'Unknown tool: {name}'


if __name__ == '__main__':
    client = Anthropic()

    history = []

    while True:
        user_input = input('User > ').strip()

        if user_input in ('q', 'quit', 'exit'):
            break

        history.append({'role': 'user', 'content': user_input})

        """
           - Append response.content (the full block list), not just text — the tool_use blocks must stay in history.                                                                                         
           - Each tool_result needs the matching tool_use_id from the tool_use block.                                                                                                                       
           - Tool results go in a user message as a list of tool_result blocks.                                                                                                                               
           - Loop until stop_reason == 'end_turn' — Claude may chain several tool calls.  
       """

        while True:
            response = client.messages.create(
                model='claude-haiku-4-5',
                max_tokens=1024,
                messages=history,
                tools=tools
            )

            history.append({'role': 'assistant', 'content': response.content})

            if response.stop_reason == 'end_turn':
                # print response and break
                for block in response.content:
                    if block.type == 'text':
                        print(f'assistant: {block.text}')
                break

            if response.stop_reason == 'tool_use':
                tool_results = []
                for block in response.content:
                    if block.type == 'text' and block.text:
                        print(f'assistant: {block.text}' )
                    if block.type == 'tool_use':
                        print(f'[tool: {block.name} {block.input}]')
                        output = run_tool(block.name, block.input)
                        tool_results.append({
                            'type': 'tool_result',
                            'tool_use_id': block.id,
                            'content': output
                        })
                history.append({'role': 'user', 'content': tool_results})




