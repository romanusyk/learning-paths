# learning-paths
Source data, code, and visualisations for the Learning Paths article about pains and triumphs of Ukrainian IT specialists in learning English.

## The Article Series

*   [Part I: The Uphill Struggle](https://medium.com/@romanysik/learning-paths-part-i-the-uphill-struggle-1c59cb769d19)
*   [Part II: Finding Your Stride](https://medium.com/@romanysik/learning-paths-part-ii-finding-your-stride-d7bb86363f8e)

## Running the Code

To run the project locally, follow these steps:

1.  **Activate the virtual environment**:
    This ensures you are using the correct Python dependencies installed for this project.
    ```bash
    . .venv/bin/activate
    ```

2.  **Preview the website**:
    Start a local server to view the website. It will automatically reload when you make changes.
    ```bash
    quarto preview
    ```

3.  **Build for production**:
    Render the static website to the `docs/` directory, ready for deployment (e.g., to GitHub Pages).
    ```bash
    quarto render
    ```
