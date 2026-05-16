from anthropic import Anthropic

if __name__ == '__main__':
    client = Anthropic()

    history = []

    while True:
        user_input = input('User > ').strip()

        if user_input in ('q', 'quit', 'exit'):
            break

        history.append({'role': 'user', 'content': user_input})

        response = client.messages.create(
            model='claude-haiku-4-5',
            max_tokens=1024,
            messages=history
        )

        for block in response.content:
            if block.type == 'text':
                history.append({'role': 'assistant', 'content': block.text})
                print(f'assistant: {block.text}')




