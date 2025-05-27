import os
import sys
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from .db.database import db
from .db.models import Conversation, Message

load_dotenv()


class ChatBot:
    def __init__(self, conversation_id: Optional[int] = None) -> None:
        api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("Error: OPENROUTER_API_KEY not found in .env file")
            sys.exit(1)

        self.client: OpenAI = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

        self.model: str = "qwen/qwen-2.5-72b-instruct"
        self.messages: List[Dict[str, str]] = []
        self.conversation_id: Optional[int] = conversation_id
        self.session: Optional[Session] = None

        self._initialize_conversation()

    def _initialize_conversation(self) -> None:
        session_gen = db.get_session()
        self.session = next(session_gen)

        if self.conversation_id:
            conversation = self.session.query(Conversation).filter_by(
                id=self.conversation_id
            ).first()

            if conversation:
                print(f"Resuming conversation: {conversation.title or f'Conversation {conversation.id}'}")
                for message in conversation.messages:
                    self.messages.append({
                        "role": message.role,
                        "content": message.content
                    })
            else:
                print(f"Conversation {self.conversation_id} not found. Starting new conversation.")
                self.conversation_id = None

        if not self.conversation_id:
            conversation = Conversation()
            self.session.add(conversation)
            self.session.commit()
            self.conversation_id = conversation.id

            system_message = Message(
                conversation_id=self.conversation_id,
                role="system",
                content="You are a helpful assistant. Keep your responses concise and clear."
            )
            self.session.add(system_message)
            self.session.commit()

            self.messages.append({
                "role": "system",
                "content": system_message.content
            })

            print(f"Started new conversation {self.conversation_id}")

        print("Type 'quit' or 'exit' to end the conversation.\n")

    def chat(self, user_input: str) -> str:
        user_message = Message(
            conversation_id=self.conversation_id,
            role="user",
            content=user_input
        )
        self.session.add(user_message)
        self.session.commit()

        self.messages.append({
            "role": "user",
            "content": user_input
        })

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                max_tokens=500,
                temperature=0.5,
            )

            bot_response: str = response.choices[0].message.content

            assistant_message = Message(
                conversation_id=self.conversation_id,
                role="assistant",
                content=bot_response
            )
            self.session.add(assistant_message)
            self.session.commit()

            self.messages.append({
                "role": "assistant",
                "content": bot_response
            })

            conversation = self.session.query(Conversation).filter_by(
                id=self.conversation_id
            ).first()
            if conversation and not conversation.title and len(self.messages) >= 3:
                conversation.title = user_input[:100]
                self.session.commit()

            return bot_response

        except Exception as e:
            error_msg: str = f"Error: {str(e)}"
            print(f"\n{error_msg}")
            return "I'm sorry, I encountered an error. Please try again."

    def run(self) -> None:
        print("ChatBot: Hi, how are you?")

        while True:
            try:
                user_input: str = input("\nYou: ").strip()

                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\nChatBot: Goodbye! Have a great day!")
                    break

                if not user_input:
                    continue

                print("\nChatBot: ", end="", flush=True)
                response: str = self.chat(user_input)
                print(response)

            except KeyboardInterrupt:
                print("\n\nChatBot: Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Please try again.")

        if self.session:
            self.session.close()


def list_conversations() -> None:
    session_gen = db.get_session()
    session = next(session_gen)

    conversations = session.query(Conversation).order_by(
        Conversation.updated_at.desc()
    ).all()

    if not conversations:
        print("No conversations found.")
        return

    print("\nPrevious conversations:")
    print("-" * 60)
    for conv in conversations:
        title = conv.title or f"Conversation {conv.id}"
        print(f"[{conv.id}] {title} - {conv.updated_at.strftime('%Y-%m-%d %H:%M')}")
    print("-" * 60)

    session.close()


def main() -> None:
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            list_conversations()
            return
        elif sys.argv[1] == "continue" and len(sys.argv) > 2:
            try:
                conversation_id = int(sys.argv[2])
                chatbot = ChatBot(conversation_id=conversation_id)
                chatbot.run()
                return
            except ValueError:
                print("Invalid conversation ID")
                return

    print("Starting new conversation...")
    print("Tip: Use 'python -m chatbot list' to see previous conversations")
    print("     Use 'python -m chatbot continue <id>' to resume a conversation\n")

    chatbot = ChatBot()
    chatbot.run()
