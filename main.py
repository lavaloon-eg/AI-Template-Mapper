import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
from typing import Dict, List, Tuple

class TemplateMapper:
    def __init__(self, standard_template: List[str]):
        """
        Initialize the template mapper with your standard template columns
        
        Args:
            standard_template: List of column names in your standard template
        """
        self.standard_template = standard_template
        self.vectorizer = TfidfVectorizer()
        self.column_vectors = None
        
    def preprocess_column_name(self, column: str) -> str:
        """Clean and standardize column names"""
        # More aggressive normalization
        processed = column.lower()
        processed = processed.replace('_', ' ').replace('-', ' ').replace('/', ' ')
        processed = processed.replace('name', '').replace('id', '').replace('date', '')
        return ' '.join(processed.split())
    
    def train_on_examples(self, mapping_examples: List[Dict[str, str]]):
        """
        Train the mapper using example mappings
        
        Args:
            mapping_examples: List of dictionaries mapping source columns to standard columns
        """
        # Create corpus of all possible column names and their mapped standard names
        self.training_mappings = {}  # Store training mappings for reference
        corpus = []
        
        for mapping in mapping_examples:
            for source, standard in mapping.items():
                processed_source = self.preprocess_column_name(source)
                corpus.append(processed_source)
                self.training_mappings[processed_source] = standard
                
        # Generate TF-IDF vectors for the corpus
        self.column_vectors = self.vectorizer.fit_transform(corpus)
    
    def map_template(self, input_template: List[str], threshold: float = 0.3) -> Dict[str, str]:
        """
        Map a new template to the standard template
        
        Args:
            input_template: List of column names from the new template
            threshold: Minimum similarity score to consider a match (lowered default)
            
        Returns:
            Dictionary mapping input columns to standard template columns
        """
        mappings = {}
        
        for input_col in input_template:
            processed_input = self.preprocess_column_name(input_col)
            
            # Direct match from training examples
            if processed_input in self.training_mappings:
                mappings[input_col] = self.training_mappings[processed_input]
                continue
            
            # Calculate similarity scores
            tfidf_similarity = self._get_tfidf_similarity(processed_input)
            fuzzy_scores = self._get_fuzzy_scores(processed_input)
            
            # Combine similarity scores with higher weight for fuzzy matching
            combined_scores = {
                std_col: (tfidf_similarity[std_col] * 0.3 + fuzzy_scores[std_col] * 0.7)
                for std_col in self.standard_template
            }
            
            # Find best match above threshold
            best_match = max(combined_scores.items(), key=lambda x: x[1])
            if best_match[1] >= threshold:
                mappings[input_col] = best_match[0]
            
        return mappings
    
    def _get_tfidf_similarity(self, input_col: str) -> Dict[str, float]:
        """Calculate TF-IDF based similarity scores"""
        input_vector = self.vectorizer.transform([input_col])
        similarities = {}
        
        for std_col in self.standard_template:
            std_vector = self.vectorizer.transform([self.preprocess_column_name(std_col)])
            similarity = cosine_similarity(input_vector, std_vector)[0][0]
            similarities[std_col] = similarity
            
        return similarities
    
    def _get_fuzzy_scores(self, input_col: str) -> Dict[str, float]:
        """Calculate fuzzy string matching scores"""
        scores = {}
        
        for std_col in self.standard_template:
            # Calculate both standard and partial ratios
            ratio = fuzz.ratio(input_col, self.preprocess_column_name(std_col))
            partial_ratio = fuzz.partial_ratio(input_col, self.preprocess_column_name(std_col))
            token_sort_ratio = fuzz.token_sort_ratio(input_col, self.preprocess_column_name(std_col))
            
            # Combine different fuzzy matching scores
            combined_ratio = (ratio + partial_ratio + token_sort_ratio) / (3 * 100)
            scores[std_col] = combined_ratio
            
        return scores

    def transform_data(self, data: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
        """
        Transform input data to match standard template exactly
        
        Args:
            data: Input DataFrame
            column_mapping: Dictionary mapping input columns to standard columns
            
        Returns:
            Transformed DataFrame with all standard template columns in correct order
        """
        # Create a new DataFrame with the same index as input
        result = pd.DataFrame(index=data.index)
        
        # Initialize all standard columns with None
        for std_col in self.standard_template:
            result[std_col] = None
            
        # Copy data from input columns using the mapping
        for input_col, std_col in column_mapping.items():
            if input_col in data.columns:
                result[std_col] = data[input_col]
        
        return result

def main():
    # Define your standard template
    standard_template = ['CUSTOMER_NUMBER', 'ACC_NO', 'Case', 'Customer_Name', 'BKT_IS','BKT_Was',]
    
    # Create mapper instance
    mapper = TemplateMapper(standard_template)
    
    # Training examples
    mapping_examples = [
        {
            'Act RIM': 'CUSTOMER_NUMBER',
            'APPLICATION ID': 'ACC_NO',
            'Case': 'Case',
            'CUST NAME': 'Customer_Name',
            'Is': 'BKT_IS',
            'Was': 'BKT_Was'
        },
        {
            'رقم القرض': 'CUSTOMER_NUMBER',
            'رقم حساب العميل': 'ACC_NO',
            'Case': 'Case',
            'اسم العميل': 'Customer_Name',
            'BKT': 'BKT_IS',
            'BKT': 'BKT_Was'
        },
        {
            'RIM': 'CUSTOMER_NUMBER',
            'Card Acc Number': 'ACC_NO',
            'Case': 'Case',
            'Customer Name': 'Customer_Name',
            'Is': 'BKT_IS',
            'Was': 'BKT_Was'
        }
    ]
    
    # Train the mapper
    mapper.train_on_examples(mapping_examples)
    
    # Test with complete data
    print("\nExample 1: Complete data")
    complete_data = pd.DataFrame({
        'RIM': ['13587', '11478'],
        'Card Acc': ['5558899662147521EG', '5558899662147521UK'],
        'Case': ['P123', 'P456'],
        'Customer Name': ["Ali", "Ahmed"],
        'Is': [99.99, 149.934],
        'Was': [88.99, 149.921]
    })
    
    mapping = mapper.map_template(complete_data.columns)
    print("\nGenerated mapping:", mapping)
    transformed_complete = mapper.transform_data(complete_data, mapping)
    print("\nTransformed complete data:")
    print(transformed_complete)
    
    # # Test with partial data
    # print("\nExample 2: Partial data")
    # partial_data = pd.DataFrame({
    #     'ClientName': ['Bob Wilson'],
    #     'ProdID': ['P789'],
    #     'Quantity': [2]
    # })
    
    # mapping = mapper.map_template(partial_data.columns)
    # print("\nGenerated mapping:", mapping)
    # transformed_partial = mapper.transform_data(partial_data, mapping)
    # print("\nTransformed partial data:")
    # print(transformed_partial)

if __name__ == "__main__":
    main()