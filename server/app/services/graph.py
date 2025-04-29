from typing import List, TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.schema import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command, interrupt
from langchain_community.tools.tavily_search import TavilySearchResults

from app.config import settings
from app.models.schemas import AgentState, GradeQuestion, GradeDocument
from app.services.vector_store import get_vector_store

# Initialize tools
tavily_search = TavilySearchResults(max_results=2)

def create_graph():
    """
    Create the LangGraph for the RAG application
    """
    # Initialize language models
    llm = ChatOpenAI(model=settings.LLM_MODEL)
    
    # Get retriever
    retriever = get_vector_store()
    
    # Create RAG prompt template
    rag_template = """Answer the question based on the following context and the Chathistory. Especially take the latest question into consideration. If the context does not have the answer to the question, simply say you don't know

    Chathistory: {history}
    
    Context: {context}
    
    Question: {question}
    """
    rag_prompt = ChatPromptTemplate.from_template(rag_template)
    
    # Create RAG chain
    rag_chain = rag_prompt | llm
    
    # Create memory saver for checkpoints
    checkpointer = MemorySaver()
    
    # Define LangGraph nodes
    def question_rewriter(state: AgentState):
        print(f"Entering question_rewriter with following state: {state}")
    
        # Reset state variables except for 'question' and 'messages'
        state["documents"] = []
        state["on_topic"] = ""
        state["rephrased_question"] = ""
        state["proceed_to_generate"] = False
        state["rephrase_count"] = 0
    
        if "messages" not in state or state["messages"] is None:
            state["messages"] = []
    
        if state["question"] not in state["messages"]:
            state["messages"].append(state["question"])
    
        if len(state["messages"]) > 1:
            conversation = state["messages"][:-1]
            current_question = state["question"].content
            messages = [
                SystemMessage(
                    content="You are a helpful assistant that rephrases the user's question to be a standalone question optimized for retrieval."
                )
            ]
            messages.extend(conversation)
            messages.append(HumanMessage(content=current_question))
            rephrase_prompt = ChatPromptTemplate.from_messages(messages)
            prompt = rephrase_prompt.format()
            response = llm.invoke(prompt)
            better_question = response.content.strip()
            print(f"question_rewriter: Rephrased question: {better_question}")
            state["rephrased_question"] = better_question
        else:
            state["rephrased_question"] = state["question"].content
        return state
    
    def question_classifier(state: AgentState):
        print("Entering question_classifier")
        system_message = SystemMessage(
            content="""You are a classifier that determines whether a user's question or message should be handled by a system design expert.

    Respond with 'Yes' for:
    1. Any system design related questions (architecture, scalability, databases, etc.)
    2. General greetings or casual conversation (like "hi", "hello", "how are you")
    3. Questions about your capabilities or what topics you can discuss
    
    The main topics you're knowledgeable about include:
    - Backend System Design
    - Infrastructure and Scaling
    - Reliability Engineering
    - API and Communication
    - Cloud and Infrastructure
    - Distributed Systems
    - Data Storage
    - Event-Driven Architecture
    - Security Architecture
    - Observability
    - Performance Engineering
    - Real-world Applications

    Respond with 'No' only for:
    1. Questions completely unrelated to system design or general conversation
    2. Questions about unrelated topics (like history, biology, sports)
    3. Inappropriate or offensive content
    """
        )
    
        human_message = HumanMessage(
            content=f"User question: {state['rephrased_question']}"
        )
        grade_prompt = ChatPromptTemplate.from_messages([system_message, human_message])
        structured_llm = llm.with_structured_output(GradeQuestion)
        grader_llm = grade_prompt | structured_llm
        result = grader_llm.invoke({})
        state["on_topic"] = result.score.strip()
        print(f"question_classifier: on_topic = {state['on_topic']}")
        return state
    
    def on_topic_router(state: AgentState):
        print("Entering on_topic_router")
        on_topic = state.get("on_topic", "").strip().lower()
        if on_topic == "yes":
            print("Routing to retrieve")
            return "retrieve"
        else:
            print("Routing to off_topic_response")
            return "off_topic_response"
    
    def retrieve(state: AgentState):
        print("Entering retrieve")
        documents = retriever.invoke(state["rephrased_question"])
        print(f"retrieve: Retrieved {len(documents)} documents")
        state["documents"] = documents
        return state
    
    def retrieval_grader(state: AgentState):
        print("Entering retrieval_grader")
        system_message = SystemMessage(
            content="""You are a grader assessing the relevance of a retrieved document to a user question.
    Only answer with 'Yes' or 'No'.
    
    If the document contains information relevant to the user's question, respond with 'Yes'.
    Otherwise, respond with 'No'."""
        )
    
        structured_llm = llm.with_structured_output(GradeDocument)
    
        relevant_docs = []
        for doc in state["documents"]:
            human_message = HumanMessage(
                content=f"User question: {state['rephrased_question']}\n\nRetrieved document:\n{doc.page_content}"
            )
            grade_prompt = ChatPromptTemplate.from_messages([system_message, human_message])
            grader_llm = grade_prompt | structured_llm
            result = grader_llm.invoke({})
            print(
                f"Grading document: {doc.page_content[:30]}... Result: {result.score.strip()}"
            )
            if result.score.strip().lower() == "yes":
                relevant_docs.append(doc)
        state["documents"] = relevant_docs
        state["proceed_to_generate"] = len(relevant_docs) > 0
        print(f"retrieval_grader: proceed_to_generate = {state['proceed_to_generate']}")
        return state
    
    def proceed_router(state: AgentState):
        print("Entering proceed_router")
        rephrase_count = state.get("rephrase_count", 0)
        if state.get("proceed_to_generate", False):
            print("Routing to generate_answer")
            return "generate_answer"
        elif rephrase_count >= 1:
            print("Maximum rephrase attempts reached. Cannot find relevant documents.")
            return "cannot_answer"
        else:
            print("Routing to refine_question")
            return "refine_question"
        
    def refine_question(state: AgentState):
        print("Entering refine_question")
        rephrase_count = state.get("rephrase_count", 0)
        if rephrase_count >= 2:
            print("Maximum rephrase attempts reached")
            return state
        question_to_refine = state["rephrased_question"]
        system_message = SystemMessage(
            content="""You are a helpful assistant that slightly refines the user's question to improve retrieval results.
    Provide a slightly adjusted version of the question."""
        )
        human_message = HumanMessage(
            content=f"Original question: {question_to_refine}\n\nProvide a slightly refined question."
        )
        refine_prompt = ChatPromptTemplate.from_messages([system_message, human_message])
        prompt = refine_prompt.format()
        response = llm.invoke(prompt)
        refined_question = response.content.strip()
        print(f"refine_question: Refined question: {refined_question}")
        state["rephrased_question"] = refined_question
        state["rephrase_count"] = rephrase_count + 1
        return state
    
    def generate_answer(state: AgentState):
        print("Entering generate_answer")
        if "messages" not in state or state["messages"] is None:
            raise ValueError("State must include 'messages' before generating an answer.")
    
        history = state["messages"]
        documents = state["documents"]
        rephrased_question = state["rephrased_question"]
    
        response = rag_chain.invoke(
            {"history": history, "context": documents, "question": rephrased_question}
        )
    
        generation = response.content.strip()
    
        state["messages"].append(AIMessage(content=generation))
        print(f"generate_answer: Generated response: {generation}")
        return state
    
    def research_node(state: AgentState): 
        print("Entering the research node")
        # Create the research agent
        research_agent = create_react_agent(
            llm,
            tools=[tavily_search],
            state_modifier="""
            You are a research assistant helping to answer questions that couldn't be sufficiently answered using information from System Design books, particularly "System Design Interview" by Alex Xu and "Designing Data-Intensive Applications".

            INSTRUCTIONS:
            1. The user asked a question that our database couldn't answer with information from our system design knowledge base.
            2. Use the Tavily search tool to find relevant and accurate information related to the question.
            3. Focus on system design patterns, architectural solutions, and engineering best practices.
            4. Provide complete, technical answers based on your research.
            5. Cite sources where appropriate.
            6. When possible, include real-world examples of how companies have implemented similar solutions.

            Your goal is to provide helpful, practical information when our primary knowledge base is insufficient.
        """
        )
    
        result = research_agent.invoke(state)
    
        content = result["messages"][-1].content
        state["messages"].append(AIMessage(content=content))

        print(content, "research_node content") 
    
        return state
    
    def cannot_answer(state: AgentState) -> Command[Literal["research_node", END]]:
        print("Entering cannot_answer")
        # Directly proceed to research_node without asking for approval
        return Command(goto="research_node")
    
    def off_topic_response(state: AgentState):
        print("Entering off_topic_response")
        if "messages" not in state or state["messages"] is None:
            state["messages"] = []
        state["messages"].append(AIMessage(content="I'm sorry! I cannot answer this question as it doesn't appear to be related to system design topics, distributed systems, or software architecture principles covered in System Design books like Alex Xu's 'System Design Interview' or 'Designing Data-Intensive Applications'."))
        return state
    
    # Create the StateGraph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("question_rewriter", question_rewriter)
    workflow.add_node("question_classifier", question_classifier)
    workflow.add_node("off_topic_response", off_topic_response)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("retrieval_grader", retrieval_grader)
    workflow.add_node("generate_answer", generate_answer)
    workflow.add_node("refine_question", refine_question)
    workflow.add_node("cannot_answer", cannot_answer)
    workflow.add_node("research_node", research_node)
    
    # Add edges
    workflow.add_edge("question_rewriter", "question_classifier")
    workflow.add_conditional_edges(
        "question_classifier",
        on_topic_router,
        {
            "retrieve": "retrieve",
            "off_topic_response": "off_topic_response",
        },
    )
    workflow.add_edge("retrieve", "retrieval_grader")
    workflow.add_conditional_edges(
        "retrieval_grader",
        proceed_router,
        {
            "generate_answer": "generate_answer",
            "refine_question": "refine_question",
            "cannot_answer": "cannot_answer",  
        },
    )
    workflow.add_edge("refine_question", "retrieve")
    workflow.add_edge("generate_answer", END)
    workflow.add_edge("cannot_answer", "research_node")
    workflow.add_edge("research_node", END)
    workflow.add_edge("off_topic_response", END)
    workflow.set_entry_point("question_rewriter")
    
    # Compile the graph
    graph = workflow.compile(checkpointer=checkpointer)
    
    return graph