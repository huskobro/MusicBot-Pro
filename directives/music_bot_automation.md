# Music Generation Automation Directive

## Goal
Automate the creation of music via Suno.ai and generation of image prompts via Gemini using a headless (or headed) browser with persistent user context.

## Inputs
- `data/metadata.csv`: A CSV file containing prompts and styles.
    - Format: `id,prompt,style,title`

## Tools
- `execution/browser_controller.py`: Core browser interaction class.
- `execution/suno_generator.py`: Script to drive Suno.ai.
- `execution/gemini_prompter.py`: Script to drive Gemini.

## Procedure
1.  **Preparation**
    - Ensure Google Chrome is closed.
    - Ensure `data/metadata.csv` is populated.

2.  **Suno Generation**
    - Run `execution/suno_generator.py`.
    - The script will:
        - Open Suno.ai.
        - For each row in CSV:
            - Enter prompt and style.
            - Trigger generation.
            - Wait for completion.
            - Download audio.

3.  **Gemini Prompting**
    - Run `execution/gemini_prompter.py`.
    - The script will:
        - Open Gemini.
        - Send a request to generate an image prompt based on the song concept.
        - Extract the result.

## Error Handling
- **Network/Element Persistence**: The `BrowserController` includes a retry mechanism (3 attempts) for all interactions.
- **Login Expired**: If the script detects it is not logged in, it should pause or alert the user (currently requires manual login once).
