# Template Mapper

A Python tool for automatically mapping different data templates to a standardized format using machine learning and fuzzy matching techniques.

### Key Features

- Automatic column name mapping using machine learning
- Learns from example mappings
- Handles common naming variations and patterns
- Preserves data while standardizing format
- Supports both complete and partial data mapping

## Key Components

1. **Column Name Preprocessing**
   - Standardizes column names for better matching
   - Removes common variations and special characters
   - Handles different separator styles

2. **Mapping Algorithm**
   - TF-IDF vectorization for text similarity
   - Fuzzy string matching for handling variations
   - Pattern recognition for common naming conventions
   - Fallback rules for unmatched columns

3. **Data Transformation**
   - Preserves original data values
   - Handles missing columns gracefully
   - Maintains standard column order
   - Supports partial data mapping
