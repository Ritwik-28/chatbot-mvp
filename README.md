<h1 align="center">Chatbot MVP with Rasa and React</h1>

<p align="justified">This project sets up a chatbot MVP using Rasa for the backend and React for the frontend. The chatbot can handle user interactions, collect lead information, and provide responses based on predefined intents and entities.</p>

## Prerequisites

- Docker and Docker Compose
- Node.js and npm

## Project Structure

```
chatbot-mvp/
│
├── actions/
│   └── actions.py  # Custom actions for Rasa, including integration with Elasticsearch and Weights & Biases (W&B)
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
├── index_data.py  # Script to index data into Elasticsearch
│
├── company_data.json  # Sample data for Elasticsearch indexing
│
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

1. **Start Docker Compose**:

```bash
docker-compose up --build
```

2. **Interact with the Chatbot**:

Navigate to `http://localhost:3000` in your browser to interact with the chatbot.

## Importance of Weights & Biases (W&B)

Weights & Biases (W&B) is used for experiment tracking, model evaluation, and hyperparameter tuning. In this project, W&B helps monitor the training process of the Rasa models, ensuring there is no overfitting or underfitting. It provides detailed insights into model performance and helps improve the model iteratively.

### How W&B is Integrated

1. **Initialization**: W&B is initialized in the `actions.py` file.
2. **Tracking**: W&B tracks the performance of the Rasa models during training and provides detailed logs and visualizations.
3. **Evaluation**: W&B helps evaluate the models and compare different versions to select the best performing model.

## Detailed Steps

### Backend

1. **Dockerfile**: Defines the environment setup for Rasa, including installation of required packages and running the Rasa server.

2. **docker-compose.yml**: Configures multiple services including Rasa, the action server, and Elasticsearch.

3. **requirements.txt**: Lists all the Python dependencies for the project.

4. **rasa init**: Initializes a new Rasa project with default configurations and data.

5. **nlu.yml**: Contains training data for the NLU model, including intents and examples.

6. **domain.yml**: Defines the structure of the chatbot, including intents, entities, slots, responses, forms, and actions.

7. **actions.py**: Contains custom actions for the chatbot, including interaction with Elasticsearch and handling user profiles.

### Frontend

1. **package.json**: Lists all the dependencies for the React frontend.

2. **public/index.html**: The main HTML file for the React app.

3. **src/App.js**: The main React component.

4. **src/Chatbot.js**: The chatbot component handling user interactions and displaying messages.

5. **src/Chatbot.css**: The CSS file for styling the chatbot component.

## License

This project is licensed under the Apache-2.0 License. See the [LICENSE](LICENSE) file for details.
