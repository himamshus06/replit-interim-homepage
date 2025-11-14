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
    /* Global Reset & Base Styles */
    * {
        box-sizing: border-box;
    }
    
    /* Main container with beautiful gradient background */
    .gradio-container {
        font-family: 'Inter', 'Segoe UI', 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #fdebd0 0%, #f7cac9 50%, #fdebd0 100%);
        background-attachment: fixed;
        min-height: 100vh;
        padding: 20px;
    }
    
    /* Header Section - Modern & Eye-catching */
    .gradio-container .header-section {
        background: linear-gradient(135deg, #dc143c 0%, #f75270 100%);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 8px 24px rgba(220, 20, 60, 0.25);
        margin-bottom: 25px;
        text-align: center;
    }
    
    .gradio-container h1 {
        color: #ffffff;
        font-weight: 800;
        font-size: 2.5em;
        margin: 0;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.2);
        letter-spacing: -0.5px;
    }
    
    .gradio-container h2 {
        color: #ffffff;
        font-weight: 500;
        font-size: 1.2em;
        margin: 10px 0 0 0;
        opacity: 0.95;
    }
    
    .gradio-container h3 {
        color: #dc143c;
        font-weight: 700;
        font-size: 1.4em;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 3px solid #f75270;
    }
    
    /* Markdown sections with glassmorphism effect */
    .gradio-container .markdown {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(220, 20, 60, 0.1);
        margin: 15px 0;
        border: 1px solid rgba(247, 82, 112, 0.2);
    }
    
    /* Chatbot Interface - Modern Card Design */
    .chatbot {
        min-height: 550px;
        max-height: 600px;
        background: #ffffff;
        border-radius: 16px;
        border: none;
        box-shadow: 0 8px 32px rgba(220, 20, 60, 0.15);
        padding: 20px;
        overflow-y: auto;
    }
    
    /* Chat Message Bubbles */
    .chatbot .message {
        padding: 14px 18px;
        margin: 12px 0;
        border-radius: 18px;
        max-width: 85%;
        word-wrap: break-word;
        line-height: 1.6;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* User messages - Right aligned with pink gradient */
    .chatbot .message.user-message,
    .chatbot .message[data-author="user"] {
        background: linear-gradient(135deg, #f75270 0%, #dc143c 100%);
        color: #000000;
        margin-left: auto;
        margin-right: 0;
        border-bottom-right-radius: 4px;
        box-shadow: 0 4px 12px rgba(220, 20, 60, 0.2);
    }
    
    /* Bot messages - Left aligned with cream background */
    .chatbot .message.bot-message,
    .chatbot .message[data-author="bot"] {
        background: linear-gradient(135deg, #fdebd0 0%, #f7cac9 100%);
        color: #333333;
        margin-left: 0;
        margin-right: auto;
        border-bottom-left-radius: 4px;
        box-shadow: 0 4px 12px rgba(247, 82, 112, 0.15);
    }
    
    /* Text Input - Modern & Accessible */
    .gradio-container textarea,
    .gradio-container input[type="text"] {
        background: #ffffff;
        border: 2px solid #f7cac9;
        border-radius: 12px;
        padding: 16px 20px;
        font-size: 15px;
        font-family: inherit;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        resize: none;
        box-shadow: 0 2px 8px rgba(220, 20, 60, 0.08);
    }
    
    .gradio-container textarea:focus,
    .gradio-container input[type="text"]:focus {
        border-color: #f75270;
        outline: none;
        box-shadow: 0 0 0 4px rgba(247, 82, 112, 0.15), 0 4px 16px rgba(220, 20, 60, 0.2);
        transform: translateY(-2px);
    }
    
    .gradio-container textarea::placeholder,
    .gradio-container input[type="text"]::placeholder {
        color: #999;
        opacity: 0.7;
    }
    
    /* Primary Button - Send Button */
    .gradio-container button.primary {
        background: linear-gradient(135deg, #dc143c 0%, #f75270 100%);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 16px 32px;
        font-weight: 700;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px rgba(220, 20, 60, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        position: relative;
        overflow: hidden;
    }
    
    .gradio-container button.primary::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .gradio-container button.primary:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(220, 20, 60, 0.4);
        background: linear-gradient(135deg, #f75270 0%, #dc143c 100%);
    }
    
    .gradio-container button.primary:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .gradio-container button.primary:active {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(220, 20, 60, 0.3);
    }
    
    /* Secondary Button - Clear Button */
    .gradio-container button:not(.primary) {
        background: #ffffff;
        color: #dc143c;
        border: 2px solid #f75270;
        border-radius: 12px;
        padding: 16px 32px;
        font-weight: 600;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(247, 82, 112, 0.15);
    }
    
    .gradio-container button:not(.primary):hover {
        background: #f7cac9;
        border-color: #dc143c;
        color: #dc143c;
        transform: translateY(-3px);
        box-shadow: 0 4px 16px rgba(247, 82, 112, 0.25);
    }
    
    .gradio-container button:not(.primary):active {
        transform: translateY(-1px);
    }
    
    /* Examples Section - Interactive Cards */
    .gradio-container .examples {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(247, 82, 112, 0.2);
        box-shadow: 0 4px 20px rgba(220, 20, 60, 0.1);
    }
    
    .gradio-container .example {
        background: linear-gradient(135deg, #fdebd0 0%, #f7cac9 100%);
        border: 2px solid transparent;
        border-radius: 12px;
        padding: 14px 18px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 14px;
        color: #333;
        box-shadow: 0 2px 8px rgba(220, 20, 60, 0.1);
    }
    
    .gradio-container .example:hover {
        background: linear-gradient(135deg, #f75270 0%, #dc143c 100%);
        color: #ffffff;
        border-color: #dc143c;
        transform: translateX(8px) translateY(-2px);
        box-shadow: 0 6px 20px rgba(220, 20, 60, 0.3);
    }
    
    /* Labels - Clear & Prominent */
    .gradio-container label {
        color: #dc143c;
        font-weight: 700;
        font-size: 16px;
        margin-bottom: 10px;
        display: block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 14px;
    }
    
    /* Info Cards */
    .info-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
        border-left: 4px solid #f75270;
        box-shadow: 0 4px 20px rgba(220, 20, 60, 0.1);
    }
    
    .info-card ul {
        list-style: none;
        padding: 0;
    }
    
    .info-card li {
        padding: 8px 0;
        padding-left: 25px;
        position: relative;
        color: #333;
    }
    
    .info-card li::before {
        content: '✓';
        position: absolute;
        left: 0;
        color: #dc143c;
        font-weight: bold;
        font-size: 18px;
    }
    
    /* Scrollbar - Custom Styled */
    .gradio-container ::-webkit-scrollbar {
        width: 12px;
    }
    
    .gradio-container ::-webkit-scrollbar-track {
        background: #f7cac9;
        border-radius: 10px;
    }
    
    .gradio-container ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #f75270 0%, #dc143c 100%);
        border-radius: 10px;
        border: 2px solid #f7cac9;
    }
    
    .gradio-container ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #dc143c 0%, #f75270 100%);
    }
    
    /* Row and Column Spacing */
    .gradio-container .row {
        gap: 20px;
        margin: 20px 0;
    }
    
    .gradio-container .column {
        gap: 20px;
    }
    
    /* Focus States for Accessibility */
    .gradio-container *:focus-visible {
        outline: 3px solid #f75270;
        outline-offset: 3px;
        border-radius: 4px;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .gradio-container {
            padding: 10px;
        }
        
        .gradio-container h1 {
            font-size: 1.8em;
        }
        
        .chatbot {
            min-height: 400px;
            max-height: 450px;
        }
    }
    
    /* Loading Animation */
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    .gradio-container .loading {
        animation: pulse 1.5s ease-in-out infinite;
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