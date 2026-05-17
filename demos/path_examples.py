
from pathlib import Path

def safe_path(p: str):
    WORK_DIR = Path.cwd().resolve()
    print(WORK_DIR)

if __name__ == '__main__':
    print('Hello')
    safe_path('a')

    print(Path('/Users/sunny/code/').is_relative_to('/Users/sunny/code/claude-code-learn/demos'))
    print(Path('/Users/sunny/code/claude-code-learn/demos').is_relative_to('/Users/sunny/code/'))

    content_file = Path.cwd() / 'content.txt'
    print(content_file)

    content_file_text = content_file.read_text()

    print(content_file_text)

    r = content_file_text.splitlines()

    j = '\n'.join(r)

    print('end')

