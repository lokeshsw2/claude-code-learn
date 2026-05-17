from pydoc import describe

from anthropic import Anthropic

client = Anthropic()

tools = [

    {
        'name': 'get_weather',
        'description': 'get weather for city',
        'input_schema': {
            'type': 'object',
            'properties': {
                'city': {
                    'type': 'string',
                    'description': 'the city provided by user'
                }
            },
            'required': ['city']
        }
    }
]

def run_tool(name, tool_input):
    if name == 'get_weather':
        city  = tool_input['city']
        return f'Weather in {city} is 50 degrees'

    return f'Tool named {name} not available'

if __name__ == '__main__':
    print('Hello')

    # create a core agent loop
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
                        tool_results.append(
                            {
                                'tool_use_id': block.id,
                                'type': 'tool_result',
                                'content': result
                            }
                        )

                history.append({'role': 'user', 'content': tool_results})


