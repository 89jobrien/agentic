from src.agentic.models import Message, ChatRequest, ChatResponse, ChatSession, Embedding, CodeChunk

def test_message_model():
    msg = Message(role="user", content="hi")
    assert msg.role == "user"
    assert msg.content == "hi"

def test_chat_request_model():
    req = ChatRequest(message="hello", session_id="abc")
    assert req.message == "hello"
    assert req.session_id == "abc"

def test_chat_response_model(sample_message):
    resp = ChatResponse(session_id="sid", reply="ok", history=[sample_message])
    assert resp.session_id == "sid"
    assert resp.reply == "ok"
    assert resp.history[0].role == "user"

def test_chat_session_model(sample_message):
    sess = ChatSession(session_id="sid", messages=[sample_message])
    assert sess.session_id == "sid"
    assert sess.messages[0].content == "Hello, world!"

def test_embedding_model():
    emb = Embedding(vector=[1.0, 2.0])
    assert emb.vector == [1.0, 2.0]

def test_code_chunk_model(sample_embedding):
    chunk = CodeChunk(file_path="foo.py", chunk="def x(): pass", embedding=sample_embedding)
    assert chunk.file_path == "foo.py"
    assert chunk.embedding.vector == [0.1, 0.2, 0.3]
