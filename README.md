# AURA Milestones

## Milestone 2 -- Database Integration (MongoDB Atlas)

This project connects the **AURA Journaling App** to a **MongoDB Atlas**
cloud database.

------------------------------------------------------------------------

### Setup Instructions

1.  **Install dependencies**

    ``` bash
    python -m pip install -r requirements.txt
    ```

2.  **Create a `.env` file** in the same folder with the following
    variables:

    ``` env
    MONGODB_URI=<your connection string>
    DB_NAME=aura
    COLLECTION=entries
    ```

3.  **Run the program**

    ``` bash
    python demo_db.py
    ```

------------------------------------------------------------------------

### Expected Output

The script will:

-   Insert a sample journal entry: `"Milestone 2 hello world"` into
    MongoDB\
-   Print:
    -   **Inserted document ID**
    -   **Fetched document**
    -   **Total documents** in the `entries` collection

------------------------------------------------------------------------

## Milestone 3 -- API Connection (Hugging Face)

This script connects to the **Hugging Face Inference API** to analyze
the sentiment of short text using the model:

`cardiffnlp/twitter-roberta-base-sentiment`

It outputs **positive**, **neutral**, and **negative** scores.

------------------------------------------------------------------------

### How to Run

1.  **Install required libraries**

    ``` bash
    pip install -r requirements.txt
    ```

2.  **Create a `.env` file** in the same folder and add:

    ``` env
    HF_TOKEN=hf_your_token_here
    ```

3.  **Run the script**

    ``` bash
    python demo_api.py
    ```
