"""Gemini API service for flashcard generation and explanations."""

import json
import os
from typing import List, Dict, Any, Optional

# Try multiple approaches for Gemini API
try:
    import google.generativeai as genai
    USE_DIRECT_API = True
except ImportError:
    USE_DIRECT_API = False
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain.schema import HumanMessage, SystemMessage
        USE_LANGCHAIN = True
    except ImportError:
        USE_LANGCHAIN = False

from app.config import settings
from app.curriculum import get_course_by_code


class GeminiService:
    """Service for interacting with Google Gemini API."""
    
    def __init__(self):
        """Initialize the Gemini service."""
        api_key = settings.google_api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set in environment variables")
        
        self.api_key = api_key
        self.use_direct_api = False
        self.model = None
        self.llm = None
        self.model_name = None
        
        # Try to use direct Google Generative AI SDK first (for Gemini 2.5 Flash Pro)
        if USE_DIRECT_API:
            try:
                genai.configure(api_key=self.api_key)
                
                # First, try to list available models to see what's actually available
                try:
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    print(f"Available Gemini models: {available_models}")
                    
                    # Filter for flash/flash-pro models (Student Pack models)
                    flash_models = [m for m in available_models if 'flash' in m.lower() or '2.5' in m.lower() or '2.0' in m.lower()]
                    if flash_models:
                        print(f"Found Flash models: {flash_models}")
                except Exception as e:
                    print(f"Could not list models: {e}")
                    available_models = []
                    flash_models = []
                
                # Try Gemini models - prioritize student pack models
                # Note: The actual model name might be different (e.g., gemini-2.0-flash-exp might be the 2.5 Flash Pro)
                model_names = [
                    "gemini-2.0-flash-exp",  # This might actually be 2.5 Flash Pro in student packs
                    "gemini-2.0-flash-thinking-exp",  # Another variant
                    "gemini-2.0-flash",      # Gemini 2.0 Flash
                    "gemini-1.5-flash-8b",   # Gemini 1.5 Flash 8B
                    "gemini-1.5-flash",      # Gemini 1.5 Flash
                    "gemini-1.5-pro",        # Gemini 1.5 Pro
                    "gemini-pro",            # Fallback
                ]
                
                # If we found flash models, prioritize them
                if flash_models:
                    # Add found flash models to the front of the list
                    model_names = flash_models + model_names
                
                for model_name in model_names:
                    try:
                        # Clean model name (remove 'models/' prefix if present)
                        clean_name = model_name.replace('models/', '')
                        self.model = genai.GenerativeModel(clean_name)
                        self.model_name = clean_name
                        self.use_direct_api = True
                        print(f"✅ Successfully using Gemini model: {clean_name}")
                        break
                    except Exception as e:
                        error_str = str(e)
                        if "404" in error_str or "not found" in error_str.lower():
                            print(f"  Model {model_name} not available, trying next...")
                        else:
                            print(f"  Failed to load {model_name}: {error_str[:100]}")
                        continue
                
                if not self.model:
                    print("⚠️  Direct API initialization failed, trying LangChain...")
                    self.use_direct_api = False
            except Exception as e:
                print(f"Direct API initialization failed: {e}")
                self.use_direct_api = False
        
        # Fallback to LangChain if direct API not available
        if not self.use_direct_api and USE_LANGCHAIN:
            try:
                # Try Gemini models - use same priority as direct API
                # Note: gemini-2.5-flash-pro doesn't exist, Student Pack uses gemini-2.0-flash-exp
                model_names = [
                    "gemini-2.0-flash-exp",  # This is likely the Student Pack "2.5 Flash Pro"
                    "gemini-2.0-flash-thinking-exp",  # Another variant
                    "gemini-2.0-flash",      # Gemini 2.0 Flash
                    "gemini-1.5-flash-8b",   # Gemini 1.5 Flash 8B
                    "gemini-1.5-flash",      # Gemini 1.5 Flash
                    "gemini-1.5-pro",        # Gemini 1.5 Pro
                    "gemini-pro"             # Fallback
                ]
                
                self.llm = None
                self.model_name = None
                for model_name in model_names:
                    try:
                        self.llm = ChatGoogleGenerativeAI(
                            model=model_name,
                            google_api_key=self.api_key,
                            temperature=0.7
                        )
                        self.model_name = model_name
                        print(f"✅ Successfully using Gemini model via LangChain: {model_name}")
                        break
                    except Exception as e:
                        error_str = str(e)
                        if "404" in error_str or "not found" in error_str.lower():
                            print(f"  Model {model_name} not available via LangChain, trying next...")
                        else:
                            print(f"  Failed to load {model_name}: {error_str[:100]}")
                        continue
                
                if not self.llm:
                    raise ValueError("Could not initialize Gemini via LangChain")
            except Exception as e:
                print(f"LangChain initialization failed: {e}")
                raise ValueError(f"Could not initialize Gemini service: {e}")
        elif not self.use_direct_api:
            raise ValueError("Neither google-generativeai nor langchain-google-genai is available")
    
    def generate_flashcards_for_course(
        self, 
        course_code: str, 
        course_name: str,
        degree_program: str = None,
        semester: int = None,
        num_flashcards: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate flashcards for a course using Gemini API with full context.
        
        Args:
            course_code: Course code (e.g., "CS1002")
            course_name: Course name (e.g., "Programming Fundamentals")
            degree_program: Degree program (e.g., "CS", "SE", "AI")
            semester: Semester number (e.g., 1, 2, 3)
            num_flashcards: Number of flashcards to generate (default: 10)
        
        Returns:
            List of flashcard dictionaries with 'front', 'back', 'difficulty', and 'tags'
        """
        try:
            system_prompt = """You are an expert educational content creator specializing in university-level computer science and software engineering courses. 
Generate high-quality, comprehensive flashcards that help students learn effectively.

Each flashcard must have:
- A clear, concise, and well-formulated question on the front
- A comprehensive, detailed, and educational answer on the back with examples when appropriate
- Appropriate difficulty level (easy for basics, medium for intermediate, hard for advanced concepts)
- Relevant tags for categorization

Return ONLY a valid JSON array. Each flashcard must follow this exact structure:
{
  "front": "Question text",
  "back": "Detailed answer with explanation and examples",
  "difficulty": "easy|medium|hard",
  "tags": ["tag1", "tag2", "tag3"]
}

Focus on:
- Core concepts and fundamentals
- Important definitions and terminology
- Key principles and theories
- Practical applications
- Common problems and solutions
- Real-world examples"""

            # Build comprehensive user prompt with all context
            context_parts = [
                f"Course Code: {course_code}",
                f"Course Name: {course_name}"
            ]
            
            if degree_program:
                degree_names = {
                    "CS": "Computer Science",
                    "SE": "Software Engineering", 
                    "AI": "Artificial Intelligence",
                    "DS": "Data Science",
                    "CYS": "Cybersecurity"
                }
                degree_full = degree_names.get(degree_program, degree_program)
                context_parts.append(f"Degree Program: {degree_full} ({degree_program})")
            
            if semester:
                context_parts.append(f"Semester: {semester}")
            
            context_str = "\n".join(context_parts)
            
            user_prompt = f"""Generate {num_flashcards} high-quality flashcards for the following course:

{context_str}

Requirements:
1. Cover fundamental concepts, key definitions, important principles, and practical applications
2. Include a mix of difficulty levels: approximately 30% easy, 50% medium, 20% hard
3. Make questions clear and answerable
4. Provide detailed, educational answers that help students understand the concepts deeply
5. Include examples in answers where appropriate
6. Focus on topics typically covered in this course at this level

Return the flashcards as a JSON array. Ensure all flashcards are relevant to this specific course and academic level."""

            # Use direct API if available, otherwise use LangChain
            if self.use_direct_api:
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = self.model.generate_content(full_prompt)
                content = response.text.strip()
            else:
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ]
                response = self.llm.invoke(messages)
                content = response.content.strip()
            
            # Try to extract JSON from the response
            # Sometimes Gemini wraps JSON in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            flashcards_data = json.loads(content)
            
            # Validate and format
            if not isinstance(flashcards_data, list):
                flashcards_data = [flashcards_data]
            
            # Ensure all required fields are present
            formatted_flashcards = []
            for card in flashcards_data:
                if isinstance(card, dict) and "front" in card and "back" in card:
                    formatted_card = {
                        "front": card["front"],
                        "back": card["back"],
                        "difficulty": card.get("difficulty", "medium"),
                        "tags": card.get("tags", [course_code.lower(), course_name.lower().replace(" ", "-")])
                    }
                    formatted_flashcards.append(formatted_card)
            
            return formatted_flashcards[:num_flashcards]
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from Gemini: {e}")
            print(f"Response content: {content[:500]}")
            # Fallback: return empty list or use hardcoded flashcards
            return []
        except Exception as e:
            print(f"Error generating flashcards with Gemini: {e}")
            return []
    
    def generate_flashcards_for_multiple_courses(
        self,
        courses: List[Dict[str, str]],  # List of {"code": "CS1002", "name": "Programming Fundamentals"}
        degree_program: str = None,
        semester: int = None,
        num_flashcards_per_course: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate flashcards for multiple courses in a SINGLE API call to optimize rate limits.
        
        Args:
            courses: List of course dictionaries with 'code' and 'name'
            degree_program: Degree program (e.g., "CS", "SE", "AI")
            semester: Semester number (e.g., 1, 2, 3)
            num_flashcards_per_course: Number of flashcards per course (default: 10)
        
        Returns:
            Dictionary mapping course_code to list of flashcards
        """
        try:
            system_prompt_template = """You are an expert educational content creator specializing in university-level computer science and software engineering courses. 
Generate high-quality, comprehensive flashcards that help students learn effectively.

Each flashcard must have:
- A clear, concise, and well-formulated question on the front
- A comprehensive, detailed, and educational answer on the back with examples when appropriate
- Appropriate difficulty level (easy for basics, medium for intermediate, hard for advanced concepts)
- Relevant tags for categorization
- The course_code field to identify which course the flashcard belongs to

Return ONLY a valid JSON object. The structure should be:
{
  "CS1002": [
    {
      "front": "Question text",
      "back": "Detailed answer with explanation and examples",
      "difficulty": "easy|medium|hard",
      "tags": ["tag1", "tag2", "tag3"],
      "course_code": "CS1002"
    }
  ],
  "CS1004": [...]
}

Focus on:
- Core concepts and fundamentals
- Important definitions and terminology
- Key principles and theories
- Practical applications
- Common problems and solutions
- Real-world examples

Generate approximately NUM_FLASHCARDS_PER_COURSE flashcards per course."""
            
            # Replace the placeholder with actual number
            system_prompt = system_prompt_template.replace("NUM_FLASHCARDS_PER_COURSE", str(num_flashcards_per_course))

            # Build comprehensive user prompt with all courses
            context_parts = []
            
            if degree_program:
                degree_names = {
                    "CS": "Computer Science",
                    "SE": "Software Engineering", 
                    "AI": "Artificial Intelligence",
                    "DS": "Data Science",
                    "CYS": "Cybersecurity"
                }
                degree_full = degree_names.get(degree_program, degree_program)
                context_parts.append(f"Degree Program: {degree_full} ({degree_program})")
            
            if semester:
                context_parts.append(f"Semester: {semester}")
            
            # List all courses
            courses_list = []
            for course in courses:
                courses_list.append(f"  - {course['code']}: {course['name']}")
            
            context_str = "\n".join(context_parts) if context_parts else ""
            courses_str = "\n".join(courses_list)
            
            user_prompt = f"""Generate {num_flashcards_per_course} high-quality flashcards for EACH of the following courses:

{context_str}

Courses in this semester:
{courses_str}

Requirements:
1. Generate approximately {num_flashcards_per_course} flashcards per course
2. Cover fundamental concepts, key definitions, important principles, and practical applications for each course
3. Include a mix of difficulty levels: approximately 30% easy, 50% medium, 20% hard per course
4. Make questions clear and answerable
5. Provide detailed, educational answers that help students understand the concepts deeply
6. Include examples in answers where appropriate
7. Focus on topics typically covered in each course at this academic level
8. Ensure each flashcard includes the "course_code" field matching the course it belongs to

Return the flashcards as a JSON object where keys are course codes and values are arrays of flashcards for that course.
Ensure all flashcards are relevant to their specific course and academic level."""

            # System prompt is already formatted (using string replacement instead of .format() to avoid brace escaping issues)
            formatted_system_prompt = system_prompt
            
            # Use direct API if available, otherwise use LangChain
            if self.use_direct_api:
                full_prompt = formatted_system_prompt + "\n\n" + user_prompt
                try:
                    response = self.model.generate_content(full_prompt)
                    content = response.text.strip()
                except Exception as api_error:
                    # Handle quota/rate limit errors gracefully
                    error_str = str(api_error)
                    if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower() or "ResourceExhausted" in error_str:
                        print(f"⚠️  Gemini API quota/rate limit exceeded. Using hardcoded flashcards only.")
                        print(f"   Error: {error_str[:150]}...")
                        # Return empty dict - hardcoded flashcards will still be used
                        return {course["code"]: [] for course in courses}
                    else:
                        raise  # Re-raise if it's a different error
            else:
                messages = [
                    SystemMessage(content=formatted_system_prompt),
                    HumanMessage(content=user_prompt)
                ]
                try:
                    response = self.llm.invoke(messages)
                    content = response.content.strip()
                except Exception as api_error:
                    # Handle quota/rate limit errors gracefully
                    error_str = str(api_error)
                    if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower() or "ResourceExhausted" in error_str:
                        print(f"⚠️  Gemini API quota/rate limit exceeded. Using hardcoded flashcards only.")
                        print(f"   Error: {error_str[:150]}...")
                        # Return empty dict - hardcoded flashcards will still be used
                        return {course["code"]: [] for course in courses}
                    else:
                        raise  # Re-raise if it's a different error
            
            # Try to extract JSON from the response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            flashcards_by_course = json.loads(content)
            
            # Validate structure
            if not isinstance(flashcards_by_course, dict):
                print(f"Warning: Expected dict, got {type(flashcards_by_course)}. Converting...")
                # If it's a list, try to organize by course_code
                if isinstance(flashcards_by_course, list):
                    flashcards_by_course = {}
                    for card in flashcards_by_course:
                        course_code = card.get("course_code", courses[0]["code"] if courses else "UNKNOWN")
                        if course_code not in flashcards_by_course:
                            flashcards_by_course[course_code] = []
                        flashcards_by_course[course_code].append(card)
                else:
                    raise ValueError("Invalid response format")
            
            # Ensure all courses have entries
            result = {}
            for course in courses:
                course_code = course["code"]
                if course_code in flashcards_by_course:
                    result[course_code] = flashcards_by_course[course_code]
                else:
                    result[course_code] = []
                    print(f"Warning: No flashcards generated for {course_code}")
            
            total_flashcards = sum(len(cards) for cards in result.values())
            print(f"Generated {total_flashcards} flashcards for {len(courses)} courses in a single API call")
            
            return result
            
        except Exception as e:
            error_str = str(e)
            # Check if it's a quota/rate limit error
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower() or "ResourceExhausted" in error_str:
                print(f"⚠️  Gemini API quota/rate limit exceeded in batch generation.")
                print(f"   Using hardcoded flashcards only. Error: {error_str[:200]}...")
            else:
                print(f"Error generating batch flashcards: {e}")
                import traceback
                traceback.print_exc()
            # Return empty dict with course codes as keys - hardcoded flashcards will still work
            return {course["code"]: [] for course in courses}
    
    def generate_detailed_explanation(
        self,
        question: str,
        correct_answer: str,
        user_answer: str,
        accuracy: float
    ) -> str:
        """
        Generate a detailed explanation when user's answer is incorrect or partially correct.
        
        Args:
            question: The flashcard question
            correct_answer: The correct answer
            user_answer: The user's answer
            accuracy: Accuracy score (0.0 to 1.0)
        
        Returns:
            Detailed explanation string
        """
        try:
            if accuracy >= 0.8:
                # Answer is mostly correct, provide reinforcement
                prompt = f"""The user answered this question mostly correctly. Provide a brief reinforcement and any additional context.

Question: {question}
Correct Answer: {correct_answer}
User's Answer: {user_answer}

Provide a brief, encouraging explanation that reinforces the correct answer and adds any helpful context."""
            else:
                # Answer needs correction, provide detailed explanation
                prompt = f"""The user's answer to this question is incorrect or incomplete. Provide a detailed, educational explanation.

Question: {question}
Correct Answer: {correct_answer}
User's Answer: {user_answer}

Provide a detailed explanation that:
1. Acknowledges what the user got right (if anything)
2. Clearly explains the correct answer
3. Explains why the correct answer is correct
4. Provides additional context or examples to help understanding
5. Is encouraging and educational

Keep it concise but comprehensive."""

            # Use direct API if available, otherwise use LangChain
            if self.use_direct_api:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            else:
                messages = [
                    HumanMessage(content=prompt)
                ]
                response = self.llm.invoke(messages)
                return response.content.strip()
            
        except Exception as e:
            print(f"Error generating explanation with Gemini: {e}")
            # Fallback explanation
            return f"The correct answer is: {correct_answer}. Review the material to better understand this concept."


# Global instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> Optional[GeminiService]:
    """Get or create the Gemini service instance."""
    global _gemini_service
    if _gemini_service is None:
        try:
            _gemini_service = GeminiService()
        except ValueError as e:
            print(f"Warning: Gemini service not available: {e}")
            return None
    return _gemini_service

