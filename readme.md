# arXiv Paper Recommender

A hackable tool to swim through daily arXiv papers, powered by LLMs.

## Usage

Customize the following content, then run `python main.py`.

1. Put your OpenAI API key (started with `sk-`) in `.openai_api_key`.
2. Customize `CATEGORY_LIST` in `main.py` to be the list of categories you want to keep tracks of (e.g. `['cs.LG']`)
2. arXiv-Recommender will filter out papers with authors in `MY_AUTHOR_LIST` of `filter_util.py`. Please customize so you won't miss any paper by them.
3. arXiv-Recommender will use ChatGPT to filter out papers that are relevant to your research topics defined in `research_topic.py`. Please customize so you won't miss relevant papers.

## Advanced

- In `llm.py`, you can customize prompts, the LLM model to use (default is GPT-3.5)
- You can setup your email account in `mail_config.py` and arXiv-Recommender can send a summary email to your mailbox.

### Acknowledgements

Thank you to arXiv for use of its open access interoperability.

### Contribute

Feel free to contribute to the project via Pull Requests, Issues, or contact me via `kaixuanh@princeton.edu`
