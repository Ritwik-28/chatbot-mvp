<h1 align="center">Chatbot MVP with Rasa and React</h1>

<p align="justified">This project sets up a chatbot MVP using Rasa for the backend and React for the frontend. The chatbot can handle user interactions, collect lead information, and provide responses based on predefined intents and entities. The chatbot also includes Neo4j to store and retrieve structured and interconnected data like user profiles, historical interactions, and course information and text-embedding-ada-002 to enhances Neo4j’s ability to find semantically similar nodes, improving information retrieval and recommendation accuracy along with GPT-3.5-Turbo to handle complex or unexpected user queries, hence generating fallback responses, and enriching the conversations beyond predefined intents</p>

## Prerequisites

- Docker and Docker Compose
- Node.js and npm
- OpenAI API Credits

## Project Structure

```
chatbot-mvp/
│
├── actions/
│   └── actions.py  # Custom actions for Rasa, including integration with Neo4j and Weights & Biases (W&B)
│
├── data/
│   ├── nlu.yml  # Training data for NLU model, including intents and examples
│   ├── rules.yml  # Rules for handling specific conversation paths
│   └── stories.yml  # Training data for Core model, including conversation stories
│
├── models/  # Directory where trained models are stored
│
├── tests/  # Directory for test files
│
├── config.yml  # Configuration file for Rasa NLU and Core
│
├── credentials.yml  # Credentials for external services
│
├── docker-compose.yml  # Docker Compose file to manage multiple services
│
├── Dockerfile  # Dockerfile to set up the Rasa environment
│
├── domain.yml  # Defines intents, entities, slots, responses, forms, and actions for the chatbot
│
├── endpoints.yml  # Configuration file for action server and tracker store
│
├── LICENSE  # License for the project
│
├── README.md  # Detailed instructions and information about the project
│
├── requirements.txt  # Python dependencies for the project
│
├── train_rasa_model.py  # Script to train the Rasa model
│
├── index_data.py  # Script to index data into Neo4j
│
├── company_data.json  # Data for Neo4j indexing generated by scrapping the organisation's webiste. Refer crio_scrapper. {scrapy crawl crio_spider -o ../company_data.json}
│
├── combined_data.json # Data for Neo4j indexing generated by transcribing the organisation's youtube videos.
└── frontend/
    ├── package.json  # Dependencies for the React frontend
    ├── public/
    │   └── index.html  # Main HTML file for the React app
    └── src/
        ├── App.js  # Main React component
        ├── Chatbot.js  # Chatbot component handling user interactions and displaying messages
        ├── Chatbot.css  # CSS file for styling the chatbot component
        └── index.js  # Entry point for the React app
```

## Backend Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/Ritwik-28/chatbot-mvp.git
cd chatbot-mvp
```

### Step 2: Create Dockerfile for Environment Setup

Create a `Dockerfile` in the root of your repository. Refer to the code in the repository.

### Step 3: Create `docker-compose.yml`

Create a `docker-compose.yml` file in the root of your repository. Refer to the code in the repository.

### Step 4: Create `requirements.txt`

List all Python dependencies in `requirements.txt`.

### Step 5: Initialize Rasa Project

Initialize a new Rasa project:

```bash
rasa init --no-prompt
```

### Step 6: Update `nlu.yml`

Add intents and examples to `data/nlu.yml`. Refer to the code in the repository.

### Step 7: Update `domain.yml`

Define intents, entities, slots, responses, forms, and actions in `domain.yml`. Refer to the code in the repository.

### Step 8: Create Custom Actions

Create `actions.py` in the `actions` directory. Refer to the code in the repository.

## Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Start the React App

```bash
npm start
```

## Running the Chatbot

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

2. **Start Docker Compose**:

```bash
docker-compose up --build
```

3. **Send Data to Neo4j**

```bash
python index_data.py
```

4. **Update Rasa**

* **Step 1:** Stop Rasa Server

If the Rasa server is already running, stop it by pressing Ctrl+C in the terminal where it is running.

* **Step 2:** Train Rasa Model

Train the Rasa model with any new or updated data:

```bash
rasa train
```

This command will train the NLU and Core models based on the data defined in the data/ directory.

5. **Start Rasa Server**

Start the Rasa server again to use the updated model:

```bash
rasa run --enable-api --cors "*" --endpoints endpoints.yml
```

6. **Start Action Server**

In a separate terminal, start the action server:

```bash
rasa run actions
```

To get the Weight & Biases Authentication key vist: https://wandb.ai/authorize

7. **Interact with the Chatbot**:

In a seprate terminal, enter the chatbot-frontend directory:

```bash
cd chatbot-frontend
```

Build React Application:

```bash
npm start
```

## Importance of Weights & Biases (W&B)

Weights & Biases (W&B) is used for experiment tracking, model evaluation, and hyperparameter tuning. In this project, W&B helps monitor the training process of the Rasa models, ensuring there is no overfitting or underfitting. It provides detailed insights into model performance and helps improve the model iteratively.

### How W&B is Integrated

1. **Initialization**: W&B is initialized in the `actions.py` file.
2. **Tracking**: W&B tracks the performance of the Rasa models during training and provides detailed logs and visualizations.
3. **Evaluation**: W&B helps evaluate the models and compare different versions to select the best performing model.

## Detailed Steps

### Backend

1. **Dockerfile**: Defines the environment setup for Rasa, including installation of required packages and running the Rasa server.

2. **docker-compose.yml**: Configures multiple services including Rasa, the action server, and Neo4j.

3. **requirements.txt**: Lists all the Python dependencies for the project.

4. **rasa init**: Initializes a new Rasa project with default configurations and data.

5. **nlu.yml**: Contains training data for the NLU model, including intents and examples.

6. **domain.yml**: Defines the structure of the chatbot, including intents, entities, slots, responses, forms, and actions.

7. **actions.py**: Contains custom actions for the chatbot, including interaction with Neo4j and handling user profiles.

### Frontend

1. **package.json**: Lists all the dependencies for the React frontend.

2. **public/index.html**: The main HTML file for the React app.

3. **src/App.js**: The main React component.

4. **src/Chatbot.js**: The chatbot component handling user interactions and displaying messages.

5. **src/Chatbot.css**: The CSS file for styling the chatbot component.

## License

This project is licensed under the Apache-2.0 License. See the [LICENSE](LICENSE) file for details.

## Apendix

1. **Rasa Open-source**: https://rasa.com/docs/rasa/
2. **Neo4j**: https://github.com/neo4j/neo4j
3. **Weight & Biases**: https://docs.wandb.ai/
4. **OpenAI**: https://platform.openai.com/docs/overview