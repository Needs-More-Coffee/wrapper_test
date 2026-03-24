import os
from pathlib import Path
from google import genai
from dotenv import load_dotenv

# Load .env from project root (one level up from this file)
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

DOCUMENTS_DIR = Path(__file__).parent / "documents"


class JediWrapper:

    def __init__(self):
        """
        Find the first .txt file in the documents folder and load it
        as the system instruction. This means you can name the governing
        document anything — just drop it in jedi/documents/ and it
        will be picked up automatically.
        """
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY environment variable not set. "
                "Check your .env file in the project root."
            )

        if not DOCUMENTS_DIR.exists():
            raise FileNotFoundError(
                f"Documents folder not found at: {DOCUMENTS_DIR}"
            )

        txt_files = list(DOCUMENTS_DIR.glob("*.txt"))
        if not txt_files:
            raise FileNotFoundError(
                f"No .txt governing document found in: {DOCUMENTS_DIR}"
            )

        governing_document_path = txt_files[0]

        with open(governing_document_path, "r", encoding="utf-8") as f:
            self.system_instruction = f.read()

        self.client = genai.Client(api_key=api_key)

    def respond(self, exchange_doc_path: str) -> str:
        """
        Read the full exchange document from disk and send it as the
        prompt to the Gemini model with the governing document as
        system instruction.

        Returns the model's response as a plain string.
        """
        exchange_path = Path(exchange_doc_path)

        if not exchange_path.exists():
            raise FileNotFoundError(
                f"Exchange document not found at: {exchange_doc_path}"
            )

        with open(exchange_path, "r", encoding="utf-8") as f:
            exchange_content = f.read()

        response = self.client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=exchange_content,
            config=genai.types.GenerateContentConfig(
                system_instruction=self.system_instruction
            )
        )

        return response.text