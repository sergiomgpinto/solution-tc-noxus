import os
import sys
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class ChatBot:
    def __init__(self) -> None:
        api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
        model: Optional[str] = os.getenv("DEFAULT_MODEL")

        if not api_key or not model:
            print("Error: Keys not found in .env file")
            sys.exit(1)

        self.client: OpenAI = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model
        self.messages: List[Dict[str, str]] = []
        self.messages.append({
            "role": "system",
            "content": "You are a helpful assistant. Keep your responses concise and clear."
        })

        print(f"ChatBot initialized with model: {self.model}")
        print("Type 'quit' or 'exit' to end the conversation.\n")

    def chat(self, user_input: str) -> str:
        self.messages.append({
            "role": "user",
            "content": user_input
        })

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                max_tokens=500,
                temperature=0.4,
            )

            bot_response: str = response.choices[0].message.content

            self.messages.append({
                "role": "assistant",
                "content": bot_response
            })

            return bot_response

        except Exception as e:
            error_msg: str = f"Error: {str(e)}"
            print(f"\n{error_msg}")
            return "I'm sorry, I encountered an error. Please try again."

    def run(self) -> None:
        print("ChatBot: Hi, how are you?")

        while True:
            try:
                user_input: str = input("\nUser: ").strip()

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


def main() -> None:
    chatbot: ChatBot = ChatBot()
    chatbot.run()


if __name__ == "__main__":
    main()
