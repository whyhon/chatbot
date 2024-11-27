import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("AI-Powered Multi-Agent Chatbot")

# Define a centralized product knowledge base (editable)
PRODUCT_KNOWLEDGE = {
    "Epson T3 SCARA Robot": {
        "price": "$8,000",
        "features": [
            "Compact design",
            "Easy integration",
            "High-speed assembly"
        ],
        "link": "https://catalog.fa.com.my/Industrial-Robots",
        "competitor": {
            "name": "ABB IRB 910SC",
            "price": "$9,500",
            "comparison": "Epson T3 is more cost-effective and provides similar performance for standard tasks."
        }
    },
    # Add more products here...
}

# Define agents (editable)
if "agents" not in st.session_state:
    st.session_state.agents = {
        "default": {
            "role": "default",
            "description": "Routes queries to the appropriate agent.",
            "content": "Hello! I will help direct your query to the right expert."
        },
        "sales": {
            "role": "sales",
            "description": "Handles inquiries about FA Controls' robotics products and pricing.",
            "content": (
                "Welcome! I can assist with product information, pricing, and comparisons. Here's an example:\n\n"
                "**Epson T3 SCARA Robot**:\n- Price: $8,000 (base model)\n- Features: Compact design, easy integration, high-speed assembly.\n"
                "For more details, visit: [Epson Robots](https://catalog.fa.com.my/Industrial-Robots).\n\n"
                "Let me know if you need help with other products or customized pricing!"
            )
        },
        "support": {
            "role": "support",
            "description": "Provides technical support for troubleshooting.",
            "content": "I'm here to assist with troubleshooting and technical support. Please describe your issue."
        },
        "faq": {
            "role": "faq",
            "description": "Answers FAQs about pricing policies, shipping, and product comparisons.",
            "content": (
                "Our pricing policies are designed to offer competitive value. For competitor comparisons, "
                "like ABB vs Epson T3, visit [Product Info](https://catalog.fa.com.my/Industrial-Robots)."
            )
        },
        "escalation": {
            "role": "escalation",
            "description": "Handles complex queries or escalations to human representatives.",
            "content": (
                "I'm unable to assist further. Please contact Jacky Lim via WhatsApp using this link: "
                "[Contact Jacky Lim](http://wa.me/60122152688)."
            )
        },
    }

# Function to generate product-specific responses
def generate_product_response(prompt, product_knowledge):
    for product, details in product_knowledge.items():
        if product.lower() in prompt.lower():
            features = ", ".join(details["features"])
            return (
                f"The **{product}**:\n"
                f"- Price: {details['price']}\n"
                f"- Features: {features}\n"
                f"For more details: [Link]({details['link']})\n"
                f"Competitor: {details['competitor']['name']} "
                f"at {details['competitor']['price']}.\n"
                f"Comparison: {details['competitor']['comparison']}"
            )
    return "I'm sorry, I couldn't find the product you're asking about. Can you provide more details?"

# Function to determine the agent using OpenAI
def determine_agent_with_ai(prompt):
    roles = {key: agent["role"] for key, agent in st.session_state.agents.items()}
    role_descriptions = "\n".join(
        [f"- {key}: {desc['description']}" for key, desc in st.session_state.agents.items()]
    )

    # Prepare OpenAI prompt
    openai_prompt = (
        f"Classify the following query into one of the predefined roles below:\n\n"
        f"Query: {prompt}\n\n"
        f"Roles:\n{role_descriptions}\n\n"
        f"Choose the best role for the query. Respond ONLY with the role key: default, sales, support, faq, or escalation."
    )

    try:
        # Use OpenAI to determine the agent
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": openai_prompt},
            ],
        )

        # Corrected way to access the response
        message_content = response.choices[0].message.content.strip().lower()

        # Check for product-specific query first
        product_response = generate_product_response(prompt, PRODUCT_KNOWLEDGE)
        if product_response != "I'm sorry, I couldn't find the product you're asking about. Can you provide more details?":
            return "sales"

        # Validate the returned role
        if message_content in roles:
            return message_content
        
        # Fallback to default if no valid role found
        return "default"

    except Exception as e:
        st.error(f"Error determining agent: {e}")
        return "default"

# Chat messages history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input box for the user's query
if prompt := st.chat_input("Ask me anything!"):
    # Append user message to the conversation
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Determine agent using AI
    selected_agent_key = determine_agent_with_ai(prompt)
    agent = st.session_state.agents[selected_agent_key]

    # Generate agent response
    with st.chat_message("assistant"):
        st.markdown(agent["content"])

    # Save assistant response in session history
    st.session_state.messages.append({"role": "assistant", "content": agent["content"]})