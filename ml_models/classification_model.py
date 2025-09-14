from transformers import pipeline

class DocumentClassifier:
    """Classifies documents using a zero-shot approach."""
    
    def __init__(self):
        # Use a zero-shot classification pipeline from Hugging Face
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        self.candidate_labels = [
            "Finance",
            "HR",
            "Technical Reports",
            "Contracts",
            "Invoices",
            "Legal",
            "Marketing",
            "Project Management"
        ]

    def classify_document(self, text: str) -> str:
        """
        Classifies the document text into one of the predefined categories.
        
        Args:
            text: The content of the document.
        
        Returns:
            The predicted category with the highest confidence.
        """
        # Truncate text to fit model's max sequence length (512)
        truncated_text = text[:512]
        result = self.classifier(truncated_text, self.candidate_labels)
        
        return result['labels'][0]