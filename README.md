```
███████╗███████╗███╗   ██╗████████╗██╗███████╗███╗   ██╗████████╗   ███████╗
██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║██╔════╝████╗  ██║╚══██╔══╝   ██╔════╝
███████╗█████╗  ██╔██╗ ██║   ██║   ██║█████╗  ██╔██╗ ██║   ██║█████╗███████╗
╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██╔══╝  ██║╚██╗██║   ██║╚════╝╚════██║
███████║███████╗██║ ╚████║   ██║   ██║███████╗██║ ╚████║   ██║      ███████║
╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝      ╚══════╝
```


![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)  ![DeepFace](https://img.shields.io/badge/DeepFace-Emotion_Engine-yellow?style=flat-square)  ![Ollama](https://img.shields.io/badge/LLM-Ollama_Required-red?style=flat-square)  ![Status](https://img.shields.io/badge/Status-Experimental-orange?style=flat-square)

### **Emotion in silico - insight, or intrusion?**  

## **Features**  

- **Dynamic Conversation**: Powered by LLMs from Ollama (Llama 3.2).  
- **Emotion Recognition**: Real-time facial analysis using DeepFace and OpenCV.  
- **Personality Profiling**: Analyze the Big Five traits dynamically through conversation.  
- **Katarsis**: An ironic critique, reflecting how technology observes and categorizes humans.  

---

## **Installation**

### **Prerequisites**
1. **Python 3.12+**  
   Ensure Python is installed. [Download here](https://www.python.org/downloads/).  

2. **Ollama Installation**  
   Ollama must be installed and running locally. Follow their [installation guide](https://github.com/ollama/ollama).  

3. **Install Required System Libraries**  
   On Linux systems, install libraries for OpenCV:  


---

### **Setup Steps**

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/CarlosClassen/sentient-5.git
   cd sentient-5
   ```

2. **Install Dependencies**  
   Install all required Python libraries using `pip`:  
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Ollama**  
   Make sure Ollama is running locally:
   ```bash
   ollama serve
   ```

4. **Run Sentient-5**  
   Launch the application:  
   ```bash
   python sentient-5/main.py
   ```

---

## **Session Flow**

1. **Idle Screen**  
   The installation starts with a idle screen. After the first detected input, the idle screen disappears and users can interact by entering their first message to the system.  

2. **Conversation Stages**:  
   - **Greeting**: Sentient-5 builds rapport with you.  
   - **Assessment**: It explores your personality traits dynamically.  
   - **Katarsis**: The system itself is challenging the role of surveillance technologies.  

3. **Emotion Analysis**  
   Sentient-5 captures your facial reactions after each message and analyzes emotions to enhance the assessment and conversation.  

---

## **System Requirements**

| **Component**      | **Specification**                          |  
|---------------------|--------------------------------------------|  
| Python Version      | 3.12+                                     |  
| Operating System    | Linux, macOS, Windows                     |  
| GPU (Optional)      | For faster emotion detection with DeepFace|  
| RAM                 | 8GB+                                      |  

---

## **Project Structure**  

```plaintext
sentient-5
├── main.py            # Entry point
├── chat_engine.py     # Conversation engine logic
├── emotion_engine.py  # Emotion analysis with DeepFace
├── scoring_system.py  # Personality scoring
├── prompt_manager.py  # Handles prompts and dynamic injection
├── utils.py           # Terminal UI logic
├── data               # Prompts, settings, and stimuli
│   ├── prompts.json
│   ├── settings.json
│   └── stimuli.json
└── logs               # Emotion logs (created dynamically)
```

---

## **Credits**

- **LLM Powered by Ollama**  
- **Emotion Analysis via DeepFace**  

**Created for experimental installations.**  

---

### **Disclaimer**  
This project is for **artistic and educational purposes** only.  
No data is transmitted or stored beyond the local system.  

---

## **License**  
This project is licensed under the [MIT License](LICENSE).  