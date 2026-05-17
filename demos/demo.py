import subprocess

from anthropic import Anthropic
client = Anthropic()

# define tools
tools = [
    {
        'name': 'bash',
        'description': 'execute bash command',
        'input_schema': {
           'type': 'object',
            'properties': {
                'command': {
                    'type': 'string',
                    'description': 'bash command to execute'
                }
            },
            'required': ['command']
       }
    },
    {
        'name': 'get_weather',
        'description': 'get weather of city',
        'input_schema': {
            'type': 'object',
            'properties': {
                'city': {
                    'type': 'string',
                    'description': 'City provided by user for fetching weather'
                }
            },
            'required': ['city']
        }

    }
]

def run_tool(name, tool_input):
    if name == 'bash':
        command = tool_input['command']

        result = subprocess.run(
            command,
            capture_output=True,
            shell=True,
            text=True
        )

        return result.stdout + result.stderr


    if name == 'get_weather':
        city = tool_input['city']
        return f'weather in {city} is 50 degrees'

    return f'tool named {name} not found'

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
                max_tokens=1024,
                messages=history,
                tools=tools
            )

            history.append({'role': 'assistant', 'content': response.content})

            if response.stop_reason == 'end_turn':
                for block in response.content:
                    if block.type == 'text':
                        print(f'assistant > {block.text}')
                break

            if response.stop_reason == 'tool_use':

                tool_results = []

                for block in response.content:
                    if block.type == 'tool_use':

                        print(f'Tool call {block.name} : {block.input}')

                        result = run_tool(block.name, block.input)


                        tool_results.append({
                            'type': 'tool_result',
                            'tool_use_id': block.id,
                            'content': result
                        })

                history.append({'role': 'user', 'content': tool_results})