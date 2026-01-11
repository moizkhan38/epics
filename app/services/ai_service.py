from anthropic import Anthropic, AsyncAnthropic
from typing import List, Dict, Any
import json

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class AIService:
    """Service for interacting with Anthropic Claude API"""

    def __init__(self):
        """Initialize the Anthropic client"""
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
        self.max_tokens = settings.MAX_TOKENS

    async def generate_epics_and_stories(
        self,
        project_description: str,
        similar_projects: List[Dict[str, Any]],
        additional_context: str | None = None,
        rejection_feedback: str | None = None
    ) -> Dict[str, Any]:
        """
        Generate epics and user stories for a project using Claude

        Args:
            project_description: Description of the project
            similar_projects: List of similar projects for context
            additional_context: Additional context or requirements
            rejection_feedback: Feedback from previous rejection (for regeneration)

        Returns:
            Dictionary containing generated epics and user stories
        """
        # Build the prompt
        prompt = self._build_generation_prompt(
            project_description,
            similar_projects,
            additional_context,
            rejection_feedback
        )

        try:
            logger.info(
                "requesting_ai_generation",
                model=self.model,
                prompt_length=len(prompt)
            )

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract the response content
            content = response.content[0].text

            # Parse the JSON response
            result = json.loads(content)

            logger.info(
                "ai_generation_successful",
                epics_count=len(result.get("epics", [])),
                total_stories=sum(len(epic.get("user_stories", [])) for epic in result.get("epics", []))
            )

            return result

        except json.JSONDecodeError as e:
            logger.error("failed_to_parse_ai_response", error=str(e))
            raise ValueError(f"Failed to parse AI response: {str(e)}")
        except Exception as e:
            logger.error("ai_generation_failed", error=str(e))
            raise

    def _build_generation_prompt(
        self,
        project_description: str,
        similar_projects: List[Dict[str, Any]],
        additional_context: str | None,
        rejection_feedback: str | None
    ) -> str:
        """Build the prompt for epic and user story generation"""

        similar_projects_text = ""
        if similar_projects:
            similar_projects_text = "\n\n## Similar Projects (for reference)\n"
            for i, proj in enumerate(similar_projects, 1):
                similar_projects_text += f"\n{i}. **{proj['name']}** (similarity: {proj['similarity_score']:.2f})\n"
                similar_projects_text += f"   Description: {proj['description']}\n"

        additional_context_text = ""
        if additional_context:
            additional_context_text = f"\n\n## Additional Context\n{additional_context}"

        rejection_feedback_text = ""
        if rejection_feedback:
            rejection_feedback_text = f"\n\n## Previous Feedback (address these points)\n{rejection_feedback}"

        prompt = f"""You are an expert software project manager and business analyst. Your task is to analyze a SaaS project description and generate comprehensive Epics and User Stories with story points and test cases.

## Project Description
{project_description}
{similar_projects_text}
{additional_context_text}
{rejection_feedback_text}

## Instructions
1. Analyze the project description and identify major features and functionalities
2. Create epics that group related user stories
3. For each epic, generate detailed user stories following the format: "As a [user type], I want to [action] so that [benefit]"
4. Assign story points (1, 2, 3, 5, 8, 13, 21) using Fibonacci sequence for each user story
5. Assign priority (high, medium, low) for each epic and user story
6. Generate comprehensive test cases for each user story
7. Ensure acceptance criteria are clear and testable

## Output Format (JSON)
Return ONLY valid JSON in this exact structure:

{{
  "epics": [
    {{
      "title": "Epic title",
      "description": "Detailed epic description",
      "priority": "high|medium|low",
      "story_points": 50,
      "user_stories": [
        {{
          "title": "As a [user], I want to [action] so that [benefit]",
          "description": "Detailed description of the user story",
          "acceptance_criteria": "Clear, testable acceptance criteria",
          "story_points": 5,
          "priority": "high|medium|low",
          "test_cases": [
            {{
              "id": "TC001",
              "title": "Test case title",
              "description": "What is being tested",
              "steps": [
                "Step 1",
                "Step 2",
                "Step 3"
              ],
              "expected_result": "Expected outcome",
              "priority": "high|medium|low"
            }}
          ]
        }}
      ]
    }}
  ]
}}

Generate comprehensive epics and user stories that cover all aspects of the project. Be thorough and detailed."""

        return prompt


# Singleton instance
_ai_service: AIService | None = None


def get_ai_service() -> AIService:
    """Get or create the AI service singleton"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
