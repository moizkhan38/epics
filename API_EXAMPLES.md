# API Examples

Complete examples for using the Epics Generator API.

## Authentication

All API requests (except health checks) require authentication via API key in the header:

```bash
X-API-Key: your-api-key-here
```

## Example 1: Complete Workflow

### Step 1: Generate Epics for a New Project

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev_key_123456789" \
  -d '{
    "project_name": "E-commerce Platform",
    "project_description": "A modern e-commerce platform for selling physical products online. Features include product catalog, shopping cart, checkout with multiple payment methods, order management, customer accounts, reviews and ratings, inventory management, and admin dashboard. Target audience: small to medium businesses.",
    "additional_context": "Must support Stripe and PayPal payments. Mobile-first design required."
  }'
```

**Response:**
```json
{
  "project_id": 1,
  "generation_history_id": 1,
  "version": 1,
  "status": "pending",
  "similar_projects": [
    {
      "project_id": 3,
      "name": "Online Store Builder",
      "description": "Platform for creating online stores...",
      "similarity_score": 0.82
    }
  ],
  "epics": [
    {
      "id": 1,
      "project_id": 1,
      "generation_history_id": 1,
      "title": "User Authentication and Account Management",
      "description": "Implement secure user registration, login, password management, and profile management",
      "story_points": 34,
      "priority": "high",
      "is_approved": false,
      "user_stories": [
        {
          "id": 1,
          "epic_id": 1,
          "title": "As a customer, I want to register an account so that I can make purchases and track orders",
          "description": "Users should be able to create an account with email and password",
          "acceptance_criteria": "- User can enter email, password, and confirm password\n- Email validation is performed\n- Password strength requirements are enforced\n- Confirmation email is sent\n- User is redirected to login after registration",
          "story_points": 5,
          "priority": "high",
          "is_approved": false,
          "test_cases": {
            "test_cases": [
              {
                "id": "TC001",
                "title": "Successful user registration",
                "description": "Test the complete registration flow with valid data",
                "steps": [
                  "Navigate to registration page",
                  "Enter valid email address",
                  "Enter strong password",
                  "Confirm password",
                  "Submit form"
                ],
                "expected_result": "User account is created, confirmation email sent, redirected to login",
                "priority": "high"
              },
              {
                "id": "TC002",
                "title": "Registration with duplicate email",
                "description": "Test registration with already registered email",
                "steps": [
                  "Navigate to registration page",
                  "Enter email that already exists",
                  "Enter password",
                  "Submit form"
                ],
                "expected_result": "Error message displayed: 'Email already registered'",
                "priority": "high"
              }
            ]
          },
          "created_at": "2026-01-11T10:00:00Z",
          "updated_at": "2026-01-11T10:00:00Z"
        }
      ],
      "created_at": "2026-01-11T10:00:00Z",
      "updated_at": "2026-01-11T10:00:00Z"
    },
    {
      "id": 2,
      "title": "Product Catalog and Search",
      "description": "Enable customers to browse products, search, filter, and view details",
      "story_points": 21,
      "priority": "high",
      "user_stories": [
        {
          "id": 5,
          "title": "As a customer, I want to browse products by category so that I can find what I need",
          "description": "Customers should see organized product categories",
          "acceptance_criteria": "- Categories are displayed prominently\n- Products are grouped by category\n- Category navigation is intuitive\n- Product count shown per category",
          "story_points": 5,
          "priority": "high",
          "test_cases": {
            "test_cases": [
              {
                "id": "TC010",
                "title": "Browse products by category",
                "description": "Test category navigation",
                "steps": [
                  "Navigate to home page",
                  "Click on a category",
                  "Verify products are filtered"
                ],
                "expected_result": "Only products from selected category are displayed",
                "priority": "high"
              }
            ]
          }
        }
      ]
    }
  ],
  "message": "Epics and user stories generated successfully. Please review and approve."
}
```

### Step 2: Review and Reject (if needed)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/approve" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev_key_123456789" \
  -d '{
    "generation_history_id": 1,
    "is_approved": false,
    "rejection_reason": "Need more detailed user stories for the payment integration. Please add stories for handling payment failures and refunds."
  }'
```

**Response:**
```json
{
  "message": "Generation rejected. Use /regenerate endpoint to create a new version.",
  "generation_history_id": 1
}
```

### Step 3: Regenerate with Feedback

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/regenerate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev_key_123456789" \
  -d '{
    "project_id": 1,
    "generation_history_id": 1,
    "rejection_reason": "Need more detailed user stories for the payment integration",
    "additional_instructions": "Add comprehensive stories for payment failures, retries, refunds, and error handling. Include stories for both Stripe and PayPal."
  }'
```

**Response:**
```json
{
  "project_id": 1,
  "generation_history_id": 2,
  "version": 2,
  "status": "pending",
  "similar_projects": [...],
  "epics": [
    {
      "id": 10,
      "title": "Payment Processing and Transaction Management",
      "description": "Complete payment integration with Stripe and PayPal, including error handling, retries, and refunds",
      "story_points": 55,
      "priority": "high",
      "user_stories": [
        {
          "id": 50,
          "title": "As a customer, I want to pay with credit card via Stripe so that I can complete my purchase",
          "description": "Integrate Stripe for credit card payments",
          "story_points": 8,
          "priority": "high"
        },
        {
          "id": 51,
          "title": "As a customer, I want to receive a refund if payment fails after being charged",
          "description": "Automatic refund handling for failed orders",
          "story_points": 5,
          "priority": "high"
        }
      ]
    }
  ],
  "message": "Epics regenerated successfully. Please review and approve."
}
```

### Step 4: Approve

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/approve" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev_key_123456789" \
  -d '{
    "generation_history_id": 2,
    "is_approved": true
  }'
```

**Response:**
```json
{
  "message": "Generation approved successfully",
  "generation_history_id": 2,
  "epics_count": 8
}
```

## Example 2: View Project History

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/history/1" \
  -H "X-API-Key: dev_key_123456789"
```

**Response:**
```json
[
  {
    "id": 2,
    "project_id": 1,
    "version": 2,
    "status": "approved",
    "similar_projects": [...],
    "rejection_reason": null,
    "created_at": "2026-01-11T10:15:00Z"
  },
  {
    "id": 1,
    "project_id": 1,
    "version": 1,
    "status": "rejected",
    "similar_projects": [...],
    "rejection_reason": "Need more detailed user stories for the payment integration",
    "created_at": "2026-01-11T10:00:00Z"
  }
]
```

## Example 3: List All Projects

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/projects?page=1&page_size=10" \
  -H "X-API-Key: dev_key_123456789"
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "E-commerce Platform",
      "description": "A modern e-commerce platform...",
      "created_at": "2026-01-11T10:00:00Z",
      "updated_at": "2026-01-11T10:00:00Z"
    },
    {
      "id": 2,
      "name": "CRM System",
      "description": "Customer relationship management...",
      "created_at": "2026-01-11T09:00:00Z",
      "updated_at": "2026-01-11T09:00:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

## Example 4: Python Client

```python
import requests
import json

class EpicsGeneratorClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

    def generate_epics(self, project_name: str, description: str, context: str = None):
        """Generate epics and user stories for a new project"""
        payload = {
            "project_name": project_name,
            "project_description": description,
            "additional_context": context
        }

        response = requests.post(
            f"{self.base_url}/api/v1/generate",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def approve_generation(self, generation_history_id: int):
        """Approve a generation"""
        payload = {
            "generation_history_id": generation_history_id,
            "is_approved": True
        }

        response = requests.post(
            f"{self.base_url}/api/v1/approve",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def reject_and_regenerate(self, project_id: int, history_id: int, reason: str, instructions: str = None):
        """Reject and regenerate with feedback"""
        # First reject
        reject_payload = {
            "generation_history_id": history_id,
            "is_approved": False,
            "rejection_reason": reason
        }

        requests.post(
            f"{self.base_url}/api/v1/approve",
            headers=self.headers,
            json=reject_payload
        )

        # Then regenerate
        regen_payload = {
            "project_id": project_id,
            "generation_history_id": history_id,
            "rejection_reason": reason,
            "additional_instructions": instructions
        }

        response = requests.post(
            f"{self.base_url}/api/v1/regenerate",
            headers=self.headers,
            json=regen_payload
        )
        response.raise_for_status()
        return response.json()

    def get_project_history(self, project_id: int):
        """Get generation history for a project"""
        response = requests.get(
            f"{self.base_url}/api/v1/history/{project_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()


# Usage example
if __name__ == "__main__":
    client = EpicsGeneratorClient(
        base_url="http://localhost:8000",
        api_key="dev_key_123456789"
    )

    # Generate epics
    result = client.generate_epics(
        project_name="Task Manager",
        description="A simple task management application for personal use",
        context="Should support priorities, due dates, and categories"
    )

    print(f"Generated {len(result['epics'])} epics")
    print(f"Project ID: {result['project_id']}")
    print(f"Generation ID: {result['generation_history_id']}")

    # Review the epics...
    # If satisfied, approve
    approval = client.approve_generation(result['generation_history_id'])
    print(f"Approved: {approval['message']}")
```

## Example 5: JavaScript/TypeScript Client

```typescript
interface GenerationRequest {
  project_name: string;
  project_description: string;
  additional_context?: string;
}

interface GenerationResponse {
  project_id: number;
  generation_history_id: number;
  version: number;
  status: string;
  similar_projects: any[];
  epics: any[];
  message: string;
}

class EpicsGeneratorClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string, apiKey: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  private async request<T>(
    endpoint: string,
    method: string = 'GET',
    body?: any
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey,
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  async generateEpics(
    projectName: string,
    description: string,
    context?: string
  ): Promise<GenerationResponse> {
    return this.request<GenerationResponse>('/api/v1/generate', 'POST', {
      project_name: projectName,
      project_description: description,
      additional_context: context,
    });
  }

  async approveGeneration(generationHistoryId: number): Promise<any> {
    return this.request('/api/v1/approve', 'POST', {
      generation_history_id: generationHistoryId,
      is_approved: true,
    });
  }

  async getProjectHistory(projectId: number): Promise<any[]> {
    return this.request(`/api/v1/history/${projectId}`);
  }
}

// Usage
const client = new EpicsGeneratorClient(
  'http://localhost:8000',
  'dev_key_123456789'
);

async function main() {
  const result = await client.generateEpics(
    'Fitness Tracker',
    'A mobile app for tracking workouts, nutrition, and progress',
    'Should integrate with wearables and provide analytics'
  );

  console.log(`Generated ${result.epics.length} epics`);

  // Approve if satisfied
  await client.approveGeneration(result.generation_history_id);
}
```

## Error Handling Examples

### Invalid API Key
```bash
curl -X GET "http://localhost:8000/api/v1/projects" \
  -H "X-API-Key: invalid_key"
```

**Response (401):**
```json
{
  "detail": "Invalid API key"
}
```

### Validation Error
```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev_key_123456789" \
  -d '{
    "project_name": "Test",
    "project_description": "Too short"
  }'
```

**Response (422):**
```json
{
  "error": "validation_error",
  "message": "Invalid request data",
  "details": [
    {
      "type": "string_too_short",
      "loc": ["body", "project_description"],
      "msg": "String should have at least 50 characters",
      "input": "Too short"
    }
  ]
}
```

### Resource Not Found
```bash
curl -X GET "http://localhost:8000/api/v1/projects/999" \
  -H "X-API-Key: dev_key_123456789"
```

**Response (404):**
```json
{
  "detail": "Project 999 not found"
}
```

## Tips for Best Results

1. **Detailed Descriptions**: Provide comprehensive project descriptions for better epic generation
2. **Specify Context**: Include technical requirements, target audience, and constraints
3. **Iterate**: Use the regeneration feature to refine results
4. **Review Test Cases**: The generated test cases can help validate your acceptance criteria
5. **Story Points**: Use the generated story points as a starting point for sprint planning
