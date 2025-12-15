from transformers import pipeline

class Summarizer:
    def __init__(self):
        # Initialize the summarization pipeline using a free HuggingFace model
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def summarize_text(self, text: str, max_length: int = 130, min_length: int = 30, do_sample: bool = False) -> str:
        """
        Summarizes the given text using the HuggingFace summarization model.

        Args:
            text (str): The text to summarize.
            max_length (int): The maximum length of the summary.
            min_length (int): The minimum length of the summary.
            do_sample (bool): Whether to use sampling; use greedy decoding otherwise.

        Returns:
            str: The summarized text.
        """
        if not text:
            return "No content to summarize."

        summary = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=do_sample)
        return summary[0]['summary_text'] if summary else "Summary could not be generated."