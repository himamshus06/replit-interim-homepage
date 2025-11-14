import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import List, Dict
import re
import gradio as gr

class EducationChatbot:
    def __init__(self):
        # Using free, open-access models that don't require permission
        self.model_options = {
            "tiny-llama": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # Fast and free
            "phi-2": "microsoft/phi-1_5",  # Good for educational content
            "qwen": "Qwen/Qwen1.5-0.5B-Chat"  # Another free option
        }
        self.model_name = self.model_options["tiny-llama"]  # Default model
        self.tokenizer = None
        self.model = None
        self.conversation_history = []
        self.curriculum_context = self.load_curriculum_context()
        self.setup_model()
        
    def setup_model(self):
        """Initialize the model and tokenizer"""
        try:
            print(f"🔄 Loading model: {self.model_name}")
            
            # Use pipeline for easier handling
            self.pipe = pipeline(
                "text-generation",
                model=self.model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            print("🤖 Education Chatbot initialized successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("🔄 Trying fallback model...")
            self.setup_fallback_model()
    
    def setup_fallback_model(self):
        """Setup a simpler fallback model"""
        try:
            self.model_name = "microsoft/DialoGPT-small"
            self.pipe = pipeline("text-generation", model=self.model_name)
            print("🤖 Fallback model initialized successfully!")
        except Exception as e:
            print(f"Fallback model also failed: {e}")
            self.pipe = None
    
    def load_curriculum_context(self) -> Dict:
        """Load Indian curriculum context"""
        return {
            "physics": {
                "11th": ["Physical World", "Units and Measurements", "Motion in Straight Line", 
                        "Laws of Motion", "Work, Energy and Power", "System of Particles", 
                        "Gravitation", "Mechanical Properties", "Thermodynamics", "Kinetic Theory", 
                        "Oscillations", "Waves"],
                "12th": ["Electric Charges and Fields", "Electrostatic Potential", "Current Electricity", 
                        "Moving Charges and Magnetism", "Magnetism", "Electromagnetic Induction", 
                        "Alternating Current", "Electromagnetic Waves", "Ray Optics", "Wave Optics", 
                        "Dual Nature", "Atoms", "Nuclei", "Semiconductors"]
            },
            "chemistry": {
                "11th": ["Basic Concepts", "Structure of Atom", "Classification", "Chemical Bonding", 
                        "States of Matter", "Thermodynamics", "Equilibrium", "Redox Reactions", 
                        "Hydrogen", "s-Block", "p-Block", "Organic Chemistry", "Hydrocarbons", 
                        "Environmental Chemistry"],
                "12th": ["Solid State", "Solutions", "Electrochemistry", "Chemical Kinetics", 
                        "Surface Chemistry", "p-Block", "d and f Block", "Coordination Compounds", 
                        "Haloalkanes", "Alcohols", "Ethers", "Aldehydes", "Ketones", "Carboxylic Acids", 
                        "Amines", "Biomolecules", "Polymers", "Chemistry in Everyday Life"]
            },
            "mathematics": {
                "11th": ["Sets", "Relations and Functions", "Trigonometric Functions", 
                        "Complex Numbers", "Linear Inequalities", "Permutations", "Combinations", 
                        "Binomial Theorem", "Sequence and Series", "Straight Lines", "Conic Sections", 
                        "Introduction to 3D", "Limits and Derivatives", "Mathematical Reasoning", 
                        "Statistics", "Probability"],
                "12th": ["Relations and Functions", "Inverse Trigonometric Functions", "Matrices", 
                        "Determinants", "Continuity and Differentiability", "Application of Derivatives", 
                        "Integrals", "Application of Integrals", "Differential Equations", "Vector Algebra", 
                        "Three Dimensional Geometry", "Linear Programming", "Probability"]
            },
            "biology": {
                "11th": ["The Living World", "Biological Classification", "Plant Kingdom", 
                        "Animal Kingdom", "Morphology of Flowering Plants", "Anatomy of Flowering Plants", 
                        "Structural Organisation in Animals", "Cell-The Unit of Life", "Biomolecules", 
                        "Cell Cycle and Cell Division", "Transport in Plants", "Mineral Nutrition", 
                        "Photosynthesis in Higher Plants", "Respiration in Plants", "Plant Growth and Development", 
                        "Digestion and Absorption", "Breathing and Exchange of Gases", "Body Fluids and Circulation", 
                        "Excretory Products and their Elimination", "Locomotion and Movement", 
                        "Neural Control and Coordination", "Chemical Coordination and Integration"],
                "12th": ["Reproduction in Organisms", "Sexual Reproduction in Flowering Plants", 
                        "Human Reproduction", "Reproductive Health", "Principles of Inheritance and Variation", 
                        "Molecular Basis of Inheritance", "Evolution", "Human Health and Disease", 
                        "Strategies for Enhancement in Food Production", "Microbes in Human Welfare", 
                        "Biotechnology: Principles and Processes", "Biotechnology and its Applications", 
                        "Organisms and Populations", "Ecosystem", "Biodiversity and Conservation", 
                        "Environmental Issues"]
            },
            "computer science": {
                "11th": ["Computer Systems and Organisation", "Computational Thinking and Programming", 
                        "Society, Law and Ethics", "Python Programming", "Data Handling", 
                        "Flow of Control", "Functions", "Strings", "Lists, Tuples and Dictionaries", 
                        "Computer Networks", "Database Concepts", "SQL"],
                "12th": ["Python Revision", "Advanced Programming with Python", "File Handling", 
                        "Data Structures", "Computer Networks", "Database Management", "SQL Queries", 
                        "Interface Python with SQL", "Society, Law and Ethics"]
            },
            "english": {
                "11th": ["Reading Comprehension", "Writing Skills", "Grammar", "Literature", 
                        "Poetry", "Prose", "Drama", "Communication Skills"],
                "12th": ["Advanced Reading", "Professional Writing", "Advanced Grammar", 
                        "Flamingo (Prose)", "Flamingo (Poetry)", "Vistas", "Novel", "Report Writing"]
            }
        }
    
    def detect_subject(self, question: str) -> str:
        """Detect the subject from the question"""
        question_lower = question.lower()
        
        subject_keywords = {
            'physics': ['physics', 'force', 'energy', 'motion', 'electricity', 'optics', 'magnetism', 'newton', 'quantum', 'wave', 'atom'],
            'chemistry': ['chemistry', 'atom', 'molecule', 'reaction', 'organic', 'periodic', 'chemical', 'bond', 'compound', 'element'],
            'mathematics': ['math', 'calculus', 'algebra', 'trigonometry', 'equation', 'derivative', 'integral', 'geometry', 'probability', 'statistics'],
            'biology': ['biology', 'cell', 'dna', 'evolution', 'respiration', 'photosynthesis', 'organism', 'reproduction', 'genetics', 'plant', 'animal'],
            'computer science': ['programming', 'python', 'java', 'algorithm', 'database', 'computer', 'code', 'software', 'binary', 'variable'],
            'english': ['english', 'grammar', 'literature', 'writing', 'comprehension', 'poem', 'story', 'essay', 'tense', 'vocabulary']
        }
        
        for subject, keywords in subject_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                return subject
        
        return "general"
    
    def create_enhanced_prompt(self, question: str, subject: str) -> str:
        """Create enhanced prompt with curriculum context"""
        
        curriculum_info = ""
        if subject in self.curriculum_context:
            curriculum_info = f"""
This is for Indian 11th/12th standard {subject} curriculum.
Key topics include: {', '.join(self.curriculum_context[subject]['11th'][:3])} in 11th and {', '.join(self.curriculum_context[subject]['12th'][:3])} in 12th.

"""
        
        prompt = f"""You are a friendly tutor for Indian 11th and 12th standard students. Answer the question clearly and simply.

{curriculum_info}
Question: {question}

Please provide:
- Clear explanation in simple English
- Step-by-step reasoning if needed
- Examples from daily life when possible
- Key points to remember

Answer:"""
        
        return prompt
    
    def generate_response(self, question: str) -> str:
        """Generate enhanced response with curriculum context"""
        if not hasattr(self, 'pipe') or self.pipe is None:
            return "I'm still getting ready to help you. Please wait a moment and try again."
        
        subject = self.detect_subject(question)
        prompt = self.create_enhanced_prompt(question, subject)
        
        try:
            # Generate response using pipeline
            response = self.pipe(
                prompt,
                max_new_tokens=400,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.pipe.tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
            
            # Extract the generated text
            generated_text = response[0]['generated_text']
            
            # Remove the prompt from response
            answer = generated_text.replace(prompt, "").strip()
            
            # Clean up response
            answer = self.clean_response(answer)
            
            # Store conversation
            self.conversation_history.append({
                "question": question,
                "response": answer,
                "subject": subject
            })
            
            return answer
            
        except Exception as e:
            return f"I apologize, but I'm having trouble generating a response right now. Please try again with a different question. Error: {str(e)[:100]}"
    
    def clean_response(self, response: str) -> str:
        """Clean and format the response"""
        # Remove any incomplete sentences at the end
        response = re.sub(r'[^.!?]*$', '', response)
        
        # Ensure proper formatting
        response = response.strip()
        
        # Add proper punctuation if missing
        if response and not response[-1] in ['.', '!', '?']:
            response += '.'
            
        return response

# Initialize chatbot instance
chatbot = EducationChatbot()

def gradio_respond(message, history):
    """Response function for Gradio interface"""
    if not message.strip():
        return "Please ask a question about your studies!"
    
    # Show typing indicator
    yield "🔄 Thinking..."
    
    response = chatbot.generate_response(message)
    yield response

def create_gradio_interface():
    """Create and configure Gradio interface"""
    
    # Modern, user-friendly CSS with Color Hunt palette
custom_css = """
:root {
    --primary: #DC143C;
    --secondary: #F75270;
    --light: #F7CAC9;
    --background: #FDEBD0;
}

/* Background */
.gradio-container {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, var(--background), var(--light));
    min-height: 100vh;
    padding: 22px;
    color: #333;
}

/* HEADER */
.header-section {
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    padding: 35px;
    border-radius: 22px;
    text-align: center;
    color: white;
    box-shadow: 0 10px 35px rgba(220,20,60,0.35);
}
.header-section h1 {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 10px;
}
.header-section h2 {
    opacity: 0.9;
    font-size: 18px;
}

/* LEFT SIDEBAR */
.markdown, .info-card, .examples {
    background: rgba(255,255,255,0.9);
    backdrop-filter: blur(6px);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(247,82,112,0.18);
    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
}

/* Example cards */
.example {
    background: linear-gradient(135deg, var(--background), var(--light));
    border-radius: 14px;
    padding: 14px;
    margin: 6px 0;
    transition: 0.25s ease;
    cursor: pointer;
}
.example:hover {
    background: linear-gradient(135deg, var(--secondary), var(--primary));
    color: white;
    transform: translateX(6px);
    box-shadow: 0 8px 14px rgba(220,20,60,0.25);
}

/* CHAT WINDOW */
.gr-chatbot {
    background: rgba(255,255,255,0.9);
    backdrop-filter: blur(8px);
    border-radius: 20px;
    border: 1px solid rgba(247,82,112,0.18);
    box-shadow: 0 10px 30px rgba(220,20,60,0.16);
    padding: 14px;
}

/* Chat bubbles */
.message {
    font-size: 15px !important;
    padding: 14px 18px;
    border-radius: 18px;
    margin: 8px 0 !important;
    max-width: 85%;
    line-height: 1.6;
}

/* User bubble */
.message.user {
    background: linear-gradient(135deg, var(--secondary), var(--primary));
    color: white;
    border-bottom-right-radius: 6px;
    margin-left: auto;
    box-shadow: 0 4px 10px rgba(220,20,60,0.25);
}

/* Bot bubble */
.message.bot {
    background: linear-gradient(135deg, var(--background), var(--light));
    border-bottom-left-radius: 6px;
    margin-right: auto;
    color: #222;
    box-shadow: 0 4px 10px rgba(247,82,112,0.15);
}

/* INPUT BOX */
textarea, input[type="text"] {
    border-radius: 14px !important;
    border: 2px solid var(--light) !important;
    background: white !important;
    padding: 16px !important;
    transition: 0.3s;
}
textarea:focus, input[type="text"]:focus {
    border-color: var(--secondary) !important;
    box-shadow: 0 0 0 4px rgba(247,82,112,0.2);
}

/* BUTTONS */
button {
    border-radius: 14px !important;
    padding: 14px 26px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    transition: 0.28s ease !important;
}

button.primary {
    background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
    color: white !important;
    box-shadow: 0 8px 22px rgba(220,20,60,0.35);
}
button.primary:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(220,20,60,0.4);
}

button:not(.primary) {
    background: white !important;
    border: 2px solid var(--secondary) !important;
    color: var(--primary) !important;
}
button:not(.primary):hover {
    background: var(--light) !important;
    box-shadow: 0 4px 18px rgba(247,82,112,0.25);
    transform: translateY(-3px);
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 10px;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, var(--secondary), var(--primary));
    border-radius: 10px;
}
"""

    with gr.Blocks(css=custom_css, title="EduBot - Study Assistant", theme=gr.themes.Soft()) as demo:
        # Header Section
        with gr.Row():
            gr.Markdown(
                """
                <div class="header-section">
                    <h1>🎓 EduBot</h1>
                    <h2>Your AI Study Assistant for 11th & 12th Grade</h2>
                </div>
                """
            )
        
        # Main Content Area
        with gr.Row():
            # Left Sidebar - Examples and Info
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("### 📚 Quick Start Examples")
                examples = gr.Examples(
                    examples=[
                        "Explain Newton's third law of motion",
                        "What is chemical bonding?",
                        "How to solve quadratic equations?",
                        "What is photosynthesis?",
                        "Explain Python functions",
                        "What is DNA replication?",
                        "How does electricity work?"
                    ],
                    inputs=gr.Textbox(
                        label="",
                        lines=3,
                        placeholder="💬 Type your question here or click an example above...",
                        show_label=False
                    ),
                    label=""
                )
                
                gr.Markdown("### ℹ️ How EduBot Helps You")
                gr.Markdown(
                    """
                    <div class="info-card">
                        <ul>
                            <li>Clear concept explanations</li>
                            <li>Step-by-step problem solving</li>
                            <li>Homework assistance</li>
                            <li>Exam preparation support</li>
                            <li>Doubt clarification</li>
                        </ul>
                        <p style="margin-top: 15px; font-size: 12px; color: #666; font-style: italic;">
                            📖 Always verify answers with your teachers and textbooks
                        </p>
                    </div>
                    """
                )
                
                gr.Markdown("### 📖 Supported Subjects")
                gr.Markdown(
                    """
                    <div style="background: rgba(255,255,255,0.9); padding: 15px; border-radius: 12px; border-left: 4px solid #f75270;">
                        <p style="margin: 5px 0;">🔬 Physics | ⚗️ Chemistry | 📐 Mathematics</p>
                        <p style="margin: 5px 0;">🧬 Biology | 💻 Computer Science | 📝 English</p>
                    </div>
                    """
                )
            
            # Right Side - Chat Interface
            with gr.Column(scale=2):
                chatbot_interface = gr.Chatbot(
                    label="💬 Chat with EduBot",
                    height=550,
                    show_label=True,
                    container=True,
                    bubble_full_width=False,
                    avatar_images=(None, "🎓")
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        label="",
                        placeholder="💭 Ask any question from your 11th or 12th grade syllabus...",
                        lines=3,
                        show_label=False,
                        scale=4
                    )
                
                with gr.Row():
                    submit_btn = gr.Button("Send Message 📤", variant="primary", scale=1)
                    clear_btn = gr.Button("Clear Chat 🗑️", scale=1)
        
        # Handle interactions
        def respond_message(message, chat_history):
            if not message.strip():
                return chat_history, ""
            
            chat_history.append([message, ""])
            
            for response in gradio_respond(message, chat_history):
                chat_history[-1][1] = response
                yield chat_history, ""
        
        def clear_chat():
            chatbot.conversation_history.clear()
            return None, ""
        
        # Connect components
        msg.submit(
            respond_message,
            [msg, chatbot_interface],
            [chatbot_interface, msg]
        )
        
        submit_btn.click(
            respond_message,
            [msg, chatbot_interface],
            [chatbot_interface, msg]
        )
        
        clear_btn.click(
            clear_chat,
            outputs=[chatbot_interface, msg]
        )
    
    return demo

def main():
    """Main function to run the application"""
    print("🚀 Starting EduBot Web Interface...")
    print("📚 AI Tutor for 11th/12th Grade Indian Students")
    print("🌐 Server will start at: http://localhost:7860")
    
    try:
        demo = create_gradio_interface()
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True
        )
    except Exception as e:
        print(f"Error starting the application: {e}")
        print("Please make sure all dependencies are installed.")

if __name__ == "__main__":
    main()