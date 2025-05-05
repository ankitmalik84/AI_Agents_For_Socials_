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
from pydantic import BaseModel


from app.config import settings
from app.models.schemas import AgentState, GradeQuestion, GradeDocument, WorkflowType, ConversationResponse, OffTopicResponse
from app.services.vector_store import get_vector_store

# Initialize tools
tavily_search = TavilySearchResults(max_results=5)



def create_graph():
    """
    Create the LangGraph for the RAG application with specialized workflows
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
    
   
    def workflow_manager(state: AgentState):
        """
        Initial manager that determines which workflow to follow
        """
        print("Entering workflow_manager")
        
        # Initialize state if needed
        if not isinstance(state, dict):
            state = {}
        
        # Initialize workflow_type if not present
        if 'workflow_type' not in state:
            state['workflow_type'] = ''
        
        system_message = SystemMessage(
            content="""You are a workflow manager that classifies user messages into specific categories.
            You must respond with exactly one of these categories:
            - "system_design" - For technical questions about system design, architecture, scalability, etc.
            - "casual" - For general greetings, casual conversation, or questions about identity
            - "off_topic" - For questions completely unrelated to system design or casual conversation
            
            Base your decision on the following criteria:
            - System Design: Technical questions about architecture, scalability, databases, distributed systems
            - Casual: Greetings, identity questions, general conversation about AI or the assistant
            - Off Topic: Questions about unrelated topics or nonsensical input
            """
        )
        
        human_message = HumanMessage(
            content=f"Classify this message: {state['question'].content}"
        )
        
        classification_prompt = ChatPromptTemplate.from_messages([system_message, human_message])
        structured_llm = llm.with_structured_output(WorkflowType)
        grader_llm = classification_prompt | structured_llm
        result = grader_llm.invoke({})
        
        
        state['workflow_type'] = result.type
        return state

    def workflow_router(state: AgentState):
        """
        Routes to specific workflow based on classification
        """
        workflow_type = state.get('workflow_type', '')
        print(f"workflow_router: Received type: '{workflow_type}'")
        print(f"workflow_router: Type comparison: {workflow_type == 'casual'}")
        
        if workflow_type == 'system_design':
            return "system_design_workflow"
        elif workflow_type == 'casual':
            return "casual_workflow"
        else:
            return "off_topic_workflow"

    def casual_conversation_handler(state: AgentState):
        """
        Handles casual conversations and identity questions
        """
        print("Entering casual_conversation_handler")
        if "messages" not in state:
            state["messages"] = []
        
        system_prompt = """You are a friendly AI assistant specialized in system design, created by Ankit Malik.
        While your main expertise is in system design, you can engage in casual conversation while maintaining your identity.
        
        - Be friendly and professional
        - Mention your system design expertise when appropriate
        - If the conversation allows, try to steer it towards technical discussions
        """
        
        human_message = HumanMessage(content=state['question'].content)
        conversation_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            human_message
        ])
        
        structured_llm = llm.with_structured_output(ConversationResponse)
        grader_llm = conversation_prompt | structured_llm
        result = grader_llm.invoke({})
        state["messages"].append(AIMessage(content=result.response))
        return state

    def off_topic_handler(state: AgentState):
        """
        Handles completely off-topic questions
        """
        print("Entering off_topic_handler")
        if "messages" not in state:
            state["messages"] = []
        
        system_prompt = """You are a focused system design AI assistant.
        Politely explain that you're specialized in system design and technical architecture discussions.
        Suggest redirecting the conversation to system design topics.
        """
        
        human_message = HumanMessage(content=state['question'].content)
        off_topic_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            human_message
        ])
        
        structured_llm = llm.with_structured_output(OffTopicResponse)
        grader_llm = off_topic_prompt | structured_llm
        result = grader_llm.invoke({})
        state["messages"].append(AIMessage(content=result.response))
        return state

    # Create the StateGraph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("workflow_manager", workflow_manager)
    workflow.add_node("question_rewriter", question_rewriter)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("retrieval_grader", retrieval_grader)
    workflow.add_node("generate_answer", generate_answer)
    workflow.add_node("refine_question", refine_question)
    workflow.add_node("cannot_answer", cannot_answer)
    workflow.add_node("research_node", research_node)
    workflow.add_node("casual_conversation_handler", casual_conversation_handler)
    workflow.add_node("off_topic_handler", off_topic_handler)

    # Add conditional edges for workflow routing
    workflow.add_conditional_edges(
        "workflow_manager",
        workflow_router,
        {
            "system_design_workflow": "question_rewriter",
            "casual_workflow": "casual_conversation_handler",
            "off_topic_workflow": "off_topic_handler"
        },
    )

    # System design workflow edges - simplified
    workflow.add_edge("question_rewriter", "retrieve")
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
    
    # Direct endings for other workflows
    workflow.add_edge("casual_conversation_handler", END)
    workflow.add_edge("off_topic_handler", END)
    
    # Set entry point
    workflow.set_entry_point("workflow_manager")
    
    # Compile the graph
    graph = workflow.compile(checkpointer=checkpointer)
    
    return graph