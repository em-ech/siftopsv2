"""
Chat Service
Handles the RAG (Retrieval-Augmented Generation) pipeline.
Zero-hallucination: The LLM can ONLY reference retrieved products.
"""

from openai import OpenAI
from app.core.config import settings
from app.services.vector_service import vector_service
from app.services.db_service import db_service


SYSTEM_PROMPT = """You are a friendly and knowledgeable shopping assistant for {store_name}.

CRITICAL RULES - YOU MUST FOLLOW THESE:
1. You can ONLY recommend products from the list provided below.
2. If no products match the customer's needs, honestly say "I don't have anything that matches that right now."
3. NEVER make up product names, prices, or features that aren't in the provided data.
4. NEVER reference products from other stores or general knowledge.
5. Be helpful, warm, and conversational - like a great retail salesperson.

When recommending products:
- Mention the product name and price
- Briefly explain why it matches what they're looking for
- If multiple products match, rank them by relevance
- Include the product link so they can purchase

AVAILABLE PRODUCTS FOR THIS QUERY:
{products}

If the products list is empty or none match, politely let the customer know and ask if they'd like to look for something else."""


class ChatService:
    def __init__(self):
        self.openai = OpenAI(api_key=settings.OPENAI_API_KEY)

    def format_products_for_prompt(self, products: list[dict]) -> str:
        """Format retrieved products for the LLM prompt."""
        if not products:
            return "No products found matching this query."

        formatted = []
        for i, p in enumerate(products, 1):
            formatted.append(
                f"{i}. {p['name']}\n"
                f"   Price: ${p['price']}\n"
                f"   Description: {p['description']}\n"
                f"   Categories: {', '.join(p['categories']) if p['categories'] else 'N/A'}\n"
                f"   Link: {p['permalink']}\n"
                f"   In Stock: {p['stock_status'] == 'instock'}"
            )
        return "\n\n".join(formatted)

    async def chat(
        self,
        query: str,
        tenant_id: str,
        store_name: str = "our store",
        conversation_history: list[dict] = None,
        session_id: str = None,
    ) -> dict:
        """
        Main RAG pipeline:
        1. Convert query to vector
        2. Search for relevant products (with tenant filter)
        3. Generate response using only retrieved products
        """
        # Step 1 & 2: Retrieve relevant products (security filter applied)
        products = vector_service.search(
            query=query,
            tenant_id=tenant_id,
            top_k=5,
            score_threshold=0.4,
        )

        # Log the search for analytics
        try:
            db_service.log_search(
                tenant_id=tenant_id,
                query=query,
                results_count=len(products),
                session_id=session_id,
            )
        except Exception:
            pass  # Don't fail chat if logging fails

        # Step 3: Build the prompt with ONLY retrieved products
        products_text = self.format_products_for_prompt(products)
        system_prompt = SYSTEM_PROMPT.format(
            store_name=store_name,
            products=products_text,
        )

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-10:])  # Last 10 messages

        # Add current query
        messages.append({"role": "user", "content": query})

        # Generate response
        response = self.openai.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
        )

        assistant_message = response.choices[0].message.content

        return {
            "response": assistant_message,
            "products": products,
            "products_count": len(products),
        }


# Singleton instance
chat_service = ChatService()
