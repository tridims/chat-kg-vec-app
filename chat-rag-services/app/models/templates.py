# ======================================================
# AI Prompt Templates
# ======================================================

QUESTION_TRANSFORM_TEMPLATE = "Given the below conversation, generate a search query to look up in order to get information relevant to the conversation. Only respond with the query, nothing else."

CHAT_SYSTEM_TEMPLATE = """
You are an AI-powered question-answering agent. Your task is to provide accurate and comprehensive responses to user queries based on the given context, chat history, and available resources.

### Response Guidelines:
1. **Direct Answers**: Provide clear and thorough answers to the user's queries without headers unless requested. Avoid speculative responses.
2. **Utilize History and Context**: Leverage relevant information from previous interactions, the current user input, and the context provided below.
3. **No Greetings in Follow-ups**: Start with a greeting in initial interactions. Avoid greetings in subsequent responses unless there's a significant break or the chat restarts.
4. **Admit Unknowns**: Clearly state if an answer is unknown. Avoid making unsupported statements.
5. **Avoid Hallucination**: Only provide information based on the context provided. Do not invent information.
6. **Response Length**: Keep responses concise and relevant. Aim for clarity and completeness within 4-5 sentences unless more detail is requested.
7. **Tone and Style**: Maintain a professional and informative tone. Be friendly and approachable.
8. **Error Handling**: If a query is ambiguous or unclear, ask for clarification rather than providing a potentially incorrect answer.
9. **Fallback Options**: If the required information is not available in the provided context, provide a polite and helpful response. Example: "I don't have that information right now." or "I'm sorry, but I don't have that information. Is there something else I can help with?"
10. **Context Availability**: If the context is empty, do not provide answers based solely on internal knowledge. Instead, respond appropriately by indicating the lack of information.


**IMPORTANT** : DO NOT ANSWER FROM YOUR KNOWLEDGE BASE. USE THE BELOW CONTEXT

### Context:
<context>
{context}
</context>

### Example Responses:
User: Hi 
AI Response: 'Hello there! How can I assist you today?'

User: "What is Langchain?"
AI Response: "Langchain is a framework that enables the development of applications powered by large language models, such as chatbots. It simplifies the integration of language models into various applications by providing useful tools and components."

User: "Can you explain how to use memory management in Langchain?"
AI Response: "Langchain's memory management involves utilizing built-in mechanisms to manage conversational context effectively. It ensures that the conversation remains coherent and relevant by maintaining the history of interactions and using it to inform responses."

User: "I need help with PyCaret's classification model."
AI Response: "PyCaret simplifies the process of building and deploying machine learning models. For classification tasks, you can use PyCaret's setup function to prepare your data. After setup, you can compare multiple models to find the best one, and then fine-tune it for better performance."

User: "What can you tell me about the latest realtime trends in AI?"
AI Response: "I don't have that information right now. Is there something else I can help with?"

Note: This system does not generate answers based solely on internal knowledge. It answers from the information provided in the user's current and previous inputs, and from the context.
"""

# ======================================================
# Vector Graph Search Query
# ======================================================

VECTOR_GRAPH_SEARCH_ENTITY_LIMIT = 25
VECTOR_GRAPH_SEARCH_QUERY = """
WITH node as chunk, score
// find the document of the chunk
MATCH (chunk)-[:PART_OF]->(d:Document)

// aggregate chunk-details
WITH d, collect(DISTINCT {{chunk: chunk, score: score}}) AS chunks, avg(score) as avg_score
// fetch entities
CALL {{ WITH chunks
UNWIND chunks as chunkScore
WITH chunkScore.chunk as chunk
// entities connected to the chunk
// todo only return entities that are actually in the chunk, remember we connect all extracted entities to all chunks
// todo sort by relevancy (embeddding comparision?) cut off after X (e.g. 25) nodes?
OPTIONAL MATCH (chunk)-[:HAS_ENTITY]->(e)
WITH e, count(*) as numChunks
ORDER BY numChunks DESC LIMIT {no_of_entites}
// depending on match to query embedding either 1 or 2 step expansion
WITH CASE WHEN true // vector.similarity.cosine($embedding, e.embedding ) <= 0.95
THEN
collect {{ OPTIONAL MATCH path=(e)(()-[rels:!HAS_ENTITY&!PART_OF]-()){{0,1}}(:!Chunk&!Document) RETURN path }}
ELSE
collect {{ OPTIONAL MATCH path=(e)(()-[rels:!HAS_ENTITY&!PART_OF]-()){{0,2}}(:!Chunk&!Document) RETURN path }}
END as paths, e
WITH apoc.coll.toSet(apoc.coll.flatten(collect(distinct paths))) as paths, collect(distinct e) as entities
// de-duplicate nodes and relationships across chunks
RETURN collect{{ unwind paths as p unwind relationships(p) as r return distinct r}} as rels,
collect{{ unwind paths as p unwind nodes(p) as n return distinct n}} as nodes, entities
}}

// generate metadata and text components for chunks, nodes and relationships
WITH d, avg_score,
     [c IN chunks | c.chunk.text] AS texts,
     [c IN chunks | {{id: c.chunk.id, score: c.score}}] AS chunkdetails,
  apoc.coll.sort([n in nodes |

coalesce(apoc.coll.removeAll(labels(n),['__Entity__'])[0],"") +":"+
n.id + (case when n.description is not null then " ("+ n.description+")" else "" end)]) as nodeTexts,
	apoc.coll.sort([r in rels
    // optional filter if we limit the node-set
    // WHERE startNode(r) in nodes AND endNode(r) in nodes
  |
coalesce(apoc.coll.removeAll(labels(startNode(r)),['__Entity__'])[0],"") +":"+
startNode(r).id +
" " + type(r) + " " +
coalesce(apoc.coll.removeAll(labels(endNode(r)),['__Entity__'])[0],"") +":" + endNode(r).id
]) as relTexts
, entities
// combine texts into response-text

WITH d, avg_score,chunkdetails,
"Text Content:\\n" +
apoc.text.join(texts,"\\n----\\n") +
"\\n----\\nEntities:\\n"+
apoc.text.join(nodeTexts,"\\n") +
"\\n----\\nRelationships:\\n" +
apoc.text.join(relTexts,"\\n")

as text,entities

RETURN text, avg_score as score, {{length:size(text), source: COALESCE(d.file_name), chunkdetails: chunkdetails}} AS metadata
""".format(
    no_of_entites=VECTOR_GRAPH_SEARCH_ENTITY_LIMIT
)

# RETURN text, avg_score as score, {{length:size(text), source: COALESCE( CASE WHEN d.url CONTAINS "None" THEN d.file_name ELSE d.url END, d.file_name), chunkdetails: chunkdetails}} AS metadata
