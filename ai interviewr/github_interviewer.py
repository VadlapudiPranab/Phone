import os
from github import Github
from dotenv import load_dotenv
import json
import random
from datetime import datetime

# Load environment variables
load_dotenv()

class GitHubInterviewer:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            raise ValueError("Please set GITHUB_TOKEN in .env file")
        
        self.github = Github(self.github_token)
        self.repo_name = os.getenv('GITHUB_REPO', 'interview-data')
        self.username = os.getenv('GITHUB_USERNAME')
        
        # Initialize repository
        self.init_repository()
        
    def init_repository(self):
        """Initialize or get the repository for storing interview data"""
        try:
            self.user = self.github.get_user()
            try:
                self.repo = self.user.get_repo(self.repo_name)
                print(f"Connected to existing repository: {self.repo_name}")
            except:
                self.repo = self.user.create_repo(
                    self.repo_name,
                    description="AI Mock Interview Data Repository",
                    private=True
                )
                print(f"Created new repository: {self.repo_name}")
                self.init_questions()
        except Exception as e:
            print(f"Error initializing repository: {str(e)}")
            raise

    def init_questions(self):
        """Initialize the repository with default questions"""
        default_questions = {
            "technical": [
                "Explain the concept of object-oriented programming.",
                "What is the difference between a list and a tuple in Python?",
                "How do you handle exceptions in Python?",
                "Explain the concept of version control and Git.",
                "What are the principles of clean code?"
            ],
            "behavioral": [
                "Tell me about a challenging project you worked on.",
                "How do you handle conflicts in a team?",
                "What's your approach to learning new technologies?",
                "Describe a time when you had to meet a tight deadline.",
                "How do you prioritize your tasks?"
            ]
        }
        
        try:
            content = json.dumps(default_questions, indent=2)
            self.repo.create_file(
                "questions.json",
                "Initial questions setup",
                content
            )
        except Exception as e:
            print(f"Error initializing questions: {str(e)}")

    def get_questions(self):
        """Retrieve questions from the repository"""
        try:
            questions_file = self.repo.get_contents("questions.json")
            questions = json.loads(questions_file.decoded_content)
            return questions
        except Exception as e:
            print(f"Error retrieving questions: {str(e)}")
            return None

    def save_interview_session(self, responses):
        """Save interview responses to the repository"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"interviews/session_{timestamp}.json"
            content = json.dumps(responses, indent=2)
            
            # Create interviews directory if it doesn't exist
            try:
                self.repo.get_contents("interviews")
            except:
                self.repo.create_file(
                    "interviews/.gitkeep",
                    "Create interviews directory",
                    ""
                )

            self.repo.create_file(
                filename,
                f"Interview session - {timestamp}",
                content
            )
            print(f"Interview session saved to GitHub: {filename}")
        except Exception as e:
            print(f"Error saving interview session: {str(e)}")

def conduct_interview():
    try:
        interviewer = GitHubInterviewer()
        questions = interviewer.get_questions()
        
        if not questions:
            print("Failed to retrieve questions. Exiting...")
            return

        responses = {
            "timestamp": datetime.now().isoformat(),
            "answers": []
        }

        print("\nWelcome to the AI Mock Interview!\n")
        print("This interview will include both technical and behavioral questions.")
        print("Your responses will be saved to your GitHub repository.\n")

        # Mix technical and behavioral questions
        all_questions = []
        for q_type in questions:
            for question in questions[q_type]:
                all_questions.append({"type": q_type, "question": question})
        random.shuffle(all_questions)

        for i, q_data in enumerate(all_questions, 1):
            print(f"\nQuestion {i} ({q_data['type'].capitalize()}):")
            print(q_data['question'])
            answer = input("\nYour answer: ")
            
            responses["answers"].append({
                "type": q_data["type"],
                "question": q_data["question"],
                "answer": answer
            })
            
            # Simple feedback based on answer length
            if len(answer) < 50:
                print("\nTip: Consider providing more detail in your answer.")
            else:
                print("\nGood detailed response!")

        print("\nInterview complete! Saving your responses...")
        interviewer.save_interview_session(responses)
        print("\nThank you for participating in the mock interview!")
        print("You can find your interview responses in your GitHub repository.")

    except Exception as e:
        print(f"An error occurred during the interview: {str(e)}")

if __name__ == "__main__":
    conduct_interview()
