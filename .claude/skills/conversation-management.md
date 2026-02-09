# Conversation Management Skill

Internal tools for managing AI chatbot conversations, message history, and conversation state.

## Overview

This skill provides MCP tools for handling conversation lifecycle management, including creating conversations, storing messages, and retrieving conversation history. These tools are designed for internal use by the AI chatbot system to maintain conversation context and state.

---

## MCP Tools

The following MCP tools provide programmatic access to conversation management functionality:

### create_conversation

**Purpose:** Create a new conversation for a user

**Parameters:**
- `user_id` (string, required): The user identifier

**Returns:**
```json
{
  "conversation_id": "conv_abc123",
  "user_id": "user_123",
  "status": "created",
  "created_at": "2026-02-08T10:30:00Z"
}
```

**Database Operation:** Inserts a new conversation record with a unique conversation_id

**Usage Notes:**
- Automatically called when a user starts a new chat session
- Each conversation is isolated and maintains its own message history
- Conversation IDs are unique and used to group related messages

---

### store_message

**Purpose:** Save a message (user or assistant) to a conversation

**Parameters:**
- `conversation_id` (string, required): The conversation identifier
- `user_id` (string, required): The user identifier
- `role` (string, required): Message role - accepts "user" or "assistant"
- `content` (string, required): The message content/text

**Returns:**
```json
{
  "message_id": "msg_xyz789",
  "conversation_id": "conv_abc123",
  "role": "user",
  "status": "stored",
  "created_at": "2026-02-08T10:31:00Z"
}
```

**Database Operation:** Inserts a new message record linked to the conversation

**Validation:**
- Verifies conversation exists and belongs to the user
- Role must be either "user" or "assistant"
- Content cannot be empty

**Usage Notes:**
- Called after each user input and assistant response
- Messages are stored in chronological order
- Maintains conversation context for AI responses

---

### fetch_conversation_history

**Purpose:** Retrieve all messages for a specific conversation

**Parameters:**
- `conversation_id` (string, required): The conversation identifier
- `user_id` (string, required): The user identifier
- `limit` (integer, optional): Maximum number of messages to return (default: 100)
- `offset` (integer, optional): Number of messages to skip for pagination (default: 0)

**Returns:**
```json
{
  "conversation_id": "conv_abc123",
  "messages": [
    {
      "message_id": "msg_001",
      "role": "user",
      "content": "Hello, how can you help me?",
      "created_at": "2026-02-08T10:30:00Z"
    },
    {
      "message_id": "msg_002",
      "role": "assistant",
      "content": "I can help you manage tasks and answer questions.",
      "created_at": "2026-02-08T10:30:05Z"
    }
  ],
  "total_count": 2,
  "has_more": false
}
```

**Database Operation:** Fetches messages from the messages table filtered by conversation_id and user_id, ordered by created_at

**Security:** Only returns messages for conversations owned by the requesting user

**Usage Notes:**
- Messages are returned in chronological order (oldest first)
- Use limit and offset for pagination with long conversations
- The `has_more` flag indicates if additional messages exist beyond the current page

---

## Data Model

### Conversation Schema
```
conversations:
  - conversation_id (string, primary key)
  - user_id (string, foreign key)
  - created_at (timestamp)
  - updated_at (timestamp)
  - status (string: "active", "archived")
```

### Message Schema
```
messages:
  - message_id (string, primary key)
  - conversation_id (string, foreign key)
  - role (enum: "user", "assistant")
  - content (text)
  - created_at (timestamp)
```

---

## Implementation Notes

### Conversation Lifecycle

**New Conversation Flow:**
```
1. User initiates chat
2. Call create_conversation(user_id)
3. Receive conversation_id
4. Store conversation_id in session/context
5. Use conversation_id for all subsequent messages
```

**Message Exchange Flow:**
```
1. User sends message
2. Call store_message(conversation_id, user_id, "user", content)
3. Fetch conversation history for context
4. Generate AI response
5. Call store_message(conversation_id, user_id, "assistant", response)
6. Return response to user
```

**History Retrieval Flow:**
```
1. User requests conversation history
2. Call fetch_conversation_history(conversation_id, user_id)
3. Display messages in chronological order
4. Use pagination for long conversations
```

### Context Management

- **Context Window:** Fetch recent messages (e.g., last 10-20) to provide context for AI responses
- **Token Limits:** Consider message length when building context to stay within model token limits
- **Summarization:** For very long conversations, consider summarizing older messages

### Performance Considerations

- **Indexing:** Ensure database indexes on conversation_id and user_id for fast queries
- **Caching:** Cache recent conversation history to reduce database queries
- **Pagination:** Always use limit/offset for conversations with many messages
- **Archiving:** Consider archiving old conversations to maintain performance

---

## Error Handling

### create_conversation Errors
- `400 Bad Request` - Missing or invalid user_id
- `500 Internal Server Error` - Database insertion failure

### store_message Errors
- `400 Bad Request` - Missing required parameters or invalid role
- `404 Not Found` - Conversation does not exist
- `403 Forbidden` - User does not own the conversation
- `422 Unprocessable Entity` - Empty content or invalid format

### fetch_conversation_history Errors
- `400 Bad Request` - Invalid conversation_id or user_id
- `403 Forbidden` - User does not own the conversation
- `404 Not Found` - Conversation does not exist

---

## Security Considerations

1. **Ownership Verification:**
   - Always verify user_id matches the conversation owner
   - Prevent users from accessing other users' conversations

2. **Content Validation:**
   - Sanitize message content to prevent injection attacks
   - Enforce maximum message length limits
   - Filter sensitive information before storage

3. **Rate Limiting:**
   - Implement rate limits on message creation to prevent abuse
   - Limit conversation creation per user per time period

4. **Data Privacy:**
   - Encrypt sensitive conversation data at rest
   - Implement data retention policies
   - Provide user data export and deletion capabilities

---

## Integration with AI Chatbot

The conversation management tools integrate with the AI chatbot system to:

- **Maintain Context:** Fetch conversation history to provide context for AI responses
- **Persist State:** Store all user inputs and AI responses for continuity
- **Enable Features:** Support conversation history viewing, search, and export
- **Track Usage:** Monitor conversation patterns and user engagement

**Example Integration:**
```javascript
// Handle incoming user message
async function handleUserMessage(userId, conversationId, userMessage) {
  // Store user message
  await store_message({
    conversation_id: conversationId,
    user_id: userId,
    role: "user",
    content: userMessage
  });

  // Fetch recent history for context
  const history = await fetch_conversation_history({
    conversation_id: conversationId,
    user_id: userId,
    limit: 20
  });

  // Generate AI response with context
  const aiResponse = await generateAIResponse(history.messages);

  // Store AI response
  await store_message({
    conversation_id: conversationId,
    user_id: userId,
    role: "assistant",
    content: aiResponse
  });

  return aiResponse;
}
```
